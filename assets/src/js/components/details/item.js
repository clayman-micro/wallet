import '../../../less/details/list-item.less';

import React from 'react';
import { Link } from 'react-router';
import Icon from 'react-fa';


export default function DetailItem(props) {
    const { detail } = props;
    const url = `/transactions/${props.transaction.id}/details/${detail.id}`;

    return (
        <li className="objects-list__item">
            <Link className="view" to={url}>
                <div className="detail">
                    <div className="detail__info">
                        <div className="detail__name">{detail.name}</div>
                        <div className="detail__properties">
                            <div className="detail__price-per-unit">
                                Price per unit: {detail.price_per_unit}&nbsp;<Icon name="rub" />
                            </div>
                            <div className="detail__count">Count: {detail.count}</div>
                        </div>
                    </div>
                    <div className="detail__amount">{detail.total}&nbsp;<Icon name="rub" /></div>
                </div>
            </Link>
        </li>
    );
}
