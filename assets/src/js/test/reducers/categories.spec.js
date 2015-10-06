import expect from 'expect';
import { ActionTypes } from '../../constants/categories';
import reducer from '../../reducers/categories';


describe('Categories reducers', () => {
    it('should handle initial state', () => {
        expect(reducer(undefined, {})).toEqual({
            isFetching: false,
            items: [],
            errors: []
        })
    });

    describe('Get categories', () => {
        it('should handle GET_CATEGORIES_REQUEST', () => {
            const action = { type: ActionTypes.GET_CATEGORIES_REQUEST };
            expect(reducer(undefined, action)).toEqual({
                isFetching: true,
                items: [],
                errors: []
            })
        });

        describe('response', () => {
            it('should handle GET_CATEGORIES_RESPONSE with empty initial state', () => {
                const categories = [{ id: 1, name: 'First' }, { id: 2, name: 'Second' }];
                const action = { type: ActionTypes.GET_CATEGORIES_RESPONSE, categories: categories };
                expect(reducer(undefined, action)).toEqual({
                    isFetching: false,
                    items: categories,
                    errors: []
                });
            });

            //it('should handle GET_CATEGORIES_RESPONSE with existed state', () => {
            //    const action = { type: ActionTypes.GET_CATEGORIES_RESPONSE,
            //        categories: [{ id: 1, name: 'First' }, { id: 2, name: 'Second' }] };
            //    const initial = { isFetching: true, items: [{ id: 1, name: 'First' }], errors: [] };
            //    expect(reducer(initial, action)).toEqual({
            //        isFetching: false,
            //        items: [{ id: 1, name: 'First' }, { id: 2, name: 'Second' }],
            //        errors: []
            //    });
            //});
        });

        it('should handle GET_CATEGORIES_FAILED', () => {
            const errors = { unauthorized: 'Auth required' };
            const action = { type: ActionTypes.GET_CATEGORIES_FAILED, errors: errors };
            expect(reducer(undefined, action)).toEqual({
                isFetching: false,
                items: [],
                errors: errors
            });
        });
    });

    describe('Create category', () => {
        it('should handle CREATE_CATEGORY_REQUEST', () => {
            const action = { type: ActionTypes.CREATE_CATEGORY_REQUEST, name: 'Test' };
            expect(reducer(undefined, action)).toEqual({
                isFetching: true,
                items: [],
                errors: []
            })
        });

        it('should handle CREATE_CATEGORY_RESPONSE', () => {
            const action = { type: ActionTypes.CREATE_CATEGORY_RESPONSE, category: { id: 1, name: 'Test' }};
            expect(reducer(undefined, action)).toEqual({
                isFetching: false,
                items: [{ id: 1, name: 'Test' }],
                errors: []
            });
        });

        it('should handle CREATE_CATEGORY_FAILED', () => {
            const action = { type: ActionTypes.CREATE_CATEGORY_FAILED, errors: { name: 'Could not be empty' }};
            expect(reducer(undefined, action)).toEqual({
                isFetching: false,
                items: [],
                errors: { name: 'Could not be empty' }
            });
        });
    });
});
