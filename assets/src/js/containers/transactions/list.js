import React from 'react';
import { connect } from 'react-redux';

import { getCategoriesIfNeeded } from '../../actions/categories';
import { getTransactions } from '../../actions/transactions';

import TransactionItem from '../../components/transactions/item';
import List from '../common/list';


class TransactionList extends List {
    constructor(props) {
        super(props);

        this.title = 'Transactions';
        this.rightButtonPath = '/transactions/add';
    }

    componentWillMount() {
        super.componentWillMount();

        this.props.getCategoriesIfNeeded();
    }

    getObjects() {
        const { categories } = this.props;

        let objects = '';
        if (categories.items.length) {
            objects = this.props.collection.items.map(item => {
                return (
                    <TransactionItem
                        key={item.id}
                        item={item}
                        category={categories.items.find(category => category.id === item.category_id)}
                    />
                );
            });
        }

        return objects;
    }
}

TransactionList.propTypes = {
    // Props from Store
    categories: React.PropTypes.object.isRequired,
    collection: React.PropTypes.object.isRequired,

    // ActionCreators
    fetchObjects: React.PropTypes.func.isRequired,
    getCategoriesIfNeeded: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        categories: state.categories,
        collection: state.transactions
    };
}

const mapDispatchToProps = {
    fetchObjects: getTransactions,
    getCategoriesIfNeeded
};

export default connect(mapStateToProps, mapDispatchToProps)(TransactionList);
