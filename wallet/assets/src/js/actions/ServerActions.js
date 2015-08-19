import Dispatcher from '../dispatcher';
import { ActionTypes } from '../constants/SessionConstants';

export default {
    receiveLogin: function (response, errors) {
        let user = null;
        let token = null;

        if (response) {
            user = response.user;
            token = response.token;
        }

        Dispatcher.dispatch({
            actionType: ActionTypes.LOGIN_RESPONSE,
            user: user,
            token: token,
            errors: errors
        });
    }
};
