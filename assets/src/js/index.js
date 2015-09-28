import 'babel-core/polyfill';
import 'less/app.less';

import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { Route } from 'react-router';
import { ReduxRouter } from 'redux-router';
import configureStore from './store/configureStore';
// import { DevTools, DebugPanel, LogMonitor } from 'redux-devtools/lib/react';

import App from 'js/containers/App';
import LoginPage from 'js/containers/LoginPage';
import CategoriesPage from 'js/containers/CategoriesPage';
import Accounts from 'js/components/accounts/Accounts';


const store = configureStore();

function requireAuth(nextState, redirect) {
    const session = store.getState().session;
    if (!session.user) {
        redirect({}, '/login', { next: nextState.location.pathname });
    }
}

function anonymousOnly(nextState, redirect) {
    const session = store.getState().session;
    if (session.isAuthenticated) {
        redirect({}, '/');
    }
}


class Root extends Component {
    render() {
        return (
            <div>
                <Provider store={store}>
                    <ReduxRouter>
                        <Route path="/" component={App} onEnter={requireAuth}>
                            <Route path="accounts" components={Accounts} />
                            <Route path="categories" components={CategoriesPage} />
                        </Route>
                        <Route path="/login" components={LoginPage} onEnter={anonymousOnly} />
                    </ReduxRouter>
                </Provider>
            </div>
        );
    }
}

ReactDOM.render(<Root />, document.getElementById('root'));