import React, { Component, PropTypes } from 'react';
import { Link } from 'react-router';
import { connect } from 'react-redux';
import { goBack } from 'redux-router';


class Header extends Component {
    render() {
        const { leftLink, rightLink } = this.props;

        return (
            <header className="header">
                <div className="header__title">{ this.props.title }</div>
                { Object.keys(leftLink).length ?
                    <Link className="header__link header__link_left" style={leftLink.style}
                        onClick={leftLink.handle}
                        to={leftLink.path}>{leftLink.text}</Link> : '' }
                { Object.keys(rightLink).length ?
                    <Link className="header__link header__link_right" style={rightLink.style}
                          onClick={rightLink.handle}
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
    leftLink: { text: 'Back', path: '#' },
    rightLink: {}
};

export default connect()(Header);
