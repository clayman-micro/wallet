/* eslint camelcase: 0 */

import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';
import classNames from 'classnames';


class ManageForm extends Component {
    constructor(props, context) {
        super(props, context);

        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            name: '',
            errors: props.errors
        };

        this.types = ['expense', 'income'];
    }

    componentWillReceiveProps(nextProps) {
        this.setState({ errors: nextProps.errors });
    }

    handleSubmit(event) {
        event.preventDefault();

        this.setState({ errors: {} });

        let payload = {
            type: ReactDOM.findDOMNode(this.refs.type).value.trim(),
            description: ReactDOM.findDOMNode(this.refs.description).value.trim(),
            amount: parseFloat(ReactDOM.findDOMNode(this.refs.amount).value.trim()),
            created_on: ReactDOM.findDOMNode(this.refs.created_on).value.trim(),
            account_id: parseInt(ReactDOM.findDOMNode(this.refs.account).value.trim(), 10),
            category_id: parseInt(ReactDOM.findDOMNode(this.refs.category).value.trim(), 10)
        };

        try {
            this.validatePayload(payload);
            this.props.addAction(payload);
        } catch (err) {
            this.setState({ errors: err.errors });
        }
    }

    // noinspection JSMethodCanBeStatic
    validatePayload(payload) {
        let errors = {};
        if (!payload.description) {
            errors.description = 'Could not be empty';
        }

        if (isNaN(payload.amount)) {
            errors.amount = 'Should be numeric';
        }

        if (Object.keys(errors).length) {
            let error = new Error('Bad payload');
            error.errors = errors;
            throw error;
        }
    }

    getTypeField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && this.state.errors.type
        });

        return (
            <div className="form__section">
                <label htmlFor="type" className="form__label">Type</label>
                <select id="type" ref="type" placeholder="Type" className={className}>
                    {this.types.map((type, index) =>
                        <option key={index} value={type}>{type}</option>
                    )}
                </select>
            </div>
        );
    }

    getDescriptionField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && this.state.errors.description
        });

        let error = '';
        if (typeof this.state.errors.description !== 'undefined') {
            error = (<span className="form__error">{this.state.errors.description}</span>);
        }

        return (
            <div className="form__section">
                <label htmlFor="description" className="form__label">Description</label>
                <input type="text" ref="description" placeholder="Description" className={className} />
                {error}
            </div>
        );
    }

    getAmountField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && this.state.errors.amount
        });

        let error = '';
        if (typeof this.state.errors.amount !== 'undefined') {
            error = (<span className="form__error">{this.state.errors.amount}</span>);
        }

        return (
            <div className="form__section">
                <label htmlFor="amount" className="form__label">Amount</label>
                <input type="text" ref="amount" placeholder="Amount" className={className} />
                {error}
            </div>
        );
    }

    getCreatedOnField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && this.state.errors.created_on
        });

        return (
            <div className="form__section">
                <label htmlFor="created_on" className="form__label">Date</label>
                <input type="date" ref="created_on" placeholder="Date" className={className} />
            </div>
        );
    }

    getAccountField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && this.state.errors.account
        });

        return (
            <div className="form__section">
                <label htmlFor="account" className="form__label">Account</label>
                <select ref="account" placeholder="Account" className={className}>
                    {this.props.accounts.items.map((account) =>
                        <option key={account.id} value={account.id}>{account.name}</option>
                    )}
                </select>
            </div>
        );
    }

    getCategoryField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && this.state.errors.category
        });

        return (
            <div className="form__section">
                <label htmlFor="category" className="form__label">Category</label>
                <select ref="category" className={className}>
                    {this.props.categories.items.map((category) =>
                        <option key={category.id} value={category.id}>{category.name}</option>
                    )}
                </select>
            </div>
        );
    }

    render() {
        return (
            <form className="form">
                {this.getTypeField()}
                {this.getDescriptionField()}
                {this.getAmountField()}
                {this.getCreatedOnField()}
                {this.getAccountField()}
                {this.getCategoryField()}
                <button type="submit" className="form__submit" onClick={this.handleSubmit}>Submit</button>
            </form>
        );
    }
}

ManageForm.propTypes = {
    accounts: PropTypes.object.isRequired,
    categories: PropTypes.object.isRequired,
    transaction: PropTypes.object,
    addAction: PropTypes.func.isRequired
};

ManageForm.defaultProps = {
    transaction: {}
};

export default ManageForm;
