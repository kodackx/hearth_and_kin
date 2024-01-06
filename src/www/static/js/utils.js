export function handleResponse(response, successCallback) {
    // Checks the response from the API and either raises an error containing the 
    // text from the HTTTPException from FastAPI, or returns the model as a JSON object
    if (!response.ok) {
        return response.json().then(data => {
            throw new Error(data.detail);
        });
    }
    return response.json().then(successCallback);
}