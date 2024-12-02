document.getElementById("editBtn").addEventListener("click", function () {
    // Lấy tất cả các input có class 'editable-field'
    const editableInputs = document.querySelectorAll(".editable-field");

    // Mở khóa các input có class 'editable-field' để chỉnh sửa
    editableInputs.forEach(input => {
        input.removeAttribute("readonly"); 
        input.setAttribute("required", "true");
        
        if (input.id === "ngayvaolam" || input.id === "ngaymothe") {
            flatpickr(input, {
                dateFormat: "d/m/Y",
                maxDate: "today"
            });
        }

        if (input.id === "ngaysinh" ){
            flatpickr(input, {
                dateFormat: 'd/m/Y',
                maxDate: new Date().setFullYear(new Date().getFullYear() - 18)
            })
        }
    });

    // Ẩn nút "Sửa thông tin" và hiện nút "Lưu thông tin"
    document.getElementById("editBtn").style.display = "none";
    document.getElementById("saveBtn").style.display = "inline-block";

});
