import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from '../../actions/transactions';

import Header from '../../components/header/header';
import TransactionItem from '../../components/transactions/item';


class TransactionList extends Component {
    componentDidMount() {
        this.props.dispatch(actions.getTransactions());
    }

    render() {
        const { transactions, dispatch } = this.props;
        const actionCreators = bindActionCreators(actions, dispatch);

        return (
            <div>
                <Header title="Transactions" rightLink={{ text: 'Add', path: '/transactions/add' }} />
                <ul className="transactions-list">
                    { transactions.items.map(transaction =>
                        <TransactionItem key={transaction.id} transaction={transaction} {...actionCreators} />
                    )}
                </ul>
            </div>
        );
    }
}

TransactionList.propTypes = {
    transactions: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired,
    children: PropTypes.node
};

function mapStateToProps(state) {
    return { transactions: state.transactions };
}

export default connect(mapStateToProps)(TransactionList);
