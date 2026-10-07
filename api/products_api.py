import requests
from api.base_api import BaseApi


class ProductsApi(BaseApi):
    ENDPOINT = "productsList"
    SEARCH_ENDPOINT = "searchProduct"

    def get_all_products(self) -> requests.Response:
        return self.get(self.ENDPOINT)

    def post_products_list(self) -> requests.Response:
        # API returns 405 for POST — used in negative tests
        return self.post(self.ENDPOINT)

    def search_product(self, search_product: str) -> requests.Response:
        return self.post(self.SEARCH_ENDPOINT, data={"search_product": search_product})

    def search_without_param(self) -> requests.Response:
        # Missing required param — expects responseCode 400
        return self.post(self.SEARCH_ENDPOINT)
