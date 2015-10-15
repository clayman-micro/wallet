/* eslint max-nested-callbacks: 0 camelcase: 0 */

import chai from 'chai';
import sinon from 'sinon';
import sinonChai from 'sinon-chai';
import nock from 'nock';

import { ActionTypes } from '../../constants/transactions';
import * as actions from '../../actions/transactions';

chai.should();
chai.use(sinonChai);


describe('Transaction actions', () => {
    let dispatchSpy;
    let getState = function () {
        return {
            session: {
                accessToken: {
                    value: 'token',
                    isValid: function () {
                        return true;
                    }
                }
            }
        };
    };
    let action;

    describe('getTransactions action', () => {
        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.getTransactions();
        });

        it('should dispatch GET_TRANSACTIONS_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .get('/api/transactions')
                .reply(200,
                    '{"transactions":[{"id":1,"description":"Meal","amount":300,"account_id":1,"category_id":1}]}',
                    { 'Content-Type': 'application/json' });

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.GET_TRANSACTIONS_REQUEST
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_TRANSACTIONS_RESPONSE,
                    json: { transactions: [{ id: 1, description: 'Meal', amount: 300, account_id: 1, category_id: 1 }] }
                });
            });
        });

        it('should dispatch GET_TRANSACTIONS_RESPONSE action on failure', () => {
            nock('http://localhost:5000')
                .get('/api/transactions')
                .reply(403, 'Forbidden');

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.GET_TRANSACTIONS_REQUEST
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_TRANSACTIONS_FAILED,
                    errors: 'Forbidden'
                });
            });
        });
    });

    describe('createTransaction action', () => {
        let rawTransaction = { description: 'Meal', amount: 300, category_id: 1, account_id: 1 };

        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.createTransaction(rawTransaction);
        });

        it('should dispatch CREATE_TRANSACTION_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .post('/api/transactions', rawTransaction)
                .reply(200,
                    '{"transaction":{"id":1,"description":"Meal","amount":300,"account_id":1,"category_id":1}}',
                    { 'Content-Type': 'application/json' });

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_TRANSACTION_REQUEST,
                    payload: rawTransaction
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_TRANSACTION_RESPONSE,
                    json: { transaction: { id: 1, description: 'Meal', amount: 300, account_id: 1, category_id: 1 } }
                });
            });
        });

        it('should dispatch CREATE_TRANSACTION_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .post('/api/transactions', rawTransaction)
                .reply(400, '{"errors":{"category_id":"Does not exist"}}',
                    { 'Content-Type': 'application/json' });

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_TRANSACTION_REQUEST,
                    payload: rawTransaction
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_TRANSACTION_FAILED,
                    payload: rawTransaction,
                    errors: { category_id: 'Does not exist' }
                });
            });
        });
    });

    describe('editTransaction action', () => {
        let transaction = { id: 1, description: 'Meal', amount: 300, category_id: 1, account_id: 1 };

        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.editTransaction(transaction, { amount: 330 });
        });

        it('should dispatch EDIT_TRANSACTION_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .put('/api/transactions/1', {
                    amount: 330
                })
                .reply(200,
                    '{"transaction":{"id":1,"description":"Meal","amount":330,"account_id":1,"category_id":1}}',
                    { 'Content-Type': 'application/json' });

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_TRANSACTION_REQUEST,
                    payload: { amount: 330 },
                    transaction: transaction
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_TRANSACTION_RESPONSE,
                    transaction: transaction,
                    json: { transaction: { id: 1, description: 'Meal', amount: 330, account_id: 1, category_id: 1 } }
                });
            });
        });

        it('should dispatch EDIT_TRANSACTION_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .put('/api/transactions/1', {
                    amount: 330
                })
                .reply(400, '{"errors":{"amount": "Could not be equal 330"}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_TRANSACTION_REQUEST,
                    payload: { amount: 330 },
                    transaction: transaction
                });

                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_TRANSACTION_FAILED,
                    payload: { amount: 330 },
                    transaction: transaction,
                    errors: { amount: 'Could not be equal 330' }
                });
            });
        });
    });

    describe('removeTransaction action', () => {
        let transaction = { id: 1, description: 'Meal', amount: 300, category_id: 1, account_id: 1 };

        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.removeTransaction(transaction);
        });

        it('should dispatch REMOVE_TRANSACTION_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .delete('/api/transactions/1')
                .reply(200, 'removed');

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_TRANSACTION_REQUEST, transaction
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_TRANSACTION_RESPONSE, transaction
                });
            });
        });

        it('should dispatch REMOVE_TRANSACTION_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .delete('/api/transactions/1')
                .reply(400, '{"errors":{"id": "Does not exist"}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getState).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_TRANSACTION_REQUEST, transaction
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_TRANSACTION_FAILED, transaction,
                    errors: { id: 'Does not exist' }
                });
            });
        });
    });
});
