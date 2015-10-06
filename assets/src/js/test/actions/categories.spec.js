import chai from 'chai';
import sinon from 'sinon';
import sinonChai from 'sinon-chai';
import nock from 'nock';

import { ActionTypes, APIEndpoints } from '../../constants/categories';
import * as actions from '../../actions/categories';

chai.should();
chai.use(sinonChai);


describe('Category actions', () => {
    let dispatchSpy, getStateSpy, action;

    describe('getCategories action', () => {
        beforeEach(() => {
            dispatchSpy = sinon.spy();
            getStateSpy = sinon.spy();
            action = actions.getCategories('token');
        });

        it('should dispatch GET_CATEGORIES_RESPONSE action on success', () => {
            nock('http://localhost:5000')
                .get('/api/categories')
                .reply(200, '{ "categories": [{ "id": 1, "name": "Test" }]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({ type: ActionTypes.GET_CATEGORIES_REQUEST });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_CATEGORIES_RESPONSE,
                    categories: [{ "id": 1, "name": "Test" }]
                });
            });
        });

        it('should dispatch GET_CATEGORIES_FAILED action on failure', () => {
            nock('http://localhost:5000')
                .get('/api/categories')
                .reply(403, 'Forbidden');

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({ type: ActionTypes.GET_CATEGORIES_REQUEST });
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.GET_CATEGORIES_FAILED,
                    errors: 'Forbidden'
                });
            })
        });
    });

    describe('createCategory action', () => {
        beforeEach(() => {
            dispatchSpy = sinon.spy();
            getStateSpy = sinon.spy();
            action = actions.createCategory('token', { name: 'Test' });
        });

        it('should dispatch CREATE_CATEGORY_RESPONSE action on success', () => {
             nock('http://localhost:5000')
                .post('/api/categories', {
                    name: 'Test'
                })
                .reply(200, '{ "category": [{ "id": 1, "name": "Test", "owner_id": 1 }]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({ type: ActionTypes.CREATE_CATEGORY_REQUEST, payload: { name: 'Test' }});
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_CATEGORY_RESPONSE,
                    category: [{ "id": 1, "name": "Test", owner_id: 1 }]
                });
            });
        });

        it('should dispatch CREATE_CATEGORY_FAILED action on failed', () => {
            nock('http://localhost:5000')
                .post('/api/categories', {
                    name: 'Test'
                })
                .reply(400, '{ "errors": [{ "name": "Already exist" }]}', {
                    'Content-Type': 'application/json'
                });

            return action(dispatchSpy, getStateSpy).then(() => {
                dispatchSpy.should.have.callCount(2);
                dispatchSpy.firstCall.should.have.been.calledWith({ type: ActionTypes.CREATE_CATEGORY_REQUEST, payload: { name: 'Test' }});
                dispatchSpy.secondCall.should.have.been.calledWith({
                    type: ActionTypes.CREATE_CATEGORY_FAILED,
                    errors: [ { name: 'Already exist'}]
                });
            })
        });
    })
});
