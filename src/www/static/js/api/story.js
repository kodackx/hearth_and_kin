import { handleResponse, fetchDataAsync } from "../utils.js";

const username = localStorage.getItem('username')
export const webSocketEndpoint = 'ws://127.0.0.1:8000/ws/story'
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
    .then(response => handleResponse(response, data => {}))
    .catch((error) => {
        alert(error);
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
    .then(response => handleResponse(response, data => {}))
    .catch((error) => {
        alert(error);
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
    .then(response => handleResponse(response, data => {}))
    .catch((error) => {
        alert(error);
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
    .then(response => handleResponse(response, data => {}))
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
    .then(response => handleResponse(response, data => {}))
    .catch((error) => {
        alert(error);
    });
};