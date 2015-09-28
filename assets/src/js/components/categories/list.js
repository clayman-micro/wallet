import React, { Component, PropTypes } from 'react';

import AddCategory from './add';
import CategoryItem from './item';


class Categories extends Component {
    render() {
        const { categories, actions } = this.props;

        return (
            <div>
                <AddCategory />
                <ul className="categories-list">
                    {categories.items.map(category =>
                        <CategoryItem key={category.id} category={category} {...actions} />
                    )}
                </ul>
            </div>
        );
    }
}


Categories.propTypes = {
    categories: PropTypes.object.isRequired,
    actions: PropTypes.object.isRequired
};

export default Categories;
