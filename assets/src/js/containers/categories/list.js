import { connect } from 'react-redux';

import { getCategoriesIfNeeded } from '../../actions/categories';
import CategoryItem from '../../components/categories/item';
import List from '../common/list';


class CategoriesList extends List {
    constructor(props) {
        super(props);

        this.title = 'Categories';
        this.rightButtonPath = '/categories/add';

        this.listItemComponent = CategoryItem;
    }
}

function mapStateToProps(state) {
    return {
        collection: state.categories
    };
}

const mapDispatchToProps = {
    fetchObjects: getCategoriesIfNeeded
};

export default connect(mapStateToProps, mapDispatchToProps)(CategoriesList);
