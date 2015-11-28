import React from 'react';
import { connect } from 'react-redux';
import Icon from 'react-fa';

import { getCategoriesIfNeeded } from '../../actions/categories';
import { getTransactions } from '../../actions/transactions';

import Page from '../../components/common/page';
import TransactionItem from '../../components/transactions/item';


class TransactionList extends React.Component {
    componentWillMount() {
        this.props.getCategoriesIfNeeded();
        this.props.getTransactions();
    }

    render() {
        const { categories, transactions } = this.props;
        const leftButton = {
            text: (<span><Icon name="chevron-left" /></span>),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/'
        };
        const rightButton = {
            text: (<Icon name="plus" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/transactions/add'
        };

        return (
            <Page title="Transactions" leftButton={leftButton} rightButton={rightButton}>
                <ul className="transactions-list objects-list">
                    { transactions.items.map(transaction =>
                        <TransactionItem
                            key={transaction.id}
                            transaction={transaction}
                            category={categories.items.find(category => category.id === transaction.category_id)}
                        />
                    )}
                </ul>
            </Page>
        );
    }
}

TransactionList.propTypes = {
    // Props from Store
    categories: React.PropTypes.object.isRequired,
    transactions: React.PropTypes.object.isRequired,

    // ActionCreators
    getCategoriesIfNeeded: React.PropTypes.func.isRequired,
    getTransactions: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        categories: state.categories,
        transactions: state.transactions
    };
}

const mapDispatchToProps = {
    getCategoriesIfNeeded,
    getTransactions
};

export default connect(mapStateToProps, mapDispatchToProps)(TransactionList);
