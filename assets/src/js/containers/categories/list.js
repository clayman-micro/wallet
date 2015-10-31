import React from 'react';
import { connect } from 'react-redux';
import Icon from 'react-fa';

import { getCategoriesIfNeeded } from '../../actions/categories';

import CategoryItem from '../../components/categories/item';
import Page from '../../components/common/page';


class CategoriesList extends React.Component {
    componentWillMount() {
        this.props.getCategoriesIfNeeded();
    }

    render() {
        const leftLink = {
            text: (<span><Icon name="chevron-left" /></span>),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/'
        };
        const rightLink = {
            text: (<Icon name="plus" />),
            style: { fontSize: '20px', padding: '15px 5px 11px' },
            path: '/categories/add'
        };

        return (
            <Page title="Categories" leftLink={leftLink} rightLink={rightLink} >
                <ul className="objects-list">
                    {this.props.categories.items.map((category, index) =>
                        <CategoryItem key={index} category={category} />
                    )}
                </ul>
            </Page>
        );
    }
}

CategoriesList.propTypes = {
    // Props from Store
    categories: React.PropTypes.object.isRequired,

    // Action creators
    getCategoriesIfNeeded: React.PropTypes.func.isRequired
};

function mapStateToProps(state) {
    return {
        categories: state.categories
    };
}

const mapDispatchToProps = {
    getCategoriesIfNeeded
};

export default connect(mapStateToProps, mapDispatchToProps)(CategoriesList);
