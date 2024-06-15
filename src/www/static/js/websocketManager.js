const websocketMap = new Map();

export function connectToWebSocket(endpoint, messageHandler) {
    const socket = new WebSocket(endpoint);
    socket.onmessage = messageHandler;
    websocketMap.set(endpoint, socket);
    //socket.onclose = closeWebSocket(endpoint)
    return socket
}

export function sendMessage(endpoint, action, data) {
    const socket = websocketMap.get(endpoint);
    if (socket) {
        socket.send(JSON.stringify({
            action: action,
            data: data
        }))
    } else {
        console.error(`WebSocket connection for endpoint ${endpoint} not found.`);
    }
}

export function closeWebSocket(endpoint) {
    const socket = websocketMap.get(endpoint);
    if (socket) {
        socket.close();
        websocketMap.delete(endpoint);
    } else {
        console.error(`WebSocket connection for endpoint ${endpoint} not found.`);
    }
}