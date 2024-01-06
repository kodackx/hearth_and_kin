import { handleResponse } from './utils.js'


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

function drawCreatedStory(box) {
    // refreshBox(box);
    box.boxElement.style.backgroundColor = 'blue';
    box.storyCreated = true;
    box.creator = username;
    box.storyId = box.boxId;
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    //box.boxElement.removeEventListener('click', createClickHandler(box));
    box.boxElement.addEventListener('click', () => joinStory(box), { 'once': true});
}

function drawActiveStory(box) {
    box.boxElement.querySelector('.box-footer').textContent = 'Resume Story';
    box.boxElement.style.backgroundColor = 'purple';
    box.boxElement.addEventListener('click', () => playOrResumeStory(box), { 'once': true});
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
            box.storyId = story.story_id;
            // Join any previously joined story
            // TODO: only draw joined if user is in story
            if (story.active && username == story.creator) {
                console.log('hej')
                drawActiveStory(box)
            }
            else if (!story.active && username == story.creator) {
                drawJoinedStory(box);
            } else {
                drawCreatedStory(box);
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
            drawCreatedStory(box);
            alert('Story created!')
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
            drawJoinedStory(box);
            alert('Story joined!')
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
        drawLeftStory(box);
    }))
    .catch((error) => {
        alert(error);
    });
};


function createButtons(box) {
    box.boxElement.removeEventListener('click', createClickHandler(box));
    var playButton = document.createElement('button');
    playButton.innerHTML = 'Play Story';
    playButton.id = 'playButton' + box.boxId;  // Add a unique id
    playButton.addEventListener('click', () => playStory(box))
    box.boxElement.appendChild(playButton);

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
var boxes = [
    { boxElement: document.getElementById('box1'), boxId: 1, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('box2'), boxId: 2, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('box3'), boxId: 3, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
]

initializeDashboard(boxes);