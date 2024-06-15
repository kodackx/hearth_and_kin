import {handleApiErrors} from '../utils.js'
import {showToast} from '../utils.js'

export function sendMessage(message, story_id, character_id, character_name) {
    // Retrieve selectedCharacter from localStorage
    const selectedCharacter = JSON.parse(localStorage.getItem('selectedCharacter'));
    const portraitPath = selectedCharacter ? selectedCharacter.portrait_path : '';
    fetch('/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            story_id: story_id,
            character: "PC",
            character_id: parseInt(character_id),
            character_name: character_name,
            portrait_path: portraitPath
        }),
    })
    .then(response => handleApiErrors(response, data => {
        // processMessage(data)
    }))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    });
};

function processMessage(data) {
    console.log('Processing message...')
    try {
        if (data.soundtrack_path) {
            tryPlaySoundtrack(data.soundtrack_path);
        } else {
            tryPlaySoundtrack();
        }
        // var formattedMessage = narratorMessage.replace(/\n/g, '<br>');
        let formattedMessage = data.narrator_reply;
        console.log('Received successful reply: ' + formattedMessage);
        document.getElementById('send-button').style.display = 'block';
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
        var intervalId = setInterval(function () {
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

        tryPlayAudio(data.audio_path);
        tryChangeBackgroundImage(data.image_path);
        tryPlaySubtitles(data.narrator_reply);
    } catch {(error) => {
            console.error(error);
            document.getElementById('spinner').style.display = 'none';
            document.getElementById('send-button').style.display = 'block';
            alert(error)
        }
    }
}