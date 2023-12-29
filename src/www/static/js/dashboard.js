function initializeDashboard(boxes) {
    document.getElementById('username').textContent = username;

    fetch('/rooms', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(rooms => {

        rooms.forEach(room => {
            var box = boxes.find(box => box.boxId === room.room_id);
            box.boxElement.style.backgroundColor = 'blue';
            box.roomId = room.room_id;
            box.roomCreated = true;
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });

    // Add event listeners to the boxes
    boxes.forEach(box => {
        box.boxElement.addEventListener('click', () => handleBoxClick(box));
    });
}

function createRoom(box) {
    fetch('/room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            room_id: box.boxId,
            username: username,
        }),
    })
    .then(response => {
        if (response.ok) {
            box.boxElement.style.backgroundColor = 'blue';
            box.roomCreated = true;
            box.roomId = box.boxId;
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
            username: localStorage.getItem('username'),
        }),
    })
    .then(response => {
        if (response.ok) {
            box.boxElement.style.backgroundColor = 'green';
            createButtons(box);
        } else {
            alert('Joining the room failed')
            console.error('Error:', response);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

function handleBoxClick(box) {
    if (box.roomCreated) {
        joinRoom(box)
    } else {
        createRoom(box)
    }
};

function createButtons(box) {
    box.boxElement.removeEventListener('click', handleBoxClick);
    var leftButton = document.createElement('button');
    leftButton.innerHTML = 'Play Game';
    leftButton.id = 'leftButton' + box.boxId;  // Add a unique id
    leftButton.addEventListener('click', () => startGame(box))
    box.boxElement.appendChild(leftButton);

    var rightButton = document.createElement('button');
    rightButton.innerHTML = 'Leave Room';
    rightButton.addEventListener('click', () => leaveRoom(box))
    rightButton.id = 'rightButton' + box.boxId;  // Add a unique id
    box.boxElement.appendChild(rightButton);
}

function removeButtons(box) {
    // Find the left and right buttons within the boxElement
    var leftButton = document.getElementById('leftButton' + box.boxId);
    var rightButton = document.getElementById('rightButton' + box.boxId);
    
    // Remove the left and right buttons if they exist
    if (leftButton) {
        leftButton.parentNode.removeChild(leftButton);
        leftButton.remove();
    }
    if (rightButton) {
        rightButton.parentNode.removeChild(rightButton);
        rightButton.remove();

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
    .then(response => response.json())
    .then(data => {
        box.boxElement.removeEventListener('click', () => handleBoxClick(box));
        removeButtons(box)
        alert(data.message);
        box.boxElement.style.backgroundColor = 'white';
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

let username = localStorage.getItem('username');
var boxes = [
    { boxElement: document.getElementById('box1'), boxId: 1, roomId: undefined, roomCreated: false},
    { boxElement: document.getElementById('box2'), boxId: 2, roomId: undefined, roomCreated: false},
    { boxElement: document.getElementById('box3'), boxId: 3, roomId: undefined, roomCreated: false},
]

initializeDashboard(boxes);