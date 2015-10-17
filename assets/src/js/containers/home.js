import React from 'react';
import { Link } from 'react-router';

import Header from '../components/header/header';


export default function HomePage() {
    const links = [
        { id: 1, url: '/accounts', name: 'Accounts' },
        { id: 2, url: '/categories', name: 'Categories' },
        { id: 3, url: '/transactions', name: 'Transactions' }
    ].map(link =>
      <p key={link.id}>
        <Link to={link.url}>{link.name}</Link>
      </p>
    );

    return (
        <div className="home-page">
            <Header title="Wallet" leftLink={{}} />
            {links}
        </div>
    );
}
