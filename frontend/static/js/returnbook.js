document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("book-modal");
  const modalOverlay = document.querySelector(".modal-overlay");
  const modalContent = document.querySelector(".modal-content");
  const returnBtn = document.getElementById("return-btn");

  returnBtn.addEventListener("click", async () => {
      const res = await fetch(`/returnbook?book_id=${selectedBookId}`, { method: "POST", credentials: "include" });
      if (res.ok) location.reload();
  });

  document.querySelectorAll(".book").forEach(book => {
    book.addEventListener("click", () => {
      openBookModal(book);
      const avgColor = book.dataset.avgColor;
      modalContent.style.backgroundColor = invertedLuminosity(avgColor);
      modalOverlay.style.display = "flex";
    });
  });

  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
      closeBookModal();
    }
  });
});

let selectedBookId = null;

function openBookModal(book) {
  selectedBookId = book.dataset.id;
  document.getElementById("modal-title").textContent = book.dataset.title;
  document.getElementById("modal-author").textContent = book.dataset.author;
  document.getElementById("modal-cover").src = book.dataset.cover;
  document.getElementById("book-modal").classList.remove("hidden");
}

function closeBookModal() {
  document.getElementById("book-modal").classList.add("hidden");
}

function rgbToHsl(r, g, b) {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;

  if (max === min) {
    h = s = 0;
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }

    h /= 6;
  }

  return [h * 360, s * 100, l * 100];
}

function invertedLuminosity(rgb) {
  const [r, g, b] = rgb.match(/\d+/g).map(Number);
  let [h, s, l] = rgbToHsl(r, g, b);
  l = 100 - l;
  ret = `hsl(${h.toFixed(0)}, ${s.toFixed(0)}%, ${l.toFixed(0)}%)`
  console.log(ret)
  return ret;
}