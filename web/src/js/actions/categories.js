import { ActionTypes, APIEndpoints } from '../constants/categories';
import { StatusChoices } from '../constants/status';
import APIService from '../services/base';
import { makeActionCreator } from './base';
import { authRequired } from './auth';


const getCategoriesRequest = makeActionCreator(ActionTypes.GET_CATEGORIES_REQUEST);
const getCategoriesResponse = makeActionCreator(ActionTypes.GET_CATEGORIES_RESPONSE, 'json');
const getCategoriesFailed = makeActionCreator(ActionTypes.GET_CATEGORIES_FAILED, 'errors');

export function getCategories() {
    return (dispatch, getState) => {
        dispatch(getCategoriesRequest());

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.getCollection(APIEndpoints.COLLECTION)
                .then(response => dispatch(getCategoriesResponse(response.data)));
        }, getCategoriesFailed);
    };
}

function shouldGetCategories(state) {
    const { categories } = state;
    if (!categories.items.length) {
        return true;
    } else if (categories.status === StatusChoices.FETCHING) {
        return false;
    }

    return false;
}

export function getCategoriesIfNeeded() {
    return (dispatch, getState) => {
        if (shouldGetCategories(getState())) {
            return dispatch(getCategories());
        }
    };
}


const createCategoryRequest = makeActionCreator(ActionTypes.CREATE_CATEGORY_REQUEST, 'payload');
const createCategoryResponse = makeActionCreator(ActionTypes.CREATE_CATEGORY_RESPONSE, 'json');
const createCategoryFailed = makeActionCreator(ActionTypes.CREATE_CATEGORY_FAILED, 'payload', 'errors');

export function createCategory(payload) {
    return (dispatch, getState) => {
        dispatch(createCategoryRequest(payload));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.createResource(APIEndpoints.COLLECTION, payload)
                .then(response => dispatch(createCategoryResponse(response.data)));
        }, createCategoryFailed.bind(this, payload));
    };
}


const editCategoryRequest = makeActionCreator(ActionTypes.EDIT_CATEGORY_REQUEST, 'category', 'payload');
const editCategoryResponse = makeActionCreator(ActionTypes.EDIT_CATEGORY_RESPONSE, 'category', 'json');
const editCategoryFailed = makeActionCreator(ActionTypes.EDIT_CATEGORY_FAILED, 'category', 'payload', 'errors');

export function editCategory(category, payload) {
    return (dispatch, getState) => {
        dispatch(editCategoryRequest(category, payload));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.editResource(APIEndpoints.RESOURCE.replace('{id}', category.id), payload)
                .then(response => dispatch(editCategoryResponse(category, response.data)));
        }, editCategoryFailed.bind(this, category, payload));
    };
}


const removeCategoryRequest = makeActionCreator(ActionTypes.REMOVE_CATEGORY_REQUEST, 'category');
const removeCategoryResponse = makeActionCreator(ActionTypes.REMOVE_CATEGORY_RESPONSE, 'category');
const removeCategoryFailed = makeActionCreator(ActionTypes.REMOVE_CATEGORY_FAILED, 'category', 'errors');

export function removeCategory(category) {
    return (dispatch, getState) => {
        dispatch(removeCategoryRequest(category));

        return authRequired(dispatch, getState, (token) => {
            const service = new APIService(token);
            return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', category.id))
                .then(() => dispatch(removeCategoryResponse(category)));
        }, removeCategoryFailed.bind(this, category));
    };
}
