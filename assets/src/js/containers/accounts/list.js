import React from 'react';
import { connect } from 'react-redux';
import Icon from 'react-fa';

import { getAccountsIfNeeded } from '../../actions/accounts';

import AccountItem from '../../components/accounts/item';
import Page from '../../components/common/page';


class AccountsList extends React.Component {
    componentWillMount() {
        this.props.getAccountsIfNeeded();
    }

    render() {
        const leftLink = {
            text: (<span><Icon name="chevron-left" /></span>),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/'
        };
        const rightLink = {
            text: (<Icon name="plus" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/accounts/add'
        };

        return (
            <Page title="Accounts" leftLink={leftLink} rightLink={rightLink}>
                <ul className="objects-list">
                    { this.props.accounts.items.map((account, index) =>
                        <AccountItem key={index} account={account} />
                    )}
                </ul>
            </Page>
        );
    }
}

AccountsList.propTypes = {
    // Props from Store
    accounts: React.PropTypes.object.isRequired,

    // Action creators
    getAccountsIfNeeded: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        accounts: state.accounts
    };
}

const mapDispatchToProps = {
    getAccountsIfNeeded
};

export default connect(mapStateToProps, mapDispatchToProps)(AccountsList);
