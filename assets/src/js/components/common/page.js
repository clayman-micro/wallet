import React from 'react';
import classNames from 'classnames';

import Header from '../header/header';


class Page extends React.Component {
    render() {
        return (
            <div className={classNames('page', this.props.className)}>
                <Header title={this.props.title} rightLink={this.props.rightLink} leftLink={this.props.leftLink} />
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
    leftLink: React.PropTypes.object.isRequired,
    rightLink: React.PropTypes.object.isRequired,

    children: React.PropTypes.node
};

Page.defaultProps = {
    className: ''
};

export default Page;
