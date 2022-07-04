function sendMailClicked(e) {
  var theValue = e;
  var modalContainer = document.getElementById("removeModal");
  var form = document.getElementById("removeForm");
  var myModal = new bootstrap.Modal(modalContainer, { backdrop: "static" });
  form.action = form.action + "/" + e;

  myModal.show();
}
