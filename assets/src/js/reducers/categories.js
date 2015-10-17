import { StatusChoices } from '../constants/status';
import { ActionTypes } from '../constants/categories';
import { createCRUDReducer } from './base';

const initialState = {
    status: StatusChoices.INITIAL,
    items: [],
    errors: {}
};

const mapHandlersToActions = {
    [ActionTypes.GET_CATEGORIES_REQUEST]: 'getCollectionRequest',
    [ActionTypes.GET_CATEGORIES_RESPONSE]: 'getCollectionResponse',
    [ActionTypes.GET_CATEGORIES_FAILED]: 'getCollectionFailed',

    [ActionTypes.CREATE_CATEGORY_REQUEST]: 'createResourceRequest',
    [ActionTypes.CREATE_CATEGORY_RESPONSE]: 'createResourceResponse',
    [ActionTypes.CREATE_CATEGORY_FAILED]: 'createResourceFailed',

    [ActionTypes.EDIT_CATEGORY_REQUEST]: 'editResourceRequest',
    [ActionTypes.EDIT_CATEGORY_RESPONSE]: 'editResourceResponse',
    [ActionTypes.EDIT_CATEGORY_FAILED]: 'editResourceFailed',

    [ActionTypes.REMOVE_CATEGORY_REQUEST]: 'removeResourceRequest',
    [ActionTypes.REMOVE_CATEGORY_RESPONSE]: 'removeResourceResponse',
    [ActionTypes.REMOVE_CATEGORY_FAILED]: 'removeResourceFailed'
};

const categories = createCRUDReducer(initialState, mapHandlersToActions, {
    getCollectionResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.FETCH_DONE, items: [...action.json.categories], errors: {} }),
    createResourceResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.CREATE_DONE, items: [...state.items, action.json.category], errors: {} }),
    editResourceResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.EDIT_DONE,
        items: state.items.map(category =>
            category.id === action.json.category.id ?
                Object.assign({}, category, action.json.category) : category),
        errors: {}
    }),
    removeResourceResponse: (state, action) => Object.assign({
        status: StatusChoices.REMOVE_DONE,
        items: state.items.filter(category =>
            category.id !== action.category.id
        ),
        errors: {}
    })
});

export default categories;
