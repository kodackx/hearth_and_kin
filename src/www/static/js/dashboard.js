import { handleResponse } from './utils.js'


// Event listener for communication of messages
// TODO add websocket file and functions for handling the received websocket actions
const socket = new WebSocket('ws://127.0.0.1:8000/ws/story');
socket.onmessage = function(message) {
    let parsedMessage = JSON.parse(message.data)
    let action = parsedMessage.action
    let data = parsedMessage.data
    console.log('client received: ', parsedMessage)
    let box = boxes[data.story_id - 1]
    switch (action) {
        case 'create_story':
            console.log('create story received, drawing box')
            drawCreatedStory(box, data)
            box.boxElement.querySelector('.box-content').textContent = data.creator;
            break;
        case 'join_story':
            if (data.username == username) {
                drawJoinedStory(box)
            } else {
                box.boxElement.querySelector('.box-content').textContent = data.username;
            }
        case 'leave_story':
            if (data.username == username) {
                drawLeftStory(box)
            } else {
                box.boxElement.querySelector('.box-content').textContent = '+';
            }
        case 'delete_story':
            drawDeletedStory(box)
        default:
            break;
    }
};

function sendSocket(action, data) {
    socket.send(JSON.stringify({
        action: action,
        data: data 
    }))
}

// Close connection when user exits website
window.addEventListener('beforeunload', function() {
    socket.close();
});

function initializeDashboard(boxes) {
    document.getElementById('username').textContent = username;
    loadStories();

    // Add event listeners to the boxes
    boxes.forEach(box => {
        // box.boxElement.addEventListener('click', createClickHandler(box));
        box.boxElement.addEventListener('click', () => createStory(box), { 'once': true});
    });
}

function createClickHandler(box) {
    return function() {
        createStory(box);
    };
}

function playOrResumeStory(box) {
    localStorage.setItem('story_id', box.storyId);
    window.location.href = '/story';
}

function drawCreatedStory(box, story) {
    // refreshBox(box);
    box.boxElement.style.backgroundColor = 'blue';
    box.storyCreated = true;
    box.creator = story.creator;
    box.storyId = story.story_id;
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    //box.boxElement.removeEventListener('click', createClickHandler(box));
    box.boxElement.addEventListener('click', () => joinStory(box), { 'once': true});
}

function drawActiveStory(box) {
    box.boxElement.querySelector('.box-footer').textContent = 'Resume Story';
    box.boxElement.style.backgroundColor = 'purple';
    box.boxElement.addEventListener('click', () => playOrResumeStory(box), { 'once': true});
    createButtons(box);
}

function drawJoinedStory(box) {
    box.boxElement.querySelector('.box-footer').textContent = undefined;
    box.boxElement.style.backgroundColor = 'green';
    createButtons(box);
}

function drawLeftStory(box) {
    box.boxElement.style.backgroundColor = 'blue';
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    box.boxElement.addEventListener('click', () => joinStory(box), { 'once': true});
    removeButtons(box);
}

function drawDeletedStory(box) {
    box.boxElement.querySelector('.box-footer').textContent = 'Create New Story';
    box.boxElement.style.backgroundColor = 'white';
    box.storyId = undefined;
    box.storyCreated = false;
    box.creator = undefined;
    box.boxElement.addEventListener('click', () => createStory(box), { 'once': true});
    removeButtons(box);
}

function loadStories() {
    fetch('/stories', {
        method: 'GET',
    })
    .then(response => handleResponse(response, stories => {
        // Draw created storys
        stories.forEach(story => {
            var box = boxes.find(box => box.boxId === story.story_id);
            if (story.story_id <= 3) { // we only support 3 boxes/stories for now
                // Join any previously joined story
                if (story.active && story_id == story.story_id) {
                    drawActiveStory(box)
                }
                else if (!story.active && story_id == story.story_id) {
                    drawJoinedStory(box);
                } else {
                    drawCreatedStory(box, story);
                }
            }
        });

        
    }))
    .catch((error) => {
        alert(error);
    });
}

function createStory(box) {
    fetch('/story', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.boxId,
            creator: username,
        }),
    })
    .then(response => handleResponse(response, data => {
        sendSocket('create_story', data)
        //drawCreatedStory(box, data);
        //alert('Story created!')
    }))
    .catch((error) => {
        alert(error);
    });
};

function joinStory(box) {
    fetch('/story/' + box.storyId + '/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            username: username,
        }),
    })
    .then(response => handleResponse(response, data => {
            sendSocket('join_story', data)
            localStorage.setItem('story_id', data.storyId);
            //alert('Story joined!')
    }))
    .catch((error) => {
        alert(error);
    })
};

function playStory(box) {
    fetch('/story/' + box.storyId + '/play', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            username: username,
        }),
    })
    .then(response => handleResponse(response, data => {
        sendSocket('play_story', data)
        playOrResumeStory(box)
    }))
    .catch((error) => {
        alert(error);
    })
};

function deleteStory(box) {
    fetch('/story/' + box.storyId, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            story_id: box.storyId
        }),
    })
    .then(response => handleResponse(response, data => {
        sendSocket('delete_story', data)
        localStorage.setItem('story_id', undefined);
        alert('Story deleted!')
        drawDeletedStory(box);
    }))
};

function leaveStory(box) {
    fetch('/story/' + box.storyId + '/leave', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            username: username,
        }),
    })
    .then(response => handleResponse(response, data => {
        sendSocket('leave_story', data)
        localStorage.setItem('story_id', undefined);
        drawLeftStory(box);
    }))
    .catch((error) => {
        alert(error);
    });
};


function createButtons(box) {
    box.boxElement.removeEventListener('click', createClickHandler(box));
    if (box.creator === username) {
        var playButton = document.createElement('button');
        if (box.storyId === story_id) {
            playButton.innerHTML = 'Resume Story';
            playButton.addEventListener('click', () => resumeStory(box))
        } else {
            playButton.innerHTML = 'Play Story';
            playButton.addEventListener('click', () => playStory(box))
        }
        playButton.id = 'playButton' + box.boxId;  // Add a unique id
        box.boxElement.appendChild(playButton);
    }
    var leaveButton = document.createElement('button');
    leaveButton.innerHTML = 'Leave Story';
    leaveButton.addEventListener('click', () => leaveStory(box))
    leaveButton.id = 'leaveButton' + box.boxId;  // Add a unique id
    box.boxElement.appendChild(leaveButton);

    if (box.creator === username) {
        var thirdButton = document.createElement('button');
        thirdButton.innerHTML = 'Delete Story';
        thirdButton.id = 'deleteButton' + box.boxId;  // Add a unique id
        thirdButton.addEventListener('click', () => deleteStory(box));
        box.boxElement.appendChild(thirdButton);
    }
}

function refreshBox(box) {
    var parent = box.parentNode;
    var newBox = box.cloneNode(true);
    parent.replaceChild(newBox, box);
}
function removeButtons(box) {
    // Find the left and right buttons within the boxElement
    var playButton = document.getElementById('playButton' + box.boxId);
    var leaveButton = document.getElementById('leaveButton' + box.boxId);
    var deleteButton = document.getElementById('deleteButton' + box.boxId);
    
    // Remove the left and right buttons if they exist
    if (playButton) {
        playButton.parentNode.removeChild(playButton);
        playButton.remove();
        
    }
    if (leaveButton) {
        leaveButton.parentNode.removeChild(leaveButton);
        leaveButton.remove();

    }
    if (deleteButton) {
        deleteButton.parentNode.removeChild(deleteButton);
        deleteButton.remove();

    }
}

let username = localStorage.getItem('username');
let story_id = localStorage.getItem('story_id');
var boxes = [
    { boxElement: document.getElementById('box1'), boxId: 1, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('box2'), boxId: 2, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('box3'), boxId: 3, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
]

initializeDashboard(boxes);