import pytest
from api.brands_api import BrandsApi


@pytest.fixture(scope="module")
def brands_api(api_base_url: str) -> BrandsApi:
    return BrandsApi(api_base_url)


@pytest.mark.api
class TestBrandsApi:
    @pytest.mark.smoke
    def test_get_all_brands_returns_200(self, brands_api: BrandsApi) -> None:
        response = brands_api.get_all_brands()
        assert response.status_code == 200

    def test_get_all_brands_returns_list(self, brands_api: BrandsApi) -> None:
        data = brands_api.get_all_brands().json()
        assert data["responseCode"] == 200
        assert "brands" in data
        assert len(data["brands"]) > 0

    def test_brand_has_required_fields(self, brands_api: BrandsApi) -> None:
        brands = brands_api.get_all_brands().json()["brands"]
        for brand in brands:
            assert "id" in brand
            assert "brand" in brand

    def test_put_brands_list_returns_405(self, brands_api: BrandsApi) -> None:
        data = brands_api.put_brands_list().json()
        assert data["responseCode"] == 405
