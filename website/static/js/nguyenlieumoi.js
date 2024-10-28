// Khi bấm nút, hiển thị form
document.getElementById('showFormButton').addEventListener('click', function () {
    var form = document.getElementById('addIngredientForm');
    var hideform = document.getElementById('addIngredientForm2')
    if (form.style.display === "none") {
        form.style.display = "block"; // Hiển thị form
        hideform.style.display = "none";
    } else {
        form.style.display = "none"; // Ẩn form nếu đang hiển thị
        hideform.style.display = "none";
    }
});