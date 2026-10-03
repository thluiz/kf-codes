---
title: "Space shooter multiplayer com Phoenix — 6º ELUG RJ"
date: "2016-07-14"
description: "Um jogo de naves em tempo real com Phoenix Channels, Phoenix Presence e Phaser.js, apresentado no sexto encontro do ELUG RJ."
tags: ["tecnico", "elixir", "phoenix", "gamedev"]
canonicalURL: "https://silva.thluiz.com/posts/space-shooter-phoenix-elug-rj-6/"
silvaeSlug: "space-shooter-phoenix-elug-rj-6"
silvaeCommit: "8c5583805d153c511bda20803892e40f806d6020"
---
No sexto encontro do [ELUG RJ](https://github.com/elug-rj) apresentei uma demonstração de **Phoenix Channels e Phoenix Presence** usando um formato que funcionou bem: um jogo de naves multiplayer ao vivo, com todos no evento conectados pelo browser.

O projeto ([sexto_elug_rj](https://github.com/thluiz/sexto_elug_rj)) usava o [Phaser.js](https://phaser.io/) no frontend para renderizar as naves e o Phoenix como espinha dorsal do servidor — cada movimento e disparo passava por um Channel, e o estado completo do jogo era reenviado a todos os clientes a cada 100ms via um `GenServer` (`GameBroadcaster`).

---

A arquitetura tinha três peças principais:

**GameState** — um `Agent` que mantinha as posições de todos os jogadores e projéteis. Ele também fazia a detecção de colisões no servidor: distância euclidiana menor que 50 unidades entre um projétil e um jogador contava como acerto.

**GameBroadcaster** — um `GenServer` com timer de 100ms que fazia `broadcast!` do estado atual para todos os clientes conectados no canal `spaceship:lobby`.

**Phoenix Presence** — usado para rastrear jogadores conectados e lidar com desconexões limpamente, sem deixar naves fantasmas voando pela tela.

---

O ponto da apresentação era mostrar que o Phoenix não precisa ceder nada para casos de uso em tempo real que normalmente justificariam Node.js. O modelo de atores do Elixir — um processo por jogador, estado compartilhado via Agent, broadcast pelo PubSub — encaixa naturalmente nesse tipo de problema.

A demo rodou no Heroku durante o evento para que todos pudessem entrar pelo celular sem configuração local.

Código: [github.com/thluiz/sexto_elug_rj](https://github.com/thluiz/sexto_elug_rj) — Phoenix 1.2, Elixir 1.2, Phaser.js v2.
