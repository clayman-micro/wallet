/* eslint max-nested-callbacks: 0 camelcase: 0 */

import chai from 'chai';
import sinon from 'sinon';
import sinonChai from 'sinon-chai';
import nock from 'nock';

import { ActionTypes } from '../../constants/categories';
import * as actions from '../../actions/categories';

chai.should();
chai.use(sinonChai);


describe('Category actions', () => {
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

    describe('getCategories action', () => {
        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.getCategories();
        });

        it('should dispatch GET_CATEGORIES_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .get('/api/categories')
                .reply(200, '{ "categories": [{ "id": 1, "name": "Test" }]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.GET_CATEGORIES_REQUEST
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_CATEGORIES_RESPONSE,
                    json: { categories: [{ id: 1, name: 'Test' }] }
                });
            });
        });

        it('should dispatch GET_CATEGORIES_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .get('/api/categories')
                .reply(403, 'Forbidden');

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.GET_CATEGORIES_REQUEST
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_CATEGORIES_FAILED,
                    errors: 'Forbidden'
                });
            });
        });
    });

    describe('createCategory action', () => {
        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.createCategory({ name: 'Test' });
        });

        it('should dispatch CREATE_CATEGORY_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .post('/api/categories', {
                    name: 'Test'
                })
                .reply(200, '{"category":{"id": 1, "name": "Test", "owner_id": 1}}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_CATEGORY_REQUEST,
                    payload: { name: 'Test' }
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_CATEGORY_RESPONSE,
                    json: { category: { id: 1, name: 'Test', owner_id: 1 } }
                });
            });
        });

        it('should dispatch CREATE_CATEGORY_FAILED action on failed', () => {
            nock('http://localhost:5000')
                .post('/api/categories', {
                    name: 'Test'
                })
                .reply(400, '{"errors": [{"name": "Already exist"}]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_CATEGORY_REQUEST,
                    payload: { name: 'Test' }
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_CATEGORY_FAILED,
                    payload: { name: 'Test' },
                    errors: [{ name: 'Already exist' }]
                });
            });
        });
    });

    describe('editCategory action', () => {
        let category = { id: 1, name: 'Normal' };

        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.editCategory(category, { name: 'Test' });
        });

        it('should dispatch EDIT_CATEGORY_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .put('/api/categories/1', {
                    name: 'Test'
                })
                .reply(200, '{  "category": [{ "id": 1, "name": "Test", "owner_id": 1 }]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_CATEGORY_REQUEST,
                    payload: { name: 'Test' }, category: category
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_CATEGORY_RESPONSE,
                    category: category,
                    json: { category: [{ id: 1, name: 'Test', owner_id: 1 }] }
                });
            });
        });

        it('should dispatch EDIT_CATEGORY_FAILED action on failed', () => {
            nock('http://localhost:5000')
                .put('/api/categories/1', {
                    name: 'Test'
                })
                .reply(400, '{ "errors": [{ "name": "Already exist" }]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_CATEGORY_REQUEST,
                    payload: { name: 'Test' }, category: category
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.EDIT_CATEGORY_FAILED,
                    category: category,
                    payload: { name: 'Test' },
                    errors: [{ name: 'Already exist' }]
                });
            });
        });
    });

    describe('removeCategory action', () => {
        let category = { id: 1, name: 'Normal' };

        beforeEach(() => {
            dispatchSpy = sinon.spy();
            action = actions.removeCategory(category);
        });

        it('should dispatch REMOVE_CATEGORY_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .delete('/api/categories/1')
                .reply(200, 'removed');

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_CATEGORY_REQUEST,
                    category: category
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_CATEGORY_RESPONSE,
                    category: category
                });
            });
        });

        it('should dispatch REMOVE_CATEGORY_FAILED action on failed', () => {
            nock('http://localhost:5000')
                .delete('/api/categories/1')
                .reply(400, '{ "errors": { "id": "Does not exist" }}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_CATEGORY_REQUEST,
                    category: category
                });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.REMOVE_CATEGORY_FAILED,
                    category: category,
                    errors: { id: 'Does not exist' }
                });
            });
        });
    });
});
