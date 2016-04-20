import React from 'react';
import { connect } from 'react-redux';

import { getDetails } from '../../actions/details';

import DetailItem from '../../components/details/item';
import List from '../common/list';


class DetailsList extends List {
    constructor(props) {
        super(props);

        this.title = 'Details';
        this.transactionID = 0;
        this.instanceID = 0;
    }

    componentWillMount() {
        const transactionID = this.getTransactionID();
        this.props.fetchObjects({ id: transactionID });
    }

    getTransactionID() {
        if (!this.transactionID) {
            const { transactionID } = this.props.routeParams;
            this.transactionID = typeof transactionID !== 'undefined' ? parseInt(transactionID, 10) : 0;
        }

        return this.transactionID;
    }

    getInstanceID() {
        if (!this.instanceID) {
            const { instanceID } = this.props.routeParams;
            this.instanceID = typeof instanceID !== 'undefined' ? parseInt(instanceID, 10) : 0;
        }

        return this.instanceID;
    }

    getLeftButtonPath() {
        return `/transactions/${this.getTransactionID()}`;
    }

    getRightButtonPath() {
        return `/transactions/${this.getTransactionID()}/details/add`;
    }

    getObjects() {
        const transactionID = this.getTransactionID();
        const details = this.props.collection.items.filter(detail => detail.transaction_id === transactionID);
        return details.map(item => {
            return (
                <DetailItem
                    key={item.id}
                    item={item}
                    transaction={{ id: transactionID }}
                />
            );
        });
    }
}

DetailsList.propTypes = {
    // Props from Store
    collection: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,

    // Action creators
    fetchObjects: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        collection: state.details,
        routerState: state.router
    };
}

const mapDispatchToProps = {
    fetchObjects: getDetails
};

export default connect(mapStateToProps, mapDispatchToProps)(DetailsList);
