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
        getCollectionRequest: state => Object.assign({}, state, { isFetching: true }),
        getCollectionResponse: (state, action) => Object.assign({}, state, {
            isFetching: false, items: [...action.json.collection], errors: {} }),
        getCollectionFailed: (state, action) => Object.assign({}, state, {
            isFetching: false, errors: action.errors }),

        getResourceRequest: state => Object.assign({}, state, { isFetching: true }),
        getResourceResponse: (state, action) => Object.assign({}, state,
            { isFetching: false, items: [...state.items, action.json.resource], errors: {} }),
        getResourceFailed: (state, action) => Object.assign({}, state,
            { isFetching: false, errors: action.errors }),

        createResourceRequest: state => Object.assign({}, state, { isFetching: true }),
        createResourceResponse: (state, action) => Object.assign({}, state, {
            isFetching: false,
            items: [...state.items, action.json.resource],
            errors: {}
        }),
        createResourceFailed: (state, action) => Object.assign({}, state,
            { isFetching: false, errors: action.errors }),

        editResourceRequest: state => Object.assign({}, state, { isFetching: true }),
        editResourceResponse: (state, action) => Object.assign({}, state, {
            isFetching: false,
            items: state.items.map(resource =>
                resource.id === action.json.resource.id ?
                    Object.assign({}, resource, action.json.resource) : resource),
            errors: {}
        }),
        editResourceFailed: (state, action) => Object.assign({}, state,
            { isFetching: false, errors: action.errors }),

        removeResourceRequest: state => Object.assign({}, state, { isFetching: true }),
        removeResourceResponse: (state, action) => Object.assign({}, state, {
            isFetching: false,
            items: state.items.filter(resource => resource.id !== action.resource.id),
            errors: {}
        }),
        removeResourceFailed: (state, action) => Object.assign({}, state, {
            isFetching: false, errors: action.errors })
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
