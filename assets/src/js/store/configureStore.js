import { applyMiddleware, createStore, compose } from 'redux';
import { reduxReactRouter } from 'redux-router';
import thunkMiddleware from 'redux-thunk';

import { devTools } from 'redux-devtools';
import createHistory from 'history/lib/createBrowserHistory';

import rootReducer from '../reducers';
import authMiddleware from '../middleware/auth';


const middleware = [thunkMiddleware, authMiddleware];


export default function configureStore(initialState) {
    const store = compose(
        applyMiddleware(...middleware),
        reduxReactRouter({ createHistory }),
        devTools()
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
