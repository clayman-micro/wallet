import React from 'react';
import classNames from 'classnames';

import Header from '../header/header';


class Page extends React.Component {
    render() {
        return (
            <div className={classNames('page', this.props.className)}>
                <Header
                    title={this.props.title}
                    leftButton={this.props.leftButton}
                    rightButton={this.props.rightButton}
                />
                <div className="page__content">
                    {this.props.children}
                </div>
            </div>
        );
    }
}

Page.propTypes = {
    className: React.PropTypes.string.isRequired,
    title: React.PropTypes.string.isRequired,
    leftButton: React.PropTypes.object.isRequired,
    rightButton: React.PropTypes.object.isRequired,

    children: React.PropTypes.node
};

Page.defaultProps = {
    className: ''
};

export default Page;
