document.getElementById("editBtn").addEventListener("click", function () {
    // Lấy tất cả các input có class 'editable-field'
    const editableInputs = document.querySelectorAll(".editable-field");

    // Mở khóa các input có class 'editable-field' để chỉnh sửa
    editableInputs.forEach(input => {
        input.removeAttribute("readonly");  // Loại bỏ readonly
        input.setAttribute("required", "true");  // Thêm required cho những input cần thiết
        
        if (input.id === "ngayvaolam" || input.id === "ngaysinh" || input.id === "ngaymothe") {
            flatpickr(input, {
                dateFormat: "d/m/Y",
                clickOpens: true
            });
        }
    });

    // Ẩn nút "Sửa thông tin" và hiện nút "Lưu thông tin"
    document.getElementById("editBtn").style.display = "none";
    document.getElementById("saveBtn").style.display = "inline-block";

});
