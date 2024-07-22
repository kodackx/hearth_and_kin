import { handleApiErrors} from './utils.js'
import {showToast} from './utils.js'
document.getElementById('registerBtn').addEventListener('click', register);


function register() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    var openai_api_key = document.getElementById('openai_api_key').value || undefined;
    var nvidia_api_key = document.getElementById('nvidia_api_key').value || undefined;
    var anthropic_api_key = document.getElementById('anthropic_api_key').value || undefined;
    var groq_api_key = document.getElementById('groq_api_key').value || undefined;
    var elevenlabs_api_key = document.getElementById('elevenlabs_api_key').value || undefined;
    var elevenlabs_voice_id = document.getElementById('elevenlabs_voice_id') || undefined;
    
    var data = {'username': username, 'password': password, 'openai_api_key': openai_api_key, 'nvidia_api_key': nvidia_api_key, 'anthropic_api_key': anthropic_api_key, 'groq_api_key': groq_api_key, 'elevenlabs_api_key': elevenlabs_api_key, 'elevenlabs_voice_id': elevenlabs_voice_id};
    fetch('/user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => handleApiErrors(response, data => {
        alert('User successfully created!');
        window.location.href = '/'; // Redirect to login page
    }))
    .catch((error) => {
        showToast(error);
    });
}

function updateSettings(user_id) {
    var openai_api_key = document.getElementById('openai_api_key').value || undefined;
    var nvidia_api_key = document.getElementById('nvidia_api_key').value || undefined;
    var anthropic_api_key = document.getElementById('anthropic_api_key').value || undefined;
    var groq_api_key = document.getElementById('groq_api_key').value || undefined;
    var elevenlabs_api_key = document.getElementById('elevenlabs_api_key').value || undefined;
    var elevenlabs_voice_id = document.getElementById('elevenlabs_voice_id') || undefined;
    var data = {'user_id': user_id, 'openai_api_key': openai_api_key, 'nvidia_api_key': nvidia_api_key, 'anthropic_api_key': anthropic_api_key, 'groq_api_key': groq_api_key, 'elevenlabs_api_key': elevenlabs_api_key, 'elevenlabs_voice_id': elevenlabs_voice_id};
    fetch('/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => handleApiResponse(response, data => {
        console.log('Settings successfully updated!', data);
    }))
    .catch((error) => {
        showToast(error);
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