/* eslint camelcase: 0, no-underscore-dangle: 0 */

import React from 'react';
import isEqual from 'lodash/lang/isEqual';
import classNames from 'classnames';
import moment from 'moment';

import { TransactionTypes } from '../../constants/transactions';

import BaseManageForm from '../common/manage-form';


class ManageForm extends BaseManageForm {
    constructor(props) {
        super(props);

        this.state = {
            type: TransactionTypes.EXPENSE,
            description: '',
            amount: '',
            account_id: 0,
            category_id: 0,
            created_on: moment().format('YYYY-MM-DDTHH:mm:ss'),
            errors: {}
        };

        this._typeChoices = [TransactionTypes.EXPENSE, TransactionTypes.INCOME];
    }

    componentWillMount() {
        const { transaction } = this.props;
        if (Object.keys(transaction).length) {
            let created_on = moment(transaction.created_on, 'YYYY-MM-DDTHH:mm:ss');

            this.setState({
                type: transaction.type,
                description: transaction.description,
                amount: transaction.amount,
                account_id: transaction.account_id,
                category_id: transaction.category_id,
                created_on: created_on.format('YYYY-MM-DDTHH:mm:ss')
            });
        }
    }

    componentWillReceiveProps(nextProps) {
        const { transaction, transactions } = nextProps;
        const nextState = {};
        if (Object.keys(transaction).length && !isEqual(this.props.transaction, transaction)) {
            let created_on = moment(transaction.created_on, 'YYYY-MM-DDTHH:mm:ss');

            nextState.type = transaction.type;
            nextState.description = transaction.description;
            nextState.amount = transaction.amount;
            nextState.account_id = transaction.account_id;
            nextState.category_id = transaction.category_id;
            nextState.created_on = created_on.format('YYYY-MM-DDTHH:mm:ss');
        }

        if (Object.keys(transactions.errors).length) {
            nextState.errors = transactions.errors;
        }

        if (Object.keys(nextState).length) {
            this.setState(nextState);
        }
    }

    handleSubmit(event) {
        event.preventDefault();

        const payload = {
            type: this.state.type,
            description: this.state.description,
            amount: this.state.amount,
            account_id: this.state.account_id,
            category_id: this.state.category_id,
            created_on: this.state.created_on
        };

        try {
            ManageForm.validatePayload(payload);
            this.props.submitHandler(payload);
        } catch (err) {
            this.setState({ errors: err.errors });
        }
    }

    static validatePayload(payload) {
        let errors = {};
        if (!payload.description) {
            errors.description = 'Could not be empty';
        }

        if (isNaN(payload.amount)) {
            errors.amount = 'Should be numeric';
        }

        if (payload.account_id === 0) {
            errors.account_id = 'Choose account for transaction';
        }

        if (payload.category_id === 0) {
            errors.category_id = 'Choose category for transaction';
        }

        if (Object.keys(errors).length) {
            let error = new Error('Bad payload');
            error.errors = errors;
            throw error;
        }
    }

    render() {
        const { accounts, categories } = this.props;

        const typeChoices = this._typeChoices.map(type => {
            return { name: type, value: type };
        });
        const accountChoices = accounts.items.map(account => {
            return { name: account.name, value: account.id };
        });
        const categoryChoices = categories.items.map(category => {
            return { name: category.name, value: category.id };
        });

        return (
            <form className="form">
                {this.getField('type', 'Type', 'select', 'Choose type', typeChoices)}
                {this.getField('description', 'Description')}
                {this.getField('amount', 'Amount', 'number')}
                {this.getField('account_id', 'Account', 'select', 'Choose account', accountChoices)}
                {this.getField('category_id', 'Category', 'select', 'Choose category', categoryChoices)}
                {this.getField('created_on', 'Date', 'datetime-local')}
                <button type="submit" className="form__submit" onClick={this.handleSubmit.bind(this)}>Submit</button>
            </form>
        );
    }
}

ManageForm.propTypes = {
    accounts: React.PropTypes.object.isRequired,
    categories: React.PropTypes.object.isRequired,
    transactions: React.PropTypes.object.isRequired,
    transaction: React.PropTypes.object.isRequired,
    submitHandler: React.PropTypes.func.isRequired
};

ManageForm.defaultProps = {
    transaction: {}
};

export default ManageForm;
