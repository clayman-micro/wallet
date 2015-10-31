import { ActionTypes, APIEndpoints } from '../constants/categories';
import { StatusChoices } from '../constants/status';
import APIService from '../services/base';
import { makeActionCreator } from './base';


const getCategoriesRequest = makeActionCreator(ActionTypes.GET_CATEGORIES_REQUEST);
const getCategoriesResponse = makeActionCreator(ActionTypes.GET_CATEGORIES_RESPONSE, 'json');
const getCategoriesFailed = makeActionCreator(ActionTypes.GET_CATEGORIES_FAILED, 'errors');

export function getCategories() {
    return (dispatch, getState) => {
        dispatch(getCategoriesRequest());

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.getCollection(APIEndpoints.COLLECTION)
                .then(response => dispatch(getCategoriesResponse(response.data)))
                .catch(errors => dispatch(getCategoriesFailed(errors.data)));
        }
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

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.createResource(APIEndpoints.COLLECTION, payload)
                .then(response => dispatch(createCategoryResponse(response.data)))
                .catch(errors => dispatch(createCategoryFailed(payload, errors.data)));
        }
    };
}


const editCategoryRequest = makeActionCreator(ActionTypes.EDIT_CATEGORY_REQUEST, 'category', 'payload');
const editCategoryResponse = makeActionCreator(ActionTypes.EDIT_CATEGORY_RESPONSE, 'category', 'json');
const editCategoryFailed = makeActionCreator(ActionTypes.EDIT_CATEGORY_FAILED, 'category', 'payload', 'errors');

export function editCategory(category, payload) {
    return (dispatch, getState) => {
        dispatch(editCategoryRequest(category, payload));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.editResource(APIEndpoints.RESOURCE.replace('{id}', category.id), payload)
                .then(response => dispatch(editCategoryResponse(category, response.data)))
                .catch(errors => dispatch(editCategoryFailed(category, payload, errors.data)));
        }
    };
}


const removeCategoryRequest = makeActionCreator(ActionTypes.REMOVE_CATEGORY_REQUEST, 'category');
const removeCategoryResponse = makeActionCreator(ActionTypes.REMOVE_CATEGORY_RESPONSE, 'category');
const removeCategoryFailed = makeActionCreator(ActionTypes.REMOVE_CATEGORY_FAILED, 'category', 'errors');

export function removeCategory(category) {
    return (dispatch, getState) => {
        dispatch(removeCategoryRequest(category));

        const { session } = getState();
        if (session.accessToken && session.accessToken.isValid()) {
            const service = new APIService(session.accessToken.value);
            return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', category.id))
                .then(() => dispatch(removeCategoryResponse(category)))
                .catch(errors => dispatch(removeCategoryFailed(category, errors.data)));
        }
    };
}
