# 📚 CryptoAuth API Documentation

Dokumentasi lengkap untuk menggunakan CryptoAuth REST API - sistem autentikasi hybrid dengan enkripsi AES-256-GCM + RSA-4096.

## 🚀 Base URL

**Local Development:**
```
http://localhost:5000
```

**Production (Railway):**
```
https://your-app-name.railway.app
```

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication Flow](#authentication-flow)
3. [API Endpoints](#api-endpoints)
4. [Code Examples](#code-examples)
5. [Error Handling](#error-handling)

---

## 🎯 Quick Start

### Step 1: Check Server Health

```bash
curl https://your-app-name.railway.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "CryptoAuth API",
  "version": "1.0.0"
}
```

### Step 2: Register User

```bash
curl -X POST https://your-app-name.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "mypassword123"
  }'
```

### Step 3: Login & Get Token

```bash
curl -X POST https://your-app-name.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "mypassword123"
  }'
```

---

## 🔐 Authentication Flow

```
┌─────────┐                           ┌─────────┐
│ Client  │                           │ Server  │
└────┬────┘                           └────┬────┘
     │                                     │
     │  1. POST /api/auth/register        │
     │────────────────────────────────────>│
     │  {username, password}               │
     │                                     │
     │  2. 201 Created                     │
     │<────────────────────────────────────│
     │  {status: "success"}                │
     │                                     │
     │  3. POST /api/auth/login            │
     │────────────────────────────────────>│
     │  {username, password}               │
     │                                     │
     │  4. 200 OK                          │
     │<────────────────────────────────────│
     │  {token, expires_in: 3600}          │
     │                                     │
     │  5. POST /api/message/send          │
     │────────────────────────────────────>│
     │  {token, message}                   │
     │                                     │
     │  6. 200 OK                          │
     │<────────────────────────────────────│
     │  {encrypted_response}               │
     │                                     │
```

---

## 📡 API Endpoints

### 1. Health Check

**GET** `/health`

Check if server is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "CryptoAuth API",
  "version": "1.0.0"
}
```

---

### 2. Server Info

**GET** `/api/info`

Get server information and available endpoints.

**Response:**
```json
{
  "service": "CryptoAuth - Hybrid Authentication System",
  "version": "1.0.0",
  "algorithms": ["AES-256-GCM", "RSA-4096"],
  "endpoints": {
    "/health": "Health check",
    "/api/auth/register": "Register new user",
    "/api/auth/login": "Login and get token",
    "/api/auth/verify": "Verify token",
    "/api/message/send": "Send encrypted message",
    "/api/keys/public": "Get server public key"
  }
}
```

---

### 3. Register User

**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "username": "alice",
  "password": "alice_secret_123"
}
```

**Validation Rules:**
- Password minimum 8 characters
- Username must be unique

**Success Response (201):**
```json
{
  "status": "success",
  "message": "User alice registered"
}
```

**Error Responses:**

```json
// 400 Bad Request - Missing fields
{
  "error": "Missing username or password"
}

// 400 Bad Request - Password too short
{
  "error": "Password too short (min 8 chars)"
}

// 409 Conflict - User exists
{
  "error": "User already exists"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "alice_secret_123"
  }'
```

---

### 4. Login

**POST** `/api/auth/login`

Authenticate and receive auth token (valid for 1 hour).

**Request Body:**
```json
{
  "username": "alice",
  "password": "alice_secret_123"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "token": {
    "user_id": "alice",
    "token": "eyJhbGc...",
    "signature": "MIIEpQIB...",
    "created_at": 1718765290.5,
    "expires_at": 1718768890.5
  },
  "user_id": "alice",
  "expires_in": 3600
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "alice_secret_123"
  }'
```

---

### 5. Verify Token

**POST** `/api/auth/verify`

Check if a token is valid and not expired.

**Request Body:**
```json
{
  "token": {
    "user_id": "alice",
    "token": "eyJhbGc...",
    "signature": "MIIEpQIB...",
    "created_at": 1718765290.5,
    "expires_at": 1718768890.5
  }
}
```

**Response (200):**
```json
{
  "valid": true,
  "expired": false,
  "user_id": "alice"
}
```

---

### 6. Send Encrypted Message

**POST** `/api/message/send`

Send a message and receive encrypted response (requires valid token).

**Request Body:**
```json
{
  "token": {
    "user_id": "alice",
    "token": "eyJhbGc...",
    "signature": "MIIEpQIB...",
    "created_at": 1718765290.5,
    "expires_at": 1718768890.5
  },
  "message": "Hello Server!"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "user_id": "alice",
  "encrypted_response": {
    "encrypted_key": "abc123...",
    "ciphertext": "def456...",
    "nonce": "ghi789...",
    "tag": "jkl012..."
  }
}
```

**Error Responses:**

```json
// 401 Unauthorized - Invalid token
{
  "error": "Invalid token"
}

// 400 Bad Request - Missing fields
{
  "error": "Missing token or message"
}
```

---

### 7. Get Server Public Key

**GET** `/api/keys/public`

Get server's RSA-4096 public key for client-side encryption.

**Response (200):**
```json
{
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkq...\n-----END PUBLIC KEY-----",
  "algorithm": "RSA-4096",
  "server_id": "cryptoauth-api-v1"
}
```

**Use Case:**  
Client dapat menggunakan public key ini untuk enkripsi data sebelum dikirim ke server.

---

## 💻 Code Examples

### Python Client Example

```python
import requests
import json

BASE_URL = "http://localhost:5000"

# 1. Register user
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "username": "alice",
    "password": "alice_secret_123"
})
print(f"Register: {response.json()}")

# 2. Login
response = requests.post(f"{BASE_URL}/api/auth/login", json={
    "username": "alice",
    "password": "alice_secret_123"
})
auth_data = response.json()
token = auth_data["token"]
print(f"Login successful! Token expires in {auth_data['expires_in']}s")

# 3. Send encrypted message
response = requests.post(f"{BASE_URL}/api/message/send", json={
    "token": token,
    "message": "Hello from Python client!"
})
print(f"Response: {response.json()}")

# 4. Verify token
response = requests.post(f"{BASE_URL}/api/auth/verify", json={
    "token": token
})
print(f"Token valid: {response.json()['valid']}")
```

### JavaScript/Node.js Example

```javascript
const BASE_URL = "http://localhost:5000";

async function testCryptoAuthAPI() {
  try {
    // 1. Register user
    let response = await fetch(`${BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: "bob",
        password: "bob_secret_456"
      })
    });
    console.log("Register:", await response.json());

    // 2. Login
    response = await fetch(`${BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: "bob",
        password: "bob_secret_456"
      })
    });
    const authData = await response.json();
    const token = authData.token;
    console.log(`Login successful! Expires in ${authData.expires_in}s`);

    // 3. Send encrypted message
    response = await fetch(`${BASE_URL}/api/message/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        token: token,
        message: "Hello from JavaScript client!"
      })
    });
    console.log("Message sent:", await response.json());

    // 4. Get public key
    response = await fetch(`${BASE_URL}/api/keys/public`);
    const keyData = await response.json();
    console.log(`Server ID: ${keyData.server_id}`);
    console.log(`Algorithm: ${keyData.algorithm}`);

  } catch (error) {
    console.error("Error:", error);
  }
}

testCryptoAuthAPI();
```

### cURL Complete Workflow

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"

# 1. Check health
echo "=== Health Check ==="
curl -X GET $BASE_URL/health
echo -e "\n"

# 2. Register user
echo "=== Register User ==="
curl -X POST $BASE_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
echo -e "\n"

# 3. Login and save token
echo "=== Login ==="
TOKEN=$(curl -X POST $BASE_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }' | jq -r '.token')
echo "Token received"
echo -e "\n"

# 4. Send message with token
echo "=== Send Message ==="
curl -X POST $BASE_URL/api/message/send \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": $TOKEN,
    \"message\": \"Hello from cURL!\"
  }"
echo -e "\n"
```

---

## 👥 Demo Users

Server sudah memiliki 2 demo users yang ter-register:

| Username | Password | Description |
|----------|----------|-------------|
| `alice` | `alice_secret_123` | Demo user 1 |
| `bob` | `bob_secret_456` | Demo user 2 |

Anda bisa langsung login dengan credentials ini tanpa register terlebih dahulu.

**Example:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "alice_secret_123"
  }'
```

---

## 🛡️ Security Considerations

### 1. Password Requirements
- **Minimum length**: 8 characters
- **Recommendation**: Gunakan kombinasi huruf besar, kecil, angka, dan simbol

### 2. Token Management
- **Lifetime**: Token valid selama **1 jam** (3600 detik)
- **Storage**: Jangan simpan token di localStorage untuk production (gunakan httpOnly cookies)
- **Transmission**: Selalu gunakan HTTPS di production

### 3. Encryption Algorithms
| Component | Algorithm | Key Size |
|-----------|-----------|----------|
| Symmetric | AES-GCM | 256-bit |
| Asymmetric | RSA-OAEP | 4096-bit |
| Signatures | RSA-PKCS1v15 | 4096-bit |
| Password Hash | PBKDF2-HMAC-SHA256 | 100,000 iterations |

### 4. Best Practices
✅ **DO:**
- Gunakan HTTPS di production
- Validate input di client-side sebelum kirim
- Handle token expiry dengan refresh mechanism
- Log semua authentication attempts

❌ **DON'T:**
- Commit credentials ke git
- Share private keys atau tokens
- Hardcode passwords di client code
- Ignore error responses

---

## 🧪 Testing Guide

### Local Development

**1. Start Server:**
```bash
python main.py
```

Server akan run di `http://localhost:5000`

**2. Test dengan Python:**
```bash
# Buat test script
cat > test_api.py << 'EOF'
import requests

BASE = "http://localhost:5000"

# Health check
r = requests.get(f"{BASE}/health")
print("Health:", r.json())

# Login dengan demo user
r = requests.post(f"{BASE}/api/auth/login", json={
    "username": "alice",
    "password": "alice_secret_123"
})
print("Login:", r.json())
EOF

python test_api.py
```

**3. Test dengan Browser:**
- Buka: `http://localhost:5000/api/info`
- Anda akan lihat semua available endpoints

**4. Test dengan Postman/Insomnia:**
Import collection ini:

```json
{
  "name": "CryptoAuth API",
  "requests": [
    {
      "name": "Health Check",
      "method": "GET",
      "url": "{{base_url}}/health"
    },
    {
      "name": "Register User",
      "method": "POST",
      "url": "{{base_url}}/api/auth/register",
      "body": {
        "username": "newuser",
        "password": "password123"
      }
    },
    {
      "name": "Login",
      "method": "POST",
      "url": "{{base_url}}/api/auth/login",
      "body": {
        "username": "alice",
        "password": "alice_secret_123"
      }
    }
  ],
  "variables": {
    "base_url": "http://localhost:5000"
  }
}
```

---

## ⚠️ Error Handling

### Common Error Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| 400 | Bad Request | Missing fields, invalid format |
| 401 | Unauthorized | Invalid credentials, expired token |
| 404 | Not Found | Wrong endpoint URL |
| 409 | Conflict | User already exists |
| 500 | Internal Server Error | Server-side issue |

### Error Response Format

Semua error responses memiliki format:
```json
{
  "error": "Descriptive error message"
}
```

### Handling Errors in Code

**Python:**
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()  # Raise exception for 4xx/5xx
    return response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(f"Message: {e.response.json()['error']}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

**JavaScript:**
```javascript
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`${response.status}: ${error.error}`);
  }
  return await response.json();
} catch (error) {
  console.error("API Error:", error.message);
}
```

---

## 🔧 Troubleshooting

### Problem: "Connection refused"
**Cause:** Server tidak running  
**Solution:**
```bash
python main.py
```

### Problem: "Invalid credentials"
**Cause:** Username/password salah  
**Solution:**
- Gunakan demo users: `alice` / `alice_secret_123`
- Atau register user baru terlebih dahulu

### Problem: "Invalid token"
**Cause:** Token expired atau tidak valid  
**Solution:**
- Login ulang untuk mendapat token baru
- Check token expiry dengan `/api/auth/verify`

### Problem: Token expired setelah 1 jam
**Cause:** Default token lifetime adalah 3600 detik  
**Solution:**
- Implement token refresh mechanism
- Atau login ulang

### Problem: "Module not found: cryptography"
**Cause:** Dependencies belum terinstall  
**Solution:**
```bash
pip install -r requirements.txt
```

---

## 📞 Support & Contact

Jika ada pertanyaan atau issues:
1. Check dokumentasi ini terlebih dahulu
2. Review code di `main.py` untuk detail implementasi
3. Test dengan demo users untuk troubleshooting

---

## 📝 Changelog

### v1.0.0 (2026-06-19)
- Initial release
- 7 API endpoints
- AES-256-GCM + RSA-4096 hybrid encryption
- Token-based authentication (1 hour expiry)
- Demo users pre-configured

---

**🔥 Built with Flask + cryptography library**  
**⚡ Deployed on Railway**

