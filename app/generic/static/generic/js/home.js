function openNav() {
  const sidebar = document.getElementById("productSideBar");
  const menu = document.querySelector(".menuIcon");
  sidebar.classList.toggle("open");
  menu.classList.toggle("open");
}
function closeNav() {
  document.getElementById("productSideBar")?.classList.remove("open");
  document.getElementById("sidebarOverlay")?.classList.remove("open");
}