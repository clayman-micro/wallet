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
            <div className="layout">
                <aside className="layout__sidebar sidebar">
                    <div className="sidebar__header">Wallet</div>
                    <ul className="sidebar__menu menu">
                        <li className="menu__item">
                            <a href="#" className="menu__link">
                                <span><i className="fa fa-money"></i>Accounts</span>
                            </a>
                            <ul className="menu menu_mod_sub">
                                <li className="menu__item">
                                    <div>Deposit</div>
                                    <div>123<span className="half-space"></span>345 ₽</div>
                                </li>
                                <li className="menu__item">
                                    <div>Cash</div>
                                    <div>123<span className="half-space"></span>345 ₽</div>
                                </li>
                                <li className="menu__item">
                                    <div>Visa Classic</div>
                                    <div>123<span className="half-space"></span>345 ₽</div>
                                </li>
                            </ul>
                        </li>
                        <li className="menu__item">
                            <a href="#" className="menu__link">
                                <span><i className="fa fa-calendar"></i>Scheduled</span>
                            </a>
                        </li>
                        <li className="menu__item">
                            <a href="#" className="menu__link">
                                <span><i className="fa fa-area-chart"></i>Reports</span>
                            </a>
                        </li>
                        <li className="menu__item">
                            <a href="#" className="menu__link">
                                <span><i className="fa fa-cog"></i>Settings</span>
                            </a>
                        </li>
                    </ul>
                </aside>
                <section className="layout__content">
                    <header className="header">
                        <div className="header__row">
                            <ul className="breadcrumbs">
                                <li className="breadcrumbs__item">
                                    <a href="#" className="breadcrumbs__link">Home</a>
                                </li>
                                <li className="breadcrumbs__item">
                                    <a href="#" className="breadcrumbs__link">Accounts</a>
                                </li>
                                <li className="breadcrumbs__item">
                                    Cash
                                </li>
                            </ul>
                            <ul className="menu menu_mod_inline push-right">
                                <li className="menu__item menu__item_mod_inline">
                                    <a href="#" className="menu__link">clayman74@gmail.com</a>
                                </li>
                                <li className="menu__item menu__item_mod_inline">
                                    <a href="#" className="menu__link">
                                        Logout <i className="fa fa-sign-out"></i>
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div className="header__row">

                        </div>
                    </header>
                    <div className="content">
                        {this.props.children}
                    </div>
                </section>
            </div>
        );
    }
});
