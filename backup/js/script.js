document.addEventListener('DOMContentLoaded', function () {
    console.log('Twt Electronics - Premium Sound Experience');

    // Add to cart functionality (Mockup for now, will connect to backend)
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            console.log('Adding product to cart:', productId);
            // We will implement AJAX call here later
            animateCart();
        });
    });

    function animateCart() {
        const cartCount = document.getElementById('cart-count');
        cartCount.style.transform = 'scale(1.5)';
        setTimeout(() => {
            cartCount.style.transform = 'scale(1)';
        }, 200);
    }
});
