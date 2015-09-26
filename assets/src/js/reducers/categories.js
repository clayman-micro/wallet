import { ActionTypes } from 'js/constants/Categories';

const initialState = [{
    id: 0,
    name: 'Use Redux'
}];


export default function categories(state = initialState, action) {
    switch (action.type) {
    case (ActionTypes.ADD_CATEGORY):
        return [{
            id: state.reduce((maxId, category) => Math.max(category.id, maxId), -1 ) + 1,
            name: action.name
        }, ...state];

    case (ActionTypes.DELETE_CATEGORY):
        return state.filter(category =>
            category.id !== action.id
        );

    case (ActionTypes.EDIT_CATEGORY):
        return state.map(category =>
            category.id === action.id ?
                Object.assign({}, category, { name: action.name }) :
                category
        );

    default:
        return state;
    }
}
