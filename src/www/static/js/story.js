import { handleResponse } from './utils.js'
import * as messageApi from './api/message.js'
import { connectToWebSocket, closeWebSocket } from './websocketManager.js';

let currentSoundtrack = new Audio("static/soundtrack/ambiance.m4a"); // Default ambiance audio
const story_id = localStorage.getItem('story_id');
let selectedCharacter = JSON.parse(localStorage.getItem('selectedCharacter'));
let character_id = parseInt(selectedCharacter.character_id);
let character_name = selectedCharacter.character_name;

let narrationQueue = [];
let isProcessingNarration = false;
let fadeDuration = 1000; // Duration of the audio fade effect in milliseconds


const hostname = window.location.hostname;
export const webSocketEndpoint = `ws://${hostname}:8000/ws/story/${story_id}`;
console.log('hostname is: ' + hostname)

connectToWebSocket(webSocketEndpoint, handleMessage);
window.addEventListener('beforeunload', function () {
    closeWebSocket(webSocketEndpoint);
});

// Set up elements

// event listeners and hiding play elements for now
document.getElementById('main-content').style.display = 'none';
document.getElementById('toggle-chat-btn').style.display = 'none';
document.getElementById('start-button').style.display = 'block';
document.getElementById('dev-button').style.display = 'block';
document.getElementById('character-sheet-container').style.display = 'none';
document.getElementById('toggle-character-sheet-btn').style.display = 'none';

//adding event listeners
document.getElementById('start-button').addEventListener('click', drawStoryPage);
document.getElementById('dev-button').addEventListener('click', toggleDevPane);
document.getElementById('developer-options-container').classList.add('slideInFromBottom');
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
    document.getElementById('character-sheet-container').style.display = 'block';
    document.getElementById('main-content').style.display = 'flex';
    document.getElementById('toggle-chat-btn').style.display = 'block';
    document.getElementById('toggle-character-sheet-btn').style.display = 'block';
    // hide elements (button, party list, options frame)
    this.style.display = 'none';
    document.getElementById('party-container').style.display = 'none';
    document.getElementById('developer-options-container').style.display = 'none';
    document.getElementById('dev-button').style.display = 'none';
    var imagePath = "static/img/login1.png";
    tryChangeBackgroundImage(imagePath);
    currentSoundtrack.volume = 0.1;
    currentSoundtrack.play();

    // Call the /story/{story_id}/messages endpoint to retrieve previously sent messages
    await fetch(`/story/${story_id}/messages`)
        .then(response => handleResponse(response, messages => {

            if (messages.length === 0) {
                // If no history is found, display the current introduction message
                appendMessage(`
                Welcome to the beginning of your adventure! Type a message to get started. 
                You can also press the Enter key to send a message.
                Suggestion: You can type 'I open my eyes' or 'Describe the world, its lore and my character'.
            `, 'system');
            } else {
                // Iterate through the array of messages and append them to the main-content
                messages.forEach(message => {
                    appendMessage(`${message.character_name}: ${message.message}`, 'user');
                    appendMessage('Narrator: ' + message.narrator_reply, 'narrator');
                });

            const lastMessage = messages[messages.length - 1]
            // print lastMessage to check object for debugging
            console.log(lastMessage)
            const narration = {
                text: lastMessage.narrator_reply,
                audio_path: lastMessage.audio_path || null,
                soundtrack_path: lastMessage.soundtrack_path || null,
            };
            tryChangeBackgroundImage(lastMessage.image_path)
            narrationQueue.push(narration);
            processNextNarration();
        }
    }))
    .catch((error) => {
        alert(error);
    })
}

function populateCharacterSheet() {
    // Assuming selectedCharacter has portrait, description, and stats properties
    let character = selectedCharacter;
    // Update the character portrait
    document.querySelector('.character-portrait img').src = character.portrait_path;
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
            appendMessage(`${data.character_name}: ${data.message}`, 'user');
            break;
        case 'reply':
            try {
                if (data.narrator_reply) {
                    console.log('Received successful reply: ' + data.narrator_reply);
                    const narration = {
                        text: data.narrator_reply,
                        audio_path: data.audio_path || null,
                        soundtrack_path: data.soundtrack_path || null,
                    };
                    narrationQueue.push(narration);
                    appendMessage('Narrator: ' + data.narrator_reply, 'narrator');
                    if (!isProcessingNarration) {
                        processNextNarration();
                        break;
                    }
                }
                if (data.image_path) {
                    tryChangeBackgroundImage(data.image_path);
                }
            } catch (error) {
                console.error(error);
                document.getElementById('spinner').style.display = 'none';
                document.getElementById('send-button').style.display = 'block';
                alert(error);
            }
            break;
        default:
            alert('Got action ', action, ' from websocket. NYI');
            break;
    }
}

// Function to append a new message to the chat box
function appendMessage(message, entity) {
    const chatBox = document.getElementById('chat-box');
    let divClass = '';
    switch (entity) {
        case 'user':
            divClass = 'user-message';
            break;
        case 'narrator':
            divClass = 'narrator-message';
            break;
        case 'system':
            divClass = 'system-message';
            break;
        default:
            divClass = 'unknown-message';
    }
    const messageDiv = document.createElement('div');
    messageDiv.className = divClass;
    messageDiv.innerHTML = message;
    chatBox.appendChild(messageDiv);
    return messageDiv.id;
}

// Function to remove a message from the chat box
function removeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    messageElement.remove();
}

function processNextNarration() {
    if (narrationQueue.length === 0) {
        isProcessingNarration = false;
        document.getElementById('send-button').style.display = 'block';
        document.getElementById('spinner').style.display = 'none';
        document.getElementById('message-input-group').classList.remove('waiting-state');
        document.getElementById('message-input').disabled = false;
        document.getElementById('message-input').placeholder = "What do you do next?";
        document.getElementById('message-input').value = '';
        document.getElementById('message-input').focus();
        return;
    }

    isProcessingNarration = true;
    const narration = narrationQueue.shift();

    if (narration.audio_path) {
        const audio = new Audio(narration.audio_path);
        audio.volume = 0.5; // Start with a reasonable volume

        // Ensure that the audio is loaded before playing
        audio.addEventListener('canplaythrough', () => {
            tryPlaySoundtrack(narration.soundtrack_path);
            audio.play().then(() => {
                // Display the text and manage subtitle animations
                const subtitleDiv = document.getElementById('subtitle');
                subtitleDiv.classList.add('fade-out');

                setTimeout(() => {
                    subtitleDiv.classList.remove('fade-out'); // Remove fade-out class
                    subtitleDiv.textContent = narration.text; // Change the subtitle text
                    subtitleDiv.classList.add('fade-in');

                    // Optionally, remove fade-in class after animation to allow it to be reapplied next time
                    setTimeout(() => {
                        subtitleDiv.classList.remove('fade-in');
                    }, 1000); // This timeout should match the duration of the fade-in animation
                }, 1000); // This timeout should match the duration of the fade-out animation

                audio.addEventListener('ended', () => {
                    processNextNarration();
                });
            }).catch(error => {
                console.error('Error playing audio:', error);
                processNextNarration();
            });
        });

        audio.addEventListener('error', (error) => {
            console.error('Error loading audio:', error);
            processNextNarration();
        });
    } else {
        // Display the text and manage subtitle animations
        const subtitleDiv = document.getElementById('subtitle');
        subtitleDiv.classList.add('fade-out');

        setTimeout(() => {
            subtitleDiv.classList.remove('fade-out'); // Remove fade-out class
            subtitleDiv.textContent = narration.text; // Change the subtitle text
            subtitleDiv.classList.add('fade-in');

            // Optionally, remove fade-in class after animation to allow it to be reapplied next time
            setTimeout(() => {
                subtitleDiv.classList.remove('fade-in');
            }, 1000); // This timeout should match the duration of the fade-in animation

            const displayDuration = Math.max(2000, narration.text.length * 45.81632653061224);
            window.currentSubtitleTimeout = setTimeout(() => {
                subtitleDiv.classList.add('fade-out');
                processNextNarration();
            }, displayDuration);
        }, 1000); // This timeout should match the duration of the fade-out animation
    }
}


function tryPlaySoundtrack(soundtrackPath) {
    // Extract the filename from the soundtrackPath for comparing with the current soundtrack
    const newSoundtrackFilename = soundtrackPath ? soundtrackPath.split('/').pop() : null;
    const currentSoundtrackFilename = currentSoundtrack.src ? currentSoundtrack.src.split('/').pop() : null;

    // If the provided soundtrackPath is the same as the current, do nothing
    // If there's a new soundtrack and it's different from the current, change it
    if (soundtrackPath && newSoundtrackFilename !== currentSoundtrackFilename) {
        fadeOut(currentSoundtrack, fadeDuration, () => {
            currentSoundtrack = new Audio(soundtrackPath); // Load the new soundtrack
            currentSoundtrack.loop = true; // Loop the soundtrack
            fadeIn(currentSoundtrack, fadeDuration); // Fade in the new soundtrack
        });
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

function fadeOut(audio, duration, callback) {
    let step = audio.volume / (duration / 50); // Calculate the step size for each interval
    let fadeInterval = setInterval(() => {
        if (audio.volume > step) {
            audio.volume -= step;
        } else {
            clearInterval(fadeInterval);
            audio.pause();
            if (callback) callback();
        }
    }, 50); // Adjust the volume every 50ms
}

function fadeIn(audio, duration) {
    audio.volume = 0;
    audio.play();
    let step = 0.1 / (duration / 50); // Calculate the step size for each interval
    let fadeInterval = setInterval(() => {
        if (audio.volume < 0.1) {
            audio.volume += step;
        } else {
            clearInterval(fadeInterval);
            audio.volume = 0.1; // Ensure the volume is set to the desired level
        }
    }, 50); // Adjust the volume every 50ms
}