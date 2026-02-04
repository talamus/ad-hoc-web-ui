// Authentication utilities

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function removeToken() {
    localStorage.removeItem('access_token');
}

function isAuthenticated() {
    return !!getToken();
}

// Get CSRF token from cookies
function getCsrfToken() {
    const match = document.cookie.match(/csrf_token=([^;]+)/);
    return match ? match[1] : null;
}

// Logout function - calls API endpoint and clears local storage
async function logout() {
    const token = getToken();

    // Clear token from localStorage first
    removeToken();

    // Try to call logout endpoint if we have a token
    if (token) {
        try {
            console.info('Logging out user');
            const csrfToken = getCsrfToken();
            const headers = {
                'Authorization': `Bearer ${token}`
            };

            if (csrfToken) {
                headers['X-CSRF-Token'] = csrfToken;
            }

            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: headers
            });
        } catch (error) {
            console.error('Logout API call failed:', error);
            // Continue anyway - token is already removed
        }
    }

    // Redirect to login
    window.location.href = '/login';
}

// Verify token is valid by calling /api/auth/me
async function verifyToken() {
    const token = getToken();

    if (!token) {
        return false;
    }

    try {
        const response = await fetch('/api/auth/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            return true;
        }

    } catch (error) {
        console.error('Token verification failed:', error);
    }

    // Token is invalid
    removeToken();
    return false;
}

// Check authentication on page load for protected pages
async function checkAuth() {
    // Check if this is a public page (e.g., login)
    if (document.body.dataset.publicPage === 'true') {
        return;
    }

    const isValid = await verifyToken();

    if (!isValid) {
        // Redirect to login if token is invalid or missing
        window.location.href = '/login';
    }
}

// Add authorization header and CSRF token to fetch requests
async function authenticatedFetch(url, options = {}) {
    const token = getToken();

    if (!token) {
        window.location.href = '/login';
        throw new Error('No authentication token');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    // Add CSRF token for state-changing requests
    if (options.method && options.method !== 'GET' && options.method !== 'HEAD') {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            headers['X-CSRF-Token'] = csrfToken;
        }
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    // If unauthorized, redirect to login
    if (response.status === 401) {
        removeToken();
        window.location.href = '/login';
        throw new Error('Unauthorized');
    }

    return response;
}
