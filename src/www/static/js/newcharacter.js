import { handleApiErrors} from './utils.js'
import {showToast} from './utils.js'
// Start flow
document.getElementById('main-content').style.display = 'none';
document.getElementById('send-button').style.display = 'none';
document.getElementById('start-button').style.display = 'block';
document.getElementById('message-input').value = 'I listen to the mists of creation... Help me shape my character into reality.';
const firstTimeButton = document.querySelector('.first-time-button');
firstTimeButton.addEventListener('click', handleFirstClick);
document.getElementById('send-button').addEventListener('click', sendMessage);

document.getElementById('start-button').addEventListener('click', function() {
    document.getElementById('main-content').style.display = 'flex';
    this.style.display = 'none';
    // displayIntroText()
    var imageUrl = "";
    // changeBackgroundImage(imageUrl);
    var ambiance = "static/soundtrack/wilderness.m4a";
    let audio = new Audio(ambiance);
    audio.volume = 0.5; // 50% volume
    audio.play();
});

document.getElementById('message-input').addEventListener('keypress', function(e) {
    var key = e.which || e.keyCode;
    if (key === 13) { // 13 is the key code for Enter
        e.preventDefault(); // Prevent the default action to stop the form from submitting
        document.getElementById('send-button').click(); // Trigger the click event on the send button
    }
});

document.addEventListener('click', function(event) {
    if (event.target.classList.contains('finalize-button')) {
        // Retrieve the character data from localStorage
        var characterData = JSON.parse(localStorage.getItem('characterData'));
        characterData.username = localStorage.getItem('username');
        // characterData = { character_stats: characterData };
        console.log('Sending character data to API:', characterData);
        fetch('/createcharacter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(characterData),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('POST request sent successfully:', data);
            let overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            overlay.style.color = 'white';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.fontSize = '24px';
            overlay.style.zIndex = '1000';
            overlay.innerHTML = 'Character created. Click here to go to your dashboard and start a story.';
            overlay.addEventListener('click', function() {
                window.location.href = '/dashboard';
            });
            document.body.appendChild(overlay);
        })
        .catch(error => {
            console.error('Failed to send POST request:', error);
        });
    }
});

// define first click to initiate dialogue with the mists of creation
function handleFirstClick() {
    // Remove the one-time use class to revert to normal styling
    document.getElementById('first-time-text').style.display = 'none';
    firstTimeButton.classList.remove('first-time-button');
    document.getElementById('send-button').style.display = 'block';

    // You may want to add additional logic here to handle the first-time interaction
    sendMessage();

    // Remove the event listener since it's no longer needed
    firstTimeButton.removeEventListener('click', handleFirstClick);
}

// Function to send a new message
function sendMessage() {
    const message = document.getElementById('message-input').value;
    appendMessageUser(message);
    document.getElementById('message-input').value = '';
    // Show the spinner
    document.getElementById('spinner').style.display = 'block';
    document.getElementById('send-button').style.display = 'none';
    document.getElementById('input-group').classList.add('waiting-state');
    document.getElementById('message-input').disabled = true; // Disable input
    document.getElementById('message-input').placeholder = "The mists of creation are working...";
    scrollToBottom();
    fetch('/charactermessage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
        }),
    })
    .then(response => response.json())
    .then(data => {
        // check for finalized characters stats
        if (data.character_data) {
            let characterData = data.character_data;
            const userId = localStorage.getItem('user_id'); // Retrieve user_id from localStorage
            characterData.user_id = userId; // Add user_id to character_data
            localStorage.setItem('characterData', JSON.stringify(characterData));
            console.log('Character saved:', characterData);
        }
        // check for audio
        if (data.audio) {
            base64ToBlob(data.audio, 'audio/wav')
            .then(audioBlob => {
                let audioUrl = URL.createObjectURL(audioBlob);
                let narration = new Audio(audioUrl);
                narration.volume = 0.75; // 75% volume
                narration.play();
            })
            .catch(error => console.error('Error:', error));
        }
        // check if we have a narrator reply
        if (data.message.includes('Narrator:')) {
            var formattedMessage = data.message.replace(/\n/g, '<br>');
            formattedMessage = formattedMessage.replace('Narrator: ', '');
            console.log('Received successful reply :' + formattedMessage)
            document.getElementById('spinner').style.display = 'none';
            document.getElementById('send-button').style.display = 'block';
            document.getElementById('input-group').classList.remove('waiting-state');
            document.getElementById('message-input').disabled = false; // Enable input
            document.getElementById('message-input').placeholder = "Shape your character into reality.";
            // add append message here from creator
            creatorReply(formattedMessage).then(() => { // Wait for creatorReply to finish
                if (data.image) {
                    let imagePath = data.image;
                    appendMessagePortrait(imagePath);
                    scrollToBottom();
                }
            });
        } else {
            appendMessage('[ERROR] Failed to send message.');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('spinner').style.display = 'none';
        document.getElementById('send-button').style.display = 'block';
        document.getElementById('input-group').classList.remove('waiting-state');
        document.getElementById('message-input').disabled = false; // Enable input
        document.getElementById('message-input').placeholder = "Shape your character into reality.";
    });
};

//function to wait
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function displayIntroText() {
    const messages = [
        "From the mists of primordial space, where the planets dance in a celestial waltz, your character emerges. Begin to weave the tapestry of their existence.<br>",
        "Envision them in the vastness of this universe. Who are they? What race do they belong to – are they a stoic Dwarf, a mystical Elf, a resourceful Human, or perhaps something more arcane? Let the stars whisper their race to your mind.",
        "Now, think of their class. Are they a brave Warrior, a cunning Rogue, or a wise Wizard? Each class carries its own destiny. What path does your character tread upon?",
        "Delve deeper into their essence. What is their name – a name that echoes in the halls of time? What are their most striking features? Do they bear scars of ancient battles, or eyes that glimmer with untold knowledge?",
        "Imagine their attire and armor. Is it a suit of unbreakable mail, robes woven with the threads of magic, or leathers as silent as the night?",
        "Consider their personality. Are they driven by honor, thirst for adventure, a quest for knowledge, or the shadows of their past?",
        "Finally, picture them holding an item of great significance. Is it a weapon engraved with runes, a mystical amulet, or an ancient tome? This item will be a companion in their journey.",
        "Let your words flow freely and paint the portrait of your character. Their story begins with your imagination. Here, in the realm of Hearth and Kin, every detail you conjure breathes life into their existence."
    ]; // Your messages

    for (const message of messages) {
        appendMessage(message);
        await wait(1000); // Wait for 1 second between intro messages
    }
}

//general reply function that splits the text into chunks but still uses appendMessage function
function creatorReply(message) {
    return new Promise((resolve, reject) => {
        var lines = message.split('<br>');
        var lineIndex = 0;
        var intervalTime = 5000 / lines.length;
        var intervalId = setInterval(function() {
            var lineDiv = document.createElement('div');
            lineDiv.className = 'fade-in';
            appendMessage(lines[lineIndex]);
            // Delay scrolling to the bottom to ensure the DOM has updated
            setTimeout(() => {
                scrollToBottom();
            }, 0); // Adjust the delay as needed, even a 0ms timeout can help
            lineIndex++;
            if (lineIndex >= lines.length) {
                clearInterval(intervalId);
                resolve(); // Resolve the Promise when all messages have been appended
            }
        }, intervalTime);
    });
}

// Call scrollToBottom() function right after a new 'creation-message' is appended to the chat-box
function scrollToBottom() {
    const chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}


// Function to append a new message to the chat box
function appendMessage(message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('p');
    messageElement.innerHTML = message;  // Use innerHTML instead of textContent
    messageElement.classList.add('creation-message');  
    chatBox.appendChild(messageElement);
    return messageElement.id;
}

// Function to append a new message to the chat box
function appendMessageUser(message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('p');
    messageElement.innerHTML = message;  // Use innerHTML instead of textContent
    messageElement.classList.add('user-message');  
    chatBox.appendChild(messageElement);
    return messageElement.id;
}

// Function to append a new portrait to the chat box
function appendMessagePortrait(message) {
    // Create an image element and apply the 'rounded-image' class
    const chatBox = document.getElementById('chat-box');
    const imgElement = document.createElement('img');
    imgElement.src = message;
    imgElement.classList.add('rounded-avatar');
    chatBox.appendChild(imgElement);
    appendFinalizeButton(); // Append the button after the portrait
    return imgElement.id;
}

// Function to append a new button to the chat box
function appendFinalizeButton() {
    const chatBox = document.getElementById('chat-box');
    const buttonElement = document.createElement('button');
    buttonElement.innerHTML = "Finalize character";
    buttonElement.classList.add('finalize-button');  
    chatBox.appendChild(buttonElement);
    return buttonElement.id;
}

// Function to remove a message from the chat box
function removeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    messageElement.remove();
}

// 3rd version of changing background image but this time with functioning transition
function changeBackgroundImage(imagePath) {
    let oldBackground = document.getElementById('story-image');
    let newBackground = document.getElementById('story-image');

    // Set the new background image and fade it in
    newBackground.style.backgroundImage = `url(${imagePath})`;
    newBackground.style.opacity = 1;
}

// Function to convert a base64 string to a Blob object
function base64ToBlob(base64, mime = '') {
    return fetch(`data:${mime};base64,${base64}`).then(res => res.blob());
}