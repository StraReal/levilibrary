const modal = document.getElementById("addBookModal");
const openBtn = document.getElementById("openAddModal");
const closeBtn = document.querySelector(".close");
const coverInput = document.getElementById("coverInput");
const coverDropZone = document.getElementById("coverDropZone");
const coverPreview = document.querySelector("#coverPreview img");

openBtn.onclick = () => modal.style.display = "flex";
closeBtn.onclick = () => modal.style.display = "none";

window.onclick = (e) => {
  if (e.target == modal) modal.style.display = "none";
};

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
  payload.append("author", formData.get("author"));

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

window.onclick = (e) => {
  if (e.target === rmBookModal) {
    rmBookModal.style.display = "none";
    document.getElementById("rmBookForm").reset();
  }
};

const rmBookForm = document.getElementById("rmBookForm");

rmBookForm.addEventListener("submit", async (e) => {
  e.preventDefault(); // stop page reload

  const idInput = document.getElementById("rmBookId");
  const bookId = idInput.value;

  if (!bookId) return;

  try {
    const res = await fetch(`/adminpanel/getbook?id=${bookId}`);
    if (!res.ok) throw new Error("Book not found");

    const book = await res.json();

    document.getElementById("rmBookTitle").textContent = book.title;
    document.getElementById("rmBookAuthor").textContent = book.author;
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
