document.getElementById('registerBtn').addEventListener('click', register);
document.getElementById('loginBtn').addEventListener('click', login);
document.getElementById('createStoryBtn').addEventListener('click', createStory);
document.getElementById('joinStoryBtn').addEventListener('click', joinStory);

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
        console.log(data)
        localStorage.setItem('username', data.username);
        if (data.story_id) {
            localStorage.setItem('story_id', data.story_id);
        }
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

function createStory() {
    var story_id = $('#story_id').val();
    $.post('/story', {story_id: story_id}, function(data) {
        alert('NYI');
    });
}

function joinStory() {
    var story_id = $('#story_id').val();
    // Socket.IO logic for joining a story can go here
}