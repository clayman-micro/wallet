import React, { Component, PropTypes } from 'react';
import TextInput from './TextInput';


class Header extends Component {
    handleSave(text) {
        if (text.length !== 0) {
            this.props.addCategory(text);
        }
    }

    render() {
        return (
            <header className="header">
                <h1>Categories</h1>
                <TextInput newCategory
                           onSave={this.handleSave.bind(this)}
                           placeholder="What needs to be done?" />
            </header>
        );
    }
}

Header.propTypes = {
    addCategory: PropTypes.func.isRequired
};

export default Header;
