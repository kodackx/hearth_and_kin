import { handleResponse } from './utils.js'
import * as messageApi from './api/message.js'
import { connectToWebSocket, closeWebSocket } from './websocketManager.js';

// Retrieve stored variables
const storyId = localStorage.getItem('joinedStoryId');
const username = localStorage.getItem('username');
export const webSocketEndpoint = 'ws://127.0.0.1:8000/ws/story/' + storyId 
// Set up elements
document.getElementById('main-content').style.display = 'none';
document.getElementById('start-button').style.display = 'block';
document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('start-button').addEventListener('click', drawStoryPage)

document.getElementById('message-input').addEventListener('keypress', function(e) {
    var key = e.which || e.keyCode;
    if (key === 13) { // 13 is the key code for Enter
        e.preventDefault(); // Prevent the default action to stop the form from submitting
        document.getElementById('send-button').click(); // Trigger the click event on the send button
    }
});


connectToWebSocket(webSocketEndpoint, handleMessage);
window.addEventListener('beforeunload', function() {
    closeWebSocket(webSocketEndpoint);
});

function handleMessage(message) {
    let parsedMessage = JSON.parse(message.data);
    let action = parsedMessage.action;
    let data = parsedMessage.data;
    let userAction = data.username == username
    console.log('client received: ', parsedMessage);
    switch (action) {
        case 'message':
            appendMessage(`${data.username}: ${data.message}`);
            break;
        case 'reply':
            processMessage('Narrator: ' + data.narrator_reply)
            tryPlayAudio(data.audio_path)
            tryChangeBackgroundImage(data.image_path)
            break;
        default:
            alert('Got action ', action, ' from websocket. NYI')
            break
    }
}

async function drawStoryPage() {
    document.getElementById('main-content').style.display = 'flex';
    this.style.display = 'none';
    var imagePath = "static/img/login1.png";
    tryChangeBackgroundImage(imagePath);
    var ambianceAudioPath = "static/ambiance.m4a";
    let audio = new Audio(ambianceAudioPath);
    audio.volume = 0.5; // 50% volume
    audio.play();
    // Call the /story/{story_id}/messages endpoint to retrieve previously sent messages
    await fetch(`/story/${storyId}/messages`)
    .then(response => handleResponse(response, messages => {

        if (messages.length === 0) {
            // If no history is found, display the current introduction message
            appendMessage(`
                Welcome to the beginning of your adventure! Type a message to get started. 
                You can also press the Enter key to send a message.
                Suggestion: You can type 'I open my eyes' or 'Describe the world, its lore and my character'.
            `);
        } else {
            // Iterate through the array of messages and append them to the main-content
            messages.forEach(message => {
                appendMessage(`${message.username}: ${message.message}`);
                appendMessage('Narrator: ' + message.narrator_reply);
            });

            const lastMessage = messages[messages.length - 1]
            tryPlayAudio(lastMessage.audio_path)
            tryChangeBackgroundImage(lastMessage.image_path)
        }
    }))
    .catch((error) => {
        alert(error);
    })
}

function tryPlayAudio(audioPath) {
    if (audioPath) {
        base64ToBlob(audioPath, 'audio/wav')
        .then(audioBlob => {
            let audioUrl = URL.createObjectURL(audioBlob);
            let narration = new Audio(audioUrl);
            narration.volume = 0.75; // 75% volume
            narration.play();
        })
        .catch(error => {console.error('Error:', error)})
    }
}


function sendMessage() {
    const message = document.getElementById('message-input').value;
    document.getElementById('message-input').value = '';
    // Show the spinner
    document.getElementById('spinner').style.display = 'block';
    // changeBackgroundImage(imagePath);

    // const loadingMessageId = appendMessage('Narrator is thinking...');

    // Send data to the server
    messageApi.sendMessage(message)
}

function processMessage(narratorMessage) {
    try {
    // Remove the loading message
    // removeMessage(loadingMessageId);
        var formattedMessage = narratorMessage.replace(/\n/g, '<br>');
        console.log('Received successful reply: ' + formattedMessage)
        document.getElementById('spinner').style.display = 'none';
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
    } catch (error) {
        console.error(error);
        document.getElementById('spinner').style.display = 'none';
        alert(error);
    }
}

// Function to append a new message to the chat box
function appendMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    return messageElement.id;
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

// Function to convert a base64 string to a Blob object
function base64ToBlob(base64, mime = '') {
    return fetch(`data:${mime};base64,${base64}`).then(res => res.blob());
}