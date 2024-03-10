import { handleResponse } from './utils.js'
document.getElementById('username').textContent = localStorage.getItem('username');
let username = localStorage.getItem('username');
let story_id = localStorage.getItem('story_id');
var boxes = [
    { boxElement: document.getElementById('story1'), boxId: 1, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story2'), boxId: 2, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story3'), boxId: 3, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
];


var characterBoxes = [
    { boxElement: document.getElementById('char1'), boxId: 1, characterId: undefined, characterCreated: false, creator: undefined},
    { boxElement: document.getElementById('char2'), boxId: 2, characterId: undefined, characterCreated: false, creator: undefined},
    { boxElement: document.getElementById('char3'), boxId: 3, characterId: undefined, characterCreated: false, creator: undefined},
];


document.addEventListener('DOMContentLoaded', function() {
    // first we requests the list of characters and populate the boxes
    getCharactersForUser().then(characters => {
        if (characters && characters.length > 0) {
            characters.forEach((character, index) => {
                if (index < characterBoxes.length) {
                    const box = characterBoxes[index];
                    box.boxElement.querySelector('.box-content').innerHTML = `
                        <img src="${character.portrait_path}" alt="Character Portrait" class="rounded-avatar"></img>
                        `;
                    box.boxElement.querySelector('.box-footer').textContent = `${character.character_name}`;
                     
                    // Add event listener for selecting a character
                     box.boxElement.addEventListener('click', function() {
                        selectCharacter(box, character);
                    });
                }
            });
        }
         // After populating existing characters, add a box for creating a new character
         addCreateNewCharacterBox(characters ? characters.length : 0);
    });
    initializeDashboard(boxes);
});


async function getCharactersForUser() {
    const current_user = username; // Assuming 'username' is already defined in your scope
    const url = `/characters?current_user=${encodeURIComponent(current_user)}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('Received characters for this account:', data);
        return data; // This will return the array from data
    } catch (error) {
        console.error('There was a problem with your fetch operation:', error);
        throw error; // Rethrow the error if you want to handle it outside
    }
}


function addCreateNewCharacterBox(numberOfCharacters) {
    // Check if there's an available box to be used for creating a new character
    if (numberOfCharacters < characterBoxes.length) {
        const createBox = characterBoxes[numberOfCharacters];
        createBox.boxElement.querySelector('.box-content').innerHTML = `
            <div class="create-new-character-content">+</div>
        `;
        createBox.boxElement.querySelector('.box-footer').textContent = 'Create New Character';
        // Add click event listener to redirect to the character creation page
        createBox.boxElement.addEventListener('click', function() {
            window.location.href = '/newcharacter';
        });
    } else {
        // If all boxes are used, consider dynamically creating a new box or indicating the limit has been reached
        console.log('Maximum number of character boxes reached.');
    }
}


function selectCharacter(box, character) {
    // Check if the clicked box is already selected
    if (box.boxElement.classList.contains('selected')) {
        // If already selected, remove the selection and hide the story container
        box.boxElement.classList.remove('selected');
        const container = document.querySelector('.stories-container');
        container.style.display = 'none';
        // container.classList.remove('visible');
        console.log('No characters selected.');
    } else {
        // If not already selected, proceed with the selection

        // Optionally, clear previous selections
        characterBoxes.forEach(characterBox => {
            characterBox.boxElement.classList.remove('selected'); // Assuming 'selected' is a class that styles the selected box
        });

        // Mark the clicked box as selected
        box.boxElement.classList.add('selected');

        // Display the story container
        const container = document.querySelector('.stories-container');
        container.style.display = 'flex';
        // container.classList.add('visible');

        // Optionally, do something with the selected character data
        console.log('Selected character:', character);
        // Save selected character data to localstorage
        localStorage.setItem('selectedCharacter', JSON.stringify(character));
    }

}


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
            box.storyId = story.story_id;
            // Join any previously joined story
            if (story.active && story_id == story.story_id) {
                drawActiveStory(box)
            }
            else if (!story.active && story_id == story.story_id) {
                drawJoinedStory(box);
            } else {
                drawCreatedStory(box, story);
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
            drawCreatedStory(box, data);
            alert('Story created!')
    }))
    .catch((error) => {
        alert(error);
    });
};


function joinStory(box) {
    let selectedCharacter = JSON.parse(localStorage.getItem('selectedCharacter'));
    let character_id = selectedCharacter.character_id;
    fetch('/story/' + box.storyId + '/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            username: username,
            character_id: character_id
        }),
    })
    .then(response => handleResponse(response, data => {
            localStorage.setItem('story_id', data.storyId);
            drawJoinedStory(box);
            alert('Story joined!')
    }))
    .catch((error) => {
        alert(error);
    })
};


function playStory(box) {
    let selectedCharacter = JSON.parse(localStorage.getItem('selectedCharacter'));
    let character_id = selectedCharacter.character_id;
    fetch('/story/' + box.storyId + '/play', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            username: username,
            character_id: character_id
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

