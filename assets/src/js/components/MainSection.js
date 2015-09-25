import React, { Component, PropTypes } from 'react';
import CategoryItem from './CategoryItem';


class MainSection extends Component {
    constructor(props, context) {
        super(props, context);
        this.state = { filter: 'SHOW_ALL' }
    }

    render() {
        const { categories, actions } = this.props;
        const { filter } = this.state;

        return (
            <section className="main">
                <ul className="categories-list">
                    {categories.map(category =>
                        <CategoryItem key={category.id} category={category} {...actions} />
                    )}
                </ul>
            </section>
        );
    }
}

MainSection.propTypes = {
    categories: PropTypes.array.isRequired,
    actions: PropTypes.object.isRequired
};

export default MainSection;
