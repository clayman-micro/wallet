import { ActionTypes } from 'js/constants/categories';


const initialState = {
    isFetching: false,
    items: [{
        id: 0,
        name: 'Use Redux'
    }],
    errors: []
};

function categoriesCollection(state = initialState, action) {
    if (action.type === ActionTypes.GET_CATEGORIES_REQUEST) {
        return Object.assign({}, state, {
            isFetching: true
        });
    } else if (action.type === ActionTypes.GET_CATEGORIES_RESPONSE) {
        return Object.assign({}, state, {
            isFetching: false,
            items: [...state.items, ...action.categories],
            errors: []
        });
    } else if (action.type === ActionTypes.GET_CATEGORIES_FAILED) {
        return Object.assign({}, state, { isFetching: false, errors: action.errors });
    } else if (action.type === ActionTypes.ADD_CATEGORY) {
        return Object.assign({}, state, [{
            id: state.reduce((maxId, category) => Math.max(category.id, maxId), -1 ) + 1,
            name: action.name
        }, ...state]);
    } else if (action.type === ActionTypes.EDIT_CATEGORY) {
        return Object.assign({}, state, state.map(category =>
            category.id === action.id ?
                Object.assign({}, category, { name: action.name }) : category)
        );
    } else if (action.type === ActionTypes.DELETE_CATEGORY) {
        return Object.assign({}, state, state.filter(category =>
            category.id !== action.id
        ));
    }

    return state;
}


export default function categories(state = initialState, action) {
    if (action.type === ActionTypes.ADD_CATEGORY) {
        return Object.assign({}, state, [{
            id: state.reduce((maxId, category) => Math.max(category.id, maxId), -1 ) + 1,
            name: action.name
        }, ...state]);
    } else if (action.type === ActionTypes.EDIT_CATEGORY) {
        return Object.assign({}, state, state.map(category =>
            category.id === action.id ?
                Object.assign({}, category, { name: action.name }) : category)
        );
    } else if (action.type === ActionTypes.DELETE_CATEGORY) {
        return Object.assign({}, state, state.filter(category =>
            category.id !== action.id
        ));
    }

    return state;
}

export default categoriesCollection;
