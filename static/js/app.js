// CryptoAuth Frontend Application Logic

const API_BASE = '';

// Utility: Show alert message
function showAlert(elementId, message, type = 'success') {
    const alertEl = document.getElementById(elementId);
    if (!alertEl) return;
    
    alertEl.innerHTML = `
        <div class="alert alert-${type}">
            <span>${type === 'success' ? '✅' : '❌'}</span>
            <span>${message}</span>
        </div>
    `;
    
    setTimeout(() => {
        alertEl.innerHTML = '';
    }, 5000);
}

// Utility: Toggle loading state
function setLoading(btnTextId, spinnerId, isLoading) {
    const btnText = document.getElementById(btnTextId);
    const spinner = document.getElementById(spinnerId);
    
    if (btnText) btnText.style.display = isLoading ? 'none' : 'inline';
    if (spinner) spinner.style.display = isLoading ? 'inline-block' : 'none';
}

// Login Form Handler
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    setLoading('loginBtnText', 'loginSpinner', true);
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store token in localStorage
            localStorage.setItem('authToken', JSON.stringify(data.token));
            
            showAlert('loginAlert', 'Login successful! Redirecting...', 'success');
            
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            showAlert('loginAlert', data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showAlert('loginAlert', 'Connection error. Please try again.', 'error');
    } finally {
        setLoading('loginBtnText', 'loginSpinner', false);
    }
});

// Register Form Handler
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    
    // Validation
    if (password !== passwordConfirm) {
        showAlert('registerAlert', 'Passwords do not match!', 'error');
        return;
    }
    
    if (password.length < 8) {
        showAlert('registerAlert', 'Password must be at least 8 characters', 'error');
        return;
    }
    
    setLoading('registerBtnText', 'registerSpinner', true);
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('registerAlert', 'Account created! Please login.', 'success');
            
            // Clear form
            document.getElementById('registerForm').reset();
            
            // Auto-fill login form
            setTimeout(() => {
                document.getElementById('loginUsername').value = username;
                document.getElementById('loginPassword').focus();
            }, 1500);
        } else {
            showAlert('registerAlert', data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showAlert('registerAlert', 'Connection error. Please try again.', 'error');
    } finally {
        setLoading('registerBtnText', 'registerSpinner', false);
    }
});

// Send Message Handler (Dashboard)
document.getElementById('messageForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = document.getElementById('messageText').value;
    const token = JSON.parse(localStorage.getItem('authToken'));
    
    if (!token) {
        alert('No token found. Please login again.');
        window.location.href = '/';
        return;
    }
    
    setLoading('sendBtnText', 'sendSpinner', true);
    
    try {
        const response = await fetch(`${API_BASE}/api/message/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token, message })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('messageAlert', 'Message sent and encrypted successfully!', 'success');
            
            // Display encrypted response
            const encryptedDiv = document.getElementById('encryptedResponse');
            const encryptedDataDiv = document.getElementById('encryptedData');
            
            if (encryptedDiv && encryptedDataDiv) {
                encryptedDataDiv.innerHTML = `
                    <p><strong>Encrypted Key:</strong> ${data.encrypted_response.encrypted_key.substring(0, 80)}...</p>
                    <p><strong>Ciphertext:</strong> ${data.encrypted_response.ciphertext.substring(0, 80)}...</p>
                    <p><strong>Nonce:</strong> ${data.encrypted_response.nonce}</p>
                    <p><strong>Tag:</strong> ${data.encrypted_response.tag}</p>
                `;
                encryptedDiv.style.display = 'block';
            }
            
            // Clear form
            document.getElementById('messageText').value = '';
        } else {
            showAlert('messageAlert', data.error || 'Failed to send message', 'error');
            
            if (response.status === 401) {
                setTimeout(() => {
                    localStorage.removeItem('authToken');
                    window.location.href = '/';
                }, 2000);
            }
        }
    } catch (error) {
        showAlert('messageAlert', 'Connection error. Please try again.', 'error');
    } finally {
        setLoading('sendBtnText', 'sendSpinner', false);
    }
});

// Verify Token
async function verifyToken() {
    const token = JSON.parse(localStorage.getItem('authToken'));
    
    if (!token) {
        alert('No token found. Please login again.');
        window.location.href = '/';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/auth/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const status = data.valid ? '✅ Valid' : '❌ Invalid';
            const expiredStatus = data.expired ? '(Expired)' : '(Active)';
            alert(`Token Status: ${status} ${expiredStatus}\nUser: ${data.user_id}`);
        } else {
            alert('Failed to verify token');
        }
    } catch (error) {
        alert('Connection error. Please try again.');
    }
}

// Fetch Public Key
async function fetchPublicKey() {
    try {
        const response = await fetch(`${API_BASE}/api/keys/public`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('serverId').textContent = data.server_id;
            document.getElementById('keyAlgorithm').textContent = data.algorithm;
            document.getElementById('publicKeyPem').textContent = data.public_key;
            document.getElementById('publicKeyDisplay').style.display = 'block';
        } else {
            alert('Failed to fetch public key');
        }
    } catch (error) {
        alert('Connection error. Please try again.');
    }
}

// Download Token as JSON
function downloadToken() {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        alert('No token found');
        return;
    }
    
    const blob = new Blob([token], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cryptoauth-token.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Copy Token to Clipboard
async function copyTokenToClipboard() {
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        alert('No token found');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(token);
        alert('✅ Token copied to clipboard!');
    } catch (error) {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = token;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        alert('✅ Token copied to clipboard!');
    }
}

// Initialize smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// Add hover effects to cards
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-5px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

console.log('🔐 CryptoAuth v1.0.0 - Frontend Loaded');
console.log('🔥 Military-grade encryption active');
