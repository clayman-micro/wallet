/* eslint max-nested-callbacks: 0 camelcase: 0 */

import chai from 'chai';
import sinon from 'sinon';
import sinonChai from 'sinon-chai';
import nock from 'nock';

import { ActionTypes } from '../../constants/accounts';
import * as actions from '../../actions/accounts';

chai.should();
chai.use(sinonChai);


/** @namespace dispatchSpy.firstCall.should.have.been */
/** @namespace dispatchSpy.secondCall.should.have.been */
describe('Account actions', () => {
    let dispatchSpy;
    let getStateSpy = function () {
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

    describe('getAccounts action', () => {
        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.getAccounts();
        });

        it('should dispatch GET_ACCOUNTS_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .get('/api/accounts')
                .reply(200, '{ "accounts": [{ "id": 1, "name": "Debit", "original_amount": 30000.0 }]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.GET_ACCOUNTS_REQUEST
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_ACCOUNTS_RESPONSE,
                    json: { accounts: [{ id: 1, name: 'Debit', original_amount: 30000.0 }] }
                });
            });
        });

        it('should dispatch GET_ACCOUNTS_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .get('/api/accounts')
                .reply(403, 'Forbidden');

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.GET_ACCOUNTS_REQUEST
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_ACCOUNTS_FAILED,
                    errors: 'Forbidden'
                });
            });
        });
    });

    describe('createAccount action', () => {
        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.createAccount({ name: 'Debit card', original_amount: 30000.0 });
        });

        it('should dispatch CREATE_ACCOUNT_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .post('/api/accounts', {
                    name: 'Debit card',
                    original_amount: 30000.0
                })
                .reply(200, '{"account":{"id": 1, "name": "Debit card", "original_amount": 30000.0, "owner_id": 1}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_ACCOUNT_REQUEST,
                    payload: { name: 'Debit card', original_amount: 30000.0 }
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_ACCOUNT_RESPONSE,
                    json: { account: { id: 1, name: 'Debit card', original_amount: 30000.0, owner_id: 1 } }
                });
            });
        });

        it('should dispatch CREATE_ACCOUNT_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .post('/api/accounts', {
                    name: 'Debit card',
                    original_amount: 30000.0
                })
                .reply(400, '{"errors": {"name": "Already exist"}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_ACCOUNT_REQUEST,
                    payload: { name: 'Debit card', original_amount: 30000.0 }
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_ACCOUNT_FAILED,
                    payload: { name: 'Debit card', original_amount: 30000.0 },
                    errors: { name: 'Already exist' }
                });
            });
        });
    });

    describe('editAccount action', () => {
        let account = { id: 1, name: 'Debit card', original_amount: 30000.0 };

        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.editAccount(account, { original_amount: 20000.0 });
        });

        it('should dispatch EDIT_ACCOUNT_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .put('/api/accounts/1', {
                    original_amount: 20000.0
                })
                .reply(200, '{"account": {"id": 1, "name": "Debit card", "original_amount": 20000.0}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_ACCOUNT_REQUEST,
                    payload: { original_amount: 20000.0 }, account: account
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_ACCOUNT_RESPONSE, account,
                    json: { account: { id: 1, name: 'Debit card', original_amount: 20000.0 } }
                });
            });
        });

        it('should dispatch EDIT_ACCOUNT_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .put('/api/accounts/1', {
                    original_amount: 20000.0
                })
                .reply(400, '{"errors":{"original_amount": "Could not be equal 20000.0"}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_ACCOUNT_REQUEST,
                    payload: { original_amount: 20000.0 }, account: account
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_ACCOUNT_FAILED, account,
                    payload: { original_amount: 20000.0 },
                    errors: { original_amount: "Could not be equal 20000.0" }
                });
            });
        });
    });

    describe('removeAccount action', () => {
        let account = { id: 1, name: 'Debit card', original_amount: 30000.0 };

        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.removeAccount(account);
        });

        it('should dispatch REMOVE_ACCOUNT_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .delete('/api/accounts/1')
                .reply(200, 'removed');

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_ACCOUNT_REQUEST, account
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_ACCOUNT_RESPONSE, account
                });
            });
        });

        it('should dispatch REMOVE_ACCOUNT_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .delete('/api/accounts/1')
                .reply(400, '{"errors": {"id": "Does not exist"}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_ACCOUNT_REQUEST, account
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_ACCOUNT_FAILED, account,
                    errors: { id: 'Does not exist' }
                });
            });
        });
    });
});
