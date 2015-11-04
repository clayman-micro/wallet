import React from 'react';
import { connect } from 'react-redux';
import Icon from 'react-fa';

import { getDetails } from '../../actions/details';

import Page from '../../components/common/page';
import DetailItem from '../../components/details/item';


class DetailsList extends React.Component {
    componentWillMount() {
        const transactionID = this.getTransactionID();
        this.props.getDetails({ id: transactionID });
    }

    getTransactionID() {
        const { transactionID } = this.props.routerState.params;
        return typeof transactionID !== 'undefined' ? parseInt(transactionID, 10) : 0;
    }

    getInstanceID() {
        const { instanceID } = this.props.routerState.params;
        return typeof instanceID !== 'undefined' ? parseInt(instanceID, 10) : 0;
    }

    getLeftLink() {
        const transactionID = this.getTransactionID();
        return {
            text: (<span><Icon name="chevron-left" /></span>),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: `/transactions/${transactionID}`
        };
    }

    getRightLink() {
        const transactionID = this.getTransactionID();
        return {
            text: (<Icon name="plus" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: `/transactions/${transactionID}/details/add`
        };
    }

    render() {
        const transactionID = this.getTransactionID();
        const details = this.props.details.items.filter(detail => detail.transaction_id === transactionID);
        return (
            <Page title="Details" leftLink={this.getLeftLink()} rightLink={this.getRightLink()}>
                <ul className="transactions-list objects-list">
                    { details.map((detail, index) =>
                        <DetailItem
                            key={index}
                            transaction={{ id: transactionID }}
                            detail={detail}
                        />
                    )}
                </ul>
            </Page>
        );
    }
}

DetailsList.propTypes = {
    // Props from Store
    details: React.PropTypes.object.isRequired,
    routerState: React.PropTypes.object.isRequired,

    // Action creators
    getDetails: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        details: state.details,
        routerState: state.router
    };
}

const mapDispatchToProps = {
    getDetails
};

export default connect(mapStateToProps, mapDispatchToProps)(DetailsList);
