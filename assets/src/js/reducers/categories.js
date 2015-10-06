import { ActionTypes } from '../constants/categories';


const initialState = {
    isFetching: false,
    items: [],
    errors: {}
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

function createCategory(state = initialState, action) {
    if (action.type === ActionTypes.CREATE_CATEGORY_REQUEST) {
        return Object.assign({}, state, {
            isFetching: true
        });
    } else if (action.type === ActionTypes.CREATE_CATEGORY_RESPONSE) {
        return Object.assign({}, state, {
            items: [action.category, ...state.items],
            isFetching: false,
            errors: []
        });
    } else if (action.type === ActionTypes.CREATE_CATEGORY_FAILED) {
        return Object.assign({}, state, {
            isFetching: false,
            errors: action.errors
        });
    }

    return state;
}


function editCategory(state = initialState, action) {
    if (action.type === ActionTypes.EDIT_CATEGORY_REQUEST) {
        return Object.assign({}, state, {
            isFetching: true
        });
    } else if (action.type === ActionTypes.EDIT_CATEGORY_RESPONSE) {
        console.log(action);
        return Object.assign({}, state, {
            items: state.items.map(category =>
                category.id === action.category.id ?
                    Object.assign({}, category, action.category) : category),
            isFetching: false,
            errors: []
        });
    } else if (action.type === ActionTypes.EDIT_CATEGORY_FAILED) {
        return Object.assign({}, state, {
            isFetching: false,
            errors: action.errors
        });
    }

    return state;
}


function removeCategory(state = initialState, action) {
    if (action.type === ActionTypes.REMOVE_CATEGORY_REQUEST) {
        return Object.assign({}, state, {
            isFetching: true
        });
    } else if (action.type === ActionTypes.REMOVE_CATEGORY_RESPONSE) {
        return Object.assign({}, state, { items: state.items.filter(category =>
            category.id !== action.id
        )});
    } else if (action.type === ActionTypes.REMOVE_CATEGORY_FAILED) {
        return Object.assign({}, state, {
            isFetching: false,
            errors: action.errors
        });
    }

    return state;
}

//function categories(state = initialState, action) {
//    if (action.type === ActionTypes.ADD_CATEGORY) {
//        return Object.assign({}, state, [{
//            id: state.reduce((maxId, category) => Math.max(category.id, maxId), -1 ) + 1,
//            name: action.name
//        }, ...state]);
//    } else if (action.type === ActionTypes.EDIT_CATEGORY) {
//        return Object.assign({}, state, state.map(category =>
//            category.id === action.id ?
//                Object.assign({}, category, { name: action.name }) : category)
//        );
//    } else if (action.type === ActionTypes.DELETE_CATEGORY) {
//        return Object.assign({}, state, state.filter(category =>
//            category.id !== action.id
//        ));
//    }
//
//    return state;
//}

export default function categories(state = initialState, action) {
    let newState = categoriesCollection(state, action);
    newState = createCategory(newState, action);
    newState = editCategory(newState, action);
    newState = removeCategory(newState, action);
    return newState;
};
