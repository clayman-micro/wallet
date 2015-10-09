import { ActionTypes, APIEndpoints } from '../constants/categories';
import APIService from '../services/base';
import { makeActionCreator } from './base';


const getCategoriesRequest = makeActionCreator(ActionTypes.GET_CATEGORIES_REQUEST);
const getCategoriesResponse = makeActionCreator(ActionTypes.GET_CATEGORIES_RESPONSE, 'json');
const getCategoriesFailed = makeActionCreator(ActionTypes.GET_CATEGORIES_FAILED, 'errors');

export function getCategories(token) {
    return dispatch => {
        dispatch(getCategoriesRequest());

        const service = new APIService(token);
        return service.getCollection(APIEndpoints.COLLECTION)
            .then(response => dispatch(getCategoriesResponse(response.data)))
            .catch(errors => dispatch(getCategoriesFailed(errors.data)));
    };
}

const createCategoryRequest = makeActionCreator(ActionTypes.CREATE_CATEGORY_REQUEST, 'payload');
const createCategoryResponse = makeActionCreator(ActionTypes.CREATE_CATEGORY_RESPONSE, 'json');
const createCategoryFailed = makeActionCreator(ActionTypes.CREATE_CATEGORY_FAILED, 'payload', 'errors');

export function createCategory(token, payload) {
    return dispatch => {
        dispatch(createCategoryRequest(payload));

        const service = new APIService(token);
        return service.createResource(APIEndpoints.COLLECTION, payload)
            .then(response => dispatch(createCategoryResponse(response.data)))
            .catch(errors => dispatch(createCategoryFailed(payload, errors.data)));
    };
}


const editCategoryRequest = makeActionCreator(ActionTypes.EDIT_CATEGORY_REQUEST, 'category', 'payload');
const editCategoryResponse = makeActionCreator(ActionTypes.EDIT_CATEGORY_RESPONSE, 'category', 'json');
const editCategoryFailed = makeActionCreator(ActionTypes.EDIT_CATEGORY_FAILED, 'category', 'payload', 'errors');

export function editCategory(token, category, payload) {
    return dispatch => {
        dispatch(editCategoryRequest(category, payload));

        const service = new APIService(token);
        return service.editResource(APIEndpoints.RESOURCE.replace('{id}', category.id), payload)
            .then(response => dispatch(editCategoryResponse(category, response.data)))
            .catch(errors => dispatch(editCategoryFailed(category, payload, errors.data)));
    };
}


const removeCategoryRequest = makeActionCreator(ActionTypes.REMOVE_CATEGORY_REQUEST, 'category');
const removeCategoryResponse = makeActionCreator(ActionTypes.REMOVE_CATEGORY_RESPONSE, 'category');
const removeCategoryFailed = makeActionCreator(ActionTypes.REMOVE_CATEGORY_FAILED, 'category', 'errors');

export function removeCategory(token, category) {
    return dispatch => {
        dispatch(removeCategoryRequest(category));

        const service = new APIService(token);
        return service.removeResource(APIEndpoints.RESOURCE.replace('{id}', category.id))
            .then(() => dispatch(removeCategoryResponse(category)))
            .catch(errors => dispatch(removeCategoryFailed(category, errors.data)));
    };
}

export default {
    addCategory: function (name) {
        return { type: ActionTypes.ADD_CATEGORY, name };
    },

    editCategory: function (id, name) {
        return { type: ActionTypes.EDIT_CATEGORY, id, name };
    },

    deleteCategory: function (id) {
        return { type: ActionTypes.DELETE_CATEGORY, id };
    }
};
