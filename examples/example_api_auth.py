"""
Example 4: API Authentication & Encrypted Payloads
Backend API dengan token-based auth + encrypted request/response.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import json
from crypto_auth import AuthServer, AuthClient, HybridEncryptor


class SecureAPI:
    """Simulasi secure REST API backend."""
    
    def __init__(self):
        self.auth_server = AuthServer("api-server-v1")
        # Register API clients
        self.auth_server.register_user("mobile_app", "app_secret_key_123")
        self.auth_server.register_user("web_client", "web_secret_key_456")
        
    def handle_request(self, request: dict) -> dict:
        """
        Handle encrypted API request.
        
        Request format:
        {
            'token': '...',
            'encrypted_payload': {...}
        }
        """
        # 1. Verify token
        token_json = request['token']
        from crypto_auth import AuthToken
        token = AuthToken.from_json(token_json)
        
        if not self.auth_server.verify_token(token):
            return {'error': 'Unauthorized', 'status': 401}
        
        # 2. Decrypt payload
        try:
            payload = HybridEncryptor.decrypt(
                request['encrypted_payload'],
                self.auth_server.private_key
            )
            request_data = json.loads(payload)
        except Exception as e:
            return {'error': 'Invalid payload', 'status': 400}
        
        # 3. Process request
        response_data = self._process_request(request_data, token.user_id)
        
        # 4. Encrypt response
        encrypted_response = HybridEncryptor.encrypt(
            json.dumps(response_data),
            self.auth_server.public_key
        )
        
        return {
            'status': 200,
            'encrypted_payload': encrypted_response
        }
    
    def _process_request(self, data: dict, user_id: str) -> dict:
        """Process actual business logic."""
        endpoint = data.get('endpoint')
        
        if endpoint == '/api/user/profile':
            return {
                'user_id': user_id,
                'name': 'John Doe',
                'email': f'{user_id}@example.com',
                'balance': 1500000,
            }
        elif endpoint == '/api/transactions':
            return {
                'transactions': [
                    {'id': 1, 'amount': 50000, 'type': 'debit'},
                    {'id': 2, 'amount': 100000, 'type': 'credit'},
                ]
            }
        else:
            return {'error': 'Unknown endpoint'}


def main():
    print("=" * 60)
    print("  SECURE API DEMO")
    print("=" * 60)
    
    # --- Setup API server ---
    api = SecureAPI()
    print("\n[SERVER] Secure API server started")
    print("         Registered clients: mobile_app, web_client")
    
    # --- Client login ---
    client = AuthClient("mobile_app", api.auth_server.get_public_key_pem())
    login_ok = client.login(api.auth_server, "app_secret_key_123")
    
    if not login_ok:
        print("[ERROR] Login failed!")
        return
    
    print("\n[CLIENT] Mobile app authenticated successfully")
    print(f"         Token expires: {client.current_token.expires_at}")
    
    # --- API Request 1: Get user profile ---
    print("\n" + "-" * 60)
    print("  REQUEST 1: GET /api/user/profile")
    print("-" * 60)
    
    request_data = {
        'endpoint': '/api/user/profile',
        'method': 'GET',
    }
    
    # Encrypt request payload
    encrypted_payload = HybridEncryptor.encrypt(
        json.dumps(request_data),
        api.auth_server.public_key
    )
    
    api_request = {
        'token': client.current_token.to_json(),
        'encrypted_payload': encrypted_payload,
    }
    
    print(f"[CLIENT] Sending encrypted request...")
    print(f"         Payload size: {len(str(api_request))} bytes")
    
    # Send to server
    response = api.handle_request(api_request)
    
    if response['status'] == 200:
        # Decrypt response
        response_json = HybridEncryptor.decrypt(
            response['encrypted_payload'],
            client.private_key
        )
        response_data = json.loads(response_json)
        
        print(f"[SERVER] Response (decrypted):")
        print(f"         {json.dumps(response_data, indent=2)}")
    else:
        print(f"[ERROR] {response}")
    
    # --- API Request 2: Get transactions ---
    print("\n" + "-" * 60)
    print("  REQUEST 2: GET /api/transactions")
    print("-" * 60)
    
    request_data = {
        'endpoint': '/api/transactions',
        'method': 'GET',
    }
    
    encrypted_payload = HybridEncryptor.encrypt(
        json.dumps(request_data),
        api.auth_server.public_key
    )
    
    api_request = {
        'token': client.current_token.to_json(),
        'encrypted_payload': encrypted_payload,
    }
    
    print(f"[CLIENT] Sending encrypted request...")
    response = api.handle_request(api_request)
    
    if response['status'] == 200:
        response_json = HybridEncryptor.decrypt(
            response['encrypted_payload'],
            client.private_key
        )
        response_data = json.loads(response_json)
        
        print(f"[SERVER] Response (decrypted):")
        print(f"         {json.dumps(response_data, indent=2)}")
    
    # --- Test with expired token ---
    print("\n" + "-" * 60)
    print("  TEST: Expired token rejection")
    print("-" * 60)
    
    client.current_token.expires_at = 0  # Force expire
    
    api_request = {
        'token': client.current_token.to_json(),
        'encrypted_payload': encrypted_payload,
    }
    
    response = api.handle_request(api_request)
    print(f"[SERVER] Response: {response}")
    
    print("\n[SUMMARY]")
    print("  1. Client authenticates with username/password -> gets token")
    print("  2. Token signed with RSA (tamper-proof)")
    print("  3. All requests encrypted with hybrid encryption")
    print("  4. Server verifies token before processing")
    print("  5. Response also encrypted end-to-end")
    print("  6. Even if traffic is intercepted, data is secure")
    
    print("\n" + "=" * 60)
    print("  DEMO COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
