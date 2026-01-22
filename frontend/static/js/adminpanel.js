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
