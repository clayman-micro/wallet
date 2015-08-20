import React from 'react';

import SessionStore from '../stores/SessionStore';

export default React.createClass({
    getInitialState: function () {
        return {
            user: SessionStore.user
        };
    },

    render: function () {
        return (
            <div>
                <h1>Dashboard {this.state.user ? this.state.user.id : ''}</h1>
            </div>
        );
    }
});
