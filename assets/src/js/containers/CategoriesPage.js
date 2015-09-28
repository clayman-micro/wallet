import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import CategoryActions, { getCategories } from 'js/actions/categories';
import CategoriesList from 'js/components/categories/list';


class CategoriesPage extends Component {
    componentDidMount() {
        const { dispatch, session } = this.props;
        const token = session.accessToken.value;
        dispatch(getCategories(token));
    }

    render() {
        const { categories, dispatch } = this.props;
        const actions = bindActionCreators(CategoryActions, dispatch);

        return (
            <div>
                <CategoriesList categories={categories} actions={actions} />
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
