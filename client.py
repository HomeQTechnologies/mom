import requests


class Mother:

    def __init__(self, domain, token):
        self.domain = domain
        self.token = token

    def nuture(self, child_name, raise_exc=False):
        try:
            response = requests.post(f'{self.domain}/api/v1/nurture/{child_name}?token={self.token}')
            if response.status_code != 200:
                raise AssertionError("Mom responded with non 200 status code.")
        except Exception as e:
            if raise_exc:
                raise e
