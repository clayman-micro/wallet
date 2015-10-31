import React from 'react';
import { connect } from 'react-redux';
import { pushState } from 'redux-router';
import Icon from 'react-fa';

import { getAccountsIfNeeded, createAccount, editAccount, removeAccount } from '../../actions/accounts';

import { StatusChoices } from '../../constants/status';

import Page from '../../components/common/page';
import ManageForm from '../../components/accounts/manage';


class ManageAccount extends React.Component {
    componentWillMount() {
        this.props.getAccountsIfNeeded();
    }

    componentWillReceiveProps(nextProps) {
        const { status } = nextProps.accounts;
        const doneStatues = [
            StatusChoices.CREATE_DONE,
            StatusChoices.EDIT_DONE,
            StatusChoices.REMOVE_DONE
        ];

        if (doneStatues.indexOf(status) !== -1) {
            setTimeout(() => {
                this.props.pushState('', '/accounts');
            }, 250);
        }
    }

    handleSubmit(account, payload) {
        if (Object.keys(account).length) {
            this.props.editAccount(account, payload);
        } else {
            this.props.createAccount(payload);
        }
    }

    handleRemove(account, event) {
        event.preventDefault();
        this.props.removeAccount(account);
    }

    getInstanceID() {
        const { instanceID } = this.props.routerState.params;
        return typeof instanceID !== 'undefined' ? parseInt(instanceID, 10) : 0;
    }

    getAccount() {
        let account = {};
        const instanceID = this.getInstanceID();

        if (instanceID) {
            account = this.props.accounts.items.find(item => item.id === instanceID);
            if (typeof account === 'undefined') {
                account = {};
            }
        }

        return account;
    }

    render() {
        const instanceID = this.getInstanceID();
        let account = this.getAccount();

        let title = 'Add account';
        let rightLink = {};
        const leftLink = {
            text: (<Icon name="chevron-left" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/accounts'
        };

        if (instanceID) {
            title = 'Edit account';
            rightLink = {
                text: (<Icon name="trash-o" />),
                style: { fontSize: '20px', padding: '13px 0' },
                path: '#',
                handle: this.handleRemove.bind(this, account)
            };
        }

        return (
            <Page title={title} leftLink={leftLink} rightLink={rightLink} >
                <ManageForm
                    accounts={this.props.accounts}
                    account={account}
                    submitHandler={this.handleSubmit.bind(this, account)}
                />
            </Page>
        );
    }
}

ManageAccount.propTypes = {
    // Props from Store
    accounts: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,

    // Action creators
    pushState: React.PropTypes.func.isRequired,

    getAccountsIfNeeded: React.PropTypes.func.isRequired,
    createAccount: React.PropTypes.func.isRequired,
    editAccount: React.PropTypes.func.isRequired,
    removeAccount: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        accounts: state.accounts,
        routerState: state.router
    };
}

const mapDispatchToProps = {
    pushState,
    getAccountsIfNeeded, createAccount, editAccount, removeAccount
};

export default connect(mapStateToProps, mapDispatchToProps)(ManageAccount);
