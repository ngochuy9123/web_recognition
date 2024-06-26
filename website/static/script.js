const btnOpenCam = document.getElementById("btnOpenCam");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");
const btnStopCam = document.getElementById("btnStopCam");
const inpUsername = document.getElementById("inpUsername");
const inpEmail = document.getElementById("inpEmail");
const inpPhone = document.getElementById("inpPhone");

console.log("This Is Script.js");

let captureInterval;

btnOpenCam.addEventListener("click", async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;

  // Start capturing and processing images at intervals
  captureInterval = setInterval(captureAndProcessImage, 1000); // Capture every second (1000 ms)
});

async function captureAndProcessImage() {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(async (blob) => {
    const formData = new FormData();
    formData.append("image", blob, "capture.png");

    try {
      const response = await fetch("/processImg", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data);
      if (data.status == 1) {
        // const img = new Image();
        // img.src = "data:image/jpeg;base64," + data.image;
        // img.onload = () => {
        //   context.clearRect(0, 0, canvas.width, canvas.height);
        //   context.drawImage(img, 0, 0, canvas.width, canvas.height);
        // };
        inpUsername.value = data.username;
        inpEmail.value = data.email;
        inpPhone.value = data.phone;
      } else {
        console.log("Unknown");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }, "image/png");
}

// Optionally, you can add a stop button to stop the capture

btnStopCam.addEventListener("click", () => {
  clearInterval(captureInterval);
  if (video.srcObject) {
    const tracks = video.srcObject.getTracks();
    tracks.forEach((track) => track.stop());
    video.srcObject = null;
  }
});

document.getElementById("signUpBtn").addEventListener("click", function () {
  window.location.href = "/signup";
});
