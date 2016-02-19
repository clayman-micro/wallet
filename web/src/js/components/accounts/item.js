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
                            {props.item.original_amount}&nbsp;<Icon name="rub" />
                        </div>
                    </div>
                    <div className="account__amount">{props.item.current_amount}&nbsp;<Icon name="rub" /></div>
                </div>
            </Link>
        </li>
    );
}
