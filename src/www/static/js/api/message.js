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