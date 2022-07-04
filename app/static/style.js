function show_sidebar() {
  var sidebar = document.getElementById("sidebar");
  var icon = document.getElementById("icon-sidebar-show-btn");
  var btn = document.getElementById("sidebar-show-btn");
  var overlay = document.getElementById("overlay");

  sidebar.classList.toggle("show-sidebar");
  btn.classList.toggle("expand");

  if (sidebar.classList.contains("show-sidebar")) {
    icon.classList.remove("bi-chevron-double-right");
    icon.classList.add("bi-chevron-double-left");
    overlay.classList.add("active");
  } else {
    icon.classList.add("bi-chevron-double-right");
    icon.classList.remove("bi-chevron-double-left");
    overlay.classList.remove("active");
  }
}
