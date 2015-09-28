import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';

import LoginForm from 'js/components/auth/login-form';


class LoginPage extends Component {
    render() {
        return (
            <div>
                <LoginForm />
            </div>
        );
    }
}


LoginPage.propTypes = {
    routerState: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired
};


function mapStateToProps(state) {
    return { routerState: state.router };
}

export default connect(mapStateToProps)(LoginPage);
