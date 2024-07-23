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


export function getTokenHeaders() {
    console.log('Checking if user is logged in...');
    const token = localStorage.getItem('access_token');
    if (token === null) {
        showToast('Please login to continue.');
        localStorage.clear();
        //window.location.href = '/';
    }
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    }
}

export async function callApi(method, endpoint, body, successCallback) {
    var query = {
        method: method,
        headers: headers,
    }
    if (body) {
        query.body = JSON.stringify(body);
    }
    return fetch(endpoint, query).then(response => handleApiErrors(response, successCallback))
}

export async function fetchDataAsync(method, endpoint, body) {
    var query = {
        method: method,
        headers: headers
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
                const errorMessages = data.detail.map(error => {
                    const errorField = error.loc.join(" > ");
                    const errorMessage = error.msg;
                    return `${errorField}: ${errorMessage}`;
                });
                showToast(`FastAPI Error - ${errorMessages.join('\n')}`);
            } else {
                // Handle general API errors
                showToast(`Error: ${data.detail}`);
                if (data.detail == 'Could not validate credentials') {
                    // Token was invalid, clear local storage and redirect to login page
                    localStorage.clear();
                    window.location.href = '/';
                    alert(`Could not authorize user, please log in again`);
                }
            }
        }).catch(error => {
            // Handle frontend errors
            showToast(`Frontend Error: ${error.message}`);
            //throw error;
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

    console.log("Showing toast message: " + message);
}