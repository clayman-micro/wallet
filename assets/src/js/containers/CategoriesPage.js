import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import CategoryActions, { getCategories, editCategory, removeCategory } from '../actions/categories';
import CategoriesList from '../components/categories/list';


class CategoriesPage extends Component {
    componentDidMount() {
        const { dispatch, session } = this.props;
        if (session.accessToken) {
            const token = session.accessToken.value;
            dispatch(getCategories(token));
        }
    }

    render() {
        const { categories, session, dispatch } = this.props;
        const actions = bindActionCreators({ editCategory, removeCategory }, dispatch);
        const token = session.accessToken.value;

        return (
            <div>
                <CategoriesList categories={categories} token={token} actions={actions} />
            </div>
        );
    }
}


CategoriesPage.propTypes = {
    categories: PropTypes.object.isRequired,
    session: PropTypes.object.isRequired,
    routerState: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        categories: state.categories,
        routerState: state.router,
        session: state.session
    };
}

export default connect(mapStateToProps)(CategoriesPage);
