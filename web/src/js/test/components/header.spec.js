import { expect } from 'chai';
import React from 'react';
import TestUtils from 'react-addons-test-utils';

import Header from '../../components/header/header';


describe('Header component', () => {
    let component;

    describe('with title and without buttons', () => {
        beforeEach(() => {
            component = TestUtils.renderIntoDocument(
                <Header title="Test" />
            );
        });

        it('should have title', () => {
            const headerTitle = TestUtils.findRenderedDOMComponentWithClass(
                component, 'header__title'
            );

            expect(headerTitle.innerHTML).to.equal('Test');
        });

        it('should not have buttons', () => {
            const buttons = TestUtils.scryRenderedDOMComponentsWithClass(
                component, 'header__button'
            );

            expect(buttons.length).to.equal(0);
        });
    });

    describe('with buttons', () => {
        it('should have left button', () => {
            component = TestUtils.renderIntoDocument(
                <Header title="Test" leftButton={{ text: 'Back', path: '#' }} />
            );

            const buttons = TestUtils.scryRenderedDOMComponentsWithClass(
                component, 'header__button_left'
            );

            expect(buttons.length).to.equal(1);
            expect(buttons[0].innerHTML).to.equal('Back');
        });

        it('should have right button', () => {
            component = TestUtils.renderIntoDocument(
                <Header title="Test" rightButton={{ text: 'Remove', path: '#' }} />
            );

            const buttons = TestUtils.scryRenderedDOMComponentsWithClass(
                component, 'header__button_right'
            );

            expect(buttons.length).to.equal(1);
            expect(buttons[0].innerHTML).to.equal('Remove');
        });
    });
});
