# services/mcp

Servidor MCP del producto DATA: tools sobre servicios de dominio, nunca SQL libre.

Desde MCP-001 (D-225) tiene herramientas de solo lectura por stdio: `buscar_zonas`, `que_falta`, `explicar_zona`, `encontrar_zona` y `fuentes_de_datos`, y desde D-249 las dos de inversores, `ficha_inversor` y `viabilidad` (7 en total). Se arranca con `make mcp`. Desde D-255 también está en remoto, sin instalar nada, en `https://vidafacil-madrid.vercel.app/api/v1/mcp` (`hi_mcp/http.py`, servido junto a la API). La página pública para desarrolladores es `/desarrolladores`. Uso, configuración de clientes y pruebas: `docs/04_technical_architecture/32_mcp_server.md`. Contratos de diseño: `docs/04_technical_architecture/10_mcp_contracts_detailed.md`.
