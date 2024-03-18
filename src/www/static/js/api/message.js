import { handleResponse } from "../utils.js";

const storyId = localStorage.getItem('story_id');
const characterId = localStorage.getItem('character_id');
const username = localStorage.getItem('username')

export function sendMessage(message) {
    fetch('/message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: storyId,
            username: username,
            character_id: characterId,
            message: message,
        }),
    })
    .then(response => handleResponse(response, data => {}))
    .catch((error) => {
        alert(error);
    });
};