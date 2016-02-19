import React from 'react';
import Icon from 'react-fa';

import { StatusChoices } from '../../constants/status';

import Page from '../../components/common/page';


export default class List extends React.Component {
    constructor(props) {
        super(props);

        this.title = '';
        this.leftButtonPath = '/';
        this.rightButtonPath = '#';
        this.listItemComponent = '';
    }

    componentWillMount() {
        this.props.fetchObjects();
    }

    getLeftButtonPath() {
        return this.leftButtonPath;
    }

    getLeftButton() {
        return {
            text: (<span><Icon name="chevron-left"/></span>),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: this.getLeftButtonPath()
        };
    }

    getRightButtonPath() {
        return this.rightButtonPath;
    }

    getRightButton() {
        return {
            text: (<Icon name="plus" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: this.getRightButtonPath()
        };
    }

    isShowSpinner() {
        return this.props.collection.status === StatusChoices.FETCHING;
    }

    getSpinner() {
        let spinner = '';

        if (this.isShowSpinner()) {
            spinner = (
                <div className="objects-list__item objects-list__item_spinner">
                    <Icon spin name="spinner" />
                </div>
            );
        }

        return spinner;
    }

    getObjects() {
        return this.props.collection.items.map((item, index) =>
            React.createElement(this.listItemComponent, { key: index, item: item })
        );
    }

    render() {
        return (
            <Page title={this.title} leftButton={this.getLeftButton()} rightButton={this.getRightButton()}>
                <ul className="objects-list">
                    {this.getSpinner()}
                    {this.getObjects()}
                </ul>
            </Page>
        );
    }
}


List.propTypes = {
    // Props from Store
    collection: React.PropTypes.object.isRequired,

    // Action creators
    fetchObjects: React.PropTypes.func.isRequired
};
