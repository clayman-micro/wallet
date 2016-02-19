/* global DEBUG */

import { applyMiddleware, createStore, compose } from 'redux';
import { reduxReactRouter } from 'redux-router';
import thunkMiddleware from 'redux-thunk';
import createLogger from 'redux-logger';

import createHistory from 'history/lib/createBrowserHistory';

import rootReducer from '../reducers/index';
import authMiddleware from '../middleware/auth';


const middleware = [thunkMiddleware, authMiddleware];

if (DEBUG) {
    const logger = createLogger();
    middleware.push(logger);
}

export default function configureStore(initialState) {
    const store = compose(
        applyMiddleware(...middleware),
        reduxReactRouter({ createHistory })
    )(createStore)(rootReducer, initialState);

    if (module.hot) {
        // Enable Webpack hot module replacement for reducers
        module.hot.accept('../reducers', () => {
            const nextReducer = require('../reducers');
            store.replaceReducer(nextReducer);
        });
    }

    return store;
}
