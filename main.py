"""
CryptoAuth API Server - Simple Flask app for Railway deployment
Demonstrates authentication + encrypted messaging
"""
from flask import Flask, request, jsonify, render_template
import json
from crypto_auth import AuthServer, AuthClient, HybridEncryptor

app = Flask(__name__)

# Global server instance (in production: use database)
auth_server = AuthServer("cryptoauth-api-v1")

# Register demo users
auth_server.register_user("alice", "alice_secret_123")
auth_server.register_user("bob", "bob_secret_456")


# ============================================================================
# UI ROUTES - Web Interface
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """Landing page with login/register."""
    return render_template('index.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """User dashboard after authentication."""
    return render_template('dashboard.html')


# ============================================================================
# API ROUTES - REST Endpoints
# ============================================================================


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'CryptoAuth API',
        'version': '1.0.0',
    }), 200


@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register new user.
    
    POST /api/auth/register
    {
        "username": "john",
        "password": "secret123"
    }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    if len(password) < 8:
        return jsonify({'error': 'Password too short (min 8 chars)'}), 400
    
    success = auth_server.register_user(username, password)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': f'User {username} registered',
        }), 201
    else:
        return jsonify({'error': 'User already exists'}), 409


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login and get auth token.
    
    POST /api/auth/login
    {
        "username": "alice",
        "password": "alice_secret_123"
    }
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400
    
    token = auth_server.authenticate(username, password)
    
    if not token or not auth_server.verify_token(token):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'status': 'success',
        'token': json.loads(token.to_json()),
        'user_id': username,
        'expires_in': 3600,
    }), 200


@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """
    Verify auth token validity.
    
    POST /api/auth/verify
    {
        "token": {...}
    }
    """
    data = request.get_json()
    token_data = data.get('token')
    
    if not token_data:
        return jsonify({'error': 'Missing token'}), 400
    
    try:
        from crypto_auth import AuthToken
        token = AuthToken.from_json(json.dumps(token_data))
        valid = auth_server.verify_token(token)
        
        return jsonify({
            'valid': valid,
            'expired': token.is_expired(),
            'user_id': token.user_id,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/message/send', methods=['POST'])
def send_message():
    """
    Send encrypted message (requires valid token).
    
    POST /api/message/send
    {
        "token": {...},
        "message": "Hello Server!"
    }
    """
    data = request.get_json()
    token_data = data.get('token')
    message = data.get('message')
    
    if not token_data or not message:
        return jsonify({'error': 'Missing token or message'}), 400
    
    try:
        from crypto_auth import AuthToken
        token = AuthToken.from_json(json.dumps(token_data))
        
        if not auth_server.verify_token(token):
            return jsonify({'error': 'Invalid token'}), 401
        
        # Encrypt response message with hybrid encryption
        response_msg = f"Server received: {message}"
        encrypted = HybridEncryptor.encrypt(
            response_msg,
            auth_server.public_key
        )
        
        return jsonify({
            'status': 'success',
            'user_id': token.user_id,
            'encrypted_response': encrypted,
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/keys/public', methods=['GET'])
def get_public_key():
    """
    Get server's public RSA key for client encryption.
    """
    pub_key_pem = auth_server.get_public_key_pem().decode('utf-8')
    
    return jsonify({
        'public_key': pub_key_pem,
        'algorithm': 'RSA-4096',
        'server_id': auth_server.get_server_id(),
    }), 200


@app.route('/api/info', methods=['GET'])
def info():
    """Get server info."""
    return jsonify({
        'service': 'CryptoAuth - Hybrid Authentication System',
        'version': '1.0.0',
        'algorithms': ['AES-256-GCM', 'RSA-4096'],
        'endpoints': {
            '/health': 'Health check',
            '/api/auth/register': 'Register new user',
            '/api/auth/login': 'Login and get token',
            '/api/auth/verify': 'Verify token',
            '/api/message/send': 'Send encrypted message',
            '/api/keys/public': 'Get server public key',
        },
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
