document.addEventListener("DOMContentLoaded", function() {
    console.log("Website Loaded!");

    // scroll container
    const scrollContainer = document.querySelector('.image-scroll');
    let scrollAmount = 160 + 16; // image width + gap

    // arrow key navigation
    window.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') {
            scrollContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        }
        if (e.key === 'ArrowLeft') {
            scrollContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
    });

    // quickview
    const quickview = document.getElementById('quickview');
    const quickviewImg = quickview.querySelector('img');

    document.querySelectorAll('.image-scroll img').forEach(img => {
        img.addEventListener('click', () => {
            quickviewImg.src = img.src;             // show clicked image
            quickview.classList.remove('hidden');   // reveal lightbox
        });
    });

    quickview.addEventListener('click', () => {
        quickview.classList.add('hidden');         // hide overlay
        quickviewImg.src = '';                      // clear src
    });
});