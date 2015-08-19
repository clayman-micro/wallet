/* eslint no-underscore-dangle: 0 */

import { ActionTypes } from '../constants/SessionConstants';
import BaseStore from './BaseStore';


class SessionStore extends BaseStore {
    constructor() {
        super();

        this.subscribe(() => this._registerToActions.bind(this));

        if (typeof window.sessionStorage !== 'undefined') {
            this._accessToken = window.sessionStorage.getItem('access-token');
            this._user = window.sessionStorage.getItem('user');
            if (this._user) {
                this._user = JSON.parse(this._user);
            }
        } else {
            this._accessToken = null;
            this._user = null;
        }

        this._status = null;
        this._errors = null;
    }

    _registerToActions(action) {
        if (action.actionType === ActionTypes.LOGIN_RESPONSE) {
            this._accessToken = action.token;
            this._user = action.user;

            if (typeof window.sessionStorage !== 'undefined' && this._accessToken && this._user) {
                window.sessionStorage.setItem('access-token', this._accessToken);
                window.sessionStorage.setItem('user', JSON.stringify(this._user));
            }

            if (action.errors) {
                this._errors = action.errors;
            } else {
                this._errors = null;
            }
        } else if (action.actionType === ActionTypes.LOGOUT) {
            this._accessToken = null;
            this._user = null;

            if (typeof window.sessionStorage !== 'undefined') {
                window.sessionStorage.removeItem('access-token');
                window.sessionStorage.removeItem('user');
            }

            this._errors = action.errors;
        } else if (action.actionType === ActionTypes.UNAUTHORIZED) {
            this._accessToken = null;
            this._user = null;

            if (typeof window.sessionStorage !== 'undefined') {
                window.sessionStorage.removeItem('access-token');
                window.sessionStorage.removeItem('user');
            }
        }

        this.emitChange();
    }

    get user() {
        return this._user;
    }

    get accessToken() {
        return this._accessToken;
    }

    get status() {
        return this._status;
    }

    get errors() {
        return this._errors;
    }

    isLoggedIn() {
        return !!this._user;
    }

}

export default new SessionStore();
