import requests
from api.base_api import BaseApi


class BrandsApi(BaseApi):
    ENDPOINT = "brandsList"

    def get_all_brands(self) -> requests.Response:
        return self.get(self.ENDPOINT)

    def put_brands_list(self) -> requests.Response:
        # API returns 405 for PUT — used in negative tests
        return self.put(self.ENDPOINT)
