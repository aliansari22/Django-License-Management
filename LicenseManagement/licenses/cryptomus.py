import requests
from django.conf import settings

class CryptomusPaymentGateway:
    def __init__(self):
        self.api_url = settings.CRYPTOMUS_API_URL
        self.api_key = settings.CRYPTOMUS_API_KEY

    def create_payment(self, amount, currency, order_id, success_url, fail_url):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        data = {
            'amount': amount,
            'currency': currency,
            'order_id': order_id,
            'success_url': success_url,
            'fail_url': fail_url,
        }
        response = requests.post(self.api_url, json=data, headers=headers)
        return response.json()

    def verify_payment(self, order_id):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        response = requests.get(f'{self.api_url}/{order_id}', headers=headers)
        return response.json()
