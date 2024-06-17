console.log("This Is signUp.js");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");
const btnSignUp = document.getElementById("btnSignUp");
const inpUsername = document.getElementById("inpUsername");
const inpEmail = document.getElementById("inpEmail");
const inpPhone = document.getElementById("inpPhone");

let faceDirectionCount = 0;
const dictFaceDirec = {
  0: "Nhin Thang",
  1: "Quay Sang Phai",
  2: "Quay Sang Trai",
  3: "Nhin len",
  4: "Nhin Xuong",
};
let captureInterval;
let lstFaceDirection = [];

btnSignUp.addEventListener("click", insertAccount);

async function insertAccount(event) {
  event.preventDefault(); // Ngăn không cho form được gửi đi theo cách thông thường
  let username = document.getElementById("inpUsername").value;
  let email = document.getElementById("inpEmail").value;
  let phone = document.getElementById("inpPhone").value;

  const formData = new FormData();
  formData.append("username", username);
  formData.append("email", email);
  formData.append("phone", phone);

  try {
    const response = await fetch("/signup", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (data.status == true) {
      alert("Account created successfully!");
      // Thực hiện các hành động tiếp theo, ví dụ: gọi hàm getVideo
      hiddenFormSignUp();
      getVideo();
    } else {
      alert("Failed to create account.");
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

async function getVideo() {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;

  // Start capturing and processing images at intervals
  captureInterval = setInterval(captureAndProcessImage, 1000); // Capture every second (1000 ms)
}

// getVideo();

async function captureAndProcessImage() {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob(async (blob) => {
    const formData = new FormData();
    formData.append("image", blob, "capture.png");
    formData.append("lstFaceDirection", JSON.stringify(lstFaceDirection));
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
      if (data.status == true) {
        // Kiem soat khi them thang, trai-phai, tren-duoi
        if (lstFaceDirection.length < 1) {
          if (data.faceDirection == 0) {
            lstFaceDirection.push(data.faceDirection);
          }
        } else if (lstFaceDirection.length > 0 && lstFaceDirection < 3) {
          if (data.faceDirection == 1 || data.faceDirection == 2) {
            lstFaceDirection.push(data.faceDirection);
          }
        } else if (lstFaceDirection.length > 2 && lstFaceDirection < 5) {
          if (data.faceDirection == 3 || data.faceDirection == 4) {
            lstFaceDirection.push(data.faceDirection);
          }
        }
        //
        faceDirectionCount += 1;
        let faceDirection = data.faceDirection;
        if (faceDirectionCount >= 5) {
          clickCheckBox(faceDirection);
          displayFormSignUp();
          announceSuccess("success", "Dang Ki Thanh Cong");
          stopCamera(captureInterval, video);
          lstFaceDirection = [];
          faceDirectionCount = 0;
        } else {
          announceSuccess(
            "success",
            `Nhan huong ${dictFaceDirec[faceDirection]} thanh cong`
          );
          clickCheckBox(faceDirection);
          // alert(dictFaceDirec[faceDirection]);
        }
      } else {
        if (data.message != null) {
          displayFormSignUp();
          announceSuccess("error", data.message);
          stopCamera(captureInterval, video);
        }
        console.log("Chua dung huong khuon mat");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  }, "image/png");
}

function stopCamera(captureInterval, video) {
  clearInterval(captureInterval);
  if (video.srcObject) {
    const tracks = video.srcObject.getTracks();
    tracks.forEach((track) => track.stop());
    video.srcObject = null;
  }
}

function hiddenFormSignUp() {
  const topSignUp = document.getElementById("top-signup");
  const formSignUp = document.getElementById("signUpForm");
  const checkboxContainer = document.getElementById("checkboxContainer");
  topSignUp.classList.toggle("hidden");
  formSignUp.classList.toggle("hidden");
  checkboxContainer.classList.remove("hidden");
}

function displayFormSignUp() {
  const topSignUp = document.getElementById("top-signup");
  const formSignUp = document.getElementById("signUpForm");
  const checkboxContainer = document.getElementById("checkboxContainer");
  topSignUp.classList.remove("hidden");
  formSignUp.classList.remove("hidden");

  const lstFaceDirectionName = ["thang", "trai", "phai", "tren", "duoi"];
  for (let i = 0; i < lstFaceDirectionName.length; i++) {
    const checkbox = document.getElementById(lstFaceDirectionName[i]);
    checkbox.checked = false;
  }
  checkboxContainer.classList.toggle("hidden");
}

function clickCheckBox(num) {
  const lstFaceDirectionName = ["thang", "trai", "phai", "tren", "duoi"];
  console.log(typeof lstFaceDirectionName[num]);
  const checkbox = document.getElementById(lstFaceDirectionName[num]);
  console.log(checkbox);
  checkbox.click();
}
