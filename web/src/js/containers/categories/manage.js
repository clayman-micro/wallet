import React from 'react';
import { connect } from 'react-redux';
import { push } from 'react-router-redux';
import Icon from 'react-fa';

import { getCategoriesIfNeeded, createCategory, editCategory, removeCategory } from '../../actions/categories';

import { StatusChoices } from '../../constants/status';

import ManagePage from '../common/manage';
import Page from '../../components/common/page';
import ManageForm from '../../components/categories/manage';


class ManageCategory extends ManagePage {
    constructor(props) {
        super(props);

        this.doneRedirect = '/categories';
        this.leftLinkPath = '/categories';
    }

    componentWillMount() {
        this.props.getCategoriesIfNeeded();
    }

    render() {
        const instanceID = this.getInstanceID();
        let instance = this.getInstance();

        let title = 'Add category';

        let rightButton = {};
        if (instanceID) {
            title = 'Edit category';
            rightButton = this.getRightLink(instance);
        }

        return (
            <Page title={title} leftButton={this.getLeftLink()} rightButton={rightButton} >
                <ManageForm
                    collection={this.props.collection}
                    instance={instance}
                    submitHandler={this.handleSubmit.bind(this, instance)}
                />
            </Page>
        );
    }
}

ManageCategory.propTypes = {
    // Props from Store
    collection: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,

    // Action creators
    pushState: React.PropTypes.func.isRequired,

    getCategoriesIfNeeded: React.PropTypes.func.isRequired,
    createAction: React.PropTypes.func.isRequired,
    editAction: React.PropTypes.func.isRequired,
    removeAction: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        collection: state.categories,
        routerState: state.router
    };
}

const mapDispatchToProps = {
    pushState: push,
    getCategoriesIfNeeded,
    createAction: createCategory,
    editAction: editCategory,
    removeAction: removeCategory
};

export default connect(mapStateToProps, mapDispatchToProps)(ManageCategory);
