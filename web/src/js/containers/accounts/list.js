import { connect } from 'react-redux';

import { getAccountsIfNeeded } from '../../actions/accounts';

import AccountItem from '../../components/accounts/item';
import List from '../common/list';


class AccountsList extends List {
    constructor(props) {
        super(props);

        this.title = 'Accounts';
        this.rightButtonPath = '/accounts/add';

        this.listItemComponent = AccountItem;
    }
}

function mapStateToProps(state) {
    return {
        collection: state.accounts
    };
}

const mapDispatchToProps = {
    fetchObjects: getAccountsIfNeeded
};

export default connect(mapStateToProps, mapDispatchToProps)(AccountsList);
