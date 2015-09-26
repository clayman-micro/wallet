import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';


class App extends Component {
    render() {
        return (
            <div>
                <h1>App container</h1>
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
