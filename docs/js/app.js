document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('pre code').forEach((el) => {
        hljs.highlightElement(el);
    });

    const current = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.sidebar-link').forEach((link) => {
        if (link.getAttribute('href') === current) {
            link.classList.add('active');
        }
    });
});
