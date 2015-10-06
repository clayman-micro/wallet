import { ActionTypes, APIEndpoints } from '../constants/categories';
import APIService from '../services/base';


function getCategoriesRequest() {
    return { type: ActionTypes.GET_CATEGORIES_REQUEST };
}

function getCategoriesResponse(json) {
    return { type: ActionTypes.GET_CATEGORIES_RESPONSE, categories: json.categories };
}

function getCategoriesFailed(errors) {
    return { type: ActionTypes.GET_CATEGORIES_FAILED, errors: errors };
}

export function getCategories(token) {
    return dispatch => {
        dispatch(getCategoriesRequest());

        const service = new APIService(token);
        return service.getCollection(APIEndpoints.COLLECTION)
            .then(response => dispatch(getCategoriesResponse(response.data)))
            .catch(errors => dispatch(getCategoriesFailed(errors.data)));
    };
}


function createCategoryRequest(payload) {
    return { type: ActionTypes.CREATE_CATEGORY_REQUEST, payload: payload };
}

function createCategoryResponse(json) {
    return { type: ActionTypes.CREATE_CATEGORY_RESPONSE, category: json.category };
}

function createCategoryFailed(payload, errors) {
    return { type: ActionTypes.CREATE_CATEGORY_FAILED, payload: payload, errors: errors };
}

export function createCategory(token, payload) {
    return dispatch => {
        dispatch(createCategoryRequest(payload));

        const service = new APIService(token);
        return service.createResource(APIEndpoints.COLLECTION, payload)
            .then(response => dispatch(createCategoryResponse(response.data)))
            .catch(errors => dispatch(createCategoryFailed(payload, errors.data)));
    };
}


function editCategoryRequest(category, payload) {
    return { type: ActionTypes.EDIT_CATEGORY_REQUEST, payload: payload, category: category };
}

function editCategoryResponse(category, json) {
    return { type: ActionTypes.EDIT_CATEGORY_RESPONSE, categoryId: category.id,
             category: json.category };
}

function editCategoryFailed(category, payload, errors) {
    return { type: ActionTypes.EDIT_CATEGORY_FAILED, errors: errors,
             payload: payload, category: category };
}

export function editCategory(token, category, payload) {
    return dispatch => {
        dispatch(editCategoryRequest(category, payload));

        const service = new APIService(token);
        return service.editResource(APIEndpoints.RESOURCE.replace('{id}', category.id), payload)
            .then(response => dispatch(editCategoryResponse(category, response.data)))
            .catch(errors => dispatch(editCategoryFailed(category, payload, errors.data)));
    };
}


function removeCategoryRequest(category) {
    return { type: ActionTypes.REMOVE_CATEGORY_REQUEST, category: category };
}

function removeCategoryResponse(category) {
    return { type: ActionTypes.REMOVE_CATEGORY_RESPONSE, category: category };
}

function removeCategoryFailed(category, errors) {
    return { type: ActionTypes.REMOVE_CATEGORY_FAILED, category: category, errors: errors };
}

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
