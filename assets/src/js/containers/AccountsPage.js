import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from '../actions/accounts';

import AddAccount from '../components/accounts/add';
import AccountItem from '../components/accounts/item';


class AccountsPage extends Component {
    componentDidMount() {
        this.props.dispatch(actions.getAccounts());
    }

    render() {
        const { accounts, dispatch } = this.props;
        const actionCreators = bindActionCreators(actions, dispatch);

        return (
            <div>
                <AddAccount addAction={actionCreators.createAccount}/>
                <ul className="accounts-list">
                    {accounts.items.map(account =>
                        <AccountItem key={account.id} account={account} {...actionCreators} />
                    )}
                </ul>
            </div>
        );
    }
}


AccountsPage.propTypes = {
    accounts: PropTypes.object.isRequired,
    dispatch: PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return { accounts: state.accounts };
}

export default connect(mapStateToProps)(AccountsPage);
