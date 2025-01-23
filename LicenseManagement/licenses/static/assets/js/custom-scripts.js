document.addEventListener('DOMContentLoaded', function() {
    const toggler = document.querySelector('.custom-navbar-toggler');
    const collapse = document.querySelector('.custom-navbar-collapse');
    
    if (toggler && collapse) {
        toggler.addEventListener('click', function() {
            collapse.classList.toggle('show');
        });
    }

    const currentPath = window.location.pathname;

    const paths = {
        products: ['{% url "list_of_products" %}', '{% url "add_new_product" %}'],
        messaging: ['{% url "send_public_message" %}', '{% url "send_private_message" %}', '{% url "inbox" %}', '{% url "messaging" %}'],
        tickets: ['{% url "list_of_tickets" %}', '{% url "create_new_ticket" %}']
    };

    for (const key in paths) {
        if (paths[key].includes(currentPath)) {
            const submenu = document.getElementById(key + '-submenu');
            if (submenu) {
                submenu.style.display = 'block';
            }
        }
    }
    
    function toggleSubmenu(id) {
        const submenu = document.getElementById(id);
        if (submenu) {
            submenu.style.display = submenu.style.display === "block" ? "none" : "block";
        }
    }

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });

    document.querySelectorAll('.animate-on-scroll').forEach(element => {
        observer.observe(element);
    });
});
