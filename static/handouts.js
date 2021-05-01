window.onload = () => {
    let currentLength = localStorage.getItem('markserve.printQueueLength') || 0;
    for (let i = 0; i < currentLength; i++) {
        const content = localStorage.getItem(`markserve.printQueueItem${i}`);
        let el = document.createElement('div');
        document.body.appendChild(el);
        el.outerHTML = content;
    }
    document.querySelectorAll('.handout').forEach((el, i) => {
        const button = el.querySelector('button');
        button.innerText = 'Remove';
        button.addEventListener('click', () => {
            removeFromPrintQueue(i);
            document.body.removeChild(el);
        });
    });
};

function removeFromPrintQueue(i) {
    let currentLength = localStorage.getItem('markserve.printQueueLength');
    localStorage.removeItem(`markserve.printQueueItem${i}`);
    localStorage.setItem('markserve.printQueueLength', --currentLength);
}
