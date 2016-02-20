import React from 'react';
import { connect } from 'react-redux';
import { push } from 'react-router-redux';

import { getAccountsIfNeeded, createAccount, editAccount, removeAccount } from '../../actions/accounts';

import ManagePage from '../common/manage';
import Page from '../../components/common/page';
import ManageForm from '../../components/accounts/manage';


class ManageAccount extends ManagePage {
    constructor(props) {
        super(props);

        this.doneRedirect = '/accounts';
        this.leftLinkPath = '/accounts';
    }

    componentWillMount() {
        this.props.getAccountsIfNeeded();
    }

    render() {
        const instanceID = this.getInstanceID();
        let instance = this.getInstance();

        let title = 'Add account';
        let rightButton = {};
        if (instanceID) {
            title = 'Edit account';
            rightButton = this.getRightLink(instance);
        }

        return (
            <Page title={title} leftButton={this.getLeftLink()} rightButton={rightButton} >
                <ManageForm
                    collection={this.props.collection}
                    instance={instance}
                    submitHandler={this.handleSubmit.bind(this, instance)}
                />
            </Page>
        );
    }
}

ManageAccount.propTypes = {
    // Props from Store
    collection: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,

    // Action creators
    pushState: React.PropTypes.func.isRequired,

    getAccountsIfNeeded: React.PropTypes.func.isRequired,
    createAction: React.PropTypes.func.isRequired,
    editAction: React.PropTypes.func.isRequired,
    removeAction: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        collection: state.accounts,
        routerState: state.router
    };
}

const mapDispatchToProps = {
    pushState: push,
    getAccountsIfNeeded,
    createAction: createAccount,
    editAction: editAccount,
    removeAction: removeAccount
};

export default connect(mapStateToProps, mapDispatchToProps)(ManageAccount);
