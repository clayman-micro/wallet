import React, { Component, PropTypes } from 'react';
import classnames from 'classnames';


class TextInput extends Component {
    constructor(props, context) {
        super(props, context);
        this.state = {
            text: this.props.text || ''
        };
    }

    handleSubmit(event) {
        const text = event.target.value.trim();
        if (event.which === 13) {
            this.props.onSave(text);
            if (this.props.newCategory) {
                this.setState({ text: '' });
            }
        }
    }

    handleChange(event) {
        this.setState({ text: event.target.value });
    }

    handleBlur(event) {
        if (!this.props.newCategory) {
            this.props.onSave(event.target.value);
        }
    }

    render() {
        return (
            <input className={
                classnames({
                    edit: this.props.editing,
                    'new-category': this.props.newCategory
                })}
                type="text"
                placeholder={this.props.placeholder}
                autoFocus="true"
                value={this.state.text}
                onBlur={this.handleBlur.bind(this)}
                onChange={this.handleChange.bind(this)}
                onKeyDown={this.handleSubmit.bind(this)} />
        );
    }
}

TextInput.propTypes = {
    onSave: PropTypes.func.isRequired,
    text: PropTypes.string,
    placeholder: PropTypes.string,
    editing: PropTypes.bool,
    newCategory: PropTypes.bool
};

export default TextInput;
