// Simple JavaScript for enhanced user experience

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        if (button.textContent.includes('Delete')) {
            button.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this item?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Form validation for book addition
    const bookForm = document.querySelector('.book-form');
    if (bookForm) {
        bookForm.addEventListener('submit', function(e) {
            const title = this.querySelector('input[name="title"]').value.trim();
            const author = this.querySelector('input[name="author"]').value.trim();
            const isbn = this.querySelector('input[name="isbn"]').value.trim();
            const copies = this.querySelector('input[name="copies"]').value;

            if (!title || !author || !isbn || !copies) {
                alert('Please fill in all fields');
                e.preventDefault();
                return;
            }

            if (parseInt(copies) < 1) {
                alert('Number of copies must be at least 1');
                e.preventDefault();
                return;
            }
        });
    }

    // Search form enhancement
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && this.value.trim() === '') {
                    alert('Please enter a search term');
                    e.preventDefault();
                }
            });
        }
    }

    // Add loading state to buttons
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Loading...';
                submitBtn.disabled = true;
            }
        });
    });
});