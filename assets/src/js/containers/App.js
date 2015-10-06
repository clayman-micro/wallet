import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';

import Header from '../components/header/header';


class App extends Component {
    render() {
        const links = [
          { id: 1, url: '/accounts', name: 'Accounts' },
          { id: 2, url: '/categories', name: 'Categories' },
          { id: 3, url: '/transactions', name: 'Transactions'}
        ].map(link =>
          <p key={link.id}>
            <Link to={link.url}>{link.name}</Link>
          </p>
        );

        return (
            <div>
                <Header title="Wallet" />
                {links}
                {this.props.children}
            </div>
        );
    }
}


App.propTypes = {
    routerState: PropTypes.object.isRequired,
    children: PropTypes.node,
    dispatch: PropTypes.func.isRequired
};


function mapStateToProps(state) {
    return { routerState: state.router };
}

export default connect(mapStateToProps)(App);
