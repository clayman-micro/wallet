import { push } from 'react-router-redux';

import { handleError } from './base';


export function authRequired(dispatch, getState, wrapped, failed) {
    const { session, router } = getState();

    return wrapped(session.accessToken.value)
        .catch(error => {
            if (typeof error.status !== 'undefined') {
                if (error.status === 400) {
                    dispatch(failed(error.data));
                } else if (error.status === 401) {
                    dispatch(push({
                        pathname: '/login',
                        state: { nextPathname: router.location.pathname }
                    }));
                } else {
                    dispatch(failed({}));
                    handleError(error);
                }
            } else {
                throw error;
            }
        });
}

