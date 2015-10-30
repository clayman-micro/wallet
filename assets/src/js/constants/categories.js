import keyMirror from 'keyMirror';

export const APIEndpoints = {
    COLLECTION: '/api/categories',
    RESOURCE: '/api/categories/{id}'
};

export const ActionTypes = keyMirror({
    GET_CATEGORIES_REQUEST: '',
    GET_CATEGORIES_RESPONSE: '',
    GET_CATEGORIES_FAILED: '',

    CREATE_CATEGORY_REQUEST: '',
    CREATE_CATEGORY_RESPONSE: '',
    CREATE_CATEGORY_FAILED: '',

    EDIT_CATEGORY_REQUEST: '',
    EDIT_CATEGORY_RESPONSE: '',
    EDIT_CATEGORY_FAILED: '',

    REMOVE_CATEGORY_REQUEST: '',
    REMOVE_CATEGORY_RESPONSE: '',
    REMOVE_CATEGORY_FAILED: '',

    ADD_CATEGORY: '',
    EDIT_CATEGORY: '',
    DELETE_CATEGORY: ''
});
