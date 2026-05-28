# HayBTech Python SDK

Official Python SDK for the HayBTech Payment Gateway API -- mobile payments across West Africa .

[![PyPI](https://img.shields.io/pypi/v/haybtech-sdk.svg)](https://pypi.org/project/haybtech-sdk/)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Intégration par IA (Prompt pour Marchands)

Si vous utilisez un assistant IA (comme Cursor, GitHub Copilot, ChatGPT, Claude, etc.), vous pouvez copier-coller le prompt suivant pour intégrer ce SDK de A à Z dans votre projet :

```text
Agis en tant qu'expert en développement backend Python. Je souhaite intégrer la solution de paiement HayBTech (Afrique de l'Ouest) sur mon site marchand de A à Z avec le SDK Python officiel `haybtech-sdk`.

Voici ma stack technique actuelle :
- Framework : [ex: Django, Flask, FastAPI]
- Base de données & ORM : [ex: Django ORM, SQLAlchemy, Tortoise ORM]
- Modèle de commande : [décrivez brièvement votre structure de table Order, ex: { id, status (pending/paid/failed), amount, email }]

Tâches à accomplir dans le code généré :
1. **Initialisation & Config** : Configurer le client SDK `HayBTechClient` en chargeant la clé secrète via l'environnement (`HAYBTECH_SECRET_KEY`).
2. **Création du Paiement** : Créer une vue/route pour initier le paiement. Elle doit récupérer le montant de la commande, générer la transaction via le SDK en passant `merchant_ref`, `amount`, `currency='XOF'`, `success_url`, `failed_url`, `callback_url`, puis renvoyer l'URL de redirection vers le guichet de paiement.
3. **Webhook de Validation** : Créer une vue/route `/webhook/haybtech` acceptant le POST de HayBTech. Elle doit :
   - Récupérer le corps de la requête brut (raw request body) et le header `X-HayBTech-Signature`.
   - Utiliser `Webhook.construct_event(payload, signature, secret)` pour valider l'événement.
   - Gérer l'événement `payment.success` : marquer la commande comme payée de façon idempotente et valider le panier.
   - Gérer l'événement `payment.failed` : marquer la commande en échec.
   - Renvoyer une réponse HTTP 200.
4. **Sécurité & Gestion des Erreurs** : Intercepter `SignatureException` et `ApiException`, logger les erreurs de façon propre, et utiliser une comparaison de signature insensible aux attaques temporelles.

Génère un code propre, modulaire, commenté et prêt à être inséré dans mon projet.
```

---

## Installation

```bash
pip install haybtech-sdk
```

---

## Quick Start (Zero-Config)

If you have `HAYBTECH_SECRET_KEY` set in your environment (e.g. via `.env`), you can initialize the SDK with zero configuration:

```python
from haybtech import HayBTechClient

client = HayBTechClient()
```

*(Optional)* You can also pass the key explicitly:
```python
from haybtech import HayBTechClient

client = HayBTechClient('sk_test_your_key')

# Initiate a payment
try:
    response = client.payments.create({
        'merchant_ref': 'ORDER-12345',
        'amount': 5000,
        'currency': 'XOF',
        'success_url': 'https://mysite.com/success',
        'failed_url': 'https://mysite.com/failed',
        'callback_url': 'https://mysite.com/webhook'
    })

    print(f"Payment URL: {response['data']['payment_url']}")
    
    # Django Helper
    # return response.to_django_redirect()
except Exception as e:
    print(f"Error: {e}")
```

---

## Webhooks

### Django

```python
from haybtech import Webhook, SignatureException

def my_webhook_view(request):
    payload = request.body.decode('utf-8')
    signature = request.headers.get('X-HayBTech-Signature')
    secret = 'whsec_...'

    try:
        event = Webhook.construct_event(payload, signature, secret)
        
        if event['event'] == 'payment.success':
            merchant_ref = event['data']['merchant_ref']
            # Mark order as paid
            
        return HttpResponse("OK", status=200)
    except SignatureException:
        return HttpResponse("Invalid Signature", status=403)
```

### Flask

```python
from flask import Flask, request, jsonify
from haybtech import Webhook, SignatureException

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get('X-HayBTech-Signature')

    try:
        event = Webhook.construct_event(payload, signature, 'whsec_...')
        
        if event['event'] == 'payment.success':
            # Mark order as paid
            pass
        
        return jsonify(status='ok'), 200
    except SignatureException:
        return jsonify(error='Invalid Signature'), 403
```

### FastAPI

```python
from fastapi import FastAPI, Request, HTTPException
from haybtech import Webhook, SignatureException

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    payload = (await request.body()).decode('utf-8')
    signature = request.headers.get('X-HayBTech-Signature')

    try:
        event = Webhook.construct_event(payload, signature, 'whsec_...')
        
        if event['event'] == 'payment.success':
            # Mark order as paid
            pass
        
        return {"status": "ok"}
    except SignatureException:
        raise HTTPException(status_code=403, detail="Invalid Signature")
```

---

## Available Events

| Event                     | Description              |
|:--------------------------|:-------------------------|
| `payment.success`         | Payment confirmed        |
| `payment.failed`          | Payment failed           |
| `payment.cancelled`       | Cancelled by customer    |
| `payment.expired`         | Payment timed out        |
| `payment.expired`         | Payment timed out        |

---

## Error Handling

```python
from haybtech import HayBTechClient
from haybtech.exceptions import ApiException, HayBTechException

client = HayBTechClient('sk_test_...')

try:
    response = client.payments.create(params)
except ApiException as e:
    print(e.message)       # Human-readable message
    print(e.http_status)   # 400, 422, 500...
    print(e.error_code)    # e.g., "insufficient_funds"
except HayBTechException as e:
    # SDK not configured, key invalid, etc.
    print(e)
```

---

## Test Mode

```python
client = HayBTechClient('sk_test_...') # No real charges
```

---


---

## Security Features

This SDK is built for **Maximum Security**:

- **Zero Dependencies**: Uses only standard Python libraries (`urllib`, `hmac`, `hashlib`). No vulnerabilities from external packages.
- **Secret Masking**: Keys are automatically masked in `repr()` and protected against `pickle` serialization.
- **Memory Protection**: Webhook payloads are capped at 1 MB to prevent memory exhaustion attacks.
- **Timing Attack Resistance**: Uses `hmac.compare_digest` for signature verification.
- **Replay Protection**: 5-minute timestamp tolerance on webhook signatures.
- **CRLF Guard**: Prevents HTTP header injection via malformed keys.

---

## API Resources

| Resource               | Description                                       |
|:-----------------------|:--------------------------------------------------|
| `client.payments`      | Create, retrieve, list, and verify transactions   |
| `client.webhooks`      | Manage notification endpoints programmatically    |

MIT License

