import 'babel-polyfill';
import 'less/app.less';

import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { IndexRoute, Route, Router, browserHistory } from 'react-router';
import configureStore from './store/configureStore';

import AppRoot from './containers/root';
import HomePage from './containers/home';
import Wrapper from './containers/base';
import LoginPage from './containers/LoginPage';

import AccountsList from './containers/accounts/list';
import ManageAccount from './containers/accounts/manage';

import CategoriesList from './containers/categories/list';
import ManageCategory from './containers/categories/manage';

import TransactionList from './containers/transactions/list';
import ManageTransaction from './containers/transactions/manage';

import DetailsList from './containers/details/list';
import ManageDetail from './containers/details/manage';

const store = configureStore();

function requireAuth(nextState, replace) {
    const session = store.getState().session;
    if (!session.accessToken.value) {
        replace({
            pathname: '/login',
            state: { nextPathname: nextState.location.pathname }
        });
    }
}

function anonymousOnly(nextState, redirect) {
    const session = store.getState().session;
    if (session.isAuthenticated) {
        redirect({}, '/');
    }
}


function Root() {
    return (
        <Provider store={store}>
            <Router history={browserHistory}>
                <Route path="/" component={AppRoot} onEnter={requireAuth}>
                    <IndexRoute component={HomePage} />
                    <Route path="accounts" component={Wrapper}>
                        <IndexRoute component={AccountsList} />
                        <Route path="add" component={ManageAccount} />
                        <Route path=":instanceID" component={ManageAccount} />
                    </Route>

                    <Route path="categories" component={Wrapper}>
                        <IndexRoute component={CategoriesList} />
                        <Route path="add" component={ManageCategory} />
                        <Route path=":instanceID" component={ManageCategory} />
                    </Route>

                    <Route path="transactions" component={Wrapper} >
                        <IndexRoute component={TransactionList} />
                        <Route path="add" component={ManageTransaction} />
                        <Route path=":instanceID" component={ManageTransaction} />
                        <Route path=":transactionID/details" component={DetailsList} />
                        <Route path=":transactionID/details/add" component={ManageDetail} />
                        <Route path=":transactionID/details/:instanceID" component={ManageDetail} />
                    </Route>
                </Route>
                <Route path="/login" component={LoginPage} onEnter={anonymousOnly} />
            </Router>
        </Provider>
    );
}

ReactDOM.render(<Root />, document.getElementById('root'));
