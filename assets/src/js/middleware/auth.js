import { pushState } from 'redux-router';

import { ActionTypes } from 'js/constants/Session';


export default store => next => action => {
    if (action.type === ActionTypes.LOGIN_RESPONSE) {
        if (action.accessToken && action.accessToken.expire > Date.now()) {
            let redirectTo = store.getState().router.location.query.next;
            next(action);
            return next(pushState({}, redirectTo));
        }
    }
    return next(action);
};
