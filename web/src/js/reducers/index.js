import { combineReducers } from 'redux';
import { routeReducer } from 'react-router-redux';

import session from './session';
import accounts from './accounts';
import categories from './categories';
import transactions from './transactions';
import details from './details';


const rootReducer = combineReducers({
    router: routeReducer, session, accounts, categories, transactions, details
});

export default rootReducer;
