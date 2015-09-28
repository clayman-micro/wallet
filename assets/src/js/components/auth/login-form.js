import 'less/form/form.less';

import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import { loginUser } from 'js/actions/session';


class LoginForm extends Component {
    constructor(props, context) {
        super(props, context);

        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            username: '',
            password: '',
            errors: []
        };
    }

    handleSubmit(event) {
        event.preventDefault();

        const username = ReactDOM.findDOMNode(this.refs.username).value.trim();
        const password = ReactDOM.findDOMNode(this.refs.password).value.trim();
        if (!username || !password) {
            this.setState({
                errors: [{
                    type: 'validation',
                    message: 'Wrong username or password'
                }]
            });
            return;
        }

        this.props.loginUser(username, password);
    }

    getUsernameField() {
        let className = 'form__input';
        if (this.state.errors && this.state.errors.username) {
            className = className + ' form__input_error';
        }

        return (
            <div className="form__section">
                <label htmlFor="username" className="form__label">Username</label>
                <input type="text" ref="username" placeholder="Username" className={className} />
            </div>
        );
    }

    getPasswordField() {
        let className = 'form__input';
        if (this.state.errors && this.state.errors.password) {
            className = className + ' form__input_error';
        }

        return (
            <div className="form__section">
                <label htmlFor="password" className="form__label">Password</label>
                <input type="password"
                       ref="password"
                       placeholder="Password"
                       className={className} />
            </div>
        );
    }

    getErrorList() {
        if (this.state.errors) {
            let errors = this.state.errors.map(error => {
                return (<div key={error.type}>{error.message}</div>);
            });

            return (<div className="form__errors">{errors}</div>);
        }
        return '';
    }

    render() {
        return (
            <div className="login">
                <div className="login__wrapper">
                    <div className="login__header">wallet</div>
                    <div className="login__content">
                        <form role="form" className="form form_mod_login">
                            {this.getErrorList()}
                            {this.getUsernameField()}
                            {this.getPasswordField()}
                            <button type="submit"
                                    className="form__submit"
                                    onClick={this.handleSubmit}>
                                Submit
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        );
    }
}


LoginForm.propTypes = {
    session: PropTypes.object.isRequired,
    loginUser: PropTypes.func.isRequired
};


function mapStateToProps(state) {
    return { session: state.session };
}

function mapDispatchToProps(dispatch) {
    return bindActionCreators({ loginUser }, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(LoginForm);
