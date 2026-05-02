document.addEventListener('DOMContentLoaded', () => {
    // 1. Sticky Navbar
    const navbar = document.getElementById('navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 2. Mobile Menu Toggle
    const mobileToggle = document.getElementById('mobile-toggle');
    const navLinks = document.getElementById('nav-links');
    const navItems = navLinks.querySelectorAll('a');

    mobileToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        const icon = mobileToggle.querySelector('i');
        if (navLinks.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
    });

    // Close mobile menu when clicking a link
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navLinks.classList.remove('active');
            mobileToggle.querySelector('i').classList.remove('fa-times');
            mobileToggle.querySelector('i').classList.add('fa-bars');
        });
    });

    // 3. Smooth Scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Adjust for sticky header height
                const headerOffset = 70;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // 4. Scroll Animations (Intersection Observer)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.15
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => {
        observer.observe(el);
    });

    // 5. Quote Form Submission (UI Only)
    const quoteForm = document.getElementById('quote-form');
    const formMessage = document.getElementById('form-message');

    if (quoteForm) {
        quoteForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Get form values
            const name = document.getElementById('name').value;
            const phone = document.getElementById('phone').value;
            const location = document.getElementById('location').value;
            const requirement = document.getElementById('requirement').value;
            
            // Basic validation
            if (name && phone && location && requirement) {
                const submitBtn = quoteForm.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Submitting...';
                submitBtn.disabled = true;
                
                // Real submission to Backend
                fetch('http://127.0.0.1:5000/api/enquiries', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name, phone, location, requirement})
                })
                .then(res => res.json())
                .then(data => {
                    formMessage.textContent = `Thank you, ${name}! Your request has been received.`;
                    formMessage.className = 'form-message success';
                    quoteForm.reset();
                })
                .catch(err => {
                    formMessage.textContent = 'Failed to submit. Is the server running?';
                    formMessage.className = 'form-message error';
                })
                .finally(() => {
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    setTimeout(() => {
                        formMessage.textContent = '';
                        formMessage.className = 'form-message';
                    }, 5000);
                });
            }
        });
    }

    // 6. Solar Calculator Logic
    const billSlider = document.getElementById('bill-slider');
    const billInput = document.getElementById('bill-input');
    const resSize = document.getElementById('res-size');
    const resSpace = document.getElementById('res-space');
    const resMonthly = document.getElementById('res-monthly');
    const resPayback = document.getElementById('res-payback');
    const resSavings = document.getElementById('res-savings');
    const typeRadios = document.querySelectorAll('input[name="calc-type"]');

    if (billSlider && billInput) {
        const updateCalculator = () => {
            const bill = parseFloat(billInput.value) || 0;
            const type = document.querySelector('input[name="calc-type"]:checked').value;
            
            // Core criteria differences
            let tariff = 8; // Residential avg Rs per unit
            let spacePerKw = 100; // sq ft per kW
            let costPerKw = 60000; // Rs per kW install cost

            if (type === 'commercial') {
                tariff = 11; // Commercial tariff is higher
                spacePerKw = 90; // Often more efficient space utilization
                costPerKw = 50000; // Economies of scale for larger commercial plants
            }

            const unitsPerMonth = bill / tariff;
            
            // Required system size in kW (1 kW generates ~120 units/month)
            let systemSize = unitsPerMonth / 120;
            systemSize = Math.max(1, Math.round(systemSize * 10) / 10); // Minimum 1 kW
            
            const spaceReq = Math.round(systemSize * spacePerKw);
            
            // Financial Projections
            const totalSystemCost = systemSize * costPerKw;
            const monthlySavings = bill; // Assuming 100% offset
            const annualSavings = monthlySavings * 12;
            const lifetimeSavings = annualSavings * 25; // 25 year solar lifespan
            
            // Payback period
            let paybackYears = totalSystemCost / annualSavings;
            paybackYears = Math.max(1, Math.round(paybackYears * 10) / 10);

            resSize.textContent = `${systemSize.toFixed(1)} kW`;
            resSpace.textContent = `${spaceReq} sq.ft`;
            resMonthly.textContent = `₹ ${Math.round(monthlySavings).toLocaleString('en-IN')}`;
            resPayback.textContent = `${paybackYears} Years`;
            resSavings.textContent = `₹ ${lifetimeSavings.toLocaleString('en-IN')}`;
        };

        const updateLimits = () => {
            const type = document.querySelector('input[name="calc-type"]:checked').value;
            if (type === 'commercial') {
                billSlider.max = 500000;
                billSlider.step = 5000;
                if (parseInt(billInput.value) < 10000) {
                    billInput.value = 50000;
                    billSlider.value = 50000;
                }
            } else {
                billSlider.max = 50000;
                billSlider.step = 500;
                if (parseInt(billInput.value) > 50000) {
                    billInput.value = 5000;
                    billSlider.value = 5000;
                }
            }
            updateCalculator();
        };

        typeRadios.forEach(radio => {
            radio.addEventListener('change', updateLimits);
        });

        billSlider.addEventListener('input', (e) => {
            billInput.value = e.target.value;
            updateCalculator();
        });

        billInput.addEventListener('input', (e) => {
            let val = e.target.value;
            if (val < 0) val = 0;
            billSlider.value = val;
            updateCalculator();
        });
        
        // Initial calc
        updateCalculator();
    }

    // 7. FAQ Accordion Logic
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const faqItem = question.parentElement;
            const answer = question.nextElementSibling;
            const isActive = faqItem.classList.contains('active');
            
            // Close all other FAQs (optional, but standard for accordions)
            document.querySelectorAll('.faq-item').forEach(item => {
                item.classList.remove('active');
                item.querySelector('.faq-answer').style.maxHeight = null;
            });
            
            // Toggle the clicked one
            if (!isActive) {
                faqItem.classList.add('active');
                answer.style.maxHeight = answer.scrollHeight + "px";
            }
        });
    });

    // 8. Login Modal Logic
    const loginBtn = document.getElementById('nav-login-btn');
    const loginModal = document.getElementById('login-modal');
    const closeLogin = document.getElementById('close-login');
    const loginTabs = document.querySelectorAll('.login-tab');
    const loginForms = document.querySelectorAll('.login-form');

    if (loginBtn && loginModal) {
        // Open modal
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            loginModal.classList.add('active');
        });

        // Close modal
        closeLogin.addEventListener('click', () => {
            loginModal.classList.remove('active');
        });

        // Close when clicking outside
        loginModal.addEventListener('click', (e) => {
            if (e.target === loginModal) {
                loginModal.classList.remove('active');
            }
        });

        // Tab Switching
        loginTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active from all tabs and forms
                loginTabs.forEach(t => t.classList.remove('active'));
                loginForms.forEach(f => f.classList.remove('active'));
                
                // Add active to clicked tab
                tab.classList.add('active');
                
                // Show corresponding form
                const targetForm = document.getElementById(`${tab.dataset.tab}-login`);
                if (targetForm) targetForm.classList.add('active');
            });
        });

        // Customer Login Submit
        const customerLoginForm = document.getElementById('customer-login');
        if (customerLoginForm) {
            customerLoginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const inputs = customerLoginForm.querySelectorAll('input');
                const username = inputs[0].value;
                const password = inputs[1].value;

                try {
                    const res = await fetch('http://127.0.0.1:5000/api/login/customer', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username, password})
                    });
                    const data = await res.json();
                    if (data.success) {
                        localStorage.setItem('customerData', JSON.stringify(data.customer));
                        window.location.href = 'customer.html';
                    } else {
                        alert(data.message);
                    }
                } catch(e) {
                    alert('Error connecting to backend. Is it running?');
                }
            });
        }

        // Admin Login Submit
        const adminLoginForm = document.getElementById('admin-login');
        if (adminLoginForm) {
            adminLoginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const inputs = adminLoginForm.querySelectorAll('input');
                const username = inputs[0].value;
                const password = inputs[1].value;

                try {
                    const res = await fetch('http://127.0.0.1:5000/api/login/admin', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username, password})
                    });
                    const data = await res.json();
                    if (data.success) {
                        localStorage.setItem('adminLoggedIn', 'true');
                        window.location.href = 'admin.html';
                    } else {
                        alert(data.message);
                    }
                } catch(e) {
                    alert('Error connecting to backend. Is it running?');
                }
            });
        }
    }

    // 9. Load Dynamic Portfolio Projects
    const projectsGrid = document.querySelector('.projects-grid');
    if (projectsGrid) {
        fetch('http://127.0.0.1:5000/api/projects')
            .then(res => res.json())
            .then(data => {
                // Prepend so newest is first
                data.reverse().forEach(proj => {
                    const card = document.createElement('div');
                    card.className = 'project-card animate-on-scroll fade-up is-visible';
                    card.innerHTML = `
                        <div class="project-img-wrapper">
                            <img src="http://127.0.0.1:5000/uploads/${proj.image_path}" alt="${proj.title}">
                            <div class="project-overlay">
                                <h4>${proj.title}</h4>
                                <p>${proj.description}</p>
                            </div>
                        </div>
                    `;
                    projectsGrid.prepend(card);
                });
            })
            .catch(err => console.log('Could not load dynamic projects', err));
    }
});
