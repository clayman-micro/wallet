import React, { Component, PropTypes } from 'react';
import classnames from 'classnames';

import TextInput from '../../components/common/TextInput';


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

    handleSave(category, name) {
        if (name.length === 0) {
            // delete category
        } else if (this.props.category.name !== name) {
            this.props.editCategory(category, { name: name });
        }

        this.setState({ editing: false });
    }

    render() {
        const { category, removeCategory } = this.props;

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
                            onClick={() => removeCategory(category)} />
                </div>
            );
        }
        return (
            <li className={classnames({ editing: this.state.editing })}>{element}</li>
        );
    }
}


CategoryItem.propTypes = {
    category: PropTypes.object.isRequired,
    editCategory: PropTypes.func.isRequired,
    removeCategory: PropTypes.func.isRequired
};

export default CategoryItem;
