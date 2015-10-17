import 'babel-core/polyfill';
import 'less/app.less';

import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { IndexRoute, Route } from 'react-router';
import { ReduxRouter } from 'redux-router';
import configureStore from './store/configureStore';

import AppRoot from './containers/root';
import HomePage from './containers/home';
import LoginPage from './containers/LoginPage';
import AccountsPage from './containers/AccountsPage';
import CategoriesPage from './containers/CategoriesPage';
import TransactionsPage from './containers/transactions/main';
import TransactionList from './containers/transactions/list';
import AddTransactionPage from './containers/transactions/add';


const store = configureStore();

function requireAuth(nextState, redirect) {
    const session = store.getState().session;
    if (!session.accessToken.value) {
        redirect({}, '/login', { next: nextState.location.pathname });
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
        <div>
            <Provider store={store}>
                <ReduxRouter>
                    <Route path="/" component={AppRoot} onEnter={requireAuth}>
                        <IndexRoute component={HomePage} />
                        <Route path="accounts" component={AccountsPage} />
                        <Route path="categories" component={CategoriesPage} />
                        <Route path="transactions" component={TransactionsPage} >
                            <IndexRoute component={TransactionList} />
                            <Route path="add" component={AddTransactionPage} />
                        </Route>
                    </Route>
                    <Route path="/login" component={LoginPage} onEnter={anonymousOnly} />
                </ReduxRouter>
            </Provider>
        </div>
    );
}

ReactDOM.render(<Root />, document.getElementById('root'));
