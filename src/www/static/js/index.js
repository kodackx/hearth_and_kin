import { handleApiErrors } from './utils.js'
document.getElementById('loginBtn').addEventListener('click', login);

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
            // should not happen
            alert('User ID is missing in the response.');
        }
    }))
}