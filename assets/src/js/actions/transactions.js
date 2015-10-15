import { ActionTypes, APIEndpoints } from '../constants/transactions';
import APIService from '../services/base';
import { makeActionCreator } from './base';


const getTransactionsRequest = makeActionCreator(ActionTypes.GET_TRANSACTIONS_REQUEST);
const getTransactionsResponse = makeActionCreator(ActionTypes.GET_TRANSACTIONS_RESPONSE, 'json');
const getTransactionsFailed = makeActionCreator(ActionTypes.GET_TRANSACTIONS_FAILED, 'errors');

export function getTransactions() {
    return (dispatch, getState) => {
        dispatch(getTransactionsRequest());

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.getCollection(APIEndpoints.COLLECTION)
                .then(response => dispatch(getTransactionsResponse(response.data)))
                .catch(errors => dispatch(getTransactionsFailed(errors.data)));
        }
    };
}


const createTransactionRequest = makeActionCreator(ActionTypes.CREATE_TRANSACTION_REQUEST, 'payload');
const createTransactionResponse = makeActionCreator(ActionTypes.CREATE_TRANSACTION_RESPONSE, 'json');
const createTransactionFailed = makeActionCreator(ActionTypes.CREATE_TRANSACTION_FAILED, 'payload', 'errors');

export function createTransaction(payload) {
    return (dispatch, getState) => {
        dispatch(createTransactionRequest(payload));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.createResource(APIEndpoints.COLLECTION, payload)
                .then(response => dispatch(createTransactionResponse(response.data)))
                .catch(errors => dispatch(createTransactionFailed(payload, errors.data)));
        }
    };
}


const editTransactionRequest = makeActionCreator(ActionTypes.EDIT_TRANSACTION_REQUEST, 'transaction', 'payload');
const editTransactionResponse = makeActionCreator(ActionTypes.EDIT_TRANSACTION_RESPONSE, 'transaction', 'json');
const editTransactionFailed = makeActionCreator(ActionTypes.EDIT_TRANSACTION_FAILED, 'transaction', 'payload', 'errors');

export function editTransaction(transaction, payload) {
    return (dispatch, getState) => {
        dispatch(editTransactionRequest(transaction, payload));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.editResource(APIEndpoints.RESOURCE.replace('{id}', transaction.id), payload)
                .then(response => dispatch(editTransactionResponse(transaction, response.data)))
                .catch(errors => dispatch(editTransactionFailed(transaction, payload, errors.data)));
        }
    };
}


const removeTransactionRequest = makeActionCreator(ActionTypes.REMOVE_TRANSACTION_REQUEST, 'transaction');
const removeTransactionResponse = makeActionCreator(ActionTypes.REMOVE_TRANSACTION_RESPONSE, 'transaction');
const removeTransactionFailed = makeActionCreator(ActionTypes.REMOVE_TRANSACTION_FAILED, 'transaction', 'errors');

export function removeTransaction(transaction) {
    return (dispatch, getState) => {
        dispatch(removeTransactionRequest(transaction));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', transaction.id))
                .then(() => dispatch(removeTransactionResponse(transaction)))
                .catch(errors => dispatch(removeTransactionFailed(transaction, errors.data)));
        }
    };
}

