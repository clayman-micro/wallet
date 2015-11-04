import keyMirror from 'keyMirror';

export const APIEndpoints = {
    COLLECTION: '/api/transactions/{parentID}/details',
    RESOURCE: '/api/transactions/{parentID}/details/{instanceID}'
};

export const ActionTypes = keyMirror({
    GET_DETAILS_REQUEST: '',
    GET_DETAILS_RESPONSE: '',
    GET_DETAILS_FAILED: '',

    CREATE_DETAIL_REQUEST: '',
    CREATE_DETAIL_RESPONSE: '',
    CREATE_DETAIL_FAILED: '',

    GET_DETAIL_REQUEST: '',
    GET_DETAIL_RESPONSE: '',
    GET_DETAIL_FAILED: '',

    EDIT_DETAIL_REQUEST: '',
    EDIT_DETAIL_RESPONSE: '',
    EDIT_DETAIL_FAILED: '',

    REMOVE_DETAIL_REQUEST: '',
    REMOVE_DETAIL_RESPONSE: '',
    REMOVE_DETAIL_FAILED: ''
});
