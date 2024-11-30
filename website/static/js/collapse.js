document.addEventListener('DOMContentLoaded', function() {
    // Lấy tất cả các collapse
    var collapseElements = document.querySelectorAll('.accordion-collapse');

    collapseElements.forEach(function(element) {
        // Lắng nghe sự kiện 'show.bs.collapse' khi một collapse mở
        element.addEventListener('show.bs.collapse', function () {
            // Đóng các phần tử collapse khác khi mở một phần tử
            collapseElements.forEach((el) => {
                if (el !== element && el.classList.contains('show')) {
                    var bsCollapse = new bootstrap.Collapse(el);
                    bsCollapse.hide(); // Đóng phần tử khác
                }
            });
        });
    });
});
