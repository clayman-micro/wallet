export function getClientHeight() {
    let height = window.innerHeight;

    if (!height) {
        height = document.documentElement.clientHeight;

        if (!height) {
            height = document.body.offsetHeight;
        }
    }

    return height;
}