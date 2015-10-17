/* eslint camelcase: 0 */

import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';
import classNames from 'classnames';


class AddAccount extends Component {
    constructor(props, context) {
        super(props, context);

        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            name: '',
            errors: []
        };
    }

    handleSubmit(event) {
        event.preventDefault();

        const name = ReactDOM.findDOMNode(this.refs.name).value.trim();
        const amount = ReactDOM.findDOMNode(this.refs.amount).value.trim();
        if (!name) {
            this.setState({
                errors: {
                    name: 'Name could not be empty'
                }
            });
            return;
        }

        if (!amount) {
            this.setState({
                errors: {
                    amount: 'Amount could not be empty'
                }
            });
            return;
        }

        this.props.addAction({ name: name, original_amount: amount });
    }

    getNameField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && typeof this.state.errors.name !== 'undefined'
        });

        return (
            <div className="form__section">
                <label htmlFor="name" className="form__label">Name</label>
                <input type="text" ref="name" placeholder="Name" className={className} />
            </div>
        );
    }

    getAmountField() {
        let className = classNames('form__input', {
            form__input_error: this.state.errors && typeof this.state.errors.amount !== 'undefined'
        });

        return (
            <div className="form__section">
                <label htmlFor="amount" className="form__label">Amount</label>
                <input type="text" ref="amount" placeholder="Original amount" className={className} />
            </div>
        );
    }

    getErrorList() {
        if (this.state.errors) {
            let errors = this.state.errors.map(error => {
                return (<div key={error.type}>{error.message}</div>);
            });

            return (<div className="form__errors">{errors}</div>);
        }
    }

    render() {
        return (
            <form className="form">
                {this.getErrorList()}
                {this.getNameField()}
                {this.getAmountField()}
                <button type="submit"
                        className="form__submit"
                        onClick={this.handleSubmit}>
                    Submit
                </button>
            </form>
        );
    }
}


AddAccount.propTypes = {
    addAction: PropTypes.func.isRequired
};

export default AddAccount;
