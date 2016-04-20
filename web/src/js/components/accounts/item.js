import '../../../less/accounts/list-item.less';

import React from 'react';
import { Link } from 'react-router';
import Icon from 'react-fa';


export default function AccountItem(props) {
    return (
        <li className="objects-list__item">
            <Link to={'/accounts/' + props.item.id}>
                <div className="account">
                    <div className="account__info">
                        <div className="account__name">{props.item.name}</div>
                        <div className="account__original">
                            <span>{props.item.balance.expense}&nbsp;<Icon name="rub" /></span>
                            <span>{props.item.balance.income}&nbsp;<Icon name="rub" /></span>
                        </div>
                    </div>
                    <div className="account__amount">{props.item.balance.remain}&nbsp;<Icon name="rub" /></div>
                </div>
            </Link>
        </li>
    );
}
