import { ActionTypes, APIEndpoints } from '../constants/details';
import APIService from '../services/base';
import { makeActionCreator } from './base';


const getDetailsRequest = makeActionCreator(ActionTypes.GET_DETAILS_REQUEST, 'transaction');
const getDetailsResponse = makeActionCreator(ActionTypes.GET_DETAILS_RESPONSE, 'transaction', 'json');
const getDetailsFailed = makeActionCreator(ActionTypes.GET_DETAILS_FAILED, 'transaction', 'errors');

export function getDetails(transaction) {
    return (dispatch, getState) => {
        dispatch(getDetailsRequest(transaction));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            const url = APIEndpoints.COLLECTION.replace('{parentID}', transaction.id);
            return service.getCollection(url)
                .then(response => dispatch(getDetailsResponse(transaction, response.data)))
                .catch(errors => dispatch(getDetailsFailed(transaction, errors.data)));
        }
    };
}


const createDetailRequest = makeActionCreator(ActionTypes.CREATE_DETAIL_REQUEST, 'payload');
const createDetailResponse = makeActionCreator(ActionTypes.CREATE_DETAIL_RESPONSE, 'json');
const createDetailFailed = makeActionCreator(ActionTypes.CREATE_DETAIL_FAILED, 'payload', 'errors');

export function createDetail(transaction, payload) {
    return (dispatch, getState) => {
        dispatch(createDetailRequest(payload));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            const url = APIEndpoints.COLLECTION.replace('{parentID}', transaction.id);
            return service.createResource(url, payload)
                .then(response => dispatch(createDetailResponse(response.data)))
                .catch(errors => dispatch(createDetailFailed(errors.data)));
        }
    };
}


const getDetailRequest = makeActionCreator(ActionTypes.GET_DETAIL_REQUEST, 'detail');
const getDetailResponse = makeActionCreator(ActionTypes.GET_DETAIL_RESPONSE, 'detail', 'json');
const getDetailFailed = makeActionCreator(ActionTypes.GET_DETAIL_FAILED, 'detail', 'errors');

export function getDetail(detail) {
    return (dispatch, getState) => {
        dispatch(getDetailRequest(detail));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            const url = APIEndpoints.RESOURCE
                .replace('{parentID}', detail.transaction_id)
                .replace('{instanceID}', detail.id);
            return service.getResource(url)
                .then(response => dispatch(getDetailResponse(detail, response.data)))
                .catch(errors => dispatch(getDetailFailed(detail, errors.data)));
        }
    };
}


const editDetailRequest = makeActionCreator(ActionTypes.EDIT_DETAIL_REQUEST, 'detail', 'payload');
const editDetailResponse = makeActionCreator(ActionTypes.EDIT_DETAIL_RESPONSE, 'detail', 'json');
const editDetailFailed = makeActionCreator(ActionTypes.EDIT_DETAIL_FAILED, 'detail', 'errors');

export function editDetail(detail, payload) {
    return (dispatch, getState) => {
        dispatch(editDetailRequest(detail, payload));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            const url = APIEndpoints.RESOURCE
                .replace('{parentID}', detail.transaction_id)
                .replace('{instanceID}', detail.id);
            return service.editResource(url, payload)
                .then(response => dispatch(editDetailResponse(detail, response.data)))
                .catch(errors => dispatch(editDetailFailed(detail, errors.data)));
        }
    };
}

const removeDetailRequest = makeActionCreator(ActionTypes.REMOVE_DETAIL_REQUEST, 'detail');
const removeDetailResponse = makeActionCreator(ActionTypes.REMOVE_DETAIL_RESPONSE, 'detail');
const removeDetailFailed = makeActionCreator(ActionTypes.REMOVE_DETAIL_FAILED, 'detail', 'errors');

export function removeDetail(detail) {
    return (dispatch, getState) => {
        dispatch(removeDetailRequest(detail));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            const url = APIEndpoints.RESOURCE
                .replace('{parentID}', detail.transaction_id)
                .replace('{instanceID}', detail.id);
            return service.removeResource(url)
                .then(() => dispatch(removeDetailResponse(detail)))
                .catch(errors => dispatch(removeDetailFailed(detail, errors.data)));
        }
    };
}
