import React from 'react';
import isEqual from 'lodash/lang/isEqual';

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
        const { category } = this.props;
        if (Object.keys(category).length) {
            this.setState({
                name: category.name
            });
        }
    }

    componentWillReceiveProps(nextProps) {
        const { category, categories } = nextProps;
        const nextState = {};

        console.log('ManageForm.componentWillReceiveProps(nextProps)', nextProps, this.state);

        if (Object.keys(category).length && !isEqual(this.props.category, category)) {
            nextState.name = category.name;
        }

        if (Object.keys(categories.errors).length) {
            nextState.errors = categories.errors;
        }

        if (Object.keys(nextState).length) {
            this.setState(nextState);
        }
    }

    handleSubmit(event) {
        event.preventDefault();

        console.log('ManageForm.handleSubmit(event)', event, this.state);

        const payload = {
            name: this.state.name
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

        if (Object.keys(errors).length) {
            let error = new Error('Bad payload');
            error.errors = errors;
            throw error;
        }
    }

    render() {
        console.log('ManageForm.render()', this.props, this.state);
        return (
            <form className="form">
                {this.getField('name', 'Name')}
                <button type="submit" className="form__submit" onClick={this.handleSubmit.bind(this)}>Submit</button>
            </form>
        );
    }
}

ManageForm.propTypes = {
    categories: React.PropTypes.object.isRequired,
    category: React.PropTypes.object.isRequired,
    submitHandler: React.PropTypes.func.isRequired
};

ManageForm.defaultProps = {
    category: {}
};

export default ManageForm;
