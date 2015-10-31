/* eslint camelcase: 0 */

import React from 'react';
import classNames from 'classnames';


export default class ManageForm extends React.Component {
    handleChange(field, event) {
        this.setState({ [field]: event.target.value });
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
}
