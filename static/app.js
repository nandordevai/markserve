window.onload = () => {
    document.querySelector('.tagselector .tags').addEventListener('click', (e) => {
        e.target.classList.add('active');
        document.querySelector('.tagselector .pages').classList.remove('active');
        document.querySelector('.taglist').classList.remove('hidden');
        document.querySelector('.pagelist').classList.add('hidden');
    });
    document.querySelector('.tagselector .pages').addEventListener('click', (e) => {
        e.target.classList.add('active');
        document.querySelector('.tagselector .tags').classList.remove('active');
        document.querySelector('.pagelist').classList.remove('hidden');
        document.querySelector('.taglist').classList.add('hidden');
    });

    document.querySelectorAll('.handout').forEach((handout) => {
        const button = document.createElement('button');
        button.appendChild(document.createTextNode('Add to queue'));
        handout.appendChild(button);
        button.addEventListener('click', () => { addToPrintQueue(handout); });
    });

    document.querySelector('.print').addEventListener('click', () => {
        window.location = '/handouts';
    });

    document.querySelector('.export').addEventListener('click', () => {
        window.location = '/export';
    });

    const currentLength = localStorage.getItem('markserve.printQueueLength') || 0;
    if (currentLength > 0) {
        document.querySelector('.print').classList.remove('hidden');
    }
};

function addToPrintQueue(el) {
    const content = el.outerHTML;
    let currentLength = localStorage.getItem('markserve.printQueueLength') || 0;
    localStorage.setItem(`markserve.printQueueItem${currentLength}`, content);
    localStorage.setItem('markserve.printQueueLength', ++currentLength);
    document.querySelector('.print').classList.remove('hidden');
}
