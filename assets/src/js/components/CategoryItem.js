import React, { Component, PropTypes } from 'react';
import classnames from 'classnames';
import TextInput from './TextInput';


class CategoryItem extends Component {
    constructor(props, context) {
        super(props, context);
        this.state = {
            editing: false
        };
    }

    handleDoubleClick() {
        this.setState({ editing: true });
    }

    handleSave(id, name) {
        if (name.length === 0) {
            this.props.deleteCategory(id);
        } else {
            this.props.editCategory(id, name);
        }

        this.setState({ editing: false });
    }

    render() {
        const { category, deleteCategory } = this.props;

        let element;
        if (this.state.editing) {
            element = (
                <TextInput text={category.name}
                           editing={this.state.editing}
                           onSave={(name) => this.handleSave(category.id, name)} />
            );
        } else {
            element = (
                <div className="view">
                    <label onDoubleClick={this.handleDoubleClick.bind(this)}>
                        {category.name}
                    </label>
                    <button className="destroy"
                            onClick={() => deleteCategory(category.id)} />
                </div>
            )
        }

        return (
            <li className={classnames({ editing: this.state.editing })}>
                {element}
            </li>
        )
    }

}

CategoryItem.propTypes = {
    category: PropTypes.object.isRequired,
    editCategory: PropTypes.func.isRequired,
    deleteCategory: PropTypes.func.isRequired,
};

export default CategoryItem;
