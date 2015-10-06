import keyMirror from 'key-mirror';

export const APIEndpoints = {
    COLLECTION: 'http://localhost:5000/api/accounts',
    RESOURCE: 'http://localhost:5000/api/accounts/{id}'
};

export const ActionTypes = keyMirror({
    GET_ACCOUNTS_REQUEST: '',
    GET_ACCOUNTS_RESPONSE: '',
    GET_ACCOUNTS_FAILED: '',

    CREATE_ACCOUNT_REQUEST: '',
    CREATE_ACCOUNT_RESPONSE: '',
    CREATE_ACCOUNT_FAILED: '',

    EDIT_ACCOUNT_REQUEST: '',
    EDIT_ACCOUNT_RESPONSE: '',
    EDIT_ACCOUNT_FAILED: '',

    REMOVE_ACCOUNT_REQUEST: '',
    REMOVE_ACCOUNT_RESPONSE: '',
    REMOVE_ACCOUNT_FAILED: ''
});
