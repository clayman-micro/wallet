import React from 'react';
import classNames from 'classnames';

import Header from '../header/header';
import { getClientHeight } from '../../utils/common';


class Page extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            contentHeight: getClientHeight()
        };

        this.handleResize = this.handleResize.bind(this);
    }

    componentDidMount() {
        window.addEventListener('resize', this.handleResize);

        setTimeout(() => {
            this.updateHeight();
        }, 150);
    }

    componentWillUnmount() {
        window.removeEventListener('resize', this.handleResize);
    }

    handleResize() {
        this.updateHeight();
    }

    getHeaderHeight() {
        const header = document.getElementsByClassName('header');
        let headerHeight = 0;
        if (header.length) {
            headerHeight = header[0].clientHeight;
        }
        return headerHeight;
    }

    updateHeight() {
        this.setState({ contentHeight: getClientHeight() - this.getHeaderHeight() });
    }

    render() {
        return (
            <div className={classNames('page', this.props.className)}>
                <Header
                    title={this.props.title}
                    leftButton={this.props.leftButton}
                    rightButton={this.props.rightButton}
                />
                <div className="page__content" style={{ height: this.state.contentHeight }}>
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
