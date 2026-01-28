document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("book-modal");
  const modalOverlay = document.querySelector(".modal-overlay");
  const modalContent = document.querySelector(".modal-content");
  const borrowBtn = document.getElementById("borrow-btn");

  let selectedBookId = null;
  let isMine = false;
  let isBorrowed = false;

  document.querySelectorAll(".book").forEach(book => {
    if (book.dataset.borrowed === "True") {
      book.classList.add("borrowed");
    }

    book.addEventListener("click", () => {
      selectedBookId = book.dataset.id;
      isBorrowed = book.dataset.borrowed === "True";
      isMine = book.dataset.mine === "True";

      document.getElementById("modal-title").textContent = book.dataset.title;
      document.getElementById("modal-author").textContent = book.dataset.author;
      document.getElementById("modal-section").textContent = 'Scaffale: ' + book.dataset.section;
      document.getElementById("modal-category").textContent = book.dataset.category + ' (' + book.dataset.shortcat + ')';
      document.getElementById("modal-cover").src = book.dataset.cover;

      modalContent.style.backgroundColor = invertedLuminosity(book.dataset.avgColor);
      modalOverlay.style.display = "flex";
      modal.classList.remove("hidden");

      borrowBtn.className = "";
      borrowBtn.disabled = false;

      if (isBorrowed) {
        if (isMine) {
          borrowBtn.textContent = "Restituisci";
          borrowBtn.classList.add("return-btn");
        } else {
          borrowBtn.textContent = "Prestato";
          borrowBtn.classList.add("borrow-btn", "disabled-btn");
          borrowBtn.disabled = true;
        }
      } else {
        borrowBtn.textContent = "Prendi in Prestito";
        borrowBtn.classList.add("borrow-btn");
      }
    });
  });

  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) modal.classList.add("hidden");
  });

  borrowBtn.addEventListener("click", async () => {
    if (!selectedBookId) return;
    if (isMine) {
      const res = await fetch(`/returnbook?book_id=${selectedBookId}`, { method: "POST", credentials: "include" });
      if (res.ok) location.reload();
    } else if (!isBorrowed) {
      const res = await fetch(`/borrow?book_id=${selectedBookId}`, { method: "GET", credentials: "include" });
      if (res.ok) location.reload();
    }
  });
});

function rgbToHsl(r, g, b) {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;
  if (max === min) { h = s = 0; } else {
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

function invertedLuminosity(rgb, alpha = 0.7) {
  const [r, g, b] = rgb.match(/\d+/g).map(Number);
  let [h, s, l] = rgbToHsl(r, g, b);
  l = 100 - l;
  return `hsla(${h.toFixed(0)}, ${s.toFixed(0)}%, ${l.toFixed(0)}%, ${alpha})`;
}

document.querySelectorAll('.page-circle-form').forEach(form => {
  const totalPages = parseInt(form.dataset.totalPages);
  const input = form.querySelector('.page-circle-input');
  const currentPage = parseInt(form.dataset.currentPage) || 1;

  input.addEventListener('focus', () => { input.select(); });
  input.addEventListener('blur', () => { input.value = currentPage; });

  form.addEventListener('submit', e => {
    e.preventDefault();
    let page = parseInt(input.value);
    if (isNaN(page) || page < 1 || page > totalPages) { input.value = currentPage; input.focus(); return; }
    const searchParams = new URLSearchParams(window.location.search);
    searchParams.set('page', page);
    window.location.href = `/?${searchParams.toString()}`;
  });
});


const filter = document.getElementById("filterDropdown");
const menu = filter.querySelector(".filter-menu");
const filterBtn = filter.querySelector(".filter-btn");

const urlParams = new URLSearchParams(window.location.search);

function getFilterValue(key) {
  return urlParams.get(key) || "Qualunque";
}

function updateSelectedOptions() {
  document.querySelectorAll(".filter-category").forEach(category => {
    const filterKey = category.dataset.filter;
    const selectedValue = getFilterValue(filterKey);

    const submenu = document.querySelector(
      `.sub-menu[data-anchor="${category.id}"]`
    );

    if (!submenu) return;

    submenu.querySelectorAll(".sub-menu-option").forEach(option => {
      option.classList.toggle(
        "selected",
        option.dataset.value === selectedValue
      );
    });
  });
}

  const availability = getFilterValue("availability");
  const category = getFilterValue("category");

  const textParts = [];
  if (availability !== "Qualunque") textParts.push(`Disponibilità: ${availability}`);
  if (category !== "Qualunque") textParts.push(`Categoria: ${category}`);

  filterBtn.textContent = textParts.length ? textParts.join(", ") : "Aggiungi Filtri";

filterBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  menu.style.display = menu.style.display === "flex" ? "none" : "flex";
});

document.addEventListener("click", () => {
  menu.style.display = "none";
});

document.querySelectorAll(".filter-category").forEach(category => {
  const id = category.id;
  category.style.anchorName = `--${id}`;

  const submenu = document.querySelector(
    `.sub-menu[data-anchor="${id}"]`
  );

  if (!submenu) return;

  submenu.style.positionAnchor = `--${id}`;

  let hideTimeout;

  const show = () => {
    clearTimeout(hideTimeout);
    submenu.style.display = "flex";
  };

  const hide = () => {
    hideTimeout = setTimeout(() => {
      submenu.style.display = "none";
    }, 200);
  };

  category.addEventListener("mouseenter", () => {
    document.querySelectorAll(".sub-menu").forEach(sm => {
      if (sm !== submenu) sm.style.display = "none";
    });
    show();
  });

  category.addEventListener("mouseleave", hide);

  submenu.addEventListener("mouseenter", show);
  submenu.addEventListener("mouseleave", hide);
});

document.querySelectorAll(".sub-menu-option").forEach(option => {
  option.addEventListener("click", (e) => {
    e.stopPropagation();

const anchorId = option.closest(".sub-menu").dataset.anchor;
const category = document.getElementById(anchorId);
const filterKey = category.dataset.filter;
    const value = option.dataset.value;

    const newParams = new URLSearchParams(window.location.search);
    if (value === "Qualunque") {
      newParams.delete(filterKey);
    } else {
      newParams.set(filterKey, value);
    }

    window.location.search = newParams.toString();
  });
});

updateSelectedOptions();
