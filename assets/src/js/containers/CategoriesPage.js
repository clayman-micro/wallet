import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from '../actions/categories';

import Header from '../components/header/header';
import AddCategory from '../components/categories/add';
import CategoryItem from '../components/categories/item';


class CategoriesPage extends Component {
    componentDidMount() {
        this.props.dispatch(actions.getCategories());
    }

    render() {
        const { categories, dispatch } = this.props;
        const actionCreators = bindActionCreators(actions, dispatch);

        return (
            <div className="categories-page">
                <Header title="Categories" />
                <AddCategory addAction={actionCreators.createCategory}/>
                <ul className="categories-list">
                    {categories.items.map(category =>
                        <CategoryItem key={category.id} category={category} {...actionCreators} />
                    )}
                </ul>
            </div>
        );
    }
}


CategoriesPage.propTypes = {
    categories: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return { categories: state.categories };
}

export default connect(mapStateToProps)(CategoriesPage);
