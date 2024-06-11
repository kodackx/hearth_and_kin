import { handleApiErrors} from './utils.js'
import {showToast} from './utils.js'
document.getElementById('loginBtn').addEventListener('click', login);

function register() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var data = {'username': username, 'password': password};
    fetch('/user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => handleApiResponse(response, data => {
        alert('User successfully created!')
    }))
    .catch((error) => {
        alert(error)
    })
}

function login() {
    var username = $('#username').val();
    var password = $('#password').val();
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            username: username,
            password: password,
        }),
    })
    .then(response => handleApiErrors(response, data => {
        console.log('Response data:', data); // Log the response data for debugging
        if (data.user_id) {
            localStorage.setItem('username', username);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '/dashboard';
        } else {
            throw new Error('User ID is missing in the response.');
        }
    }))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    });
}