import { handleResponse } from './utils.js'
import { connectToWebSocket, closeWebSocket } from './websocketManager.js';
import * as storyApi from './api/story.js'

// Event listener for communication of messages
// Connect to the dashboard websocket endpoint with the specific message handler

connectToWebSocket(storyApi.webSocketEndpoint, handleStoryMessage);
window.addEventListener('beforeunload', function() {
    localStorage.setItem('joinedStoryId', joinedStoryId)
    closeWebSocket(storyApi.webSocketEndpoint);
});

function handleStoryMessage(message) {
    let parsedMessage = JSON.parse(message.data);
    let action = parsedMessage.action;
    let data = parsedMessage.data;
    let userAction = data.username == username
    console.log('client received: ', parsedMessage);
    let box = boxes.find(box => box.storyId == data.story_id);
    switch (action) {
        case 'create_story':
            // TODO: decouple boxid and storyid
            let createdBox = boxes[data.story_id - 1]
            drawCreatedStory(createdBox, data);
            break;
        case 'join_story':
            if (userAction) {
                joinedStoryId = data.story_id
                drawJoinedStory(box, data);
            }
            box.users.push(data.username)
            box.boxElement.querySelector('.box-content').textContent = `Users in story: ${box.users.join(', ')}`
            break;
        case 'leave_story':
            if (userAction) {
                joinedStoryId = null
                drawLeftStory(box,data);
            }
            box.users.pop(data.username)
            if (box.users.length == 0){
                box.boxElement.querySelector('.box-content').textContent = `No users in story`
            } else {
                box.boxElement.querySelector('.box-content').textContent = `Users in story: ${box.users.join(', ')}`
            }
            break;
        case 'delete_story':
            box.users = []
            joinedStoryId = null
            drawDeletedStory(box);
            break;
        case 'delete_story':
            box.users = []
            joinedStoryId = null
            drawDeletedStory(box);
            break;
        case 'play_story':
            if (box.users.find(user => user == username)) {
                drawResumeStory(box)
                playOrResumeStory(box);
            } else {
                drawActiveStory(box)
            }
            break;
        default:
            alert('Got action ', action, ' from websocket. NYI')
            break
    }
}

function initializeDashboard(boxes) {
    document.getElementById('username').textContent = username;
    loadStories();
}

function playOrResumeStory(box) {
    window.location.href = '/story';
}

function joinStoryHandler(storyId) {
    return function() {
        storyApi.joinStory(storyId);
    };
}

function createStoryHandler(storyId) {
    return function() {
        storyApi.createStory(storyId);
    };
}

function drawCreatedStory(box, story) {
    box.boxElement.style.backgroundColor = 'blue';
    box.storyCreated = true;
    box.creator = story.creator;
    box.storyId = story.story_id;
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    box.boxElement.querySelector('.box-header').textContent = `Story Creator: ${story.creator}`;

    updateEventListener(box, joinStoryHandler)
}

function drawActiveStory(box) {
    box.boxElement.querySelector('.box-footer').textContent = 'Story in Play';
    box.boxElement.style.backgroundColor = 'purple';
    //box.boxElement.removeEventListener('click', () => storyApi.createStory(box.storyId), { 'once': true});
    box.boxElement.removeEventListener('click', box.clickHandler);
}

function drawResumeStory(box) {
    box.boxElement.querySelector('.box-footer').textContent = 'Story in Play';
    box.boxElement.style.backgroundColor = 'purple';
    //box.boxElement.removeEventListener('click', () => storyApi.createStory(box.storyId), { 'once': true});
    box.boxElement.removeEventListener('click', box.clickHandler);
    createButtons(box);
}

function drawJoinedStory(box) {
    box.boxElement.querySelector('.box-footer').textContent = null;
    box.boxElement.style.backgroundColor = 'green';
    //box.boxElement.removeEventListener('click',  () => storyApi.joinStory(box.storyId), { 'once': true});
    box.boxElement.removeEventListener('click', box.clickHandler);
    createButtons(box);
}

function drawLeftStory(box) {
    box.boxElement.style.backgroundColor = 'blue';
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    
    updateEventListener(box, joinStoryHandler)    
    removeButtons(box);
}
// TODO: event listener handling
function drawDeletedStory(box) {
    box.boxElement.querySelector('.box-content').textContent = '+';
    box.boxElement.querySelector('.box-footer').textContent = 'Create New Story';
    box.boxElement.querySelector('.box-header').textContent = '';
    box.boxElement.style.backgroundColor = 'white';
    box.storyId = null;
    box.storyCreated = false;
    box.creator = null;
    updateEventListener(box, createStoryHandler)
    removeButtons(box);
}

function updateEventListener(box, func) {
    box.boxElement.removeEventListener('click', box.clickHandler);
    box.clickHandler = func(box.boxId);
    box.boxElement.addEventListener('click', box.clickHandler);
}

// TODO: refactor: loadStories in story api
function loadStories() {
    fetch('/stories', {
        method: 'GET',
    })
    .then(response => handleResponse(response, stories => {
        stories.forEach(story => {
            if (story.story_id <= 3) { // we only support 3 boxes/stories for now
                let box = boxes.find(box => box.boxId === story.story_id) // TODO: decide how we want to populate boxes
                if (box) {
                    box.storyId = story.story_id
                    box.creator = story.creator
                    box.storyActive = story.active
                    storyApi.getStoryUsers(story.story_id).then(users => {
                        if (users.length === 0) {
                            // Handle the case where there are no users
                        } else {
                            users.forEach(user => {
                                box.users.push(user.username);
                            });
                            box.boxElement.querySelector('.box-content').textContent = `Users in story: ${box.users.join(', ')}`
                        }   
                        if (story.active && story.story_id != joinedStoryId) {
                            drawActiveStory(box);
                        } else if (story.active && story.story_id == joinedStoryId) { 
                            drawResumeStory(box)
                        }
                        else if (!story.active && story.story_id == joinedStoryId) {
                            drawJoinedStory(box);
                        } else {
                            drawCreatedStory(box, story);
                        }
                })}
        }})
    }))
    .then( () => {
            boxes.forEach(box => {
                if(!box.storyId) {
                    box.clickHandler = createStoryHandler(box.boxId);
                    box.boxElement.addEventListener('click', box.clickHandler);
                }
            })
    })
    .catch((error) => {
        alert(error);
    })
}


function createButtons(box) {
    box.boxElement.removeEventListener('click', box.clickHandler);
    if (box.creator === username) {
        var playButton = document.createElement('button');
        if (box.storyActive) {
            playButton.innerHTML = 'Resume Story';
            playButton.addEventListener('click', () => storyApi.playStory(box.storyId))
        } else {
            playButton.innerHTML = 'Play Story';
            playButton.addEventListener('click', () => storyApi.playStory(box.storyId))
        }
        playButton.id = 'playButton' + box.boxId;  // Add a unique id
        box.boxElement.appendChild(playButton);
    }
    var leaveButton = document.createElement('button');
    leaveButton.innerHTML = 'Leave Story';
    leaveButton.addEventListener('click', () => storyApi.leaveStory(box.storyId))
    leaveButton.id = 'leaveButton' + box.boxId;  // Add a unique id
    box.boxElement.appendChild(leaveButton);

    if (box.creator === username) {
        var thirdButton = document.createElement('button');
        thirdButton.innerHTML = 'Delete Story';
        thirdButton.id = 'deleteButton' + box.boxId;  // Add a unique id
        thirdButton.addEventListener('click', () => storyApi.deleteStory(box.storyId));
        box.boxElement.appendChild(thirdButton);
    }
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

const username = localStorage.getItem('username')
var joinedStoryId = localStorage.getItem('joinedStoryId')
var boxes = [
    { boxElement: document.getElementById('box1'), boxId: 1, storyId: null, storyCreated: false, creator: null, storyActive: false, users: [], clickHandler: null},
    { boxElement: document.getElementById('box2'), boxId: 2, storyId: null, storyCreated: false, creator: null, storyActive: false, users: [], clickHandler: null},
    { boxElement: document.getElementById('box3'), boxId: 3, storyId: null, storyCreated: false, creator: null, storyActive: false, users: [], clickHandler: null},
]

initializeDashboard(boxes);