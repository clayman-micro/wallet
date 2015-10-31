import keyMirror from 'keyMirror';

export const APIEndpoints = {
    COLLECTION: '/api/transactions',
    RESOURCE: '/api/transactions/{id}'
};

export const TransactionTypes = {
    INCOME: 'income',
    EXPENSE: 'expense'
};

export const ActionTypes = keyMirror({
    GET_TRANSACTIONS_REQUEST: '',
    GET_TRANSACTIONS_RESPONSE: '',
    GET_TRANSACTIONS_FAILED: '',

    CREATE_TRANSACTION_REQUEST: '',
    CREATE_TRANSACTION_RESPONSE: '',
    CREATE_TRANSACTION_FAILED: '',

    GET_TRANSACTION_REQUEST: '',
    GET_TRANSACTION_RESPONSE: '',
    GET_TRANSACTION_FAILED: '',

    EDIT_TRANSACTION_REQUEST: '',
    EDIT_TRANSACTION_RESPONSE: '',
    EDIT_TRANSACTION_FAILED: '',

    REMOVE_TRANSACTION_REQUEST: '',
    REMOVE_TRANSACTION_RESPONSE: '',
    REMOVE_TRANSACTION_FAILED: ''
});
