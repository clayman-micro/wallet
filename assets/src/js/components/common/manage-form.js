/* eslint camelcase: 0 */

import React from 'react';
import isEqual from 'lodash/lang/isEqual';
import classNames from 'classnames';


class ManageForm extends React.Component {
    handleChange(field, event) {
        this.setState({ [field]: event.target.value });
    }

    handleSubmit(event) {
        event.preventDefault();

        const payload = this.getPayload();

        try {
            this.validatePayload(payload);
            this.props.submitHandler(payload);
        } catch (err) {
            this.setState({ errors: err.errors });
        }
    }

    validatePayload() {
        let errors = {};

        if (Object.keys(errors).length) {
            let error = new Error('Bad payload');
            error.errors = errors;
            throw error;
        }
    }

    getField(name, label, type = 'text', placeholder = '', choices = []) {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && this.state.errors[name]
        });

        let error = '';
        if (typeof this.state.errors[name] !== 'undefined') {
            error = (<span className="form__error">{this.state.errors[name]}</span>);
        }

        let field = '';
        if (type === 'select') {
            field = (
                <select value={this.state[name]} className={className} onChange={this.handleChange.bind(this, name)}>
                    <option key={0} value="0">{placeholder}</option>
                    {choices.map((item, index) =>
                        <option key={index + 1} value={item.value}>{item.name}</option>
                    )}
                </select>
            );
        } else {
            field = (
                <input
                    type={type}
                    placeholder={placeholder || label}
                    className={className}
                    value={this.state[name]}
                    onChange={this.handleChange.bind(this, name)}
                />
            );
        }

        return (
            <div className="form__section">
                <label className="form__label">{label}</label>
                {field}
                {error}
            </div>
        );
    }

    getSubmitButton() {
        return (
            <button type="submit" className="form__submit" onClick={this.handleSubmit.bind(this)}>Submit</button>
        );
    }

    updateFromState(props) {
        const { instance, collection } = props;
        let nextState = {};

        if (Object.keys(instance).length && !isEqual(this.props.instance, instance)) {
            nextState = this.getStateFromInstance(instance);
        }

        if (Object.keys(collection.errors).length) {
            nextState = Object.assign({}, nextState, collection.errors);
        }

        if (Object.keys(nextState).length) {
            this.setState(nextState);
        }
    }

    getPayload() {
        return {};
    }

    getStateFromInstance(instance) {
        return instance;
    }
}


ManageForm.propTypes = {
    instance: React.PropTypes.object.isRequired,
    collection: React.PropTypes.object.isRequired,
    submitHandler: React.PropTypes.object.isRequired
};

ManageForm.defaultProps = {
    instance: {}
};

export default ManageForm;
