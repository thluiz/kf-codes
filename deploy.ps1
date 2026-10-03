#Requires -Version 7
param(
    [switch]$SkipBuild,
    [switch]$ForceFullSync,
    [string[]]$Lang = @('pt', 'en', 'es')
)

$ErrorActionPreference = "Stop"

$REPO_DIR   = $PSScriptRoot
$PUBLIC_DIR = "$REPO_DIR\public"
$STATE_DIR  = "$REPO_DIR\.deploy"

$AWS_PROFILE = "scholion-admin"
$REGION      = "us-east-1"
$AWS_EXE     = (Get-Command aws -ErrorAction Stop).Source

# Um bucket + uma distribuição por idioma (Hugo multihost: public/<lang>/)
$SITES = @{
    pt = @{ Domain = "codigoskungfu.com"; Bucket = "s3://codigoskungfu-com"; CF = "EK2VP6A6SJGYU" }
    en = @{ Domain = "kungfu.codes";      Bucket = "s3://kungfu-codes";      CF = "E338DCHVHBSHR6" }
    es = @{ Domain = "codigoskungfu.eu";  Bucket = "s3://codigoskungfu-eu";  CF = "E3OF7PAIONYLFN" }
}

function aws { & $AWS_EXE --profile $AWS_PROFILE --region $REGION @args }

Set-Location $REPO_DIR

if (-not $SkipBuild) {
    Write-Host "==> hugo build" -ForegroundColor Cyan
    hugo --minify --gc --cleanDestinationDir
    if ($LASTEXITCODE -ne 0) { throw "Hugo build failed" }
    # O --gc apaga do resources/_gen arquivos que ainda estão versionados; devolve para não sujar o git
    git checkout -- resources 2>$null

    # Busca (Pagefind, como no Silva): um índice por site, em public/<lang>/pagefind/
    foreach ($l in $SITES.Keys) {
        Write-Host "==> pagefind [$l]" -ForegroundColor Cyan
        npx -y pagefind@1.5.2 --site "public/$l" | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Pagefind failed for $l" }
    }
}

# Posts que vieram do Silva: só avisa se algum mudou lá desde a importação
$env:PYTHONIOENCODING = "utf-8"
python scripts/silvae.py check
if ($LASTEXITCODE -ne 0) {
    Write-Host "AVISO: há posts desatualizados em relação ao Silva (python scripts/silvae.py pull --outdated)" -ForegroundColor Yellow
}

New-Item -ItemType Directory -Force $STATE_DIR | Out-Null

foreach ($l in $Lang) {
    $site = $SITES[$l]
    if (-not $site) { throw "Idioma desconhecido: $l" }
    $srcDir   = Join-Path $PUBLIC_DIR $l
    $manifest = Join-Path $STATE_DIR "manifest-$l.json"
    if (-not (Test-Path $srcDir)) { throw "Build sem $srcDir" }

    Write-Host "==> [$l] $($site.Domain)" -ForegroundColor Cyan

    $prevManifest = @{}
    if ((Test-Path $manifest) -and -not $ForceFullSync) {
        $prevManifest = Get-Content $manifest -Raw | ConvertFrom-Json -AsHashtable
    }

    # O site é pequeno: hash de tudo a cada deploy, upload só do que diferir.
    # Nunca 's3 sync': o Hugo reescreve o mtime de todo o public/ a cada build.
    $newManifest = @{}
    Get-ChildItem $srcDir -Recurse -File | Where-Object { $_.Name -ne '.DS_Store' } | ForEach-Object -Parallel {
        [PSCustomObject]@{
            Rel  = $_.FullName.Substring($using:srcDir.Length + 1)
            Hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        }
    } -ThrottleLimit 16 | ForEach-Object { $newManifest[$_.Rel] = $_.Hash }

    $toUpload = @($newManifest.Keys | Where-Object { $prevManifest[$_] -ne $newManifest[$_] })
    $toDelete = @($prevManifest.Keys | Where-Object { -not $newManifest.ContainsKey($_) })

    # O Pagefind serializa o índice de filtros (tags) em ordem variável: sem nenhuma página
    # mudar, pagefind-entry.json e dois .pf_* mudam a cada build. Se só isso mudou, o índice
    # no ar continua valendo para as mesmas páginas; não sobe nada.
    $changed = @($toUpload) + @($toDelete)
    if ($changed.Count -gt 0 -and -not ($changed | Where-Object { $_ -notmatch '^pagefind\\' })) {
        Write-Host "  só o índice do Pagefind mudou (ordem não determinística) — skip S3" -ForegroundColor Yellow
        continue
    }

    Write-Host "  upload: $($toUpload.Count) | delete: $($toDelete.Count)"
    if ($toUpload.Count -eq 0 -and $toDelete.Count -eq 0) {
        Write-Host "  sem alterações — skip S3" -ForegroundColor Yellow
        continue
    }

    if ($toUpload.Count -gt 0) {
        $uploadErrors = $toUpload | ForEach-Object -Parallel {
            $rel   = $_
            $s3Key = $rel.Replace('\', '/')
            $cc    = if ($rel -match '\.(html|xml|json|txt)$') {
                         "public, max-age=3600"
                     } else {
                         "public, max-age=31536000, immutable"
                     }
            $out = & $using:AWS_EXE --profile $using:AWS_PROFILE --region $using:REGION s3 cp `
                       (Join-Path $using:srcDir $rel) "$($using:site.Bucket)/$s3Key" `
                       --cache-control $cc --only-show-errors 2>&1
            if ($LASTEXITCODE -ne 0) { "FAIL: $s3Key — $out" }
        } -ThrottleLimit 16 | Where-Object { $_ }

        if ($uploadErrors) { throw "Falhas no upload:`n$($uploadErrors -join "`n")" }
    }

    foreach ($rel in $toDelete) {
        aws s3 rm "$($site.Bucket)/$($rel.Replace('\','/'))" --only-show-errors
    }

    $inv = aws cloudfront create-invalidation --distribution-id $site.CF --paths "/*" | ConvertFrom-Json
    Write-Host "  invalidation $($inv.Invalidation.Id) $($inv.Invalidation.Status)"

    # Grava só depois do upload OK: uma falha no meio força re-upload no próximo deploy
    $newManifest | ConvertTo-Json -Compress | Set-Content $manifest -Encoding UTF8
}

Write-Host "==> done" -ForegroundColor Green
