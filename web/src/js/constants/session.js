import keyMirror from 'keymirror';

export const APIEndpoints = {
    LOGIN: '/auth/login'
};

export const ActionTypes = keyMirror({
    LOGIN_REQUEST: '',
    LOGIN_RESPONSE: '',
    LOGIN_FAILED: '',

    UNAUTHORIZED: '',
    LOGOUT: ''
});

export const STATUS_CHOICES = keyMirror({
    UNAUTHORIZED: '',
    AUTHORIZED: '',
    LOGIN_REQUEST_SEND: ''
});
