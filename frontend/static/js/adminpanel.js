const modal = document.getElementById("addBookModal");
const openBtn = document.getElementById("openAddModal");
const closeBtn = document.querySelector(".close");
const coverInput = document.getElementById("coverInput");
const coverDropZone = document.getElementById("coverDropZone");
const coverPreview = document.querySelector("#coverPreview img");

openBtn.onclick = () => modal.style.display = "flex";
closeBtn.onclick = () => modal.style.display = "none";

coverDropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  coverDropZone.style.backgroundColor = "rgba(66, 133, 244, 0.1)";
});

coverDropZone.addEventListener("dragleave", (e) => {
  e.preventDefault();
  coverDropZone.style.backgroundColor = "";
});

coverDropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  coverDropZone.style.backgroundColor = "";
  const files = e.dataTransfer.files;
  if (files.length) {
    coverInput.files = files;
    updateCoverPreview(files[0]);
  }
});

coverInput.addEventListener("change", () => {
  if (coverInput.files.length > 0) {
    updateCoverPreview(coverInput.files[0]);
  } else {
    coverPreview.src = "static/assets/placeholder_cover.png";
  }
});

function updateCoverPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    coverPreview.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

document.getElementById("addBookForm").onsubmit = async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  const payload = new FormData();
  payload.append("title", formData.get("title"));
  payload.append("authorn", formData.get("authorn"));
  payload.append("authors", formData.get("authors"));
  payload.append("section", formData.get("section"));
  payload.append("position", formData.get("position"));
  payload.append("category", formData.get("category"));

  if (coverInput.files.length > 0) {
    payload.append("cover", coverInput.files[0]);
  }

  const res = await fetch("/adminpanel/addbook", {
    method: "POST",
    body: payload
  });

  if (res.ok) {
    modal.style.display = "none";
    location.reload();
  } else {
    const error = await res.text();
    alert("Errore: " + error);
  }
};

const rmBookModal = document.getElementById("rmBookModal");
const openRmBookBtn = document.getElementById("openRemoveModal");
const closeRmBookBtn = document.getElementById("closeRmBookModal");

const confirmBtn = document.getElementById("confirmRmBook");

confirmBtn.classList.remove("disabled");
confirmBtn.classList.add("disabled");

openRmBookBtn.onclick = () => {
  rmBookModal.style.display = "flex";
};

closeRmBookBtn.onclick = () => {
  rmBookModal.style.display = "none";
  document.getElementById("rmBookForm").reset();
};

window.addEventListener("click", (e) => {
  if (e.target === modal) modal.style.display = "none";
  if (e.target === rmBookModal) {
    rmBookModal.style.display = "none";
    rmBookForm.reset();
  }
});

const rmBookForm = document.getElementById("rmBookForm");

rmBookForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const idInput = document.getElementById("rmBookId");
  const bookId = idInput.value;

  if (!bookId) return;

  try {
    const res = await fetch(`/adminpanel/getbook?id=${bookId}`);
    if (!res.ok) throw new Error("Book not found");

    const book = await res.json();

    document.getElementById("rmBookTitle").textContent = book.title;
    document.getElementById("rmBookAuthor").textContent = book.authorn + " " + book.authors;
    document.getElementById("rmBookCover").src = book.cover;

    document.getElementById("confirmRmBook").classList.remove("disabled");

  } catch (err) {
    alert(err.message);
    document.getElementById("confirmRmBook").classList.add("disabled");
  }
});

confirmBtn.addEventListener("click", async () => {
  if (confirmBtn.classList.contains("disabled")) return;

  const bookId = document.getElementById("rmBookId").value;
  if (!bookId) return;

  try {
    const res = await fetch("/adminpanel/removebook", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: `id=${encodeURIComponent(bookId)}`,
    });

    if (!res.ok) throw new Error("Errore nella rimozione del libro");

    const data = await res.json();
    if (data.success) {
      alert("Libro rimosso correttamente");
      rmBookModal.style.display = "none";
      rmBookForm.reset();
      confirmBtn.classList.add("disabled");
      location.reload();
    } else {
      throw new Error(data.message || "Errore sconosciuto");
    }
  } catch (err) {
    alert(err.message);
  }
});

//======//

const editBookModal = document.getElementById("editBookModal");
const openEditModal = document.getElementById("openEditModal");
const closeEditModal = document.getElementById("closeEditModal");
const confirmEditBtn = document.getElementById("confirmEditBook");
const editBookForm = document.getElementById("editBookForm");

const editCoverInput = document.getElementById("editCoverInput");
const editCoverDropZone = document.getElementById("editCoverDropZone");
const editCoverPreview = document.querySelector("#editCoverPreview img");

editCoverDropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  editCoverDropZone.style.backgroundColor = "rgba(66, 133, 244, 0.1)";
});

editCoverDropZone.addEventListener("dragleave", (e) => {
  e.preventDefault();
  editCoverDropZone.style.backgroundColor = "";
});

editCoverDropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  editCoverDropZone.style.backgroundColor = "";
  const files = e.dataTransfer.files;
  if (files.length) {
    editCoverInput.files = files;
    updateEditCoverPreview(files[0]);
  }
});

editCoverInput.addEventListener("change", () => {
  if (editCoverInput.files.length > 0) {
    updateEditCoverPreview(editCoverInput.files[0]);
  } else {
    editCoverPreview.src = "static/assets/placeholder_cover.png";
  }
});

function updateEditCoverPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    editCoverPreview.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

confirmEditBtn.classList.add("disabled");

openEditModal.onclick = () => {
  editBookModal.style.display = "flex";
};

closeEditModal.onclick = () => {
  editBookModal.style.display = "none";
  editBookForm.reset();
  confirmEditBtn.classList.add("disabled");
};

window.addEventListener("click", (e) => {
  if (e.target === editBookModal) {
    editBookModal.style.display = "none";
    editBookForm.reset();
    confirmEditBtn.classList.add("disabled");
  }
});

editBookForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const bookId = document.getElementById("editBookId").value.trim();
  if (!bookId) return;

  try {
    const res = await fetch(`/adminpanel/getbook?id=${bookId}`);
    if (!res.ok) throw new Error("Libro non trovato");

    const book = await res.json();

    document.getElementById("editBookTitle").value = book.title ?? "";
    document.getElementById("editAuthorInputN").value = book.authorn ?? "";
    document.getElementById("editAuthorInputS").value = book.authors ?? "";
    document.getElementById("editBookSection").value = book.section ?? "";
    document.getElementById("editBookPosition").value = book.position ?? "";
    document.getElementById("editBookCategory").value = book.category ?? "";
    console.log(book.section, book.category)

const inputIds = [
  "editBookTitle",
  "editAuthorInputN",
  "editAuthorInputS",
  "editBookSection",
  "editBookCategory",
  "editBookPosition"
];

function updateConfirmButtonState() {
  const allFilled = inputIds.every(id => {
    const el = document.getElementById(id);
    return el && el.value.trim() !== "";
  });

  confirmEditBtn.classList.toggle("disabled", !allFilled);
  confirmEditBtn.disabled = !allFilled;
}

inputIds.forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener("input", updateConfirmButtonState);
});

document.getElementById("editBookId").addEventListener("input", updateConfirmButtonState);

updateConfirmButtonState();

existingCoverPath = book.cover || null;
editCoverPreview.src = existingCoverPath || "static/assets/placeholder_cover.png";

  } catch (err) {
    alert(err.message);
  }
});

confirmEditBtn.addEventListener("click", async () => {
  if (confirmEditBtn.classList.contains("disabled")) return;

  try {
    const id = document.getElementById("editBookId").value.trim();
    const title = document.getElementById("editBookTitle").value.trim();
    const authorn = document.getElementById("editAuthorInputN").value.trim();
    const authors = document.getElementById("editAuthorInputS").value.trim();
    const section = document.getElementById("editBookSection").value.trim();
    const position = document.getElementById("editBookPosition").value.trim();
    const category = document.getElementById("editBookCategory").value;

    if (!id || !title || !authorn || !authors || !section || !position || !category) {
      alert("Compila tutti i campi prima di confermare");
      return;
    }

    const formData = new FormData();
    formData.append("id", id);
    formData.append("title", title);
    formData.append("authorn", authorn);
    formData.append("authors", authors);
    formData.append("section", section);
    formData.append("position", position);
    formData.append("category", category);

    if (editCoverInput.files.length > 0) {
  formData.append("cover", editCoverInput.files[0]);
}

    const res = await fetch("/adminpanel/editbook", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Errore nella modifica");

    const data = await res.json();
    if (!data.success) {
      throw new Error(data.message || "Errore sconosciuto");
    }

    alert("Libro modificato correttamente");
    editBookModal.style.display = "none";
    editBookForm.reset();
    location.reload();

  } catch (err) {
    alert(err.message);
  }
});

//======//

const logList = document.getElementById("logList");

function addLog(text) {
  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.textContent = text;

  logList.appendChild(entry);

  logList.parentElement.scrollTop = logList.parentElement.scrollHeight;
}
document.addEventListener('DOMContentLoaded', () => {
  const logContainer = document.getElementById('logContainer');
  if (logContainer) {
    logContainer.scrollTop = logContainer.scrollHeight;
  }

  loadAdmins();
  attachRemoveHandlers();
});

const edAdmBookModal = document.getElementById("edAdmBookModal");
const openEdAdmModal = document.getElementById("openEdAdmModal");
const closeEdAdmBookModal = document.getElementById("closeEdAdmBookModal");
const adminListContainer = document.getElementById("adminListContainer");
const edAdmBookForm = document.getElementById("edAdmBookForm");
const newAdminInput = document.getElementById("newAdminInput");

let admins = [];

async function removeAdmin(email) {
  if (admins.length <= 1) {
    alert("Non puoi rimuovere l'ultimo admin!");
    return;
  }

  try {
    const formData = new FormData();
    formData.append("subject", email);
    formData.append("action", "1");

    const res = await fetch("/adminpanel/adminchange", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Failed to remove admin");

    window.location.reload(true);
  } catch (err) {
    alert(err.message);
  }
}

edAdmBookForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = newAdminInput.value.trim();
  if (!email || admins.includes(email)) return;

  try {
    const formData = new FormData();
    formData.append("subject", email);
    formData.append("action", "0");

    const res = await fetch("/adminpanel/adminchange", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Failed to add admin");

    window.location.reload(true);
  } catch (err) {
    alert(err.message);
  }
});

openEdAdmModal.onclick = () => {
  edAdmBookModal.style.display = "flex";
  newAdminInput.focus();
  attachRemoveHandlers();
};

closeEdAdmBookModal.onclick = () => {
  edAdmBookModal.style.display = "none";
  edAdmBookForm.reset();
};

window.addEventListener("click", (e) => {
  if (e.target === edAdmBookModal) {
    edAdmBookModal.style.display = "none";
    edAdmBookForm.reset();
  }
});

function loadAdmins() {
  admins = Array.from(
    adminListContainer.querySelectorAll('.admin-input, .golden-admin-input')
  ).map(i => i.value);
}

function attachRemoveHandlers() {
  const removeBtns = adminListContainer.querySelectorAll('.remove-admin-btn');
  removeBtns.forEach(btn => btn.replaceWith(btn.cloneNode(true)));
  const freshBtns = adminListContainer.querySelectorAll('.remove-admin-btn');

  freshBtns.forEach((btn, idx) => {
    const email = admins[idx+1];
    btn.addEventListener('click', () => removeAdmin(email));
  });
}

function clearAdminInputs() {
  newAdminInput.value = '';

  adminListContainer.querySelectorAll(".admin-input").forEach(input => {
    input.value = input.value;
  });
}

closeEdAdmBookModal.onclick = () => {
  edAdmBookModal.style.display = "none";
  edAdmBookForm.reset();
  clearAdminInputs();
};

window.addEventListener("click", (e) => {
  if (e.target === edAdmBookModal) {
    edAdmBookModal.style.display = "none";
    edAdmBookForm.reset();
    clearAdminInputs();
  }
});

window.addEventListener("blur", () => {
  clearAdminInputs();
});