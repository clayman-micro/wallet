/* eslint no-else-return: 0 */
/* global fetch */

import ServerActions from '../actions/ServerActions';
import SessionActions from '../actions/SessionActions';


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
        let params = {
            method: 'post',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                login: username,
                password: password
            })
        };

        return fetch('/auth/login', params)
            .then(checkStatus)
            .then(function (response) {
                response.json().then(function (data) {
                    ServerActions.receiveLogin({
                        user: data.user,
                        token: response.headers.get('X-ACCESS-TOKEN')
                    }, null);
                });
            })
            .catch(function (error) {
                let errors = {};
                if (error.response.status === 400) {
                    error.response.json().then(function (data) {
                        errors = data;
                    });
                } else {
                    errors[error.response.status] = error.response.statusText;
                }

                ServerActions.receiveLogin(null, errors);
            });
    }

    logout() {
        SessionActions.logout();
    }
}

export default new AuthService();
