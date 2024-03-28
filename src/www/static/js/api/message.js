import { handleResponse } from "../utils.js";

export function sendMessage(message, story_id, character_id, character_name) {
    fetch('/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: story_id,
            character_id: parseInt(character_id),
            message: message,
            character_name: character_name,
        }),
    })
    .then(response => handleResponse(response, data => {}))
    .catch((error) => {
        alert(error);
    });
};