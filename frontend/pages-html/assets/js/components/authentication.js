import config from "../config.js";

const API_URL = config.API_URL;

// Function to switch between forms
function switchForms(showForm, hideForm) {
    showForm.classList.remove('hidden');
    hideForm.classList.add('hidden');
}

// Define the forms
const signupForm = document.getElementById('signupForm');
const loginForm = document.getElementById('loginForm');

const showLoginBtn = document.getElementById('switchToLogin');
const showSignupBtn = document.getElementById('switchToSignup');

// Event listeners for form switching
showLoginBtn.addEventListener('click', (event) => {
    event.preventDefault();
    switchForms(loginForm, signupForm);
});

showSignupBtn.addEventListener('click', (event) => {
    event.preventDefault();
    switchForms(signupForm, loginForm);
});

// Handle signup form submission
signupForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = {
        name: document.getElementById('firstname').value,
        surname: document.getElementById('surname').value,
        email: document.getElementById('signupEmail').value,
        password: document.getElementById('signupPassword').value
    };

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {
            alert('Please check your email for verification link');
            switchForms(loginForm, signupForm);
        } else {
            alert(data.message || 'Registration failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during registration');
    }
});

// Handle login form submission
loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = {
        email: document.getElementById('loginEmail').value,
        password: document.getElementById('loginPassword').value,
        remember: document.getElementById('rememberMe').checked
    };

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
            credentials: 'include'
        });

        const data = await response.json();

        if (response.ok) {  // data.message and data.error are for debug purposes only, omit from codebase in production
            window.location.href = '/dashboard';
            alert(data.message || 'Login successful!')
        } else {
            alert(data.error || 'Login failed!');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login');
    }
});

// Password visibility toggle function (existing code)
const passwordToggles = document.querySelectorAll('.form-group__toggle_password');

passwordToggles.forEach(toggle => {
    toggle.addEventListener('click', function() {
        const input = this.previousElementSibling;
        const icon = this.querySelector('i');

        // toggle password visibility
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });
});