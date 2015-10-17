import { StatusChoices } from '../constants/status';

export function createReducer(initialState, handlers) {
    return function reducer(state = initialState, action = {}) {
        if (handlers.hasOwnProperty(action.type)) {
            return handlers[action.type](state, action);
        }

        return state;
    };
}

export function createCRUDReducer(initialState, mapHandlersToActions, extraHandlers) {
    let baseHandlers = {
        getCollectionRequest: state => Object.assign({}, state, {
            status: StatusChoices.FETCHING }),
        getCollectionResponse: (state, action) => Object.assign({}, state, {
            items: [...action.json.collection], errors: {}, status: StatusChoices.FETCH_DONE }),
        getCollectionFailed: (state, action) => Object.assign({}, state, {
            errors: action.errors, status: StatusChoices.FAILED }),

        getResourceRequest: state => Object.assign({}, state, { }),
        getResourceResponse: (state, action) => Object.assign({}, state,
            { items: [...state.items, action.json.resource], errors: {} }),
        getResourceFailed: (state, action) => Object.assign({}, state,
            { isFetching: false, errors: action.errors }),

        createResourceRequest: state => Object.assign({}, state, {
            status: StatusChoices.CREATING }),
        createResourceResponse: (state, action) => Object.assign({}, state, {
            status: StatusChoices.CREATE_DONE,
            items: [...state.items, action.json.resource],
            errors: {}
        }),
        createResourceFailed: (state, action) => Object.assign({}, state,
            { errors: action.errors, status: StatusChoices.FAILED }),

        editResourceRequest: state => Object.assign({}, state, {
            status: StatusChoices.EDITING }),
        editResourceResponse: (state, action) => Object.assign({}, state, {
            status: StatusChoices.EDIT_DONE,
            items: state.items.map(resource =>
                resource.id === action.json.resource.id ?
                    Object.assign({}, resource, action.json.resource) : resource),
            errors: {}
        }),
        editResourceFailed: (state, action) => Object.assign({}, state,
            { errors: action.errors, status: StatusChoices.FAILED }),

        removeResourceRequest: state => Object.assign({}, state, {
            status: StatusChoices.REMOVING }),
        removeResourceResponse: (state, action) => Object.assign({}, state, {
            status: StatusChoices.REMOVE_DONE,
            items: state.items.filter(resource => resource.id !== action.resource.id),
            errors: {}
        }),
        removeResourceFailed: (state, action) => Object.assign({}, state, {
            errors: action.errors, status: StatusChoices.FAILED })
    };

    let handlers = Object.assign({}, baseHandlers, extraHandlers);

    return function reducer(state = initialState, action = {}) {
        if (mapHandlersToActions.hasOwnProperty(action.type)) {
            if (handlers.hasOwnProperty(mapHandlersToActions[action.type])) {
                return handlers[mapHandlersToActions[action.type]](state, action);
            }
        }

        return state;
    };
}
