import json
import urllib.request
import urllib.error
import hmac
import hashlib
import time
import uuid
import sys
import os
from typing import Optional, Dict, Any, Union
from .resources.payments import Payments
from .resources.webhooks import Webhooks

class HayBTechException(Exception):
    """Base exception for HayBTech SDK"""
    pass

class ApiException(HayBTechException):
    """Exception for API errors"""
    def __init__(self, message, status_code, error_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.response_data = response_data

class HayBTechClient:
    """
    HayBTech Python Client - Hardened for maximum security.
    """
    def __init__(self, secret_key: Optional[str] = None, options: Optional[Dict[str, Any]] = None):
        secret_key = secret_key or os.getenv('HAYBTECH_SECRET_KEY')
        if not secret_key or not secret_key.startswith('sk_'):
            raise HayBTechException("Invalid secret key. Expected 'sk_live_...' or 'sk_test_...' or set HAYBTECH_SECRET_KEY environment variable.")

        # Prevent CRLF injection in headers
        if '\r' in secret_key or '\n' in secret_key:
            raise HayBTechException("Invalid secret_key: contains forbidden characters.")

        self._secret_key = secret_key
        options = options or {}
        
        # Security: Use getenv or default, avoid hardcoding secrets
        self.base_url = options.get('base_url') or 'https://api.haybtech.com/v1'
        self.timeout = options.get('timeout') or 15

        self.payments = Payments(self)
        self.webhooks = Webhooks(self)

    def __repr__(self):
        """Security: Mask secret key in representation"""
        return f"<HayBTechClient base_url={self.base_url} is_test={self.is_test_mode()} secret_key=sk_...{self._secret_key[-4:]}>"

    def __getstate__(self):
        """Security: Prevent pickling of secret key"""
        state = self.__dict__.copy()
        state['_secret_key'] = '********'
        return state

    def is_test_mode(self) -> bool:
        return self._secret_key.startswith('sk_test_')

    def request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        
        headers = {
            'Authorization': f'Bearer {self._secret_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Request-ID': str(uuid.uuid4()),
            'User-Agent': f'HayBTech-Python-SDK/1.0.0 Python/{sys.version_info.major}.{sys.version_info.minor}'
        }
        
        if extra_headers:
            headers.update(extra_headers)

        data = json.dumps(body).encode('utf-8') if body else None
        
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                res_body = response.read().decode('utf-8')
                return json.loads(res_body)
        except urllib.error.HTTPError as e:
            res_body = e.read().decode('utf-8')
            try:
                data = json.loads(res_body)
                error = data.get('error', {})
                raise ApiException(
                    error.get('message', 'Unknown API Error'),
                    e.code,
                    error.get('code'),
                    self._sanitize(data)
                )
            except json.JSONDecodeError:
                raise ApiException(f"API Error: {e.reason}", e.code)
        except urllib.error.URLError as e:
            raise HayBTechException(f"Connection Error: {e.reason}")

    def _sanitize(self, data: Any) -> Any:
        """Security: Remove sensitive fields from data"""
        sensitive = {'secret', 'password', 'token', 'key', 'pin', 'cvv'}
        
        if isinstance(data, dict):
            return {k: ('********' if k.lower() in sensitive else self._sanitize(v)) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize(v) for v in data]
        return data
