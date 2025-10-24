const users = [];

function tambahUser(event) {
  event.preventDefault();
  const nama = document.getElementById("nama").value;
  const email = document.getElementById("email").value;
  const tanggal_lahir = document.getElementById("tanggal_lahir").value;
  const jenis_kelamin = document.getElementById("jenis_kelamin").value;
  const is_admin = document.getElementById("is_admin").value;

  const user = { nama, email, tanggal_lahir, jenis_kelamin, is_admin };
  users.push(user);
  renderUsers();
  event.target.reset();
}

function hapusUser(index) {
  users.splice(index, 1);
  renderUsers();
}

function renderUsers() {
  const tbody = document.querySelector("#tabel-user tbody");
  tbody.innerHTML = "";
  users.forEach((user, i) => {
    const row = `<tr>
          <td>${user.nama}</td>
          <td>${user.email}</td>
          <td>${user.is_admin === "true" ? "Admin" : "Member"}</td>
          <td><button type="button" onclick="hapusUser(${i})">Hapus</button></td>
        </tr>`;
    tbody.innerHTML += row;
  });
}

function submitSemuaUser() {
  if (users.length === 0) {
    alert("Tambahkan setidaknya satu pengguna.");
    return false;
  }
  document.getElementById("users_json").value = JSON.stringify(users);
  return true;
}
