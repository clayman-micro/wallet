import { ActionTypes, APIEndpoints } from '../constants/accounts';
import APIService from '../services/base';
import { makeActionCreator } from './base';


const getAccountsRequest = makeActionCreator(ActionTypes.GET_ACCOUNTS_REQUEST);
const getAccountsResponse = makeActionCreator(ActionTypes.GET_ACCOUNTS_RESPONSE, 'json');
const getAccountsFailed = makeActionCreator(ActionTypes.GET_ACCOUNTS_FAILED, 'errors');

export function getAccounts(token) {
    return dispatch => {
        dispatch(getAccountsRequest());

        const service = new APIService(token);
        return service.getCollection(APIEndpoints.COLLECTION)
            .then(response => dispatch(getAccountsResponse(response.data)))
            .catch(errors => dispatch(getAccountsFailed(errors.data)));
    };
}

const createAccountRequest = makeActionCreator(ActionTypes.CREATE_ACCOUNT_REQUEST, 'payload');
const createAccountResponse = makeActionCreator(ActionTypes.CREATE_ACCOUNT_RESPONSE, 'json');
const createAccountFailed = makeActionCreator(ActionTypes.CREATE_ACCOUNT_FAILED, 'payload', 'errors');

export function createAccount(token, payload) {
    return dispatch => {
        dispatch(createAccountRequest(payload));

        const service = new APIService(token);
        return service.createResource(APIEndpoints.COLLECTION, payload)
            .then(response => dispatch(createAccountResponse(response.data)))
            .catch(errors => dispatch(createAccountFailed(payload, errors.data)));
    };
}

const editAccountRequest = makeActionCreator(ActionTypes.EDIT_ACCOUNT_REQUEST, 'account', 'payload');
const editAccountResponse = makeActionCreator(ActionTypes.EDIT_ACCOUNT_RESPONSE, 'account', 'json');
const editAccountFailed = makeActionCreator(ActionTypes.EDIT_ACCOUNT_FAILED, 'account', 'payload', 'errors');

export function editAccount(token, account, payload) {
    return dispatch => {
        dispatch(editAccountRequest(account, payload));

        const service = new APIService(token);
        return service.editResource(APIEndpoints.RESOURCE.replace('{id}', account.id), payload)
            .then(response => dispatch(editAccountResponse(account, response.data)))
            .catch(errors => dispatch(editAccountFailed(account, payload, errors.data)));
    };
}

const removeAccountRequest = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_REQUEST, 'account');
const removeAccountResponse = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_RESPONSE, 'account');
const removeAccountFailed = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_FAILED, 'account', 'errors');

export function removeAccount(token, account) {
    return dispatch => {
        dispatch(removeAccountRequest(account));

        const service = new APIService(token);
        return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', account.id))
            .then(() => dispatch(removeAccountResponse(account)))
            .catch(errors => dispatch(removeAccountFailed(account, errors.data)));
    };
}
