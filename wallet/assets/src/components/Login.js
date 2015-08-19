import React from 'react';
import { Navigation } from 'react-router';

import SessionActions from '../actions/SessionActions';
import SessionStore from '../stores/SessionStore';


let Login = React.createClass({
    mixins: [Navigation],

    getInitialState: function () {
        return {
            user: '',
            password: ''
        };
    },

    componentDidMount: function () {
        SessionStore.addChangeListener(this.onChange);
    },

    componentWillUnmount: function () {
        SessionStore.removeChangeListener(this.onChange);
    },

    handleSubmit: function (event) {
        event.preventDefault();

        const username = React.findDOMNode(this.refs.username).value.trim();
        const password = React.findDOMNode(this.refs.password).value.trim();

        if (!username || !password) {
            return;
        }

        SessionActions.loginUser(username, password);
    },

    onChange: function () {
        if (SessionStore.isLoggedIn()) {
            this.transitionTo('dashboard');
        }
    },

    render() {
        return (
            <div className="login">
                <h1>Login</h1>
                <form role="form">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            className="form-control"
                            ref="username"
                            placeholder="Username"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            className="form-control"
                            ref="password"
                            placeholder="Password"
                        />
                    </div>
                    <button
                        type="submit"
                        className="btn btn-default"
                        onClick={this.handleSubmit}
                    >Submit</button>
                </form>
            </div>
        );
    }
});

export default Login;
