import { ActionTypes } from '../constants/accounts';
import { createReducer } from './base';

const initialState = {
    isFetching: false,
    items: [],
    errors: {}
};

const accounts = createReducer(initialState, {
    // Fetch collection
    [ActionTypes.GET_ACCOUNTS_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.GET_ACCOUNTS_RESPONSE](state, action) {
        return Object.assign({}, state, {
            isFetching: false,
            items: [...action.json.accounts],
            errors: {}
        });
    },
    [ActionTypes.GET_ACCOUNTS_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    },

    // Create instance
    [ActionTypes.CREATE_ACCOUNT_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.CREATE_ACCOUNT_RESPONSE](state, action) {
        return Object.assign({}, state, {
            items: [...state.items, action.json.account],
            isFetching: false,
            errors: {}
        });
    },
    [ActionTypes.CREATE_ACCOUNT_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    },

    // Edit instance
    [ActionTypes.EDIT_ACCOUNT_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.EDIT_ACCOUNT_RESPONSE](state, action) {
        return Object.assign({}, state, {
            items: state.items.map(account =>
                account.id === action.json.account.id ?
                    Object.assign({}, account, action.json.account) : account),
            isFetching: false,
            errors: {}
        });
    },
    [ActionTypes.EDIT_ACCOUNT_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    },

    // Remove instance
    [ActionTypes.REMOVE_ACCOUNT_REQUEST](state) {
        return Object.assign({}, state, { isFetching: true });
    },
    [ActionTypes.REMOVE_ACCOUNT_RESPONSE](state, action) {
        return Object.assign({}, state, { items: state.items.filter(account =>
            account.id !== action.account.id
        ) });
    },
    [ActionTypes.REMOVE_ACCOUNT_FAILED](state, action) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    }
});

export default accounts;
