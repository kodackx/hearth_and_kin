import { handleApiErrors} from './utils.js'
import {showToast} from './utils.js'
document.getElementById('registerBtn').addEventListener('click', register);


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
        alert('User successfully created!');
        window.location.href = '/'; // Redirect to login page
    }))
    .catch((error) => {
        alert(error);
    });
}

function handleApiResponse(response, successCallback) {
    // Parses and displays any validation errors from pydantic in the errorContainer div
    document.getElementById('errorContainer').textContent = ''
    if (!response.ok) {
        console.error(response)
        return response.json().then(data => {
            if (Array.isArray(data.detail)) {
                data.detail.forEach(error => {
                    const errorField = error.loc.join(" > ");
                    const errorMessage = error.msg;
                    const errorElement = document.createElement('p');
                    errorElement.textContent = `${errorField}: ${errorMessage}`;
                    document.getElementById('errorContainer').appendChild(errorElement);
                });
            } else {
                throw new Error(data.detail)
            } 
        })
    }
    return response.json().then(successCallback)
}