import { fetchDataAsync } from "../utils.js";
import { handleApiErrors } from '../utils.js'
import { showToast } from '../utils.js'

const username = localStorage.getItem('username')
const hostname = window.location.hostname;
const port = hostname === '127.0.0.1' ? ':8000' : '';
export const webSocketEndpoint = `ws://${hostname}${port}/ws/dashboard`;
export function createStory(storyId) {
    fetch('/story', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: storyId, // TODO: remove coupling between boxes and stories
            creator: username,
        }),
    })
    .then(response => handleApiErrors(response, data => {}))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    });
};

export function joinStory(storyId) {
    fetch('/story/' + storyId + '/join', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: storyId,
            username: username,
        }),
    })
    .then(response => handleApiErrors(response, data => {}))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    })
};

export function playStory(storyId) {
    fetch('/story/' + storyId + '/play', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: storyId,
            username: username,
        }),
    })
    .then(response => handleApiErrors(response, data => {}))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    })
};

export function deleteStory(storyId) {
    fetch('/story/' + storyId, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            story_id: storyId
        }),
    })
    .then(response => handleApiErrors(response, data => {}))
};

export async function getStoryUsers(storyId) {
    return fetchDataAsync('GET', `/story/${storyId}/users`)
}

export function leaveStory(storyId) {
    fetch('/story/' + storyId + '/leave', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            story_id: storyId,
            username: username,
        }),
    })
    .then(response => handleApiErrors(response, data => {}))
    .catch((error) => {
        showToast(`Frontend Error: ${error.message}`);
    });
};