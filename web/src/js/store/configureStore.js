/* global DEBUG */

import { applyMiddleware, createStore, compose } from 'redux';

import { browserHistory } from 'react-router';
import { syncHistory } from 'react-router-redux';

import thunkMiddleware from 'redux-thunk';
import createLogger from 'redux-logger';

import rootReducer from '../reducers/index';
import authMiddleware from '../middleware/auth';


const reduxRouterMiddleware = syncHistory(browserHistory);
const middleware = [thunkMiddleware, authMiddleware, reduxRouterMiddleware];

if (DEBUG) {
    const logger = createLogger();
    middleware.push(logger);
}

export default function configureStore(initialState) {
    const store = compose(
        applyMiddleware(...middleware)
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
