import jsdom from 'node-jsdom';

global.document = jsdom.jsdom('<!doctype html><html><body></body></html>');
global.window = document.defaultView;

// from mocha-jsdom https://github.com/rstacruz/mocha-jsdom/blob/master/index.js#L80
function propagateToGlobal(window) {
    for (let key in window) {
        if (!window.hasOwnProperty(key)) {
            continue;
        }

        if (key in global) {
            continue;
        }

        global[key] = window[key];
    }
}

// take all properties of the window object and also attach it to the
// mocha global object
propagateToGlobal(global.window);
