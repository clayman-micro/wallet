import { ActionTypes } from 'js/constants/session';
import AuthService from 'js/services/auth';


function loginUserRequest(username, password) {
    return {
        type: ActionTypes.LOGIN_REQUEST,
        username: username,
        password: password
    };
}

function loginUserResponse(token, json) {
    return {
        type: ActionTypes.LOGIN_RESPONSE,
        user: json.user,
        accessToken: token,
        receivedAt: Date.now()
    };
}

function loginUserErrors(errors) {
    return {
        type: ActionTypes.LOGIN_FAILED,
        errors: errors,
        receivedAt: Date.now()
    };
}

export function loginUser(username, password) {
    return dispatch => {
        dispatch(loginUserRequest(username, password));

        return AuthService.login(username, password)
            .then((response) => {
                let token = {
                    value: response.headers.get('X-ACCESS-TOKEN'),
                    expire: parseInt(response.headers.get('X-ACCESS-TOKEN-EXPIRE'), 10)
                };
                return response.json().then(json => dispatch(loginUserResponse(token, json)));
            })
            .catch(error => {
                let errors = {};
                if (typeof error.response !== 'undefined') {
                    if (error.response.status === 400) {
                        error.response.json().then(data => {
                            errors = data;
                        });
                    } else {
                        errors[error.response.status] = error.response.statusText;
                    }
                } else {
                    errors[error.name] = error.message;
                }

                return dispatch(loginUserErrors(errors));
            });
    };
}

export function logoutUser() {
    return {
        type: ActionTypes.LOGOUT
    };
}

export function unauthorizedUser() {
    return {
        type: ActionTypes.UNAUTHORIZED
    };
}
