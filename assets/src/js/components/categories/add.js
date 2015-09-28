import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';
import { connect } from 'react-redux';

import CategoryActions from 'js/actions/categories';


class AddCategory extends Component {
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
        if (!name) {
            this.setState({
                errors: [{
                    type: 'validation',
                    message: 'Name cound not be empty'
                }]
            });
        }

        this.props.dispatch(CategoryActions.addCategory(name));
    }

    getNameField() {
        let className = 'form__input';
        if (this.state.errors && this.state.errors.name) {
            className = className + ' form__input_error';
        }

        return (
            <div className="form__section">
                <label htmlFor="name" className="form__label">Name</label>
                <input type="text" ref="name" placeholder="Name" className={className} />
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
                <button type="submit"
                        className="form__submit"
                        onClick={this.handleSubmit}>
                    Submit
                </button>
            </form>
        );
    }
}


AddCategory.propTypes = {
    dispatch: PropTypes.func.isRequired
};

export default connect()(AddCategory);