import { ActionTypes, APIEndpoints } from '../constants/categories';
import CategoriesService from '../services/categories';
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

        return CategoriesService.getCollection(token)
            .then(json => dispatch(getCategoriesResponse(json)))
            .catch(error => {
                let errors = {};
                if (typeof error.response !== 'undefined') {
                    if (error.response.status === 400) {
                        error.response.json().then(data => {
                            errors = data;
                        });
                    } else {
                        errors[error.response.status] = error.response.statusText;
                    }
                } else {
                    errors[error.name] = error.message;
                }

                return dispatch(getCategoriesFailed(errors));
            });
    };
}


function createCategoryRequest(name) {
    return { type: ActionTypes.CREATE_CATEGORY_REQUEST, name: name };
}

function createCategoryResponse(json) {
    return { type: ActionTypes.CREATE_CATEGORY_RESPONSE, category: json.category };
}

function createCategoryFailed(errors) {
    return { type: ActionTypes.CREATE_CATEGORY_FAILED, errors: errors };
}

export function createCategory(token, payload) {
    return dispatch => {
        dispatch(createCategoryRequest(payload));

        return CategoriesService.createResource(token, payload)
            .then(json => dispatch(createCategoryResponse(json)))
            .catch(error => {
                let errors = {};
                if (typeof error.response !== 'undefined') {
                    if (error.response.status === 400) {
                        error.response.json().then(data => {
                            errors = data;
                        });
                    } else {
                        errors[error.response.status] = error.response.statusText;
                    }
                } else {
                    errors[error.name] = error.message;
                }

                return dispatch(createCategoryFailed(errors));
            });
    }
}


function editCategoryRequest(payload) {
    return { type: ActionTypes.EDIT_CATEGORY_REQUEST, payload: payload };
}

function editCategoryResponse(categoryId, json) {
    return { type: ActionTypes.EDIT_CATEGORY_RESPONSE, categoryId: categoryId,
             category: json.category };
}

function editCategoryFailed(error) {
    return { type: ActionTypes.EDIT_CATEGORY_FAILED, errors: errors };
}

export function editCategory(token, category, payload) {
    return dispatch => {
        dispatch(editCategoryRequest(category, payload));
        console.log('edit category action', category);
        return CategoriesService.editResource(token, category, payload)
            .then(json => dispatch(editCategoryResponse(category, json)))
            .catch(error => {
                let errors = {};
                if (typeof error.response !== 'undefined') {
                    if (error.response.status === 400) {
                        error.response.json().then(data => {
                            errors = data;
                        });
                    } else {
                        errors[error.response.status] = error.response.statusText;
                    }
                } else {
                    errors[error.name] = error.message;
                }

                return dispatch(editCategoryFailed(errors));
            });
    }
}


function removeCategoryRequest(resourceId) {
    return { type: ActionTypes.REMOVE_CATEGORY_REQUEST, id: resourceId };
}

function removeCategoryResponse(resourceId) {
    return { type: ActionTypes.REMOVE_CATEGORY_RESPONSE, id: resourceId};
}

function removeCategoryFailed(errors) {
    return { type: ActionTypes.REMOVE_CATEGORY_FAILED, errors: errors };
}

export function removeCategory(token, resourceId) {
    return dispatch => {
        dispatch(removeCategoryRequest(resourceId));

        return CategoriesService.removeResource(token, resourceId)
            .then(response => dispatch(removeCategoryResponse(resourceId)))
            .catch(error => {
                let errors = {};
                if (typeof error.response !== 'undefined') {
                    if (error.response.status === 400) {
                        error.response.json().then(data => {
                            errors = data;
                        });
                    } else {
                        errors[error.response.status] = error.response.statusText;
                    }
                } else {
                    errors[error.name] = error.message;
                }

                return dispatch(removeCategoryFailed(errors));
            });
    }
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
