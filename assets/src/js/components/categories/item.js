import React, { Component, PropTypes } from 'react';
import classnames from 'classnames';


class CategoryItem extends Component {
    constructor(props, context) {
        super(props, context);
        this.state = {
            editing: false
        };
    }

    render() {
        const { category, deleteCategory } = this.props;

        return (
            <li className={classnames({ editing: this.state.editing })}>
                <div className="view">
                    <label>
                        {category.name}
                    </label>
                    <button className="destroy"
                            onClick={() => deleteCategory(category.id)} />
                </div>
            </li>
        );
    }
}


CategoryItem.propTypes = {
    category: PropTypes.object.isRequired,
    deleteCategory: PropTypes.func.isRequired
};

export default CategoryItem;
