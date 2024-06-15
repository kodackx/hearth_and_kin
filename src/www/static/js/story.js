import { handleApiErrors} from './utils.js'
import {showToast} from './utils.js'
import * as messageApi from './api/message.js'
import { connectToWebSocket, closeWebSocket } from './websocketManager.js';

let currentAudio = null; // Add this at the top of your script
let currentSoundtrack = new Audio("static/soundtrack/ambiance.m4a"); // Default ambiance audio
const story_id = localStorage.getItem('story_id');
let selectedCharacter = JSON.parse(localStorage.getItem('selectedCharacter'));
let avatarPath = selectedCharacter.portrait_path; //only for current player!
let character_id = parseInt(selectedCharacter.character_id);
let character_name = selectedCharacter.character_name;
let narrator_portrait = 'static/img/narrator.png';
let system_portrait = 'static/img/system.png';

const hostname = window.location.hostname;
const port = hostname === '127.0.0.1' ? ':8000' : '';
export const webSocketEndpoint = `ws://${hostname}${port}/ws/story/${story_id}`;
console.log('Attempting STORY websocket connection at: ' + webSocketEndpoint)

connectToWebSocket(webSocketEndpoint, handleMessage);
window.addEventListener('beforeunload', function () {
    closeWebSocket(webSocketEndpoint);
});

// Set up elements

// event listeners and hiding play elements for now
document.getElementById('main-content').style.display = 'none';

//adding event listeners
document.addEventListener('DOMContentLoaded', () => {
    obtainInviteCode();
});
document.getElementById('ready-btn').addEventListener('click', function() {
    document.getElementById('ready-btn').style.display = 'none';
    drawStoryPage();
});
document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('toggle-character-sheet-btn').addEventListener('click', function() {
    const characterSheet = document.getElementById('character-sheet-container');
    if (characterSheet.classList.contains('slideInFromRight')) {
        characterSheet.classList.remove('slideInFromRight');
        characterSheet.classList.add('slideOutToRight'); // Assuming you have a CSS animation for sliding out
    } else {
        characterSheet.classList.remove('slideOutToRight');
        characterSheet.classList.add('slideInFromRight'); // Slide in animation
    }
});
document.getElementById('toggle-chat-btn').addEventListener('click', function() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer.classList.contains('slideInFromLeft')) {
        // If the container is visible, slide it out
        chatContainer.classList.remove('slideInFromLeft');
        chatContainer.classList.add('slideOutToLeft');
    } else {
        // If the container is hidden, slide it in
        chatContainer.classList.remove('slideOutToLeft');
        chatContainer.classList.add('slideInFromLeft');
        chatContainer.style.zIndex = "1";
    }
});
document.getElementById('message-input').addEventListener('keypress', function(e) {
    var key = e.which || e.keyCode;
    if (key === 13) { // 13 is the key code for Enter
        e.preventDefault(); // Prevent the default action to stop the form from submitting
        document.getElementById('send-button').click(); // Trigger the click event on the send button
    }
});

async function obtainInviteCode() {
    try {
        const response = await fetch(`/story/${story_id}/invite`);
        handleApiErrors(response, inviteCode => {
            console.log('Invite Code:', inviteCode);
            // You can use the inviteCode here, for example, display it in the UI
            // document.getElementById('invite-code').textContent = inviteCode;
        });
    } catch (error) {
        showToast(`Error fetching invite code: ${error.message}`);
    }
}

async function toggleDevPane() {
    const devPane = document.getElementById('developer-options-container');
    if (devPane.classList.contains('slideInFromBottom')) {
        devPane.classList.remove('slideInFromBottom');
        devPane.classList.add('slideOutToBottom'); // Assuming you have a CSS animation for sliding out
    } else {
        devPane.classList.remove('slideOutToBottom');
        devPane.classList.add('slideInFromBottom'); // Slide in animation
    }
}

async function drawStoryPage() {
    // Call this function when you want to populate the character sheet, for example, after loading the character data
    populateCharacterSheet();
    document.getElementById('ready-btn').style.display = 'none';
    document.getElementById('main-content').style.display = 'flex';
    var imagePath = "static/img/login1.png";
    tryChangeBackgroundImage(imagePath);
    currentSoundtrack.volume = 0.3;
    currentSoundtrack.play();

    // Call the /story/{story_id}/messages endpoint to retrieve previously sent messages
    await fetch(`/story/${story_id}/messages`)
        .then(response => handleApiErrors(response, messages => {

            if (messages.length === 0) {
                // If no history is found, display the current introduction message
                appendMessage(system_portrait, `
                Welcome to the beginning of your adventure! Type a message to get started. 
                You can also press the Enter key to send a message.
                Suggestion: You can type 'I open my eyes' or 'Describe the world, its lore and my character'.
            `, 'system');
            } else {
                // Iterate through the array of messages and append them to the main-content
                messages.forEach(message => {
                    switch(message.character) {
                        case 'PC':
                            appendMessage('',`${message.character_name}: ${message.message}`, 'user');
                            break;
                        case 'NARRATOR':
                            appendMessage(narrator_portrait, `${message.character_name}: ${message.message}`, 'narrator');
                            break;
                        case 'SYSTEM':
                            appendMessage(system_portrait, `${message.character_name}: ${message.message}`, 'system');
                            break;
                        default:
                            console.log('Unknown character type');
                    }
                });

            const lastMessage = messages[messages.length - 1]
            // print lastMessage to check object for debugging
            console.log("Resuming from previous play...")
            console.log("Last incoming message was: ")
            console.log(lastMessage)
            tryPlayAudio(lastMessage.audio_path)
            tryChangeBackgroundImage(lastMessage.image_path)
            tryPlaySubtitles(lastMessage.message)
        }
    }))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    })
}

function populateCharacterSheet() {
    // Assuming selectedCharacter has portrait, description, and stats properties
    let character = selectedCharacter;
    // Update the character portrait
    document.querySelector('.character-portrait img').src = avatarPath;
    // Update the name
    document.querySelector('#name').innerHTML = character.character_name;
    // Update the character description
    document.querySelector('.character-description p').textContent = character.description;
    // Update the character stats
    document.getElementById('stat-str').textContent = character.strength;
    document.getElementById('stat-dex').textContent = character.dexterity;
    document.getElementById('stat-con').textContent = character.constitution;
    document.getElementById('stat-int').textContent = character.intelligence;
    document.getElementById('stat-wis').textContent = character.wisdom;
    document.getElementById('stat-cha').textContent = character.charisma;
}

async function sendMessage() {
    // stop audio if currently playing
    tryPlayAudio();
    // read and append message
    const message = document.getElementById('message-input').value;

    document.getElementById('send-button').style.display = 'none';
    document.getElementById('message-input-group').classList.add('waiting-state');
    document.getElementById('message-input').disabled = true;
    document.getElementById('message-input').placeholder = "The story unfolds...";
    document.getElementById('message-input').value = '';
    document.getElementById('spinner').style.display = 'flex';

    // Send data to the server
    messageApi.sendMessage(message, story_id, character_id, character_name)
}

function handleMessage(message) {
    let parsedMessage = JSON.parse(message.data);
    let action = parsedMessage.action;
    let data = parsedMessage.data;
    console.log('client received: ', parsedMessage);
    switch (action) {
        case 'message':
            appendMessage(data.portrait_path,`${data.character_name}: ${data.message}`, 'user');
            document.getElementById('send-button').style.display = 'none';
            document.getElementById('message-input-group').classList.add('waiting-state');
            document.getElementById('message-input').disabled = true;
            document.getElementById('message-input').placeholder = "The story unfolds...";
            document.getElementById('message-input').value = '';
            document.getElementById('spinner').style.display = 'flex';
            break;
        case 'reply':
            try {
                if (data.soundtrack_path) {
                    tryPlaySoundtrack(data.soundtrack_path);
                } 
                var narratorMessage = data.message;
                var formattedMessage = narratorMessage.replace(/\n/g, '<br>');
                console.log('Received successful reply: ' + formattedMessage);
                document.getElementById('send-button').style.display = 'block';
                document.getElementById('spinner').style.display = 'none';
                document.getElementById('message-input-group').classList.remove('waiting-state');
                document.getElementById('message-input').disabled = false;
                document.getElementById('message-input').placeholder = "What do you do next?";
                document.getElementById('message-input').value = '';
                document.getElementById('message-input').focus();
                tryPlayAudio(data.audio_path);
                tryChangeBackgroundImage(data.image_path);
                tryPlaySubtitles(formattedMessage);
            } catch {(error) => {
                    console.error(error);
                    document.getElementById('spinner').style.display = 'none';
                    document.getElementById('send-button').style.display = 'block';
                    alert(error)
                }
            }
            console.log('processed message: ', formattedMessage)
            appendMessage(narrator_portrait,'Narrator: ' + formattedMessage, 'narrator');
            break;
        default:
            alert('Got action ', action, ' from websocket. NYI')
            break
    }
}

// Function to append a new message to the chat box
function appendMessage(portrait, message, entity) {
    const chatBox = document.getElementById('chat-box');
    let divClass = ''
    const messageDiv = document.createElement('div');;
    switch (entity) {
        case 'user':
            divClass = 'user-message';
            if (portrait) {
                const avatarImg = document.createElement('img');
                avatarImg.src = portrait;
                avatarImg.className = 'avatar'; // Add a class for styling
                messageDiv.appendChild(avatarImg);
            }
            break;
        case 'narrator':
            divClass = 'narrator-message';
            if (portrait) {
                const avatarImg = document.createElement('img');
                avatarImg.src = portrait;
                avatarImg.className = 'avatar'; // Add a class for styling
                messageDiv.appendChild(avatarImg);
            }
            break;
        case 'system':
            divClass = 'system-message';
            if (portrait) {
                const avatarImg = document.createElement('img');
                avatarImg.src = portrait;
                avatarImg.className = 'avatar'; // Add a class for styling
                messageDiv.appendChild(avatarImg);
            }
            break;
        default:
            divClass = 'unknown-message';
    }
    
    messageDiv.className = divClass;

    const messageContent = document.createElement('span');
    messageContent.innerHTML = message;
    messageDiv.appendChild(messageContent);

    chatBox.appendChild(messageDiv);
    return messageDiv.id;
}

// Function to remove a message from the chat box
function removeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    messageElement.remove();
}

function tryPlaySubtitles(text) {
    if (window.currentSubtitleTimeout) {
        clearTimeout(window.currentSubtitleTimeout);
        window.currentSubtitleTimeout = null;
    }
    if (text) {
        const subtitleDiv = document.getElementById('subtitle');
        // Split the text into sentences
        const sentences = text.match(/[^\.!\?]+[\.!\?]+/g) || [text];
        let currentSentence = 0;

        const displayNextSentence = () => {
            if (currentSentence < sentences.length) {
                // Apply fade-out before changing the subtitle
                subtitleDiv.classList.add('fade-out');

                // Wait for the fade-out animation to complete
                setTimeout(() => {
                    subtitleDiv.classList.remove('fade-out'); // Remove fade-out class

                    // Change the subtitle text
                    subtitleDiv.textContent = sentences[currentSentence++];
                    // Calculate display duration based on text length
                    // Assuming an average reading speed and adding some padding time
                    const displayDuration = Math.max(2000, sentences[currentSentence - 1].length * 45.81632653061224);

                    subtitleDiv.classList.add('fade-in');

                    // Optionally, remove fade-in class after animation to allow it to be reapplied next time
                    setTimeout(() => {
                        subtitleDiv.classList.remove('fade-in');
                        // Hide current sentence after X seconds and show next one
                        setTimeout(displayNextSentence, displayDuration); // Adjust timing as needed
                    }, 1000); // This timeout should match the duration of the fade-in animation
                }, 1000); // This timeout should match the duration of the fade-out animation
            }
        };

        displayNextSentence();
    }
}

function tryPlayAudio(audioPath) {
    if (currentAudio && !currentAudio.paused) {
        // Fade out current audio
        let fadeOutInterval = setInterval(() => {
            if (currentAudio.volume > 0.1) {
                currentAudio.volume -= 0.1;
            } else {
                // Stop and reset the audio when the volume is low enough
                currentAudio.pause();
                currentAudio.currentTime = 0;
                currentAudio.volume = 0.5; // Reset volume for next play
                clearInterval(fadeOutInterval);
            }
        }, 100); // Adjust interval duration to control fade-out speed
    }

    if (audioPath) {
        // Wait for the current audio to fade out before starting the new one
        setTimeout(() => {
            currentAudio = new Audio(audioPath);
            currentAudio.volume = 0.5; // Start with a reasonable volume
            currentAudio.play();
        }, currentAudio && !currentAudio.paused ? 1100 : 0); // Adjust timeout to match fade-out duration
    }
}

function tryPlaySoundtrack(soundtrackPath) {
    if (soundtrackPath && currentSoundtrack.src !== new Audio(soundtrackPath).src)  {
        // If there's a new soundtrack and it's different from the current, change it
        currentSoundtrack.pause(); // Stop the current soundtrack
        currentSoundtrack = new Audio(soundtrackPath); // Load the new soundtrack
        currentSoundtrack.volume = 0.1; // Set a reasonable volume
        currentSoundtrack.loop = true; // Loop the soundtrack
        currentSoundtrack.play(); // Play the new soundtrack
    } else if (!soundtrackPath) {
        // If no soundtrackPath is provided, revert to the default ambiance audio
        // if (currentSoundtrack.src !== "static/soundtrack/ambiance.m4a") {
        //     currentSoundtrack.pause(); // Stop the current soundtrack
        //     currentSoundtrack = new Audio("static/soundtrack/ambiance.m4a"); // Revert to the default ambiance audio
        //     currentSoundtrack.volume = 0.2; // Set volume
        //     currentSoundtrack.loop = true; // Ensure it loops
        //     currentSoundtrack.play(); // Play the default ambiance audio
        // }
    } else if (currentSoundtrack.src == new Audio(soundtrackPath).src) {
        // If the provided soundtrackPath is the same as the current, do nothing
    }

}

// 3rd version of changing background image but this time with functioning transition
function tryChangeBackgroundImage(imagePath) {
    if (imagePath) {
        let newBackground = document.getElementById('story-image');
        // Set the new background image and fade it in
        newBackground.style.backgroundImage = `url('${imagePath}')`;
        newBackground.style.opacity = 1;
    }
}
