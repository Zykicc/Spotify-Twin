$("#column1-button").click(function () {
  $("#loading-overlay").css({ display: "initial" });
  console.log("sdadasdsaadada");
});

function showLoading() {
  var overlay = document.getElementById("loading-overlay");
  overlay.style.display = "flex";

  var msg0 = document.getElementById("loadingMsg0");
  var msg1 = document.getElementById("loadingMsg1");
  var msg2 = document.getElementById("loadingMsg2");
  var msg3 = document.getElementById("loadingMsg3");

  msg0.style.display = "flex";

  setTimeout(() => {
    msg0.style.display = "none";
    msg1.style.display = "flex";
  }, "15000");

  setTimeout(() => {
    msg0.style.display = "none";
    msg1.style.display = "none";
    msg2.style.display = "flex";
  }, "30000");

  setTimeout(() => {
    msg0.style.display = "none";
    msg1.style.display = "none";
    msg2.style.display = "none";
    msg3.style.display = "flex";
  }, "45000");
}
