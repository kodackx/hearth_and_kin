import { handleResponse } from './utils.js'

let currentAudio = null; // Add this at the top of your script
const story_id = localStorage.getItem('story_id');
let selectedCharacter = JSON.parse(localStorage.getItem('selectedCharacter'));
let character_id = selectedCharacter.character_id;
const username = localStorage.getItem('username');

// event listeners and hiding play elements for now
document.getElementById('main-content').style.display = 'none';
document.getElementById('toggle-chat-btn').style.display = 'none';
document.getElementById('start-button').style.display = 'block';
document.getElementById('start-button').addEventListener('click', drawStoryPage);
document.getElementById('send-button').addEventListener('click', sendMessage);
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

// define functions beggining with how to draw the full story page
async function drawStoryPage() {
    document.getElementById('main-content').style.display = 'flex';
    document.getElementById('toggle-chat-btn').style.display = 'block';
    // hide elements (button, party list, options frame)
    this.style.display = 'none';
    document.getElementById('party-container').style.display = 'none';
    document.getElementById('options-container').style.display = 'none';
    var imagePath = "static/img/login1.png";
    tryChangeBackgroundImage(imagePath);
    var ambianceAudioPath = "static/ambiance.m4a";
    let audio = new Audio(ambianceAudioPath);
    audio.volume = 0.5; // 50% volume
    audio.play();
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
                appendMessage('User: ' + message.message, 'user');
                appendMessage('Narrator: ' + message.narrator_reply, 'narrator');
            });

            const lastMessage = messages[messages.length - 1]
            // print lastMessage to check object for debugging
            console.log(lastMessage)
            tryPlayAudio(lastMessage.audio_path)
            tryChangeBackgroundImage(lastMessage.image_path)
            tryPlaySubtitles(lastMessage.narrator_reply)
        }
    }))
    .catch((error) => {
        alert(error);
    })
}

async function sendMessage() {
    // stop audio if currently playing
    tryPlayAudio();
    // read and append message
    const message = document.getElementById('message-input').value;
    appendMessage('User: ' + message, 'user');
    document.getElementById('message-input-group').classList.add('waiting-state');
    document.getElementById('message-input').disabled = true;
    document.getElementById('message-input').placeholder = "The story unfolds...";
    document.getElementById('message-input').value = '';
    document.getElementById('spinner').style.display = 'flex';

    fetch('/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message, 
            username: username,
            character_id: character_id,
            story_id: story_id
        }),
    })
    .then(response => handleResponse(response, data => {
        // Remove the loading message
        // removeMessage(loadingMessageId);
        if (data.narrator_reply) {
            // var formattedMessage = data.narrator_reply.replace(/\n/g, '<br>');
            formattedMessage = data.narrator_reply;
            console.log('Received successful reply: ' + formattedMessage);
            document.getElementById('spinner').style.display = 'none';
            document.getElementById('message-input-group').classList.remove('waiting-state');
            document.getElementById('message-input').disabled = false;
            document.getElementById('message-input').placeholder = "What do you do next?";
            document.getElementById('message-input').value = '';
            document.getElementById('message-input').focus();
            // Split the formattedMessage into lines
            var lines = formattedMessage.split('<br>');
            var lineIndex = 0;

            // Calculate the interval time
            var intervalTime = 1 / lines.length;

            // Set up the interval
            var intervalId = setInterval(function() {
                // Create a new div for the line
                var lineDiv = document.createElement('div');
                lineDiv.className = 'fade-in';
                lineDiv.innerHTML = lines[lineIndex];

                // Append the div to the message container
                document.getElementById('chat-box').appendChild(lineDiv);

                // Increment the line index
                lineIndex++;

                // If we've gone through all the lines, clear the interval
                if (lineIndex >= lines.length) {
                    clearInterval(intervalId);
                }
            }, intervalTime);
        } else {
            appendMessage('Failed to send message.', 'system');
        }

        tryPlayAudio(data.audio_path);
        tryChangeBackgroundImage(data.image_path);
        tryPlaySubtitles(data.narrator_reply);
    }))
    .catch((error) => {
        console.error(error);
        document.getElementById('spinner').style.display = 'none';
        alert(error);
    });
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
    messageDiv.textContent = message;
    chatBox.appendChild(messageDiv);
    return messageDiv.id;
}

// Function to remove a message from the chat box
function removeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    messageElement.remove();
}

function tryPlaySubtitles(text) {
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

// function tryPlayAudio(audioPath) {
//     if (audioPath) {
//         let audioNarration = new Audio(audioPath);
//         audioNarration.volume = 0.5; // 50% volume
//         audioNarration.play();
//     }
// }

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

// 3rd version of changing background image but this time with functioning transition
function tryChangeBackgroundImage(imagePath) {
    if (imagePath) {
        let newBackground = document.getElementById('story-image');

        // Set the new background image and fade it in
        newBackground.style.backgroundImage = `url('${imagePath}')`;
        newBackground.style.opacity = 1;
    }
}