import { ActionTypes, APIEndpoints } from '../constants/accounts';
import { StatusChoices } from '../constants/status';
import APIService from '../services/base';
import { makeActionCreator } from './base';
import { authRequired } from './auth';


const getAccountsRequest = makeActionCreator(ActionTypes.GET_ACCOUNTS_REQUEST);
const getAccountsResponse = makeActionCreator(ActionTypes.GET_ACCOUNTS_RESPONSE, 'json');
const getAccountsFailed = makeActionCreator(ActionTypes.GET_ACCOUNTS_FAILED, 'errors');

export function getAccounts() {
    return (dispatch, getState) => {
        dispatch(getAccountsRequest());

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.getCollection(APIEndpoints.COLLECTION)
                .then(response => dispatch(getAccountsResponse(response.data)));
        }, getAccountsFailed);
    };
}

function shouldGetAccounts(state) {
    const { accounts } = state;
    if (!accounts.items.length) {
        return true;
    } else if (accounts.status === StatusChoices.FETCHING) {
        return false;
    }

    return false;
}

export function getAccountsIfNeeded() {
    return (dispatch, getState) => {
        if (shouldGetAccounts(getState())) {
            return dispatch(getAccounts());
        }
    };
}


const createAccountRequest = makeActionCreator(ActionTypes.CREATE_ACCOUNT_REQUEST, 'payload');
const createAccountResponse = makeActionCreator(ActionTypes.CREATE_ACCOUNT_RESPONSE, 'json');
const createAccountFailed = makeActionCreator(ActionTypes.CREATE_ACCOUNT_FAILED, 'payload', 'errors');

export function createAccount(payload) {
    return (dispatch, getState) => {
        dispatch(createAccountRequest(payload));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.createResource(APIEndpoints.COLLECTION, payload)
                .then(response => dispatch(createAccountResponse(response.data)));
        }, createAccountFailed.bind(this, payload));
    };
}

const editAccountRequest = makeActionCreator(ActionTypes.EDIT_ACCOUNT_REQUEST, 'account', 'payload');
const editAccountResponse = makeActionCreator(ActionTypes.EDIT_ACCOUNT_RESPONSE, 'account', 'json');
const editAccountFailed = makeActionCreator(ActionTypes.EDIT_ACCOUNT_FAILED, 'account', 'payload', 'errors');

export function editAccount(account, payload) {
    return (dispatch, getState) => {
        dispatch(editAccountRequest(account, payload));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.editResource(APIEndpoints.RESOURCE.replace('{id}', account.id), payload)
                .then(response => dispatch(editAccountResponse(account, response.data)));
        }, editAccountFailed.bind(this, account, payload));
    };
}

const removeAccountRequest = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_REQUEST, 'account');
const removeAccountResponse = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_RESPONSE, 'account');
const removeAccountFailed = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_FAILED, 'account', 'errors');

export function removeAccount(account) {
    return (dispatch, getState) => {
        dispatch(removeAccountRequest(account));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', account.id))
                .then(() => dispatch(removeAccountResponse(account)));
        }, removeAccountFailed.bind(this, account));
    };
}
