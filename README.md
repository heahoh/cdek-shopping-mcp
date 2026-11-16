# cdek-shopping-mcp

An [MCP](https://modelcontextprotocol.io) server for the [cdek.shopping](https://cdek.shopping) storefront API. It exposes catalog browsing, search, product details, reviews and recommendations as tools an MCP client (Claude, Claude Code, etc.) can call.

This is an early, read-focused release. More endpoints/tools (orders, cart, etc.) will be added over time — see [specs/](specs) for the full raw API surface this server can grow into.

## Tools

| Tool | Description |
| --- | --- |
| `catalog_categories` | List catalog categories / subcategories |
| `search_products` | Search products, brands and categories |
| `search_autocomplete` | Search-box autocomplete suggestions |
| `get_product` | Full product details by ID |
| `get_product_summary` | Compact product summary card |
| `product_reviews` | Customer reviews for a product |
| `list_category_products` | Products inside a catalog category |
| `list_collection_products` | Products inside a curated collection |
| `recommendations` | Personalized/related product recommendations |
| `list_orders` | List the authenticated user's orders (requires a token) |

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/heahoh/cdek-shopping-mcp.git
cd cdek-shopping-mcp
uv sync
```

### Use with an MCP client

Add to your client's MCP server config (e.g. Claude Desktop/Code `mcp.json`):

```json
{
  "mcpServers": {
    "cdek-shopping": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/cdek-shopping-mcp", "run", "cdek-shopping-mcp"]
    }
  }
}
```

Or, once published, run it directly from GitHub with `uvx`:

```bash
uvx --from git+https://github.com/heahoh/cdek-shopping-mcp cdek-shopping-mcp
```

## Configuration

All configuration is via environment variables, all optional:

| Variable | Default | Purpose |
| --- | --- | --- |
| `CDEK_SHOPPING_BASE_URL` | `https://api.cdek.shopping/front-controller/v1` | API base URL |
| `CDEK_SHOPPING_TOKEN` | _(none)_ | Bearer token for authenticated endpoints (e.g. `list_orders`) |
| `CDEK_SHOPPING_LANG` | `ru` | `Accept-Language` header sent on every request |

## Development

```bash
uv sync
uv run cdek-shopping-mcp          # run the server over stdio
uv run mcp dev src/cdek_shopping_mcp/server.py  # run with the MCP inspector
```

## License

MIT
