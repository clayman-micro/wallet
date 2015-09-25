import keyMirror from 'key-mirror';

export const APIEndpoints = {
    LOGIN: '/auth/login'
};

export const ActionTypes = keyMirror({
    LOGIN_REQUEST: '',
    LOGIN_RESPONSE: '',

    UNAUTHORIZED: '',

    LOGOUT: ''
});
