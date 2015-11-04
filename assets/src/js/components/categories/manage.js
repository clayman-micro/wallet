import React from 'react';

import BaseManageForm from '../common/manage-form';


class ManageForm extends BaseManageForm {
    constructor(props) {
        super(props);

        this.state = {
            name: '',
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

        if (Object.keys(errors).length) {
            let error = new Error('Bad payload');
            error.errors = errors;
            throw error;
        }
    }

    getStateFromInstance(instance) {
        return {
            name: instance.name
        };
    }

    getPayload() {
        return {
            name: this.state.name
        };
    }

    render() {
        return (
            <form className="form">
                {this.getField('name', 'Name')}
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
