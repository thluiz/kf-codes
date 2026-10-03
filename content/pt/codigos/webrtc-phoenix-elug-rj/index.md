---
title: "WebRTC com Phoenix — ELUG RJ"
date: "2016-04-15"
description: "Como usar Phoenix Channels como servidor de sinalização para chamadas de vídeo peer-to-peer com WebRTC."
tags: ["tecnico", "elixir", "phoenix", "webrtc"]
canonicalURL: "https://silva.thluiz.com/posts/webrtc-phoenix-elug-rj/"
silvaeSlug: "webrtc-phoenix-elug-rj"
silvaeCommit: "8c5583805d153c511bda20803892e40f806d6020"
---
Em maio de 2016 apresentei no [ELUG RJ](https://github.com/elug-rj) — o grupo de usuários Elixir do Rio de Janeiro — uma demonstração de como usar **Phoenix Channels como servidor de sinalização para WebRTC**.

O projeto ([quartoElugRJ](https://github.com/thluiz/quartoElugRJ)) tinha duas partes:

**SimpleChat** — um chat em tempo real usando Phoenix Channels. Cada usuário recebe um nome aleatório via `chance.js` e as mensagens são transmitidas para todos os clientes conectados via um canal `lobby:lobby`.

**Chamada de vídeo** — uma chamada peer-to-peer usando a API nativa do browser (`RTCPeerConnection`), com Phoenix atuando apenas como intermediário para trocar os metadados da conexão: SDP offers, SDP answers e ICE candidates. Uma vez estabelecida a conexão, o stream de vídeo e áudio vai diretamente entre os browsers — o servidor sai do caminho.

---

O ponto central da demonstração era que o Phoenix não precisa entender nada sobre WebRTC. O `WebRTCChannel` faz apenas um `broadcast!` das mensagens de sinalização entre os peers — é um carteiro. Toda a lógica de negociação fica no frontend em JavaScript.

O projeto rodava em um ambiente Codio para evitar problemas de configuração local durante a apresentação — um STUN server do próprio Codio cuidava da travessia de NAT.

Código: [github.com/thluiz/quartoElugRJ](https://github.com/thluiz/quartoElugRJ) — Phoenix 1.1.4, Elixir 1.x, Brunch, ES2015.
