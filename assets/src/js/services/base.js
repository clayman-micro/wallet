/* eslint no-underscore-dangle: 0 */

export default class BaseService {
    constructor(collectionEndpoint, resourceEndpoint) {
        this._collectionEndpoint = collectionEndpoint;
        this._resourceEndpoint = resourceEndpoint;
    }

    checkStatus(response) {
        if (response.status >= 200 && response.status < 300) {
            return Promise.resolve(response);
        } else {
            let error = new Error(response.statusText);
            error.response = response;
            return Promise.reject(error);
        }
    }

    request(endpoint, params) {
        return fetch(endpoint, params).then(this.checkStatus);
    }

    getCollection(token) {
        let headers = new Headers({ 'X-ACCESS-TOKEN': token, accept: 'application/json' });
        let params = {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        };

        return this.request(this._collectionEndpoint, params).then(request => request.json());
    }

    createResource(token, payload) {
        let headers = new Headers({ 'X-ACCESS-TOKEN': token, 'Content-Type': 'application/json' });
        let params = {
            method: 'POST',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify(payload)
        };

        return this.request(this._collectionEndpoint, params).then(request => request.json());
    }

    getResource(token, resourceId) {

    }

    editResource(token, resourseId, payload) {
        let headers = new Headers({ 'X-ACCESS-TOKEN': token, 'Content-Type': 'application/json' });
        let params = {
            method: 'PUT',
            headers: headers,
            credentials: 'include',
            body: JSON.stringify(payload)
        };

        return this.request(this._resourceEndpoint.replace('{id}', resourseId), params).then(request => request.json());
    }

    removeResource(token, resourceId) {
        let headers = new Headers({ 'X-ACCESS-TOKEN': token });
        let params = {
            method: 'DELETE',
            headers: headers,
            credentials: 'include'
        };

        return this.request(this._resourceEndpoint.replace('{id}', resourceId), params);
    }
}
