import { handleApiErrors} from './utils.js'
import {showToast} from './utils.js'
import * as messageApi from './api/message.js'
import { connectToWebSocket, closeWebSocket } from './websocketManager.js';

const story_id = localStorage.getItem('story_id');

const hostname = window.location.hostname;
const port = hostname === '127.0.0.1' ? ':8000' : '';
export const webSocketEndpoint = `ws://${hostname}${port}/ws/lobby/${story_id}`;
console.log('Attempting LOBBY websocket connection at: ' + webSocketEndpoint)

let socket = connectToWebSocket(webSocketEndpoint, handleMessage);
console.log(socket)
if (socket) {
    console.log('WebSocket connection established.');
} else {
    console.error('Failed to establish WebSocket connection.');
}
socket.addEventListener('open', () => {
    console.log('WebSocket connection established.');
    notifyPresence(); // Notify others of your presence once the connection is open
});

socket.addEventListener('error', (error) => {
    console.error('WebSocket error:', error);
});

if (socket.readyState === WebSocket.OPEN) {
    notifyPresence(); // Notify others of your presence if the connection is already open
}

window.addEventListener('beforeunload', function () {
    closeWebSocket(webSocketEndpoint);
});

window.addEventListener('beforeunload', function () {
    closeWebSocket(webSocketEndpoint);
});

//write invite code and currently registered characters
document.addEventListener('DOMContentLoaded', () => {
    obtainInviteCode();
    fetchStoryCharacters(story_id); // Add this line to call the function on DOM load
});

document.getElementById('start-button').addEventListener('click', startGame);
document.getElementById('dev-button').addEventListener('click', toggleDevPane);
document.getElementById('developer-options-container').classList.add('slideInFromBottom');

async function obtainInviteCode() {
    try {
        const response = await fetch(`/story/${story_id}/invite`);
        handleApiErrors(response, inviteCode => {
            console.log('Invite Code:', inviteCode);
            // You can use the inviteCode here, for example, display it in the UI
            document.getElementById('invite-code').textContent = inviteCode;
        });
    } catch (error) {
        showToast(`Error fetching invite code: ${error.message}`);
    }
}

//TODO: API to pre-populate the party list from DB - even if some are offline by default
async function fetchStoryCharacters(story_id) {
    console.log('fetchStoryCharacters called with story_id:', story_id);
    try {
        const response = await fetch(`/story/${story_id}/characters`);
        handleApiErrors(response, characters => {
            console.log('Characters:', characters);
            const partyList = document.getElementById('party-list');
            partyList.innerHTML = ''; // Clear existing list

            characters.forEach(character => {
                const listItem = document.createElement('li');
                listItem.className = 'party-member';

                const statusIndicator = document.createElement('span');
                statusIndicator.className = 'status-indicator offline'; // Default to offline
                listItem.appendChild(statusIndicator);

                const avatar = document.createElement('img');
                avatar.className = 'avatar';
                avatar.src = character.portrait_path; // Assuming the backend provides this field
                listItem.appendChild(avatar);

                const playerName = document.createElement('span');
                playerName.className = 'player-name';
                playerName.textContent = character.character_name;
                listItem.appendChild(playerName);

                partyList.appendChild(listItem);
            });
        });
    } catch (error) {
        showToast(`Error fetching story characters: ${error.message}`);
    }
}

function notifyPresence() {
    const character = localStorage.getItem('selectedCharacter');
    if (!character) {
        showToast('No character selected.');
        return;
    }

    const characterName = JSON.parse(character).character_name;
    const message = {
        action: 'player_online',
        data: { character_name: characterName }
    };
    socket.send(JSON.stringify(message));
}

function startGame() {
    const message = {
        action: 'start_game',
        data: {}
    };
    socket.send(JSON.stringify(message));
}

function handleMessage(event) {
    const parsedMessage = JSON.parse(event.data);
    const action = parsedMessage.action;
    const data = parsedMessage.data;
    console.log('Client received: ', parsedMessage);
    switch (action) {
        case 'player_online':
            console.log("Player Online Event received");
                markPlayerOnline(data);
            break;
        case 'new_player':
            addPlayerToLobby(data);
            break;
        case 'start_game':
            redirectToStoryPage();
            break;
        default:
            console.warn('Unknown action received: ', action);
            break;
    }
}

async function toggleDevPane() {
    const devPane = document.getElementById('developer-options-container');
    if (devPane.classList.contains('slideInFromBottom')) {
        devPane.classList.remove('slideInFromBottom');
        devPane.classList.add('slideOutToBottom'); // Assuming you have a CSS animation for sliding out
    } else {
        devPane.classList.remove('slideOutToBottom');
        devPane.classList.add('slideInFromBottom'); // Slide in animation
    }
}

function markPlayerOnline(playerData) {
    console.log("markPlayerOnline called with:", playerData);
    const playerElements = document.querySelectorAll('.party-member');
    playerElements.forEach(playerElement => {
        const playerNameElement = playerElement.querySelector('.player-name');
        console.log("Checking that character name received (" + playerData.character_name + ") matches any in our list.");
        if (playerNameElement.textContent === playerData.character_name) {
            const statusIndicator = playerElement.querySelector('.status-indicator');
            statusIndicator.classList.remove('offline');
            statusIndicator.classList.add('online');
        }
    });
}

function addPlayerToLobby(playerData) {
    const roleMap = {
        'party_lead': 'party-lead',
        'member_1': 'member-1',
        'member_2': 'member-2'
    };

    const playerId = roleMap[playerData.role];
    if (!playerId) {
        console.warn('Unknown player role:', playerData.role);
        return;
    }

    const playerElement = document.getElementById(playerId);
    const statusIndicator = playerElement.previousElementSibling;

    // Update player name and status
    playerElement.textContent = playerData.character_name;
    statusIndicator.className = `status-indicator online`;

    // Update avatar if needed
    const avatar = document.createElement('img');
    avatar.src = playerData.avatar_url;
    avatar.alt = `${playerData.character_name}'s avatar`;
    avatar.classList.add('avatar');

    // Remove existing avatar if any
    const existingAvatar = playerElement.querySelector('img.avatar');
    if (existingAvatar) {
        existingAvatar.remove();
    }

    // Insert new avatar
    playerElement.insertBefore(avatar, playerElement.firstChild);
}

function redirectToStoryPage() {
    window.location.href = '/story';
}
