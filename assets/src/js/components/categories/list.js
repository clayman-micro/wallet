import React, { Component, PropTypes } from 'react';

import AddCategory from './add';
import CategoryItem from './item';


class Categories extends Component {
    render() {
        const { categories, actions } = this.props;
        console.log(actions);

        console.log(categories);
        return (
            <div>
                <AddCategory />
                <ul className="categories-list">
                    {categories.items.map(category =>
                        <CategoryItem key={category.id} token={this.props.token} category={category} {...actions} />
                    )}
                </ul>
            </div>
        );
    }
}


Categories.propTypes = {
    token: PropTypes.string,
    categories: PropTypes.object.isRequired,
    actions: PropTypes.object.isRequired
};

export default Categories;
