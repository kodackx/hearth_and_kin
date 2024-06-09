import { handleResponse } from './utils.js'
document.getElementById('username').textContent = localStorage.getItem('username');
let username = localStorage.getItem('username');
let story_id = localStorage.getItem('story_id');

var boxes = [
    { boxElement: document.getElementById('story1'), boxId: 1, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story2'), boxId: 2, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story3'), boxId: 3, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story4'), boxId: 4, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story5'), boxId: 5, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story6'), boxId: 6, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story7'), boxId: 7, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story8'), boxId: 8, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
    { boxElement: document.getElementById('story9'), boxId: 9, storyId: undefined, storyCreated: false, creator: undefined, storyActive: false},
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
        // Optionally, clear previous selections
        characterBoxes.forEach(characterBox => {
            characterBox.boxElement.classList.remove('selected');
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
        localStorage.setItem('character_id', parseInt(character.character_id));
        localStorage.setItem('story_id', character.story_id) //unsure if this is correct, why would there be just 1 story id?
        
        // Call loadStories with character_id
        loadStories(character.character_id);
    }

}

function updateEventListener(box, func) {
    box.boxElement.removeEventListener('click', box.clickHandler);
    box.clickHandler = func;
    box.boxElement.addEventListener('click', box.clickHandler);
}

function initializeDashboard(boxes) {
    document.getElementById('username').textContent = username;
    


    // Add event listeners to the boxes
    boxes.forEach(box => {
        // box.boxElement.addEventListener('click', createClickHandler(box));
        //box.boxElement.addEventListener('click', () => createStory(box), { 'once': true});
        updateEventListener(box, createClickHandler)
    });
}


function createClickHandler(box) {
    //const character = JSON.parse(localStorage.getItem('selectedCharacter'))
    return function() {
        createStory(box);
    };
}

function joinClickHandler(box) {
    return function() {
        joinStory(box);
    };
}


function playOrResumeStory(box) {
    return function() {
        localStorage.setItem('story_id', box.storyId);
        window.location.href = '/story';
    }
}


function drawCreatedStory(box, story) {
    box.boxElement.classList.add('created-story');
    box.storyCreated = true;
    box.creator = story.creator;
    box.storyId = story.story_id;
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    updateEventListener(box, joinStory);
}


function drawActiveStory(box) {
    box.storyActive = true;
    box.boxElement.classList.add('active-story');
    box.boxElement.querySelector('.box-footer').textContent = 'Resume Story';
    updateEventListener(box, playStory);
}


function drawJoinedStory(box) {
    box.boxElement.classList.add('joined-story');
    box.boxElement.querySelector('.box-footer').textContent = undefined;
    updateEventListener(box, leaveStory);
}


function drawLeftStory(box) {
    box.boxElement.classList.add('left-story');
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    updateEventListener(box, joinStory);
}


function drawDeletedStory(box) {
    box.boxElement.classList.add('deleted-story');
    box.boxElement.querySelector('.box-footer').textContent = 'Create New Story';
    box.storyId = undefined;
    box.storyCreated = false;
    box.creator = undefined;
    updateEventListener(box, createStory);
}


function loadStories(character_id) {
    fetch(`/stories?character_id=${character_id}`, {
        method: 'GET',
    })
    .then(response => handleResponse(response, stories => {
        const character = JSON.parse(localStorage.getItem('selectedCharacter'))
        
        // Clear previous story assignments
        boxes.forEach(box => {
            box.storyId = undefined;
            box.storyCreated = false;
            box.storyActive = false;
            box.creator = undefined;
            box.boxElement.classList.remove('created-story', 'active-story', 'joined-story', 'left-story', 'deleted-story');
            box.boxElement.querySelector('.box-footer').textContent = '';
            box.boxElement.style.display = 'none'; // Hide all boxes initially
        });
        
        // Determine the starting index for the boxes based on the selected character
        const characterIndex = characterBoxes.findIndex(box => box.boxElement.classList.contains('selected'));
        const startIndex = characterIndex * 3;

        // Show only the relevant story boxes
        for (let i = startIndex; i < startIndex + 3; i++) {
            if (i < boxes.length) {
                boxes[i].boxElement.style.display = 'block'; // Show relevant boxes
            }
        }
        
        // Assign stories to the appropriate boxes
        stories.forEach((story, index) => {
            const boxIndex = startIndex + index;
            if (boxIndex < boxes.length) {
                const box = boxes[boxIndex];
                box.storyId = story.story_id;
                box.storyCreated = true;
                box.storyActive = story.active;
                box.creator = story.creator;
                console.log('Drawing story:', story);

                if (story.active && story.story_id == character.story_id) {
                    drawActiveStory(box);
                } else if (!story.active && story.story_id == character.story_id) {
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
    const character_id = parseInt(localStorage.getItem('character_id'))
    fetch('/story', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.boxId,
            creator: character_id,
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
    const character_id = parseInt(localStorage.getItem('character_id'))
    fetch('/story/' + box.storyId + '/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            character_id: character_id
        }),
    })
    .then(response => handleResponse(response, data => {
        localStorage.setItem('story_id', data.story_id);
        drawJoinedStory(box);
        alert('Story joined!')
    }))
    .catch((error) => {
        alert(error);
    })
};


function playStory(box) {
    const character_id = parseInt(localStorage.getItem('character_id'))
    fetch('/story/' + box.storyId + '/play', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            character_id: character_id
        }),
    })
    .then(response => handleResponse(response, data => {
        localStorage.setItem('story_id', box.storyId);
        window.location.href = '/story';
    }))
    .catch((error) => {
        alert(error);
    })
};


function deleteStory(box) {
    const character_id = parseInt(localStorage.getItem('character_id'))
    fetch('/story/' + box.storyId, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            character_id: character_id,
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
    const character_id = parseInt(localStorage.getItem('character_id'))
    fetch('/story/' + box.storyId + '/leave', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: box.storyId,
            character_id: character_id
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