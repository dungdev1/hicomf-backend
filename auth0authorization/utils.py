from django.contrib.auth import authenticate
import json

import jwt
import requests
import os
from dotenv import load_dotenv

load_dotenv()


# Function that map the sub field from the access_token to the username,
# and use authenticate method to create a remote user in the Django authentication system
def jwt_get_username_from_payload_handler(payload):
	username = payload.get('sub').replace('|', '.')
	authenticate(remote_user=username)
	return username


# Function to fetch the JWKS from the Auth0 account to verify and decode the incoming Access Token
def jwt_decode_token(token):
	header = jwt.get_unverified_header(token)
	jwks = requests.get(f"{os.getenv('AUTH0_DOMAIN')}.well-known/jwks.json").json()
	public_key = None
	for jwk in jwks['keys']:
	    if jwk['kid'] == header['kid']:
	        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

	if public_key is None:
		raise Exception('Public key not found.')

	issuer = 'https://{}/'.format('dev-1imx6cpn.au.auth0.com')
	return jwt.decode(token, public_key, audience=os.getenv('API_IDENTIFIER'), issuer=issuer, algorithms=['RS256'])