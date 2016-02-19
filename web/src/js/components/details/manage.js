/* eslint camelcase: 0 */

import React from 'react';

import BaseManageForm from '../common/manage-form';


class ManageForm extends BaseManageForm {
    constructor(props) {
        super(props);

        this.state = {
            name: '',
            count: 1,
            price_per_unit: null,
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

        if (isNaN(payload.count)) {
            errors.amount = 'Should be numeric';
        }

        if (isNaN(payload.price_per_unit)) {
            errors.price_per_unit = 'Should be numeric';
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
            count: instance.count,
            price_per_unit: instance.price_per_unit
        };
    }

    getPayload() {
        return {
            name: this.state.name,
            count: parseFloat(this.state.count),
            price_per_unit: parseFloat(this.state.price_per_unit)
        };
    }

    render() {
        return (
            <form className="form">
                {this.getField('name', 'Name')}
                {this.getField('price_per_unit', 'Price per unit', 'number')}
                {this.getField('count', 'Count', 'number')}
                {this.getSubmitButton()}
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
