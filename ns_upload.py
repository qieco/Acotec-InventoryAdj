import requests
import json
import oauth2 as oauth
import hmac
import base64
from hashlib import sha256
import time

class SignatureMethod_HMAC_SHA256(oauth.SignatureMethod):
    name = 'HMAC-SHA256'

    def signing_base(self, request, consumer, token):
        if not hasattr(request, 'normalized_url') or request.normalized_url is None:
            raise ValueError("Base URL for request is not set.")

        sig = (
            oauth.escape(request.method),
            oauth.escape(request.normalized_url),
            oauth.escape(request.get_normalized_parameters()),
        )
        key = '%s&' % oauth.escape(consumer.secret)
        if token:
            key += oauth.escape(token.secret)
        raw = '&'.join(sig)
        return raw, key

    def sign(self, request, consumer, token):
        raw, key = self.signing_base(request, consumer, token)
        hashed = hmac.new(key.encode(), raw.encode(), sha256)
        return base64.b64encode(hashed.digest()).decode()
class NetSuiteAPI:
    def __init__(self, consumer_key, consumer_secret, token_key, token_secret):
        self.consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        self.token = oauth.Token(key=token_key, secret=token_secret)

    def _get_oauth_params(self, url, http_method, realm):
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': self.token.key,
            'oauth_consumer_key': self.consumer.key
        }
        req = oauth.Request(method=http_method, url=url, parameters=params)
        signature_method = SignatureMethod_HMAC_SHA256()
        req.sign_request(signature_method, self.consumer, self.token)
        return req.to_header(realm=realm)

    def  post(self, url, data, realm='7557353_SB1'):
        headers = self._get_oauth_params(url, "POST", realm)
        headers["Content-Type"] = "application/json"
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response