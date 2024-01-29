// window.onload = () => {
//   console.log("load");
//   document.cookie = "cookiename= session; value = ";
//   console.log(document.cookie);
// };

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

// async function sendData() {
//   var user1_playlist = window.localStorage.getItem("user1_playlist");
//   var user2_playlist = window.localStorage.getItem("user2_playlist");

//   var user1_songlist = window.localStorage.getItem("user1_songlist");
//   var user2_songlist = window.localStorage.getItem("user2_songlist");

//   const formData = new FormData();

//   // Add a text field
//   formData.append("user1_playlist", user1_playlist);

//   try {
//     const response = await fetch(`${window.origin}/setData`, {
//       method: "POST",
//       // Set the FormData instance as the request body
//       body: formData,
//     });
//     console.log(await response.json());
//   } catch (e) {
//     console.error(e);
//   }

// Form-encoded Request, like from Form
// let fetchFormEncodedRequest = {
//   cache: "no-cache",
//   method: "POST",
//   headers: {
//     "Content-Type": "application/json",
//   },
//   body: {
//     user1_playlist: user1_playlist,
//     user2_playlist: user2_playlist,
//     user1_songlist: user1_songlist,
//     user2_songlist: user2_songlist,
//   },
// };

// fetch(`${window.origin}/setData`, fetchFormEncodedRequest)
//   .then(function (response) {
//     if (response.status != 200) {
//       console.log(response.statusText);
//     }
//     response.json().then(function (data) {
//       console.log(data);
//     });
//   })
//   .catch(function (error) {
//     console.log(error);
//   });
// }
