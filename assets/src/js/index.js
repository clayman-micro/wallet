import 'babel-core/polyfill';

import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { Route } from 'react-router';
import { ReduxRouter } from 'redux-router';
import configureStore from './store/configureStore';
import { DevTools, DebugPanel, LogMonitor } from 'redux-devtools/lib/react';

import App from './containers/App';
import Accounts from './components/Accounts';
import Categories from './components/Categories';
import Login from './components/Login';


const store = configureStore();

function requireAuth(nextState, redirect) {
    const state = store.getState().session;
    if (!state.user) {
        redirect({ nextPathname: nextState.location.pathname }, '/login');
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
                            <Route path="categories" components={Categories} />
                        </Route>
                        <Route path="/login" components={Login} />
                    </ReduxRouter>
                </Provider>
                <DebugPanel top right bottom>
                    <DevTools store={store} monitor={LogMonitor} />
                </DebugPanel>
            </div>
        );
    }
}

ReactDOM.render(<Root />, document.getElementById('root'));
