import pytest
from api.products_api import ProductsApi


@pytest.fixture(scope="module")
def products_api(api_base_url: str) -> ProductsApi:
    return ProductsApi(api_base_url)


@pytest.mark.api
class TestProductsApi:
    @pytest.mark.smoke
    def test_get_all_products_returns_200(self, products_api: ProductsApi) -> None:
        response = products_api.get_all_products()
        assert response.status_code == 200

    def test_get_all_products_returns_list(self, products_api: ProductsApi) -> None:
        data = products_api.get_all_products().json()
        assert data["responseCode"] == 200
        assert "products" in data
        assert len(data["products"]) > 0

    def test_product_has_required_fields(self, products_api: ProductsApi) -> None:
        products = products_api.get_all_products().json()["products"]
        for product in products:
            assert "id" in product
            assert "name" in product
            assert "price" in product
            assert "category" in product

    def test_post_products_list_returns_405(self, products_api: ProductsApi) -> None:
        data = products_api.post_products_list().json()
        assert data["responseCode"] == 405

    def test_search_product_returns_results(self, products_api: ProductsApi) -> None:
        data = products_api.search_product("top").json()
        assert data["responseCode"] == 200
        assert len(data["products"]) > 0

    def test_search_product_without_param_returns_400(self, products_api: ProductsApi) -> None:
        data = products_api.search_without_param().json()
        assert data["responseCode"] == 400
