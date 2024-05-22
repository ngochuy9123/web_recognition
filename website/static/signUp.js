console.log("This Is signUp.js");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

let faceDirection = 0;
const dictFaceDirec = {
  0: "Nhin Thang",
  1: "Quay Sang Phai",
  2: "Quay Sang Trai",
  3: "Nhin len",
  4: "Nhin Xuong",
};
let captureInterval;

async function getVideo() {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;

  // Start capturing and processing images at intervals
  captureInterval = setInterval(captureAndProcessImage, 1000); // Capture every second (1000 ms)
}

getVideo();

async function captureAndProcessImage() {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(async (blob) => {
    const formData = new FormData();
    formData.append("image", blob, "capture.png");
    formData.append("faceDirection", faceDirection);
    try {
      const response = await fetch("/signup1", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log(data);
      if (data.isProcess == true) {
        faceDirection += 1;
        if (faceDirection >= 5) {
          alert("Dang ki hoan thanh");
        } else {
          alert(dictFaceDirec[faceDirection]);
        }
      } else {
        console.log("Chua dung huong khuon mat");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }, "image/png");
}
