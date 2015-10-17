import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { pushState } from 'redux-router';

import { StatusChoices } from '../../constants/status';
import { getAccounts } from '../../actions/accounts';
import { getCategories } from '../../actions/categories';
import { createTransaction } from '../../actions/transactions';

import Header from '../../components/header/header';
import ManageForm from '../../components/transactions/manage-form';


class AddTransactionPage extends Component {
    componentDidMount() {
        this.props.dispatch(getAccounts());
        this.props.dispatch(getCategories());
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.transactions.status === StatusChoices.CREATE_DONE) {
            setTimeout(() => {
                this.props.dispatch(pushState({}, '/transactions'));
            }, 250);
        }
    }

    render() {
        const { accounts, categories, transactions, dispatch } = this.props;
        const actions = bindActionCreators({ createTransaction }, dispatch);

        return (
            <div className="add-transaction-page">
                <Header title="Add transaction" />
                <ManageForm
                    accounts={accounts}
                    categories={categories}
                    errors={transactions.errors}
                    addAction={actions.createTransaction}
                />
            </div>
        );
    }
}


AddTransactionPage.propTypes = {
    accounts: PropTypes.object.isRequired,
    categories: PropTypes.object.isRequired,
    transactions: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return { accounts: state.accounts, categories: state.categories, transactions: state.transactions };
}

export default connect(mapStateToProps)(AddTransactionPage);
