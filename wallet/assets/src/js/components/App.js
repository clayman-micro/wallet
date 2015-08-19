import React from 'react';
import { Link, Navigation } from 'react-router';

import SessionStore from '../stores/SessionStore';
import AuthService from '../services/AuthService';


let getLoginState = function () {
    return {
        userLoggedIn: SessionStore.isLoggedIn()
    };
};

export default React.createClass({
    mixins: [ Navigation ],

    getInitialState: function () {
        return getLoginState();
    },

    componentDidMount: function () {
        SessionStore.addChangeListener(this.onChange);
    },

    componentWillUnmount: function () {
        SessionStore.removeChangeListener(this.onChange);
    },

    logout: function (event) {
        event.preventDefault();
        AuthService.logout();
    },

    onChange: function () {
        if (!SessionStore.isLoggedIn()) {
            this.transitionTo('login');
        } else {
            this.setState(getLoginState());
        }
    },

    getHeaderItems: function () {
        let headerItems;

        if (!this.state.userLoggedIn) {
            headerItems = (
                <ul className="nav navbar-nav navbar-right">
                    <li>
                        <Link to="login">Login</Link>
                    </li>
                </ul>
            );
        } else {
            headerItems = (
                <ul className="nav navbar-nav navbar-right">
                    <li>
                        <Link to="dashboard">Dashboard</Link>
                    </li>
                    <li>
                        <a href="#" onClick={this.logout}>Logout</a>
                    </li>
                </ul>
            );
        }
        return headerItems;
    },

    render: function () {
        return (
            <div className="container">
                <nav className="navbar navbar-default">
                    <div className="navbar-header">
                        <a className="navbar-brand" href="/">{this.props.appName}</a>
                    </div>
                    {this.getHeaderItems()}
                </nav>
                <h1>App root</h1>
                {this.props.children}
            </div>
        );
    }
});
