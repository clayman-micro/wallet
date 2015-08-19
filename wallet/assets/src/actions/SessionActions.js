import Dispatcher from '../dispatcher';
import { ActionTypes } from '../constants/SessionConstants';
import AuthService from '../services/AuthService';

export default {
    loginUser: function (username, password) {
        Dispatcher.dispatch({
            actionType: ActionTypes.LOGIN_REQUEST,
            username: username,
            password: password
        });

        AuthService.login(username, password);
    },

    logout: function () {
        Dispatcher.dispatch({
            actionType: ActionTypes.LOGOUT
        });
    },

    unauthorized: function () {
        Dispatcher.dispatch({
            actionType: ActionTypes.UNAUTHORIZED
        });
    }
};
