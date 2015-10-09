import { ActionTypes } from '../constants/categories';
import { createReducer } from './base';

const initialState = {
    isFetching: false,
    items: [],
    errors: {}
};

const categories = createReducer(initialState, {
    // Fetch collection
    [ActionTypes.GET_CATEGORIES_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.GET_CATEGORIES_RESPONSE](state, action) {
        return Object.assign({}, state, {
            isFetching: false,
            items: [...action.json.categories],
            errors: {}
        });
    },
    [ActionTypes.GET_CATEGORIES_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    },

    // Create instance
    [ActionTypes.CREATE_CATEGORY_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.CREATE_CATEGORY_RESPONSE](state, action) {
        return Object.assign({}, state, {
            items: [action.json.category, ...state.items],
            isFetching: false,
            errors: {}
        });
    },
    [ActionTypes.CREATE_CATEGORY_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    },

    // Edit instance
    [ActionTypes.EDIT_CATEGORY_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.EDIT_CATEGORY_RESPONSE](state, action) {
        return Object.assign({}, state, {
            items: state.items.map(category =>
                category.id === action.json.category.id ?
                    Object.assign({}, category, action.json.category) : category),
            isFetching: false,
            errors: {}
        });
    },
    [ActionTypes.EDIT_CATEGORY_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    },

    // Remove instance
    [ActionTypes.REMOVE_CATEGORY_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.REMOVE_CATEGORY_RESPONSE](state, action) {
        return Object.assign({}, state, { items: state.items.filter(category =>
            category.id !== action.category.id
        ) });
    },
    [ActionTypes.REMOVE_CATEGORY_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    }
});


export default categories;
