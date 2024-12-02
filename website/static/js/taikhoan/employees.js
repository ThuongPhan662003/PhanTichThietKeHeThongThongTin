// employeeSelection.js

document.addEventListener('DOMContentLoaded', function () {
  const employeeTable = document.getElementById('employeeTable');
  const selectedEmployeeInput = document.getElementById('selectedEmployee');
  const searchInput = document.getElementById('searchInput');
  const searchField = document.getElementById('searchField');
  let selectedRow = null; // Biến lưu trữ hàng đã chọn
  
  // Lắng nghe sự kiện click vào bảng nhân viên
  employeeTable.addEventListener('click', function (event) {
    const row = event.target.closest('tr');
    if (row && row.hasAttribute('data-id')) {
      if (selectedRow) {
        selectedRow.classList.remove('selected');
      }
      
      row.classList.add('selected');
      const employeeId = row.getAttribute('data-id');
      selectedEmployeeInput.value = employeeId;
      selectedRow = row;
    }
  });
  
  // Hàm lọc bảng nhân viên dựa trên từ khóa và thuộc tính
  function filterTable() {
    const filter = searchInput.value.toLowerCase();
    const selectedField = searchField.value;

    const rows = employeeTable.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const cells = row.getElementsByTagName('td');

      let columnText = '';

      // Lấy dữ liệu từ cột cần tìm kiếm
      if (selectedField === 'maNV') {
        columnText = cells[0].textContent.toLowerCase();
      } else if (selectedField === 'tenNV') {
        columnText = cells[1].textContent.toLowerCase();
      } else if (selectedField === 'phongBan') {
        columnText = cells[2].textContent.toLowerCase();
      }

      // Nếu tìm thấy từ khóa trong cột, hiển thị hàng, nếu không thì ẩn hàng
      if (columnText.indexOf(filter) > -1) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    }
  }

  // Lắng nghe sự kiện khi người dùng nhập từ khóa tìm kiếm hoặc chọn thuộc tính
  searchInput.addEventListener('input', filterTable);
  searchField.addEventListener('change', filterTable);
});
