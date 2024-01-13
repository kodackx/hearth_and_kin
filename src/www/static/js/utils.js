export async function handleResponse(response, successCallback) {
    const data = await response.json();
    if (!response.ok) {
        var errorDetail = ''
        if (Array.isArray(data.detail)) {
            data.detail.forEach(error => {
                const errorField = error.loc.join(" > ");
                const errorMessage = error.msg;
                errorMsg += `${errorField}: ${errorMessage}`;
            });
        } else {
            errorDetail = data.detail 
        }
        console.log(errorDetail)
        throw new Error(errorDetail);
    }
    if (successCallback && typeof successCallback === 'function') {
        return successCallback(data);
    }
    return data;
}

export function fetchData(method, endpoint, body) {
    var query = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    }
    if (body) {
        query.body = JSON.stringify(body);
    }
    return fetch(endpoint, query)
        .then(response => handleResponse(response))
        .catch(error => {
            console.error(`Error fetching data from ${endpoint}:`, error);
            throw error; // Re-throw the error to be handled by the caller
        });
}

export async function fetchDataAsync(method, endpoint, body) {
    var query = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
    }
    if (body) {
        query.body = JSON.stringify(body);
    }
    try {
        const response = await fetch(endpoint, query);
        return await handleResponse(response);
    } catch (error) {
        console.error(`Error fetching data from ${endpoint}:`, error);
        throw error; // Re-throw the error to be handled by the caller
    }
}