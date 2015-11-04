/* eslint no-underscore-dangle: 0, no-else-return: 0 */
/* global DEBUG, HOST */

import 'isomorphic-fetch';


export default class BaseService {
    constructor(token) {
        this._token = token;
    }

    request(path, params) {
        const url = [];
        if (DEBUG) {
            url.push(HOST);
        }
        url.push(path);

        return fetch(url.join(''), params)
            .then(response => {
                // check status
                let contentType = response.headers.get('Content-Type');
                if (response.status >= 200 && response.status < 300) {
                    return Promise.resolve(response).then(response => {
                        if (contentType && contentType === 'application/json') {
                            return response.json().then(json => Promise.resolve({
                                status: response.status,
                                statusText: response.statusText,
                                headers: response.headers,
                                data: json
                            }));
                        } else {
                            return response.text().then(text => Promise.resolve({
                                status: response.status,
                                statusText: response.statusText,
                                headers: response.headers,
                                data: text
                            }));
                        }
                    });
                } else {
                    let error = new Error(response.statusText);
                    error.response = response;
                    return Promise.reject(error);
                }
            }).catch(error => {
                // handle error
                console.log(errors);
                let response = error.response;
                if (typeof response !== 'undefined') {
                    let contentType = response.headers.get('Content-Type');
                    if (contentType && contentType === 'application/json') {
                        return response.json().then(json => Promise.reject({
                            status: response.status,
                            statusText: response.statusText,
                            headers: response.headers,
                            data: typeof json.errors !== 'undefined' ? json.errors : json
                        }));
                    } else {
                        return response.text().then(text => Promise.reject({
                            status: response.status,
                            statusText: response.statusText,
                            headers: response.headers,
                            data: text
                        }));
                    }
                } else {
                    throw error;
                }
            });
    }

    getCollection(url) {
        let params = {
            method: 'GET',
            headers: { 'X-ACCESS-TOKEN': this._token, accept: 'application/json' },
            credentials: 'include'
        };

        return this.request(url, params);
    }

    createResource(url, payload) {
        let params = {
            method: 'POST',
            headers: { 'X-ACCESS-TOKEN': this._token, 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        };

        return this.request(url, params);
    }

    getResource(url) {
        let params = {
            method: 'GET',
            headers: { 'X-ACCESS-TOKEN': this._token, 'Content-Type': 'application/json' },
            credentials: 'include'
        };

        return this.request(url, params);
    }

    editResource(url, payload) {
        let params = {
            method: 'PUT',
            headers: { 'X-ACCESS-TOKEN': this._token, 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(payload)
        };

        return this.request(url, params);
    }

    removeResource(url) {
        let params = {
            method: 'DELETE',
            headers: { 'X-ACCESS-TOKEN': this._token },
            credentials: 'include'
        };

        return this.request(url, params);
    }
}
