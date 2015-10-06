/* eslint no-underscore-dangle: 0 */

import { ActionTypes } from '../constants/session';

class PersistStore {
    constructor() {
        this._user = {};
        this._accessToken = {};

        if (typeof window.sessionStorage !== 'undefined') {
            const user = window.sessionStorage.getItem('user');
            if (user) {
                try {
                    this._user = JSON.parse(user);
                } catch (err) {

                }
            }

            const token = window.sessionStorage.getItem('accessToken');
            if (token) {
                try {
                    this._accessToken = JSON.parse(token);
                } catch (err) {

                }
            }
        }
    }

    get user() {
        return this._user;
    }

    set user(user) {
        this._user = user;
        window.sessionStorage.setItem('user', JSON.stringify(this._user));
    }

    get token() {
        return this._accessToken;
    }

    set token(token) {
        this._accessToken = token;
        window.sessionStorage.setItem('accessToken', JSON.stringify(this._accessToken));
    }
}

let persistStore = new PersistStore();

const initialState = {
    user: persistStore.user,
    accessToken: persistStore.token,
    isFetching: false,
    isAuthenticated: false,
    errors: []
};

export default function session(state = initialState, action) {
    if (action.type === ActionTypes.LOGIN_REQUEST) {
        return Object.assign({}, state, {
            isFetching: true,
            isAuthenticated: false
        });
    } else if (action.type === ActionTypes.LOGIN_RESPONSE) {
        persistStore.user = action.user;
        persistStore.token = action.accessToken;
        return Object.assign({}, state, {
            user: persistStore.user,
            accessToken: persistStore.token,
            isFetching: false,
            isAuthenticated: true,
            errors: []
        });
    } else if (action.type === ActionTypes.LOGIN_FAILED) {
        return Object.assign({}, state, {
            user: null,
            accessToken: null,
            isFetching: false,
            isAuthenticated: false,
            errors: action.errors
        });
    } else if (action.type === ActionTypes.UNAUTHORIZED) {
        return state;
    } else if (action.type === ActionTypes.LOGOUT) {
        return Object.assign({}, state, {
            user: null,
            accessToken: null,
            isFetching: false,
            isAuthenticated: false,
            errors: []
        });
    }

    return state;
}
