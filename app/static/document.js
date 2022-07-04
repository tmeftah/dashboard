// show only for cheques et traite

document.addEventListener("DOMContentLoaded", function (event) {
  // Your code to run since DOM is loaded and ready
  var document_div = document.getElementById("document");
  var document_div1 = document.getElementById("document1");

  if (document_div) {
    document.addEventListener("shown.bs.modal", function (e) {
      document.getElementById("amount").focus();
    });

    var document_number = document.getElementById("document_number");
    var paymentmethod = document.getElementById("payment_id").value;
    var due_date = document.getElementById("due_date");
    if (paymentmethod == 2 || paymentmethod == 3) {
      document_div.style.display = "block";
      document_number.removeAttribute("disabled");
      due_date.required = true;
    } else {
      document_div.style.display = "none";
      document_number.setAttribute("disabled", "");
      due_date.required = false;
    }
  }

  if (document_div1) {
    document.addEventListener("shown.bs.modal", function (e) {
      document.getElementById("amount1").focus();
    });
    var document_number1 = document.getElementById("document_number1");
    var paymentmethod1 = document.getElementById("payment_id1").value;
    var due_date1 = document.getElementById("due_date1");
    if (paymentmethod1 == 2 || paymentmethod1 == 3) {
      document_div1.style.display = "block";
      document_number1.removeAttribute("disabled");
      due_date1.required = true;
    } else {
      document_div1.style.display = "none";
      document_number1.setAttribute("disabled", "");
      due_date1.required = false;
    }
  }
});

function ChangePaymentmethod() {
  var document_div = document.getElementById("document");
  var document_number = document.getElementById("document_number");
  var paymentmethod = document.getElementById("payment_id").value;
  var due_date = document.getElementById("due_date");
  document.getElementById("amount").focus();

  if (paymentmethod == 2 || paymentmethod == 3) {
    document_div.style.display = "block";
    document_number.removeAttribute("disabled");
    due_date.required = true;
  } else {
    document_div.style.display = "none";
    document_number.setAttribute("disabled", "");
    due_date.required = false;
  }
}

function ChangePaymentmethod1() {
  var document_div = document.getElementById("document1");
  var document_number = document.getElementById("document_number1");
  var paymentmethod = document.getElementById("payment_id1").value;
  var due_date1 = document.getElementById("due_date1");
  document.getElementById("amount1").focus();

  if (paymentmethod == 2 || paymentmethod == 3) {
    document_div.style.display = "block";
    document_number.removeAttribute("disabled");
    due_date1.required = true;
  } else {
    document_div.style.display = "none";
    document_number.setAttribute("disabled", "");
    due_date1.required = false;
  }
}

function onlyNumberKey(evt) {
  // Only ASCII character in that range allowed
  var alert2 = document.getElementById("alert");
  var ASCIICode = evt.which ? evt.which : evt.keyCode;
  if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57)) {
    alert2.classList.remove("visually-hidden");
    return false;
  }
  alert2.classList.add("visually-hidden");
  return true;
}

function onlyNumberKey1(evt) {
  // Only ASCII character in that range allowed
  var alert2 = document.getElementById("alert1");
  var ASCIICode = evt.which ? evt.which : evt.keyCode;
  if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57)) {
    alert2.classList.remove("visually-hidden");
    return false;
  }
  alert2.classList.add("visually-hidden");
  return true;
}

function checkSize() {
  var input = document.getElementById("foto");
  var alertsize = document.getElementById("alertsize");
  // check for browser support (may need to be modified)
  if (input.files && input.files.length == 1) {
    if (input.files[0].size > 2 * 1024 * 1024) {
      alertsize.classList.remove("visually-hidden");
      input.value = "";

      return false;
    }
  }
  alertsize.classList.add("visually-hidden");
  return true;
}
