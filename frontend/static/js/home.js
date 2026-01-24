document.addEventListener("DOMContentLoaded", () => {
  const modal = document.querySelector(".modal")
  const modalOverlay = document.querySelector(".modal-overlay");
  const modalContent = document.querySelector(".modal-content");

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
      closeBookModal()
    }
  });
});

let selectedBookId = null;

function openBookModal(book) {
  selectedBookId = book.dataset.id;
  console.log(book.id)
  document.getElementById("modal-title").textContent = book.dataset.title;
  document.getElementById("modal-author").textContent = book.dataset.author;
  document.getElementById("modal-description").textContent = book.dataset.description;
  document.getElementById("modal-cover").src = book.dataset.cover;
  document.getElementById("book-modal").classList.remove("hidden");
}

document.getElementById('borrow-btn').addEventListener('click', () => {
  if (!selectedBookId) return;
  borrowBook(selectedBookId);
});

async function borrowBook(bookId) {
  try {
    const response = await fetch(`/borrow?book_id=${bookId}`, {
      method: 'GET',
      credentials: 'include'
    });

    let data;
    try {
      data = await response.json();
    } catch {
      window.location.href = response.url;
      return;
    }

    if (data.success) {
      alert('Book borrowed!');
    } else {
      alert(data.message);
    }
  } catch (err) {
    console.error(err);
    alert('An error occurred. Please try again.');
  }
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
  return `hsl(${h.toFixed(0)}, ${s.toFixed(0)}%, ${l.toFixed(0)}%)`;
}

document.querySelectorAll('.page-circle-form').forEach(form => {
  const totalPages = parseInt(form.dataset.totalPages);
  const input = form.querySelector('.page-circle-input');
  const currentPage = parseInt(form.dataset.currentPage) || 1;

  input.addEventListener('focus', () => {
    input.select();
  });

  input.addEventListener('blur', () => {
    input.value = currentPage;
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    let page = parseInt(input.value);
    if (isNaN(page) || page < 1 || page > totalPages) {
      input.value = currentPage;
      input.focus();
      return;
    }

    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set('page', page);
    window.location.href = `/?${searchParams.toString()}`;
  });
});
