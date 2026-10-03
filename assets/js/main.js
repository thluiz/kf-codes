// Comportamento do header e dos posts, equivalente aos web components do Silva
// (ThemeToggle, mobile-button, site-search e o botão de voltar ao topo).
(function () {
  var root = document.documentElement;

  // Tema
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    var sync = function () { toggle.setAttribute("aria-checked", String(root.getAttribute("data-theme") === "dark")); };
    sync();
    toggle.addEventListener("click", function () {
      window.setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
      sync();
    });
  }

  // Menu mobile
  var header = document.getElementById("main-header");
  var menuBtn = document.querySelector(".menu-toggle");
  if (header && menuBtn) {
    menuBtn.addEventListener("click", function () {
      var open = header.classList.toggle("menu-open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
  }

  // Busca: Pagefind UI carregada sob demanda (o índice é gerado por site, em /pagefind/)
  var search = document.getElementById("search");
  if (search) {
    var dialog = search.querySelector("dialog");
    var frame = search.querySelector(".dialog-frame");
    var bundle = dialog.getAttribute("data-bundle");
    var loaded = false;

    var loadUI = function () {
      if (loaded) return;
      loaded = true;
      var css = document.createElement("link");
      css.rel = "stylesheet";
      css.href = bundle + "pagefind-ui.css";
      document.head.appendChild(css);
      var s = document.createElement("script");
      s.src = bundle + "pagefind-ui.js";
      s.onload = function () {
        new PagefindUI({ element: "#site__search", bundlePath: bundle, showImages: false, showSubResults: true });
        var input = search.querySelector("input");
        if (input) input.focus();
      };
      document.head.appendChild(s);
    };

    var onWindowClick = function (e) {
      var isLink = "href" in (e.target || {});
      if (isLink || (document.body.contains(e.target) && !frame.contains(e.target))) close();
    };
    var open = function (e) {
      loadUI();
      dialog.showModal();
      var input = search.querySelector("input");
      if (input) input.focus();
      if (e) e.stopPropagation();
      window.addEventListener("click", onWindowClick);
    };
    var close = function () { dialog.close(); };
    dialog.addEventListener("close", function () { window.removeEventListener("click", onWindowClick); });

    search.querySelector("[data-open-modal]").addEventListener("click", open);
    search.querySelector("[data-close-modal]").addEventListener("click", close);
    window.addEventListener("keydown", function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        dialog.open ? close() : open();
        e.preventDefault();
      }
    });
  }

  // Botão de copiar nos blocos de código (o Silva tem o mesmo via expressive-code)
  var copyLabel = root.lang.indexOf("en") === 0 ? ["Copy", "Copied"] : ["Copiar", "Copiado"];
  document.querySelectorAll(".prose .highlight").forEach(function (block) {
    var code = block.querySelector("code");
    if (!code || !navigator.clipboard) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-code";
    btn.textContent = copyLabel[0];
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(code.innerText).then(function () {
        btn.textContent = copyLabel[1];
        setTimeout(function () { btn.textContent = copyLabel[0]; }, 1500);
      });
    });
    block.appendChild(btn);
  });

  // Voltar ao topo: aparece quando o cabeçalho do post sai da tela
  var toTop = document.getElementById("to-top-btn");
  var hero = document.getElementById("blog-hero");
  if (toTop && hero && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) { toTop.dataset.show = String(!entry.isIntersecting); });
    }).observe(hero);
    toTop.addEventListener("click", function () { root.scrollTo({ behavior: "smooth", top: 0 }); });
  }
})();
