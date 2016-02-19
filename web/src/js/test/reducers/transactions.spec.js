/* eslint max-nested-callbacks: 0, no-undefined: 0, camelcase: 0 */

import { expect } from 'chai';
import { StatusChoices } from '../../constants/status';
import { ActionTypes } from '../../constants/transactions';
import reducer from '../../reducers/transactions';


describe('Transactions reducer', () => {
    it('should handle initial state', () => {
        expect(reducer(undefined, {})).to.deep.equal({
            status: StatusChoices.INITIAL, items: [], errors: {}
        });
    });

    describe('Get transactions', () => {
        it('should handle GET_TRANSACTIONS_REQUEST', () => {
            const action = { type: ActionTypes.GET_TRANSACTIONS_REQUEST };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FETCHING, items: [], errors: {}
            });
        });

        it('should handle GET_TRANSACTIONS_RESPONSE with empty initial state', () => {
            const transactions = [{ id: 1, decription: 'Meal', amount: 300.0, account_id: 1, category_id: 1 }];
            const action = { type: ActionTypes.GET_TRANSACTIONS_RESPONSE, json: { transactions } };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FETCH_DONE, items: transactions, errors: {}
            });
        });

        it('should handle GET_TRANSACTIONS_RESPONSE with existed state', () => {
            const transactions = [{ id: 2, decription: 'Fuel', amount: 696.0, account_id: 1, category_id: 2 }];
            const action = { type: ActionTypes.GET_TRANSACTIONS_RESPONSE, json: { transactions } };
            const initial = { status: StatusChoices.FETCHING, items: [
                { id: 1, decription: 'Meal', amount: 300.0, account_id: 1, category_id: 1 }
            ] };
            expect(reducer(initial, action)).to.deep.equal({
                status: StatusChoices.FETCH_DONE, items: transactions, errors: {}
            });
        });

        it('should handle GET_TRANSACTIONS_FAILED', () => {
            const errors = { unauthorized: 'Auth required' };
            const action = { type: ActionTypes.GET_TRANSACTIONS_FAILED, errors };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [], errors
            });
        });
    });

    describe('Create transaction', () => {
        it('should handle CREATE_TRANSACTION_REQUEST', () => {
            const action = { type: ActionTypes.CREATE_TRANSACTION_REQUEST,
                payload: { description: 'Meal', amount: 300, account_id: 1, category_id: 1 }
            };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.CREATING, items: [], errors: {}
            });
        });

        it('should handle CREATE_TRANSACTION_RESPONSE', () => {
            const action = { type: ActionTypes.CREATE_TRANSACTION_RESPONSE, json: {
                transaction: { id: 1, description: 'Meal', account_id: 1, category_id: 1 }
            } };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.CREATE_DONE, errors: {},
                items: [{ id: 1, description: 'Meal', account_id: 1, category_id: 1 }]
            });
        });

        it('should handle CREATE_TRANSACTION_FAILED', () => {
            const errors = { category_id: 'Could not be empty' };
            const action = { type: ActionTypes.CREATE_TRANSACTION_FAILED, errors };
            expect(reducer(undefined, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [], errors
            });
        });
    });

    describe('Edit transaction', () => {
        const transaction = { id: 1, description: 'Meal', amount: 300, account_id: 1, category_id: 1 };
        const payload = { amount: 250 };
        const initialState = { status: StatusChoices.INITIAL, errors: {}, items: [transaction] };
        const expected = { id: 1, description: 'Meal', amount: 250, account_id: 1, category_id: 1 };

        it('should handle EDIT_TRANSACTION_REQUEST', () => {
            const action = { type: ActionTypes.EDIT_TRANSACTION_REQUEST, transaction, payload };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.EDITING, items: [transaction], errors: {}
            });
        });

        it('should handle EDIT_TRANSACTION_RESPONSE', () => {
            const action = { type: ActionTypes.EDIT_TRANSACTION_RESPONSE, transaction,
                json: { transaction: {
                    id: 1, description: 'Meal', amount: 250, account_id: 1, category_id: 1 }
                }
            };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.EDIT_DONE, items: [expected], errors: {}
            });
        });

        it('should handle EDIT_TRANSACTION_FAILED', () => {
            const action = { type: ActionTypes.EDIT_TRANSACTION_FAILED, transaction, payload,
                errors: { amount: 'Could not be equal 250' } };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [transaction], errors: { amount: 'Could not be equal 250' }
            });
        });
    });

    describe('Remove transaction', () => {
        const transaction = { id: 1, description: 'Meal', amount: 300, account_id: 1, category_id: 1 };
        const initialState = { status: StatusChoices.INITIAL, errors: {}, items: [transaction] };

        it('should handle REMOVE_TRANSACTION_REQUEST', () => {
            const action = { type: ActionTypes.REMOVE_TRANSACTION_REQUEST, transaction };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.REMOVING, items: [transaction], errors: {}
            });
        });

        it('should handle REMOVE_TRANSACTION_RESPONSE', () => {
            const action = { type: ActionTypes.REMOVE_TRANSACTION_RESPONSE, transaction };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.REMOVE_DONE, items: [], errors: {}
            });
        });

        it('should handle REMOVE_TRANSACTION_FAILED', () => {
            const action = { type: ActionTypes.REMOVE_TRANSACTION_FAILED, transaction,
                errors: { id: 'Does not exist' } };
            expect(reducer(initialState, action)).to.deep.equal({
                status: StatusChoices.FAILED, items: [transaction], errors: { id: 'Does not exist' }
            });
        });
    });
});
