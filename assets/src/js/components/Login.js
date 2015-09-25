import React from 'react';
import { Navigation } from 'react-router';

// import SessionActions from '../actions/SessionActions';
// import SessionStore from '../stores/SessionStore';


let Login = React.createClass({
    mixins: [Navigation],

    getInitialState: function () {
        return {
            user: '',
            password: ''
        };
    },

    componentDidMount: function () {
        // SessionStore.addChangeListener(this.onChange);
    },

    componentWillUnmount: function () {
        // SessionStore.removeChangeListener(this.onChange);
    },

    handleSubmit: function (event) {
        event.preventDefault();

        const username = React.findDOMNode(this.refs.username).value.trim();
        const password = React.findDOMNode(this.refs.password).value.trim();

        if (!username || !password) {
            this.setState({
                errors: ['Wrong username or password']
            });
            return;
        }

        // SessionActions.loginUser(username, password);
    },

    onChange: function () {
        // if (SessionStore.isLoggedIn()) {
        //     this.transitionTo('/');
        // } else {
        //     this.setState({
        //         user: '',
        //         password: '',
        //         // errors: SessionStore.errors
        //     });
        // }
    },

    getUsernameField: function () {
        let className = 'form__input';
        if (this.state.errors && this.state.errors.username) {
            className = className + ' form__input_error';
        }

        return (
            <div className="form__section">
                <label htmlFor="username" className="form__label">Username</label>
                <input
                    type="text"
                    className={className}
                    ref="username"
                    placeholder="Username"
                />
            </div>
        );
    },

    getPasswordField: function () {
        let className = 'form__input';
        if (this.state.errors && this.state.errors.password) {
            className = className + ' form__input_error';
        }

        return (
            <div className="form__section">
                <label htmlFor="password" className="form__label">Password</label>
                <input
                    type="password"
                    className={className}
                    ref="password"
                    placeholder="Password"
                />
            </div>
        );
    },

    getErrorsList: function () {
        if (this.state.errors) {
            let errorsList = [];

            for (let key in this.state.errors) {
                if (this.state.errors.hasOwnProperty(key)) {
                    errorsList.push((<div key={key}>{this.state.errors[key]}</div>));
                }
            }

            return (
                <div className="form__errors">{errorsList}</div>
            );
        }

        return '';
    },

    render() {
        return (
            <div className="login">
                <div className="login__wrapper">
                    <div className="login__header">Wallet</div>
                    <div className="login__content">
                        <form role="form" className="form form_mod_login">
                            {this.getErrorsList()}
                            {this.getUsernameField()}
                            {this.getPasswordField()}
                            <button
                                type="submit"
                                className="form__submit"
                                onClick={this.handleSubmit}
                            >Submit</button>
                        </form>
                    </div>
                </div>
            </div>
        );
    }
});

export default Login;
