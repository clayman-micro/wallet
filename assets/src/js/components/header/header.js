import React, { Component, PropTypes } from 'react';
// import TextInput from './TextInput';


class Header extends Component {
    // handleSave(text) {
    //     if (text.length !== 0) {
    //         this.props.addCategory(text);
    //     }
    // }

    render() {
        return (
            <header className="header">
                <div className="header__title">{ this.props.title }</div>
            </header>
        );
    }

    // <TextInput newCategory
    // onSave={this.handleSave.bind(this)}
    // placeholder="What needs to be done?" />

}

Header.propTypes = {
    title: PropTypes.string.isRequired,
    // addCategory: PropTypes.func.isRequired
};

export default Header;
