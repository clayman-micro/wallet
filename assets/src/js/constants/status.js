import keyMirror from 'keyMirror';

export const StatusChoices = keyMirror({
    INITIAL: '',
    FETCHING: '',
    FETCH_DONE: '',
    CREATING: '',
    CREATE_DONE: '',
    EDITING: '',
    EDIT_DONE: '',
    REMOVING: '',
    REMOVE_DONE: '',
    FAILED: ''
});
