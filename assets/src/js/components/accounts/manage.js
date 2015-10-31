/* eslint camelcase: 0 */

import React from 'react';
import isEqual from 'lodash/lang/isEqual';

import BaseManageForm from '../common/manage-form';


class ManageForm extends BaseManageForm {
    constructor(props) {
        super(props);

        this.state = {
            name: '',
            original_amount: 0,
            errors: {}
        };
    }

    componentWillMount() {
        const { account } = this.props;
        if (Object.keys(account).length) {
            this.setState({
                name: account.name,
                original_amount: account.original_amount
            });
        }
    }

    componentWillReceiveProps(nextProps) {
        const { account, accounts } = nextProps;
        const nextState = {};

        if (Object.keys(account).length && !isEqual(this.props.account, account)) {
            nextState.name = account.name;
            nextState.original_amount = account.original_amount;
        }

        if (Object.keys(accounts.errors).length) {
            nextState.errors = accounts.errors;
        }

        if (Object.keys(nextState).length) {
            this.setState(nextState);
        }
    }

    handleSubmit(event) {
        event.preventDefault();

        const payload = {
            name: this.state.name,
            original_amount: this.state.original_amount
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
        if (!payload.name) {
            errors.name = 'Could not be empty';
        }

        if (isNaN(payload.original_amount)) {
            errors.original_amount = 'Should be numeric';
        }

        if (Object.keys(errors).length) {
            let error = new Error('Bad payload');
            error.errors = errors;
            throw error;
        }
    }

    render() {
        return (
            <form className="form">
                {this.getField('name', 'Name')}
                {this.getField('original_amount', 'Original amount')}
                <button type="submit" className="form__submit" onClick={this.handleSubmit.bind(this)}>Submit</button>
            </form>
        );
    }
}

ManageForm.propTypes = {
    accounts: React.PropTypes.object.isRequired,
    account: React.PropTypes.object.isRequired,
    submitHandler: React.PropTypes.func.isRequired
};

ManageForm.defaultProps = {
    account: {}
};

export default ManageForm;
