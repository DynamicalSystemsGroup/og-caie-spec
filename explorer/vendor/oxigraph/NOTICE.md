# oxigraph, WebAssembly build for the web

- Package: `oxigraph` 0.5.11 from npm (files `web.js` and `web_bg.wasm`,
  the `web` target only; the Node target is not vendored).
- Source: https://github.com/oxigraph/oxigraph
- Licence: MIT OR Apache-2.0, at the user's option. Copyright the Oxigraph
  contributors. The licence texts are in the source repository above.
- Used by `explorer/index.html` for the optional in-browser SPARQL box over
  copies of this repository's Turtle files (`explorer/data/`). The d3
  explorer does not depend on it; the machine interface remains `ogc sparql`.
