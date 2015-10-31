/* eslint no-else-return: 0 */
/* global fetch, DEBUG, HOST */

import { APIEndpoints } from '../constants/session';


function checkStatus(response) {
    if (response.status >= 200 && response.status < 300) {
        return Promise.resolve(response);
    } else {
        let error = new Error(response.statusText);
        error.response = response;
        return Promise.reject(error);
    }
}


class AuthService {
    login(username, password) {
        let body = JSON.stringify({
            login: username,
            password: password
        });
        let headers = new Headers({ 'Content-Type': 'application/json' });

        let params = {
            method: 'POST',
            headers: headers,
            body: body,
            credentials: 'include'
        };

        const url = [];
        if (DEBUG) {
            url.push(HOST);
        }
        url.push(APIEndpoints.LOGIN);

        return fetch(url.join(''), params)
            .then(checkStatus);
    }
}

export default new AuthService();
