import React from 'react';
import { Router, Route } from 'react-router';
import { history } from 'react-router/lib/HashHistory';

import App from './components/App';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import SessionStore from './stores/SessionStore';


function requireAuth(nextState, redirect) {
    if (!SessionStore.isLoggedIn()) {
        redirect.to('/login', null,
            { nextPathname: nextState.location.pathname });
    }
}

React.render((
    <Router history={history}>
        <Route path="/" component={App} onEnter={requireAuth}>
            <Route path="dashboard" component={Dashboard} onEnter={requireAuth} />
        </Route>
        <Route path="/login" component={Login} />
    </Router>
), document.getElementById('todoapp'));
