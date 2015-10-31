import { ActionTypes, APIEndpoints } from '../constants/accounts';
import { StatusChoices } from '../constants/status';
import APIService from '../services/base';
import { makeActionCreator } from './base';


const getAccountsRequest = makeActionCreator(ActionTypes.GET_ACCOUNTS_REQUEST);
const getAccountsResponse = makeActionCreator(ActionTypes.GET_ACCOUNTS_RESPONSE, 'json');
const getAccountsFailed = makeActionCreator(ActionTypes.GET_ACCOUNTS_FAILED, 'errors');

export function getAccounts() {
    return (dispatch, getState) => {
        dispatch(getAccountsRequest());

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.getCollection(APIEndpoints.COLLECTION)
                .then(response => dispatch(getAccountsResponse(response.data)))
                .catch(errors => dispatch(getAccountsFailed(errors.data)));
        }
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

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.createResource(APIEndpoints.COLLECTION, payload)
                .then(response => dispatch(createAccountResponse(response.data)))
                .catch(errors => dispatch(createAccountFailed(payload, errors.data)));
        }
    };
}

const editAccountRequest = makeActionCreator(ActionTypes.EDIT_ACCOUNT_REQUEST, 'account', 'payload');
const editAccountResponse = makeActionCreator(ActionTypes.EDIT_ACCOUNT_RESPONSE, 'account', 'json');
const editAccountFailed = makeActionCreator(ActionTypes.EDIT_ACCOUNT_FAILED, 'account', 'payload', 'errors');

export function editAccount(account, payload) {
    return (dispatch, getState) => {
        dispatch(editAccountRequest(account, payload));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.editResource(APIEndpoints.RESOURCE.replace('{id}', account.id), payload)
                .then(response => dispatch(editAccountResponse(account, response.data)))
                .catch(errors => dispatch(editAccountFailed(account, payload, errors.data)));
        }
    };
}

const removeAccountRequest = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_REQUEST, 'account');
const removeAccountResponse = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_RESPONSE, 'account');
const removeAccountFailed = makeActionCreator(ActionTypes.REMOVE_ACCOUNT_FAILED, 'account', 'errors');

export function removeAccount(account) {
    return (dispatch, getState) => {
        dispatch(removeAccountRequest(account));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', account.id))
                .then(() => dispatch(removeAccountResponse(account)))
                .catch(errors => dispatch(removeAccountFailed(account, errors.data)));
        }
    };
}
