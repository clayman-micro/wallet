import React from 'react';
import { Link } from 'react-router';
import classNames from 'classnames';


class Header extends React.Component {
    getButton(options, className) {
        let content = '';

        if (Object.keys(options).length) {
            const buttonClass = classNames('header__button', className);
            content = (
                <Link className={buttonClass} style={options.style} to={options.path} onClick={options.handle}>
                    {options.text}
                </Link>
            );
        }

        return content;
    }

    render() {
        return (
            <header className="header">
                <div className="header__title">{ this.props.title }</div>
                { this.getButton(this.props.leftButton, 'header__button_left') }
                { this.getButton(this.props.rightButton, 'header__button_right') }
            </header>
        );
    }
}

Header.propTypes = {
    title: React.PropTypes.string.isRequired,
    leftButton: React.PropTypes.object,
    rightButton: React.PropTypes.object,

    dispatch: React.PropTypes.func
};

Header.defaultProps = {
    leftButton: {},
    rightButton: {}
};

export default Header;
