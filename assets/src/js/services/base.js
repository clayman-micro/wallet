/* eslint no-underscore-dangle: 0 */

export default class BaseService {
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
}
