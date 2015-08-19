import React from 'react';
import { Link } from 'react-router';

import SessionStore from '../stores/SessionStore';
import AuthService from '../services/AuthService';


let getLoginState = function () {
    return {
        userLoggedIn: SessionStore.isLoggedIn()
    };
};

export default class App extends React.Component {
    constructor(props) {
        super(props);

        this.state = getLoginState();
        this.onChange = this.onChange.bind(this);
    }

    componentDidMount() {
        SessionStore.addChangeListener(this.onChange);
    }

    componentWillUnmount() {
        SessionStore.removeChangeListener(this.onChange);
    }

    logout(event) {
        event.preventDefault();
        AuthService.logout();
    }

    onChange() {
        this.setState(getLoginState());
    }

    get headerItems() {
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
    }

    render() {
        return (
            <div className="container">
                <nav className="navbar navbar-default">
                    <div className="navbar-header">
                        <a className="navbar-brand" href="/">React Flux app </a>
                    </div>
                    {this.headerItems}
                </nav>
                <h1>App root</h1>
                {this.props.children}
            </div>
        );
    }
}
