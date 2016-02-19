/* eslint camelcase: 0 */

import React from 'react';

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
        const { instance } = this.props;
        if (Object.keys(instance).length) {
            this.setState(this.getStateFromInstance(instance));
        }
    }

    componentWillReceiveProps(nextProps) {
        this.updateFromState(nextProps);
    }

    validatePayload(payload) {
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

    getStateFromInstance(instance) {
        return {
            name: instance.name,
            original_amount: instance.original_amount
        };
    }

    getPayload() {
        return {
            name: this.state.name,
            original_amount: parseFloat(this.state.original_amount)
        };
    }

    render() {
        return (
            <form className="form">
                {this.getField('name', 'Name')}
                {this.getField('original_amount', 'Original amount', 'number')}
                <button type="submit" className="form__submit" onClick={this.handleSubmit.bind(this)}>Submit</button>
            </form>
        );
    }
}

ManageForm.propTypes = {
    instance: React.PropTypes.object.isRequired,
    collection: React.PropTypes.object.isRequired,
    submitHandler: React.PropTypes.func.isRequired
};

ManageForm.defaultProps = {
    instance: {}
};

export default ManageForm;
