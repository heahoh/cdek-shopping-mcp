"""MCP server exposing the cdek.shopping storefront API as tools.

Covers catalog browsing, search, product details/reviews and recommendations.
Most endpoints are public; order listing requires CDEK_SHOPPING_TOKEN to be set.
See README.md for the full tool list and ./specs for the raw OpenAPI sources.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from .client import CdekShoppingClient

mcp = MCPServer("cdek-shopping")
_client = CdekShoppingClient()


@mcp.tool()
async def catalog_categories(parent_id: int | None = None) -> Any:
    """List catalog categories, optionally the children of a given category.

    Args:
        parent_id: ID of the parent category. Omit to get the top-level tree.
    """
    path = "/catalogCategories" if parent_id is None else f"/catalogCategories/{parent_id}"
    return await _client.request("GET", path)


@mcp.tool()
async def search_products(
    q: str | None = None,
    filter: list[str] | None = None,
    sort: str | None = None,
    page: int | None = None,
    per_page: int | None = None,
    only_filters: bool | None = None,
) -> Any:
    """Search products, brands and categories in the cdek.shopping catalog.

    Args:
        q: Free-text search query, e.g. "Apple смартфон синий".
        filter: Facet filters as "key=value" strings (from a prior search response).
        sort: One of PRICE_ASC, PRICE_DESC, DEFAULT.
        page: Page number, 1-based.
        per_page: Results per page (max 100).
        only_filters: If true, return only the available filters, not results.
    """
    params = {
        "q": q,
        "filter": filter,
        "sort": sort,
        "page": page,
        "perPage": per_page,
        "onlyFilters": only_filters,
    }
    return await _client.request("GET", "/search", params=params)


@mcp.tool()
async def search_autocomplete(q: str) -> Any:
    """Get search-box autocomplete suggestions for a partial query.

    Args:
        q: Partial search text typed by the user.
    """
    return await _client.request("GET", "/search/autocomplete", params={"q": q})


@mcp.tool()
async def get_product(product_id: int) -> Any:
    """Get full details for a single product by ID."""
    return await _client.request("GET", f"/nuxt/product/{product_id}")


@mcp.tool()
async def get_product_summary(product_id: int) -> Any:
    """Get a short summary card for a product (for compact display/embedding)."""
    return await _client.request("GET", f"/nuxt/product/{product_id}/summary")


@mcp.tool()
async def product_reviews(
    product_id: int,
    has_media: bool | None = None,
    has_text: bool | None = None,
    page: int | None = None,
    per_page: int | None = None,
    sort_field: str | None = None,
    sort_order: str | None = None,
) -> Any:
    """List customer reviews for a product.

    Args:
        product_id: Product ID.
        has_media: If true, only reviews that include photos/video.
        has_text: If true, only reviews that include written text.
        page: Page number, 1-based.
        per_page: Reviews per page.
        sort_field: Field to sort by (e.g. date, rating).
        sort_order: Sort direction (asc/desc).
    """
    params = {
        "hasMedia": has_media,
        "hasText": has_text,
        "page": page,
        "perPage": per_page,
        "sort_field": sort_field,
        "sort_order": sort_order,
    }
    return await _client.request("GET", f"/nuxt/product/{product_id}/reviews", params=params)


@mcp.tool()
async def list_category_products(
    category_id: int,
    sort: str | None = None,
    page: int | None = None,
    per_page: int | None = None,
) -> Any:
    """List products inside a given catalog category.

    Args:
        category_id: Category ID (see catalog_categories).
        sort: One of PRICE_ASC, PRICE_DESC, DEFAULT.
        page: Page number, 1-based.
        per_page: Results per page.
    """
    params = {"sort": sort, "page": page, "perPage": per_page}
    return await _client.request("POST", f"/category/{category_id}", params=params)


@mcp.tool()
async def list_collection_products(
    collection_id: int,
    sort: str | None = None,
    page: int | None = None,
    per_page: int | None = None,
) -> Any:
    """List products inside a given curated collection/subselection.

    Args:
        collection_id: Collection ID.
        sort: One of PRICE_ASC, PRICE_DESC, DEFAULT.
        page: Page number, 1-based.
        per_page: Results per page.
    """
    params = {"sort": sort, "page": page, "perPage": per_page}
    return await _client.request("POST", f"/collection/{collection_id}", params=params)


@mcp.tool()
async def hot_offers(widget: str | None = None, user_history: str | None = None) -> Any:
    """Get the "hot offers" widget shown on the home screen.

    Args:
        widget: Specific widget variant to request, if any.
        user_history: Opaque user-history token used to personalize results.
    """
    params = {"widget": widget, "userHistory": user_history}
    return await _client.request("GET", "/hot-offers", params=params)


@mcp.tool()
async def main_structure(user_history: str | None = None) -> Any:
    """Get the structure of the app's main/home screen (banners, widgets, etc).

    Args:
        user_history: Opaque user-history token used to personalize results.
    """
    return await _client.request("GET", "/main/structure", params={"userHistory": user_history})


@mcp.tool()
async def recommendations(
    placements: list[str],
    product_id: list[int] | None = None,
    category_id: int | None = None,
    region_id: str | None = None,
    page: int | None = None,
    per_page: int | None = None,
    user_history: str | None = None,
) -> Any:
    """Get personalized/related product recommendations for given placements.

    Args:
        placements: Required list of placement codes identifying where the
            recommendations will be shown (e.g. "product_page", "cart").
        product_id: Product IDs to base "related to this" recommendations on.
        category_id: Category ID to scope recommendations to.
        region_id: Region/location ID affecting availability and pricing.
        page: Page number, 1-based.
        per_page: Results per page.
        user_history: Opaque user-history token used to personalize results.
    """
    params = {
        "placements": placements,
        "productId": product_id,
        "categoryId": category_id,
        "regionId": region_id,
        "page": page,
        "perPage": per_page,
        "userHistory": user_history,
    }
    return await _client.request("GET", "/nuxt/recommendations", params=params)


@mcp.tool()
async def list_orders() -> Any:
    """List the authenticated user's orders.

    Requires the CDEK_SHOPPING_TOKEN environment variable to be set to a
    valid bearer token; otherwise this returns an authentication error.
    """
    return await _client.request("GET", "/order/list", require_auth=True)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
