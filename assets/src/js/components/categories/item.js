import '../../../less/categories/list-item.less';

import React from 'react';
import { Link } from 'react-router';
import Icon from 'react-fa';


export default function Category(props) {
    return (
        <li className="objects-list__item">
            <Link to={'/categories/' + props.category.id} >
                <div className="category">
                    <div className="category__name">{props.category.name}</div>
                </div>
            </Link>
        </li>
    );
}
