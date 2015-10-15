import { ActionTypes } from '../constants/transactions';
import { createCRUDReducer } from './base';


const initialState = {
    isFetching: false,
    items: [],
    errors: {}
};

const mapHandlersToActions = {
    [ActionTypes.GET_TRANSACTIONS_REQUEST]: 'getCollectionRequest',
    [ActionTypes.GET_TRANSACTIONS_RESPONSE]: 'getCollectionResponse',
    [ActionTypes.GET_TRANSACTIONS_FAILED]: 'getCollectionFailed',

    [ActionTypes.CREATE_TRANSACTION_REQUEST]: 'createResourceRequest',
    [ActionTypes.CREATE_TRANSACTION_RESPONSE]: 'createResourceResponse',
    [ActionTypes.CREATE_TRANSACTION_FAILED]: 'createResourceFailed',

    [ActionTypes.EDIT_TRANSACTION_REQUEST]: 'editResourceRequest',
    [ActionTypes.EDIT_TRANSACTION_RESPONSE]: 'editResourceResponse',
    [ActionTypes.EDIT_TRANSACTION_FAILED]: 'editResourceFailed',

    [ActionTypes.REMOVE_TRANSACTION_REQUEST]: 'removeResourceRequest',
    [ActionTypes.REMOVE_TRANSACTION_RESPONSE]: 'removeResourceResponse',
    [ActionTypes.REMOVE_TRANSACTION_FAILED]: 'removeResourceFailed'
};

const transactions = createCRUDReducer(initialState, mapHandlersToActions, {
    getCollectionResponse: (state, action) => Object.assign({}, state, {
        isFetching: false, items: [...action.json.transactions], errors: {} }),
    createResourceResponse: (state, action) => Object.assign({}, state, {
        isFetching: false, items: [...state.items, action.json.transaction], errors: {} }),
    editResourceResponse: (state, action) => Object.assign({}, state, {
        isFetching: false,
        items: state.items.map(transaction =>
            transaction.id === action.json.transaction.id ?
                Object.assign({}, transaction, action.json.transaction) : transaction),
        errors: {}
    }),
    removeResourceResponse: (state, action) => Object.assign({
        isFetching: false,
        items: state.items.filter(transaction =>
            transaction.id !== action.transaction.id
        ),
        errors: {}
    })
});

export default transactions;
