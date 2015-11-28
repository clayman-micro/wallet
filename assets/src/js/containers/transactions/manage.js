import React from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';
import { pushState } from 'redux-router';
import Icon from 'react-fa';

import { getAccountsIfNeeded } from '../../actions/accounts';
import { getCategoriesIfNeeded } from '../../actions/categories';
import { getTransaction, createTransaction, editTransaction, removeTransaction } from '../../actions/transactions';

import { StatusChoices } from '../../constants/status';

import Page from '../../components/common/page';
import ManageForm from '../../components/transactions/manage';


class ManageTransaction extends React.Component {
    componentWillMount() {
        this.props.getAccountsIfNeeded();
        this.props.getCategoriesIfNeeded();

        const { instanceID } = this.props.routerState.params;
        if (typeof instanceID !== 'undefined') {
            this.props.getTransaction({ id: instanceID });
        }
    }

    componentWillReceiveProps(nextProps) {
        const { status } = nextProps.transactions;
        if (status === StatusChoices.CREATE_DONE || status === StatusChoices.REMOVE_DONE) {
            setTimeout(() => {
                this.props.pushState('', '/transactions');
            }, 250);
        }
    }

    handleRemove(transaction, event) {
        event.preventDefault();
        this.props.removeTransaction(transaction);
    }

    handleSubmit(transaction, payload) {
        if (Object.keys(transaction).length) {
            this.props.editTransaction(transaction, payload);
        } else {
            this.props.createTransaction(payload);
        }
    }

    getInstanceID() {
        const { instanceID } = this.props.routerState.params;
        return typeof instanceID !== 'undefined' ? parseInt(instanceID, 10) : 0;
    }

    getTransaction() {
        let transaction = {};
        const instanceID = this.getInstanceID();

        if (instanceID) {
            transaction = this.props.transactions.items.find(item => item.id === instanceID);
            if (typeof transaction === 'undefined') {
                transaction = {};
            }
        }

        return transaction;
    }

    render() {
        const { accounts, categories, transactions } = this.props;
        const instanceID = this.getInstanceID();
        let transaction = this.getTransaction();

        let title = 'Add transaction';
        let rightButton = {};
        const leftButton = {
            text: (<span><Icon name="chevron-left" /></span>),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/transactions'
        };

        if (instanceID) {
            title = 'Edit transaction';
            rightButton = {
                text: (<Icon name="trash-o" />),
                style: { fontSize: '20px', padding: '13px 0' },
                path: '#',
                handle: this.handleRemove.bind(this, transaction)
            };
        }

        const style = { margin: '10px', display: 'block', borderBottom: 'none' };

        return (
            <Page title={title} leftLink={leftButton} rightLink={rightButton} >
                { Object.keys(transaction).length ?
                    <Link style={style} to={'/transactions/' + transaction.id + '/details'}>Details</Link> : ''}
                <ManageForm
                    accounts={accounts}
                    categories={categories}
                    transactions={transactions}
                    transaction={transaction}
                    submitHandler={this.handleSubmit.bind(this, transaction)}
                />
            </Page>
        );
    }
}

ManageTransaction.propTypes = {
    // Props from Store
    accounts: React.PropTypes.object.isRequired,
    categories: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,
    transactions: React.PropTypes.object.isRequired,

    // Action creators
    pushState: React.PropTypes.func.isRequired,

    getAccountsIfNeeded: React.PropTypes.func.isRequired,
    getCategoriesIfNeeded: React.PropTypes.func.isRequired,

    getTransaction: React.PropTypes.func.isRequired,
    createTransaction: React.PropTypes.func.isRequired,
    editTransaction: React.PropTypes.func.isRequired,
    removeTransaction: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        accounts: state.accounts,
        categories: state.categories,
        routerState: state.router,
        transactions: state.transactions
    };
}

const mapDispatchToProps = {
    pushState,
    getAccountsIfNeeded,
    getCategoriesIfNeeded,
    getTransaction, createTransaction, editTransaction, removeTransaction
};

export default connect(mapStateToProps, mapDispatchToProps)(ManageTransaction);
