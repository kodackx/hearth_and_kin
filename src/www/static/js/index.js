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
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
    })
    .then(response => handleApiResponse(response, data => {
        localStorage.setItem('username', username);
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('access_token', data.access_token);
        window.location.href = '/dashboard';
    }))
    .catch((error) => {
        alert(error)
    })
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