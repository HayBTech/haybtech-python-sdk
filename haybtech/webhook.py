import hmac
import hashlib
import json
import time
from typing import Dict, Any

class SignatureException(Exception):
    pass

class Webhook:
    TOLERANCE = 300  # 5 minutes
    MAX_SIZE = 1024 * 1024  # 1MB

    @staticmethod
    def construct_event(payload: str, signature_header: str, secret: str) -> Dict[str, Any]:
        """
        Verify the signature and return the event payload.
        """
        if not payload or not signature_header or not secret:
            raise SignatureException("Missing required parameters.")

        if len(payload) > Webhook.MAX_SIZE:
            raise SignatureException("Payload too large.")

        # Parse header: t=123,v1=abc
        try:
            parts = {k.strip(): v.strip() for k, v in (p.split('=') for p in signature_header.split(','))}
        except ValueError:
            raise SignatureException("Invalid signature header format.")

        if 't' not in parts or 'v1' not in parts:
            raise SignatureException("Malformed signature header.")

        timestamp = int(parts['t'])
        received_sig = parts['v1']

        # Replay protection
        if abs(time.time() - timestamp) > Webhook.TOLERANCE:
            raise SignatureException("Webhook signature expired (replay protection).")

        # Compute expected signature
        signed_payload = f"{timestamp}.{payload}".encode('utf-8')
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            signed_payload,
            hashlib.sha256
        ).hexdigest()

        # Constant-time comparison
        if not hmac.compare_digest(expected_sig, received_sig):
            raise SignatureException("Invalid webhook signature.")

        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            raise SignatureException("Invalid JSON payload.")
