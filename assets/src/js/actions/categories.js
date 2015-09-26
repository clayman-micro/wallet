import { ActionTypes } from 'js/constants/Categories';

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
