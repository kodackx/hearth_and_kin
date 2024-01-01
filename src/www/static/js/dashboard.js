function initializeDashboard(boxes) {
    document.getElementById('username').textContent = username;
    fetch('/rooms', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(rooms => {

        // Draw created rooms
        rooms.forEach(room => {
            var box = boxes.find(box => box.boxId === room.room_id);
            box.roomId = room.room_id;
            console.log(room.creator);
            // Join any previously joined room
            // TODO: only draw joined if user is in room
            if (username == room.creator) {
                drawJoinedRoom(box);
            } else {
                drawCreatedRoom(box);
            }
        });

        
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    // Add event listeners to the boxes
    boxes.forEach(box => {
        // box.boxElement.addEventListener('click', createClickHandler(box));
        box.boxElement.addEventListener('click', () => createRoom(box), { 'once': true});
    });
}

function createClickHandler(box) {
    return function() {
        createRoom(box);
    };
}

function drawCreatedRoom(box) {
    // refreshBox(box);
    box.boxElement.style.backgroundColor = 'blue';
    box.roomCreated = true;
    box.creator = username;
    box.roomId = box.boxId;
    box.boxElement.querySelector('.box-footer').textContent = 'Join Room';
    //box.boxElement.removeEventListener('click', createClickHandler(box));
    box.boxElement.addEventListener('click', () => joinRoom(box), { 'once': true});
}


function drawJoinedRoom(box) {
    box.boxElement.querySelector('.box-footer').textContent = undefined;
    box.boxElement.style.backgroundColor = 'green';
    createButtons(box);
}

function drawLeftRoom(box) {
    box.boxElement.style.backgroundColor = 'blue';
    box.boxElement.querySelector('.box-footer').textContent = 'Join Room';
    box.boxElement.addEventListener('click', () => joinRoom(box), { 'once': true});
    removeButtons(box);
}

function drawDeletedRoom(box) {
    box.boxElement.querySelector('.box-footer').textContent = 'Create New Room';
    box.boxElement.style.backgroundColor = 'white';
    box.roomId = undefined;
    box.roomCreated = false;
    box.creator = undefined;
    removeButtons(box);
}

function createRoom(box) {
    fetch('/room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            room_id: box.boxId,
            creator: username,
        }),
    })
    .then(response => {
        if (response.ok) {
            drawCreatedRoom(box);
            alert('Room created!')
        } else {
            alert('Creating the room failed')
            console.error('Error:', response);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

function joinRoom(box) {
    fetch('/room/' + box.roomId + '/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            room_id: box.roomId,
            username: username,
        }),
    })
    .then(response => {
        if (response.ok) {
            drawJoinedRoom(box);
        } else {
            alert('Joining the room failed')
            console.error('Error:', response);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

function createButtons(box) {
    box.boxElement.removeEventListener('click', createClickHandler(box));
    var playButton = document.createElement('button');
    playButton.innerHTML = 'Play Game';
    playButton.id = 'playButton' + box.boxId;  // Add a unique id
    playButton.addEventListener('click', () => startGame(box))
    box.boxElement.appendChild(playButton);

    var leaveButton = document.createElement('button');
    leaveButton.innerHTML = 'Leave Room';
    leaveButton.addEventListener('click', () => leaveRoom(box))
    leaveButton.id = 'leaveButton' + box.boxId;  // Add a unique id
    box.boxElement.appendChild(leaveButton);

    if (box.creator === username) {
        var thirdButton = document.createElement('button');
        thirdButton.innerHTML = 'Delete Room';
        thirdButton.id = 'deleteButton' + box.boxId;  // Add a unique id
        thirdButton.addEventListener('click', () => deleteRoom(box));
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

function startGame(box) {
    fetch('/game', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            room_id: box.roomId,
            description: prompt('Describe your character in a few words. Mention race, class, and any other important details.'),
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (confirm(data.description)) {
            localStorage.setItem('game_id', data.game_id);
            window.location.href = '/story';
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

function deleteRoom(box) {
    fetch('/room/' + box.roomId, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            room_id: box.roomId
        }),
    })
    .then(response => response.json())
    .then(response => {
        if (response.ok) {
            drawDeletedRoom(box);
        } else {
            alert('Deleting the room failed')
            console.error('Error:', response);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

function leaveRoom(box) {
    fetch('/room/' + box.roomId + '/leave', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            room_id: box.roomId,
            username: username,
        }),
    })
    .then(response => {
        if (response.ok) {
            drawLeftRoom(box);
        } else {
            alert('Leaving the room failed')
            console.error('Error:', response);
        }

    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

let username = localStorage.getItem('username');
var boxes = [
    { boxElement: document.getElementById('box1'), boxId: 1, roomId: undefined, roomCreated: false, creator: undefined, inGame: false},
    { boxElement: document.getElementById('box2'), boxId: 2, roomId: undefined, roomCreated: false, creator: undefined, inGame: false},
    { boxElement: document.getElementById('box3'), boxId: 3, roomId: undefined, roomCreated: false, creator: undefined, inGame: false},
]

initializeDashboard(boxes);