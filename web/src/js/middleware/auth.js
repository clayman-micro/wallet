import { push } from 'react-router-redux';

import { ActionTypes } from '../constants/session';


export default store => next => action => {
    if (action.type === ActionTypes.LOGIN_RESPONSE) {
        if (action.accessToken && action.accessToken.expire > Date.now()) {
            let redirectTo = '/';

            if (store.getState().router.location.query.next) {
                redirectTo = store.getState().router.location.query.next;
            }

            next(action);
            return next(push(redirectTo));
        }
    }
    return next(action);
};
