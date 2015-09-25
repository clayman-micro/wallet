import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import Header from '../components/Header';
import MainSection from '../components/MainSection';
import CategoryActions from '../actions/Categories';


@connect(state => ({ categories: state.categories }))
class Categories extends Component {
    static propTypes = {
        categories: PropTypes.array.isRequired,
        dispatch: PropTypes.func.isRequired
    }

    render() {
        const { categories, dispatch } = this.props;
        const actions = bindActionCreators(CategoryActions, dispatch);

        return (
            <div>
                <Header addCategory={actions.addCategory} />
                <MainSection categories={categories} actions={actions} />
            </div>
        );
    }
}

export default Categories;
