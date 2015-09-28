import { ActionTypes } from 'js/constants/categories';
import CategoriesService from 'js/services/categories';


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
