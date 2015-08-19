import jQuery from 'jquery';

import ServerActions from '../actions/ServerActions';


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
        });
    }
}

export default new AuthService();
