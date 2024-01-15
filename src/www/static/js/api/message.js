import { handleResponse, fetchDataAsync } from "../utils.js";

const storyId = localStorage.getItem('joinedStoryId');
const characterId = 1; //localStorage.getItem('character_id');
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