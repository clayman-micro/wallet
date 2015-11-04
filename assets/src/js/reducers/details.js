import { StatusChoices } from '../constants/status';
import { ActionTypes } from '../constants/details';
import { createCRUDReducer } from './base';

const initialState = {
    status: StatusChoices.INITIAL,
    items: [],
    errors: {}
};


const mapHandlersToActions = {
    [ActionTypes.GET_DETAILS_REQUEST]: 'getCollectionRequest',
    [ActionTypes.GET_DETAILS_RESPONSE]: 'getCollectionResponse',
    [ActionTypes.GET_DETAILS_FAILED]: 'getCollectionFailed',

    [ActionTypes.CREATE_DETAIL_REQUEST]: 'createResourceRequest',
    [ActionTypes.CREATE_DETAIL_RESPONSE]: 'createResourceResponse',
    [ActionTypes.CREATE_DETAIL_FAILED]: 'createResourceFailed',

    [ActionTypes.GET_DETAIL_REQUEST]: 'getResourceRequest',
    [ActionTypes.GET_DETAIL_RESPONSE]: 'getResourceResponse',
    [ActionTypes.GET_DETAIL_FAILED]: 'getResourceFailed',

    [ActionTypes.EDIT_DETAIL_REQUEST]: 'editResourceRequest',
    [ActionTypes.EDIT_DETAIL_RESPONSE]: 'editResourceResponse',
    [ActionTypes.EDIT_DETAIL_FAILED]: 'editResourceFailed',

    [ActionTypes.REMOVE_DETAIL_REQUEST]: 'removeResourceRequest',
    [ActionTypes.REMOVE_DETAIL_RESPONSE]: 'removeResourceResponse',
    [ActionTypes.REMOVE_DETAIL_FAILED]: 'removeResourceFailed'
};

const details = createCRUDReducer(initialState, mapHandlersToActions, {
    getCollectionResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.FETCH_DONE,
        items: [...action.json.details],
        errors: {}
    }),
    createResourceResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.CREATE_DONE,
        items: [...state.items, action.json.detail],
        errors: {}
    }),
    getResourceResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.FETCH_DONE,
        items: [action.json.detail],
        errors: {}
    }),
    editResourceResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.EDIT_DONE,
        items: state.items.map(detail =>
            detail.id === action.json.detail.id ?
                Object.assign({}, detail, action.json.detail) : detail),
        errors: {}
    }),
    removeResourceResponse: (state, action) => Object.assign({}, state, {
        status: StatusChoices.REMOVE_DONE,
        items: state.items.filter(detail =>
            detail.id !== action.detail.id
        ),
        errors: {}
    })
});

export default details;
