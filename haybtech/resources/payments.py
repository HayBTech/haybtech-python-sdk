import json
from typing import Optional, Dict, Any

class HayBTechResponse(dict):
    """
    Enhanced dictionary with helper methods for HayBTech responses.
    """
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

    def redirect_url(self) -> Optional[str]:
        return self.get('data', {}).get('payment_url')

    def to_django_redirect(self):
        """
        Helper for Django users.
        Usage: return response.to_django_redirect()
        """
        try:
            from django.shortcuts import redirect
            url = self.redirect_url()
            if url:
                return redirect(url)
        except ImportError:
            pass
        return None

    @property
    def successful(self) -> bool:
        # Standard status code check isn't available here as we are a dict wrapper
        # but usually if we are here (not exception), it's a 2xx
        return True

class Payments:
    def __init__(self, client):
        self.client = client

    def create(self, params: Dict[str, Any], idempotency_key: str = "") -> HayBTechResponse:
        headers = {'Idempotency-Key': idempotency_key} if idempotency_key else {}
        response = self.client.request('POST', 'payments', params, headers)
        return HayBTechResponse(response)

    def retrieve(self, id: str) -> HayBTechResponse:
        return HayBTechResponse(self.client.request('GET', f'payments/{id}'))

    def list(self, params: Optional[Dict[str, Any]] = None) -> HayBTechResponse:
        import urllib.parse
        path = 'payments'
        if params:
            path += '?' + urllib.parse.urlencode(params)
        return HayBTechResponse(self.client.request('GET', path))

    def verify(self, id: str) -> HayBTechResponse:
        return HayBTechResponse(self.client.request('POST', f'payments/{id}/verify'))
