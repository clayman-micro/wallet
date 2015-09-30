import { APIEndpoints } from 'js/constants/categories';

import BaseService from './base';


class CategoriesService extends BaseService {
    getCollection(token) {
        let headers = new Headers({ 'X-ACCESS-TOKEN': token, accept: 'application/json' });
        let params = {
            method: 'GET',
            headers: headers,
            credentials: 'include'
        };

        return this.request(APIEndpoints.COLLECTION, params).then(request => request.json());
    }
}

export default new CategoriesService(APIEndpoints.COLLECTION, APIEndpoints.RESOURCE);
