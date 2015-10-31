import '../../../less/transaction/list-item.less';

import React from 'react';
import { Link } from 'react-router';
import Icon from 'react-fa';
import classNames from 'classnames';

import { TransactionTypes } from '../../constants/transactions';


export default function TransactionItem(props) {
    const { category, transaction } = props;

    const className = classNames('objects-list__item', 'objects-list__item_transaction', {
        'objects-list__item_expense-transaction': transaction.type === TransactionTypes.EXPENSE,
        'objects-list__item_income-transaction': transaction.type === TransactionTypes.INCOME
    });

    return (
        <li className={className}>
            <Link className="view" to={ '/transactions/' + transaction.id }>
                <div className="transaction">
                    <div className="transaction__info">
                        <div className="transaction__description">{ transaction.description }</div>
                        <div className="transaction__category">{ category.name }</div>
                    </div>
                    <div className="transaction__amount">{ transaction.amount }&nbsp;<Icon name="rub" /></div>
                </div>
            </Link>
        </li>
    );
}
