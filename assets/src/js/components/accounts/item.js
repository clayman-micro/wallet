import React, { Component, PropTypes } from 'react';
import classNames from 'classnames';

import TextInput from '../../components/common/TextInput';


class AccountItem extends Component {
    constructor(props, context) {
        super(props, context);
        this.state = {
            editing: false
        };
    }

    handleDoubleClick() {
        this.setState({ editing: true });
    }

    handleSave(account, name) {
        if (name.length === 0) {
            // delete account
        } else if (this.props.account.name !== name) {
            this.props.editAccount(account, { name: name });
        }
    }

    render() {
        const { account, removeAccount } = this.props;

        let element;

        if (this.state.editing) {
            element = (
                <TextInput text={account.name}
                           editing={this.state.editing}
                           onSave={(name) => this.handleSave(account, { name: name })} />
            );
        } else {
            element = (
                <div className="view">
                    <label onDoubleClick={this.handleDoubleClick.bind(this)}>
                        {account.name} - {account.original_amount}
                    </label>
                    <button className="destroy"
                            onClick={() => removeAccount(account)} />
                </div>
            );
        }

        return (
            <li className={classNames({ editing: this.state.editing })}>{element}</li>
        );
    }
}


AccountItem.propTypes = {
    account: PropTypes.object.isRequired,
    editAccount: PropTypes.func.isRequired,
    removeAccount: PropTypes.func.isRequired
};

export default AccountItem;
