export function handleResponse(response, successCallback) {
    // Checks the response from the API and either raises an error containing the 
    // text from the HTTPException from FastAPI, or returns the model as a JSON object
    if (!response.ok) {
        console.log(response)
        return response.json().then(data => {
            if (data.detail) {
                throw new Error(data.detail)
            } else {
                throw new Error(data)
            }
        });
    }
    return response.json().then(successCallback);
}