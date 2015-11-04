import React from 'react';
import Icon from 'react-fa';

import { StatusChoices } from '../../constants/status';


class ManagePage extends React.Component {
    constructor(props) {
        super(props);

        this.doneRedirect = '/';
        this.leftLinkPath = '/';
        this.rightLinkPath = '/';
    }

    componentWillReceiveProps(nextProps) {
        const { status } = nextProps.collection;
        const doneStatuses = [
            StatusChoices.CREATE_DONE,
            StatusChoices.EDIT_DONE,
            StatusChoices.REMOVE_DONE
        ];

        if (doneStatuses.indexOf(status) !== -1) {
            setTimeout(() => {
                this.props.pushState('', this.doneRedirect);
            });
        }
    }

    handleSubmit(instance, payload) {
        if (Object.keys(instance).length) {
            this.props.editAction(instance, payload);
        } else {
            this.props.createAction(payload);
        }
    }

    handleRemove(instance, event) {
        event.preventDefault();
        this.props.removeAction(instance);
    }

    getInstanceID() {
        const { instanceID } = this.props.routerState.params;
        return typeof instanceID !== 'undefined' ? parseInt(instanceID, 10) : 0;
    }

    getInstance() {
        let instance = {};
        const instanceID = this.getInstanceID();

        if (instanceID) {
            instance = this.props.collection.items.find(item => item.id === instanceID);
            if (typeof instance === 'undefined') {
                instance = {};
            }
        }

        return instance;
    }

    getLeftLink() {
        return {
            text: (<Icon name="chevron-left" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: this.leftLinkPath
        };
    }

    getRightLink(instance) {
        return {
            text: (<Icon name="trash-o" />),
            style: { fontSize: '20px', padding: '13px 0' },
            path: '#',
            handle: this.handleRemove.bind(this, instance)
        };
    }
}

ManagePage.propTypes = {
    // Props from Store
    collection: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,

    // Action creators
    pushState: React.PropTypes.func.isRequired,
    createAction: React.PropTypes.func.isRequired,
    editAction: React.PropTypes.func.isRequired,
    removeAction: React.PropTypes.func.isRequired
};

export default ManagePage;
