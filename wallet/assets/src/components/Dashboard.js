import React from 'react';

import SessionStore from '../stores/SessionStore';

export default class Dashboard extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            user: SessionStore.user
        };
    }

    render() {
        return (
            <div>
                <h1>Dashboard {this.state.user ? this.state.user.id : ''}</h1>
            </div>
        );
    }
}
