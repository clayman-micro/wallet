import { combineReducers } from 'redux';
import { routerStateReducer } from 'redux-router';

import session from './session';
import categories from './categories';


const rootReducer = combineReducers({
    router: routerStateReducer,
    session: session,
    categories: categories
});

export default rootReducer;
