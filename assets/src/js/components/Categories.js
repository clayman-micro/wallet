import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import Header from 'js/components/Header';
import MainSection from 'js/components/MainSection';
import CategoryActions from 'js/actions/Categories';


class Categories extends Component {
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


Categories.propTypes = {
    categories: PropTypes.array.isRequired,
    dispatch: PropTypes.func.isRequired
};


function mapStateToProps(state) {
    return { categories: state.categories };
}

export default connect(mapStateToProps)(Categories);
