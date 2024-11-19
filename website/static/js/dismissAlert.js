document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert.auto-dismiss');

    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);

        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                bsAlert.close();
            }, 150);
        }, 5000);

        let timeoutId;
        alert.addEventListener('mouseenter', () => {
            clearTimeout(timeoutId);
        });

        alert.addEventListener('mouseleave', () => {
            timeoutId = setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => {
                    bsAlert.close();
                }, 150);
            }, 5000);
        });
    });
});