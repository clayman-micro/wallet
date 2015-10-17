import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';
import { goBack } from 'redux-router';


class Header extends Component {

    onLeftLinkClick(event) {
        event.preventDefault();

        this.props.dispatch(goBack());
    }

    render() {
        const { leftLink, rightLink } = this.props;

        return (
            <header className="header">
                <div className="header__title">{ this.props.title }</div>
                { leftLink ?
                    <Link className="header__link header__link_left"
                        onClick={this.onLeftLinkClick.bind(this)}
                        to={leftLink.path}>{leftLink.text}</Link> : '' }
                { rightLink ?
                    <Link className="header__link header__link_right"
                        to={rightLink.path}>{rightLink.text}</Link> : '' }
            </header>
        );
    }
}

Header.propTypes = {
    title: PropTypes.string.isRequired,
    leftLink: PropTypes.object,
    rightLink: PropTypes.object,

    dispatch: PropTypes.func
};

Header.defaultProps = {
    leftLink: { text: 'Back', path: '#' }
};

export default connect()(Header);
