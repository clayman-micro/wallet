import keyMirror from 'keymirror';

export const APIEndpoints = {
    LOGIN: '/auth/login'
};

export const ActionTypes = keyMirror({
    LOGIN_REQUEST: null,
    LOGIN_RESPONSE: null,

    UNAUTHORIZED: null,

    LOGOUT: null
});
