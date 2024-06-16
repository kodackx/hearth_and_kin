// export async function handleResponse(response, successCallback) {
//     const data = await response.json();
//     if (!response.ok) {
//         var errorDetail = ''
//         if (Array.isArray(data.detail)) {
//             data.detail.forEach(error => {
//                 const errorField = error.loc.join(" > ");
//                 const errorMessage = error.msg;
//                 errorMsg += `${errorField}: ${errorMessage}`;
//             });
//         } else {
//             errorDetail = data.detail 
//         }
//         console.log(errorDetail)
//         throw new Error(errorDetail);
//     }
//     if (successCallback && typeof successCallback === 'function') {
//         return successCallback(data);
//     }
//     return data;
// }

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

export function handleApiErrors(response, successCallback) {
    if (!response.ok) {
        console.error(response);
        return response.json().then(data => {
            if (Array.isArray(data.detail)) {
                // Handle FastAPI validation errors
                data.detail.forEach(error => {
                    const errorField = error.loc.join(" > ");
                    const errorMessage = error.msg;
                    showToast(`FastAPI Error - ${errorField}: ${errorMessage}`);
                });
            } else {
                // Handle general FastAPI error
                showToast(`FastAPI Error: ${data.detail}`);
                throw new Error(data.detail);
            }
        }).catch(error => {
            // Handle frontend errors
            showToast(`Frontend Error: ${error.message}`);
            throw error;
        });
    }

    return response.json().then(successCallback);
}

export function showToast(message) {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toastContainer.appendChild(toast);

    // Show the toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Remove the toast after 5 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toastContainer.removeChild(toast);
        }, 500);
    }, 5000);

    console.log("Showing toast message for error: " + message);
}