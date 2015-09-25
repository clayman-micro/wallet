import { ActionTypes } from '../constants/Session';

const initialState = {
    user: null
};

export default function session(state = initialState, action) {
    if (action.type === ActionTypes.LOGIN_REQUEST) {
        return state;
    } else if (action.type === ActionTypes.LOGIN_RESPONSE) {
        return state;
    } else if (action.type === ActionTypes.UNAUTHORIZED) {
        return state;
    } else if (action.type === ActionTypes.LOGOUT) {
        return state;
    } else {
        return state;
    }
}
