import { ActionTypes, APIEndpoints } from '../constants/transactions';
import APIService from '../services/base';
import { makeActionCreator } from './base';
import { authRequired } from './auth';


const getTransactionsRequest = makeActionCreator(ActionTypes.GET_TRANSACTIONS_REQUEST);
const getTransactionsResponse = makeActionCreator(ActionTypes.GET_TRANSACTIONS_RESPONSE, 'json');
const getTransactionsFailed = makeActionCreator(ActionTypes.GET_TRANSACTIONS_FAILED, 'errors');

export function getTransactions() {
    return (dispatch, getState) => {
        dispatch(getTransactionsRequest());

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.getCollection(APIEndpoints.COLLECTION)
                .then(response => dispatch(getTransactionsResponse(response.data)));
        }, getTransactionsFailed);
    };
}


const createTransactionRequest = makeActionCreator(ActionTypes.CREATE_TRANSACTION_REQUEST, 'payload');
const createTransactionResponse = makeActionCreator(ActionTypes.CREATE_TRANSACTION_RESPONSE, 'json');
const createTransactionFailed = makeActionCreator(ActionTypes.CREATE_TRANSACTION_FAILED, 'payload', 'errors');

export function createTransaction(payload) {
    return (dispatch, getState) => {
        dispatch(createTransactionRequest(payload));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.createResource(APIEndpoints.COLLECTION, payload)
                .then(response => dispatch(createTransactionResponse(response.data)));
        }, createTransactionFailed.bind(this, payload));
    };
}


const getTransactionRequest = makeActionCreator(ActionTypes.GET_TRANSACTION_REQUEST, 'transaction');
const getTransactionResponse = makeActionCreator(ActionTypes.GET_TRANSACTION_RESPONSE, 'transaction', 'json');
const getTransactionFailed = makeActionCreator(ActionTypes.GET_TRANSACTION_FAILED, 'transaction', 'errors');

export function getTransaction(transaction) {
    return (dispatch, getState) => {
        dispatch(getTransactionRequest(transaction));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.getResource(APIEndpoints.RESOURCE.replace('{id}', transaction.id))
                .then(response => dispatch(getTransactionResponse(transaction, response.data)));
        }, getTransactionFailed.bind(this, transaction));
    };
}


const editTransactionRequest = makeActionCreator(ActionTypes.EDIT_TRANSACTION_REQUEST, 'transaction', 'payload');
const editTransactionResponse = makeActionCreator(ActionTypes.EDIT_TRANSACTION_RESPONSE, 'transaction', 'json');
const editTransactionFailed = makeActionCreator(ActionTypes.EDIT_TRANSACTION_FAILED, 'transaction', 'payload', 'errors');

export function editTransaction(transaction, payload) {
    return (dispatch, getState) => {
        dispatch(editTransactionRequest(transaction, payload));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.editResource(APIEndpoints.RESOURCE.replace('{id}', transaction.id), payload)
                .then(response => dispatch(editTransactionResponse(transaction, response.data)));
        }, editTransactionFailed.bind(this, transaction, payload));
    };
}


const removeTransactionRequest = makeActionCreator(ActionTypes.REMOVE_TRANSACTION_REQUEST, 'transaction');
const removeTransactionResponse = makeActionCreator(ActionTypes.REMOVE_TRANSACTION_RESPONSE, 'transaction');
const removeTransactionFailed = makeActionCreator(ActionTypes.REMOVE_TRANSACTION_FAILED, 'transaction', 'errors');

export function removeTransaction(transaction) {
    return (dispatch, getState) => {
        dispatch(removeTransactionRequest(transaction));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', transaction.id))
                .then(() => dispatch(removeTransactionResponse(transaction)));
        }, removeTransactionFailed.bind(this, transaction));
    };
}

