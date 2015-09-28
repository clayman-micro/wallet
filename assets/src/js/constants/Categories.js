import keyMirror from 'key-mirror';

export const APIEndpoints = {
    COLLECTION: 'http://localhost:5000/api/categories'
};

export const ActionTypes = keyMirror({
    GET_CATEGORIES_REQUEST: '',
    GET_CATEGORIES_RESPONSE: '',
    GET_CATEGORIES_FAILED: '',

    ADD_CATEGORY: '',
    EDIT_CATEGORY: '',
    DELETE_CATEGORY: ''
});
