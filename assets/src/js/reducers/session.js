/* eslint no-underscore-dangle: 0 */

import { ActionTypes } from '../constants/session';


class Token {
    constructor(value, expire) {
        this._value = value;

        if (Number.isInteger(expire) && expire > Date.now()) {
            this._expire = expire;
        } else {
            throw Error('Expire must be integer and bigger than now');
        }
    }

    get value() {
        return this._value;
    }

    isValid() {
        return Date.now() < this._expire;
    }
}


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

            let token = window.sessionStorage.getItem('accessToken');
            if (token) {
                try {
                    token = JSON.parse(token);
                    this._accessToken = new Token(token.value, token.expire);
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
        this._accessToken = new Token(token.value, token.expire);
        window.sessionStorage.setItem('accessToken', JSON.stringify(token));
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

export default function session(state = initialState, action = null) {
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
