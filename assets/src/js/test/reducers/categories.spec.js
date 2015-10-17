/* eslint max-nested-callbacks: 0 no-undefined: 0 */

import { expect } from 'chai';
import { StatusChoices } from '../../constants/status';
import { ActionTypes } from '../../constants/categories';
import reducer from '../../reducers/categories';


describe('Categories reducer', () => {
    it('should handle initial state', () => {
        expect(reducer(undefined, {})).to.deep.equal({
            status: StatusChoices.INITIAL,
            items: [],
            errors: {}
        });
    });

    describe('Get categories', () => {
        it('should handle GET_CATEGORIES_REQUEST', () => {
            const action = { type: ActionTypes.GET_CATEGORIES_REQUEST };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FETCHING, items: [], errors: {}
            });
        });

        it('should handle GET_CATEGORIES_RESPONSE with empty initial state', () => {
            const categories = [{ id: 1, name: 'First' }, { id: 2, name: 'Second' }];
            const action = { type: ActionTypes.GET_CATEGORIES_RESPONSE, json: { categories: categories } };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FETCH_DONE, items: categories, errors: {}
            });
        });

        it('should handle GET_CATEGORIES_RESPONSE with existed state', () => {
            const action = { type: ActionTypes.GET_CATEGORIES_RESPONSE,
                json: { categories: [{ id: 1, name: 'First' }, { id: 2, name: 'Second' }] } };
            const initial = { status: StatusChoices.FETCHING, items: [{ id: 1, name: 'First' }], errors: [] };
            expect(reducer(initial, action)).to.deep.equal({
                status: StatusChoices.FETCH_DONE,
                items: [{ id: 1, name: 'First' }, { id: 2, name: 'Second' }],
                errors: {}
            });
        });

        it('should handle GET_CATEGORIES_FAILED', () => {
            const errors = { unauthorized: 'Auth required' };
            const action = { type: ActionTypes.GET_CATEGORIES_FAILED, errors: errors };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [], errors: errors
            });
        });
    });

    describe('Create category', () => {
        it('should handle CREATE_CATEGORY_REQUEST', () => {
            const action = { type: ActionTypes.CREATE_CATEGORY_REQUEST, payload: { name: 'Test' } };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.CREATING, items: [], errors: {}
            });
        });

        it('should handle CREATE_CATEGORY_RESPONSE', () => {
            const action = { type: ActionTypes.CREATE_CATEGORY_RESPONSE, json: { category: { id: 1, name: 'Test' } } };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.CREATE_DONE, items: [{ id: 1, name: 'Test' }], errors: {}
            });
        });

        it('should handle CREATE_CATEGORY_FAILED', () => {
            const action = { type: ActionTypes.CREATE_CATEGORY_FAILED, errors: { name: 'Could not be empty' } };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [], errors: { name: 'Could not be empty' }
            });
        });
    });

    describe('Edit category', () => {
        const category = { id: 1, name: 'Test' };
        const payload = { name: 'Done' };
        const initialState = { status: StatusChoices.CREATING, errors: {}, items: [category] };

        it('should handle EDIT_CATEGORY_REQUEST', () => {
            const action = { type: ActionTypes.EDIT_CATEGORY_REQUEST, category, payload };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.EDITING, items: [category], errors: {}
            });
        });

        it('should handle EDIT_CATEGORY_RESPONSE', () => {
            const action = { type: ActionTypes.EDIT_CATEGORY_RESPONSE, category,
                json: { category: { id: 1, name: 'Done' } } };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.EDIT_DONE, items: [{ id: 1, name: 'Done' }], errors: {}
            });
        });

        it('should handle EDIT_CATEGORY_FAILED', () => {
            const action = { type: ActionTypes.EDIT_CATEGORY_FAILED, category, payload,
                errors: { name: 'Already exist' } };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [category], errors: { name: 'Already exist' }
            });
        });
    });

    describe('Remove category', () => {
        const category = { id: 1, name: 'Test' };
        const initialState = { status: StatusChoices.INITIAL, errors: {}, items: [category] };

        it('should handle REMOVE_CATEGORY_REQUEST', () => {
            const action = { type: ActionTypes.REMOVE_CATEGORY_REQUEST, category };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.REMOVING, items: [category], errors: {}
            });
        });

        it('should handle REMOVE_CATEGORY_RESPONSE', () => {
            const action = { type: ActionTypes.REMOVE_CATEGORY_RESPONSE, category };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.REMOVE_DONE, items: [], errors: {}
            });
        });

        it('should handle REMOVE_CATEGORY_FAILED', () => {
            const action = { type: ActionTypes.REMOVE_CATEGORY_FAILED, category,
                errors: { id: 'Does not exist' } };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [category], errors: { id: 'Does not exist' }
            });
        });
    });
});
