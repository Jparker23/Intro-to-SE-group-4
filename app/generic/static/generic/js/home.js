function openNav() {
  const sidebar = document.getElementById("productSideBar");
  const menu = document.querySelector(".menuIcon");

  sidebar.classList.add("open");
  menu.style.display = "none";
}

function closeNav() {
  const sidebar = document.getElementById("productSideBar");
  const menu = document.querySelector(".menuIcon");

  sidebar.classList.remove("open");
  menu.style.display = "block";
}