import React from 'react';
import { connect } from 'react-redux';
import { pushState } from 'redux-router';
import Icon from 'react-fa';

import { getCategoriesIfNeeded, createCategory, editCategory, removeCategory } from '../../actions/categories';

import { StatusChoices } from '../../constants/status';

import Page from '../../components/common/page';
import ManageForm from '../../components/categories/manage';


class ManageCategory extends React.Component {
    componentWillMount() {
        this.props.getCategoriesIfNeeded();
    }

    componentWillReceiveProps(nextProps) {
        const { status } = nextProps.categories;
        const doneStatuses = [
            StatusChoices.CREATE_DONE,
            StatusChoices.EDIT_DONE,
            StatusChoices.REMOVE_DONE
        ];

        if (doneStatuses.indexOf(status) !== -1) {
            setTimeout(() => {
                this.props.pushState('', '/categories');
            }, 250);
        }
    }

    handleSubmit(category, payload) {
        if (Object.keys(category).length) {
            this.props.editCategory(category, payload);
        } else {
            this.props.createCategory(payload);
        }
    }

    handleRemove(category, event) {
        event.preventDefault();
        this.props.removeCategory(category);
    }

    getInstanceID() {
        const { instanceID } = this.props.routerState.params;
        return typeof instanceID !== 'undefined' ? parseInt(instanceID, 10) : 0;
    }

    getCategory() {
        let category = {};
        const instanceID = this.getInstanceID();

        if (instanceID) {
            category = this.props.categories.items.find(item => item.id === instanceID);
            if (typeof category === 'undefined') {
                category = {};
            }
        }

        return category;
    }

    render() {
        const instanceID = this.getInstanceID();
        let category = this.getCategory();

        let title = 'Add category';
        let rightLink = {};
        const leftLink = {
            text: (<Icon name="chevron-left" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/categories'
        };

        if (instanceID) {
            title = 'Edit category';
            rightLink = {
                text: (<Icon name="trash-o" />),
                style: { fontSize: '20px', padding: '13px 0' },
                path: '#',
                handle: this.handleRemove.bind(this, account)
            };
        }

        return (
            <Page title={title} leftLink={leftLink} rightLink={rightLink} >
                <ManageForm
                    categories={this.props.categories}
                    category={category}
                    submitHandler={this.handleSubmit.bind(this, category)}
                />
            </Page>
        );
    }
}

ManageCategory.propTypes = {
    // Props from Store
    categories: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,

    // Action creators
    pushState: React.PropTypes.func.isRequired,

    getCategoriesIfNeeded: React.PropTypes.func.isRequired,
    createCategory: React.PropTypes.func.isRequired,
    editCategory: React.PropTypes.func.isRequired,
    removeCategory: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        categories: state.categories,
        routerState: state.router
    };
}

const mapDispatchToProps = {
    pushState,
    getCategoriesIfNeeded, createCategory, editCategory, removeCategory
};

export default connect(mapStateToProps, mapDispatchToProps)(ManageCategory);
