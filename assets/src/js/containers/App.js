import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';


@connect(state => ({ routerState: state.router }))
class App extends Component {
    static propTypes = {
        routerState: PropTypes.array.isRequired,
        children: PropTypes.node,
        dispatch: PropTypes.func.isRequired
    }

    render() {
        return (
            <div>
                <h1>App container</h1>
                {this.props.children}
            </div>
        );
    }
}

export default App;
