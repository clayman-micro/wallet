import Dispatcher from '../dispatcher';
import { ActionTypes } from '../constants/SessionConstants';

export default {
    receiveLogin: function (response, errors) {
        Dispatcher.dispatch({
            actionType: ActionTypes.LOGIN_RESPONSE,
            user: response.user,
            token: response.token,
            errors: errors
        });
    }
};
