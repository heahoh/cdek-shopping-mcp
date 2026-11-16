Raw OpenAPI/Swagger specs for the cdek.shopping front-controller API, fetched from
https://api.cdek.shopping/front-controller/swagger/index.html (choices: `superapp`, `nuxt`, `shopping`).

Kept here as the reference for extending the MCP server with more tools. Note the
swagger UI rewrites `/api/v1/...` paths to `/front-controller/v1/...` for actual
requests — the client in this repo already targets the rewritten base URL.
