from typing import Optional, Dict, Any

class Webhooks:
    def __init__(self, client):
        self.client = client

    def all(self):
        return self.client.request('GET', 'webhooks')

    def create(self, params: Dict[str, Any]):
        return self.client.request('POST', 'webhooks', params)

    def reveal(self, id: str, otp: Optional[str] = None):
        body = {'otp': otp} if otp else {}
        return self.client.request('POST', f'webhooks/{id}/reveal', body)

    def rotate(self, id: str, otp: Optional[str] = None):
        body = {'otp': otp} if otp else {}
        return self.client.request('POST', f'webhooks/{id}/rotate', body)

    def test(self, id: str):
        return self.client.request('POST', f'webhooks/{id}/test')

    def delete(self, id: str, otp: Optional[str] = None):
        headers = {'X-OTP': otp} if otp else {}
        return self.client.request('DELETE', f'webhooks/{id}', extra_headers=headers)
