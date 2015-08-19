import jQuery from 'jquery';

import ServerActions from '../actions/ServerActions';
import SessionActions from '../actions/SessionActions';


class AuthService {
    login(username, password) {
        return jQuery.ajax({
            cache: false,
            url: '/auth/login',
            method: 'POST',
            dataType: 'json',
            data: {
                login: username,
                password: password
            }
        }).done(function (data, status, response) {
            let token = response.getResponseHeader('X-ACCESS-TOKEN');
            ServerActions.receiveLogin({
                user: data.user,
                token: token
            }, null);
        }).fail(function (response) {
            console.log(response);

            let errors = {};
            if (typeof response.responseJSON !== 'undefined') {
                errors = response.responseJSON.errors;
            } else {
                errors.common = response.statusText;
            }

            ServerActions.receiveLogin(null, errors);
        });
    }

    logout() {
        SessionActions.logout();
    }
}

export default new AuthService();
