import React from 'react';


function TransactionItem(props) {
    const { transaction } = props;

    return (
        <li className="transaction-list__item transaction">
            <a className="view" href="#">
                <div className="transaction__description">{ transaction.description }</div>
                <div className="transaction__info clearfix">
                    <span className="transaction__type">{ transaction.type }</span>
                    <span className="transaction__amount">{ transaction.amount }</span>
                </div>
            </a>
        </li>
    );
}

export default TransactionItem;
