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
};
