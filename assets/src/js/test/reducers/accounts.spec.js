/* eslint max-nested-callbacks: 0, no-undefined: 0, camelcase: 0 */

import { expect } from 'chai';
import { ActionTypes } from '../../constants/accounts';
import reducer from '../../reducers/accounts';


/** @namespace expect(reducer(undefined, action)).to.deep */
/** @namespace expect(reducer(undefined, {})).to.deep */
describe('Accounts reducer', () => {
    it('should handle initial state', () => {
        expect(reducer(undefined, {})).to.deep.equal({
            isFetching: false, items: [], errors: {}
        });
    });

    describe('Get accounts', () => {
        it('should handle GET_ACCOUNTS_REQUEST', () => {
            const action = { type: ActionTypes.GET_ACCOUNTS_REQUEST };
            expect(reducer(undefined, action)).to.deep.equal({
                isFetching: true, items: [], errors: {}
            });
        });

        it('should handle GET_ACCOUNTS_RESPONSE with empty initial state', () => {
            const accounts = [{ id: 1, name: 'Debut card', original_amount: 30000.0 }];
            const action = { type: ActionTypes.GET_ACCOUNTS_RESPONSE, json: { accounts } };
            expect(reducer(undefined, action)).to.deep.equal({
                isFetching: false, items: accounts, errors: {}
            });
        });

        it('should handle GET_ACCOUNTS_RESPONSE with existed state', () => {
            const accounts = [{ id: 1, name: 'Debut card', original_amount: 30000.0 }];
            const action = { type: ActionTypes.GET_ACCOUNTS_RESPONSE, json: { accounts } };
            const initial = { isFetching: true, items: accounts };
            expect(reducer(initial, action)).to.deep.equal({
                isFetching: false, items: accounts, errors: {}
            });
        });

        it('should handle GET_ACCOUNTS_FAILED', () => {
            const errors = { unauthorized: 'Auth requred' };
            const action = { type: ActionTypes.GET_ACCOUNTS_FAILED, errors };
            expect(reducer(undefined, action)).to.deep.equal({
                isFetching: false, items: [], errors
            });
        });
    });

    describe('Create account', () => {
        it('should handle CREATE_ACCOUNT_REQUEST', () => {
            const action = { type: ActionTypes.CREATE_ACCOUNT_REQUEST,
                payload: { name: 'Debit card', origial_amount: 30000.0 } };
            expect(reducer(undefined, action)).to.deep.equal({
                isFetching: true, items: [], errors: {}
            });
        });

        it('should handle CREATE_ACCOUNT_RESPONSE', () => {
            const action = { type: ActionTypes.CREATE_ACCOUNT_RESPONSE, json: {
                account: { id: 1, name: 'Debit card', original_amount: 30000.0 }
            } };
            expect(reducer(undefined, action)).to.deep.equal({
                isFetching: false, items: [{ id: 1, name: 'Debit card', original_amount: 30000.0 }], errors: {}
            });
        });

        it('should handle CREATE_ACCOUNT_FAILED', () => {
            const action = { type: ActionTypes.CREATE_ACCOUNT_FAILED, errors: { name: 'Could not be empty' } };
            expect(reducer(undefined, action)).to.deep.equal({
                isFetching: false, items: [], errors: { name: 'Could not be empty' }
            });
        });
    });

    describe('Edit account', () => {
        const account = { id: 1, name: 'Debit card', original_amount: 30000.0 };
        const payload = { original_amount: 20000.0 };
        const initialState = { isFetching: false, errors: {}, items: [account] };

        it('should handle EDIT_ACCOUNT_REQUEST', () => {
            const action = { type: ActionTypes.EDIT_ACCOUNT_REQUEST, account, payload };
            expect(reducer(initialState, action)).to.deep.equal({
                isFetching: true, items: [account], errors: {}
            });
        });

        it('should handle EDIT_ACCOUNT_RESPONSE', () => {
            const action = { type: ActionTypes.EDIT_ACCOUNT_RESPONSE, account,
                json: { account: { id: 1, name: 'Debit card', original_amount: 20000.0 } } };
            expect(reducer(initialState, action)).to.deep.equal({
                isFetching: false, items: [{ id: 1, name: 'Debit card', original_amount: 20000.0 }], errors: {}
            });
        });

        it('should handle EDIT_ACCOUNT_FAILED', () => {
            const action = { type: ActionTypes.EDIT_ACCOUNT_FAILED, account, payload,
                errors: { name: 'Already exist' } };
            expect(reducer(initialState, action)).to.deep.equal({
                isFetching: false, items: [account], errors: { name: 'Already exist' }
            });
        });
    });

    describe('Remove account', () => {
        const account = { id: 1, name: 'Debit card', original_amount: 30000.0 };
        const initialState = { isFetching: false, errors: {}, items: [account] };

        it('should handle REMOVE_ACCOUNT_REQUEST', () => {
            const action = { type: ActionTypes.REMOVE_ACCOUNT_REQUEST, account };
            expect(reducer(initialState, action)).to.deep.equal({
                isFetching: true, items: [account], errors: {}
            });
        });

        it('should handle REMOVE_ACCOUNT_RESPONSE', () => {
            const action = { type: ActionTypes.REMOVE_ACCOUNT_RESPONSE, account };
            expect(reducer(initialState, action)).to.deep.equal({
                isFetching: false, items: [], errors: {}
            });
        });

        it('should handle REMOVE_ACCOUNT_FAILED', () => {
            const action = { type: ActionTypes.REMOVE_ACCOUNT_FAILED, account,
                errors: { id: 'Does not exist' } };
            expect(reducer(initialState, action)).to.deep.equal({
                isFetching: false, items: [account], errors: { id: 'Does not exist' }
            });
        });
    });
});
