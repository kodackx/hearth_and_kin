import {handleApiErrors} from './utils.js'
import {showToast} from './utils.js'
document.getElementById('username').textContent = localStorage.getItem('username');
let username = localStorage.getItem('username');
let story_id = localStorage.getItem('story_id');

var boxes = [
    { boxElement: document.getElementById('story1'), boxId: 1, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story2'), boxId: 2, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story3'), boxId: 3, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story4'), boxId: 4, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story5'), boxId: 5, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story6'), boxId: 6, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story7'), boxId: 7, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story8'), boxId: 8, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
    { boxElement: document.getElementById('story9'), boxId: 9, storyId: undefined, inviteCode: undefined, storyCreated: false, party_lead: undefined, storyActive: false},
];


var characterBoxes = [
    { boxElement: document.getElementById('char1'), boxId: 1, characterId: undefined, characterCreated: false, party_lead: undefined},
    { boxElement: document.getElementById('char2'), boxId: 2, characterId: undefined, characterCreated: false, party_lead: undefined},
    { boxElement: document.getElementById('char3'), boxId: 3, characterId: undefined, characterCreated: false, party_lead: undefined},
];

document.addEventListener('DOMContentLoaded', welcomePopUp);
document.addEventListener('DOMContentLoaded', InitializeInviteCodePopUp);
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

function welcomePopUp() {
    // Check if the user has seen the popup before
    if (!localStorage.getItem('welcomePopupShown')) {
        // Show the popup
        document.getElementById('welcome-popup').style.display = 'block';
        // Set the flag in localStorage
        localStorage.setItem('welcomePopupShown', 'false');
    }
    // Get the <span> element that closes the popup
    var closeBtn = document.getElementsByClassName('close-btn')[0];
    // When the user clicks on <span> (x), close the popup
    closeBtn.onclick = function() {
        document.getElementById('welcome-popup').style.display = 'none';
    }
    // When the user clicks anywhere outside of the popup, close it
    window.onclick = function(event) {
        if (event.target == document.getElementById('welcome-popup')) {
            document.getElementById('welcome-popup').style.display = 'none';
        }
    }
    localStorage.setItem('welcomePopupShown', 'false');
}

function InitializeInviteCodePopUp() {
    console.log('Initializing invite code functionality...')
    // Add event listener for the "Use Invite Code" button
    document.getElementById('use-invite-code-btn').addEventListener('click', function() {
        console.log('Clicked on the invite code button!')
        document.getElementById('invite-code-popup').style.display = 'block';
    });

    // Add event listener for the close button in the popup
    document.querySelector('#invite-code-popup .close-btn').addEventListener('click', function() {
        document.getElementById('invite-code-popup').style.display = 'none';
    });

    // Add event listener for the submit button in the popup
    document.getElementById('submit-invite-code-btn').addEventListener('click', function() {
        const inviteCode = document.getElementById('invite-code-input').value;
        if (inviteCode) {
            console.log('Trying to conenct with invite code')
            console.log(inviteCode)
            joinStoryByInviteCode(inviteCode);
        }
    });
}

async function getCharactersForUser() {
    const user_id = localStorage.getItem('user_id');
    if (!user_id) {
        alert("No current user was identified. Please log in and try again.");
        window.location.href = '/';
        return;
    }
    const url = `/characters?current_user_id=${encodeURIComponent(user_id)}`;
    try {
        const response = await fetch(url);
        return handleApiErrors(response, data => {
            console.log('Received characters for this account:', data);
            return data;
        });
    } catch (error) {
        showToast(`Frontend Error: ${error.message}`);
        throw error;
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

function initializeDashboard(boxes) {
    document.getElementById('username').textContent = username;
    // Add event listeners to the boxes
    boxes.forEach(box => {
        drawEmptyStory(box)
    });
}

function loadStories(character_id) {
    fetch(`/stories?character_id=${character_id}`, {
        method: 'GET',
    })
    .then(response => handleApiErrors(response, stories => {
        const character = JSON.parse(localStorage.getItem('selectedCharacter'))
        
        // Clear previous story assignments
        boxes.forEach(box => {
            box.storyId = undefined;
            box.storyCreated = false;
            box.storyActive = false;
            box.party_lead = undefined;
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
                boxes[i].boxElement.style.display = 'flex'; // Show relevant boxes
            }
        }
        
        // Assign stories to the appropriate boxes
        stories.forEach((story, index) => {
            const boxIndex = startIndex + index;
            if (boxIndex < boxes.length) {
                const box = boxes[boxIndex];
                box.storyId = story.story_id;
                console.log(`Setting storyId for box ${box.boxId}: ${box.storyId}`);
                box.storyCreated = true; //we know this because of how we entered the loop
                box.storyActive = story.has_started;
                box.party_lead = story.party_lead;
                console.log('Drawing story:', story);
                console.log('Printing boolean checks...')
                console.log('Story active: ' + box.storyActive)
                console.log('Story party_lead: ' + box.party_lead);
                console.log('Story party_member_1: ' + box.party_member_1);
                console.log('Story party_member_2: ' + box.party_member_2);
                console.log('Story ID: ' + box.storyId);
                // Reasoning: We already know the box we are populating is for the currently selected character
                // All that remains to find out is if the story has started or not
                // Remember, if this data is pulled, it already means the character is involved with
                // this story either as a memeber or a leader
                if (box.storyActive) {
                    drawActiveStory(box);
                } else {
                    drawJoinedStory(box);
                } 
            }
        });

         // Mark any remaining boxes as empty
         for (let i = startIndex + stories.length; i < startIndex + 3; i++) {
            if (i < boxes.length) {
                drawEmptyStory(boxes[i]);
            }
        };
    }))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    });
}

function createStory(box) {
    const character_id = parseInt(localStorage.getItem('character_id'));
    fetch('/story', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            party_lead: character_id
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('API response:', data);
        const { story, invite_code } = data;

        if (story.story_id && invite_code && story.party_lead) {
            console.log('Story created:', story.story_od);
            console.log('Invite code:', invite_code);
            console.log('Party Lead', story.party_lead)
            // Set story id, party lead and invite code on the box before draw
            box.inviteCode = invite_code;
            box.storyId = story.story_id; 
            box.partyLead = story.party_lead; 
            localStorage.setItem(`invite_code_${story.story_id}`, invite_code); // Save invite code in local storage
            drawCreatedStory(box, story, invite_code);
            showToast('Story created!');
        } else {
            console.error('Error: storyId is undefined or API response is malformed');
            showToast('Error: Failed to create story. Please try again.');
        }
    })
    .catch((error) => {
        console.error('Fetch error:', error);
        showToast(`Frontend Error: ${error.message}`);
    });
}

// function joinStory(box) {
//     const character_id = parseInt(localStorage.getItem('character_id'));
//     fetch('/story/' + box.storyId + '/join', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//             story_id: box.storyId,
//             character_id: character_id
//         }),
//     })
//     .then(response => handleApiErrors(response, data => {
//         localStorage.setItem('story_id', data.story_id);
//         drawJoinedStory(box);
//         showToast('Story joined!');
//     }))
//     .catch((error) => {
//         showToast(`Frontend Error: ${error.message}`);
//     });
// }

async function joinStoryByInviteCode(inviteCode) {
    try {
        const response = await fetch(`/join_by_invite?invite_code=${inviteCode}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ invite_code: inviteCode }),
        });

        handleApiErrors(response, async story => {
            const storyId = story.story_id;
            const character_id = parseInt(localStorage.getItem('character_id'));

            // Make another API call to add the player to the story
            const addPlayerResponse = await fetch(`/story/${storyId}/add_player`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ character_id: character_id , story_id: storyId}),
            });

            handleApiErrors(addPlayerResponse, () => {
                // Find the appropriate box and draw it as a joined story
                const box = boxes.find(box => box.storyId === undefined); // Find the first empty box
                if (box) {
                    box.storyId = storyId;
                    drawJoinedStory(box);
                    showToast('Successfully joined the story!');
                } else {
                    // TODO, stop player BEFORE joining a story if all boxes are full!
                    showToast('No available box to display the joined story.');
                }
            });
        });
    } catch (error) {
        showToast(`Error: ${error.message}`);
    }
}

function goToLobby(box) {
    const storyId = box.storyId || box.story_id; // Handle both cases
    if (!storyId) {
        console.error("Error: We don't have the storyId");
        return;
    }
    // Save story_id to localStorage
    localStorage.setItem('story_id', storyId);
    // Navigate to the lobby
    window.location.href = '/lobby';
}


function deleteStory(box) {
    const character_id = parseInt(localStorage.getItem('character_id'));
    console.log("Attempting to DELETE '/story/'" + box.storyId);
    console.log("Character ID: " + character_id);
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
    .then(response => handleApiErrors(response, data => {
        localStorage.setItem('story_id', undefined);
        showToast('Story deleted!');
        drawDeletedStory(box);
    }))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    });
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
    .then(response => handleApiErrors(response, data => {
        localStorage.setItem('story_id', undefined);
        drawLeftStory(box);
    }))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    });
};

function addDeleteButton(box) {
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.classList.add('delete-button');
    deleteButton.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevent triggering the box click event
        if (confirm('Are you sure you want to delete this story?')) {
            deleteStory(box);
        }
    });
    box.boxElement.appendChild(deleteButton);
};

function drawCreatedStory(box, story, invite_code) {
    box.boxElement.classList.add('created-story');
    box.boxElement.querySelector('.box-content').innerHTML = `
    <img src="static/img/HAK_story_icons_3.png" alt="Begin Adventure" class="story-icon">
    `;
    // These are set for a second time but might not be needed
    box.inviteCode = invite_code;
    box.storyId = story.story_id; 
    box.partyLead = story.party_lead; 
    box.storyCreated = true;
    box.boxElement.classList.add('joined-story');
    box.boxElement.querySelector('.box-footer').textContent = 'Begin adventure...';
    box.boxElement.removeEventListener('click', box.clickHandler); // Remove previous handler if any
    box.clickHandler = () => goToLobby(box); // Assign new handler
    box.boxElement.addEventListener('click', box.clickHandler);

    // Add delete button if the character is the party lead
    if (box.party_lead === parseInt(localStorage.getItem('character_id'))) {
        addDeleteButton(box);
    }
}

function drawActiveStory(box) {
    console.log(`[drawActiveStory] Checking storyId for box ${box.boxId}: ${box.storyId}`);
    box.storyActive = true;
    box.boxElement.classList.add('active-story');
    box.boxElement.querySelector('.box-content').innerHTML = `
    <img src="static/img/HAK_story_icons_4.png" alt="Resume Adventure" class="story-icon">
    `;
    box.boxElement.querySelector('.box-footer').textContent = 'Resume adventure';
    box.boxElement.removeEventListener('click', box.clickHandler); // Remove previous handler if any
    box.clickHandler = () => goToLobby(box); // Assign new handler
    box.boxElement.addEventListener('click', box.clickHandler);
    // Add delete button if the character is the party lead
    if (box.party_lead === parseInt(localStorage.getItem('character_id'))) {
        addDeleteButton(box);
    }
}

function drawJoinedStory(box) {
    box.boxElement.classList.add('joined-story');
    box.boxElement.querySelector('.box-content').innerHTML = `
    <img src="static/img/HAK_story_icons_2.png" alt="Join Story" class="story-icon">
    `;
    box.boxElement.querySelector('.box-footer').textContent = 'Join your kin...';
    box.boxElement.removeEventListener('click', box.clickHandler); // Remove previous handler if any
    box.clickHandler = () => goToLobby(box); // Assign new handler
    box.boxElement.addEventListener('click', box.clickHandler);
    // Add delete button if the character is the party lead
    if (box.party_lead === parseInt(localStorage.getItem('character_id'))) {
        addDeleteButton(box);
    }
}

function drawLeftStory(box) {
    box.boxElement.classList.add('left-story');
    box.boxElement.querySelector('.box-footer').textContent = 'Join Story';
    box.boxElement.removeEventListener('click', box.clickHandler); // Remove previous handler if any
    box.clickHandler = () => createStory(box); // Assign new handler
    box.boxElement.addEventListener('click', box.clickHandler);
}

function drawDeletedStory(box) {
    box.boxElement.classList.add('deleted-story');
    box.boxElement.querySelector('.box-content').innerHTML = `
    <img src="static/img/HAK_story_icons_1.png" alt="Create New Story" class="story-icon">
    `;
    box.boxElement.querySelector('.box-footer').textContent = 'Create New Story';
    box.storyId = undefined;
    box.storyCreated = false;
    box.party_lead = undefined;
    box.boxElement.removeEventListener('click', box.clickHandler); // Remove previous handler if any
    box.clickHandler = () => createStory(box); // Assign new handler
    box.boxElement.addEventListener('click', box.clickHandler);
}

function drawEmptyStory(box) {
    box.boxElement.classList.add('empty-story');
    box.boxElement.querySelector('.box-content').innerHTML = `
    <img src="static/img/HAK_story_icons_1.png" alt="Create New Story" class="story-icon">
    `;
    box.boxElement.querySelector('.box-footer').textContent = 'Create New Story';
    box.storyId = undefined;
    box.storyCreated = false;
    box.party_lead = undefined;
    box.boxElement.removeEventListener('click', box.clickHandler); // Remove previous handler if any
    box.clickHandler = () => createStory(box); // Assign new handler
    box.boxElement.addEventListener('click', box.clickHandler);
}