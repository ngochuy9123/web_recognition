// Lấy tất cả các nút có class 'openCam'
const buttons = document.querySelectorAll(".openCam");

// Gán sự kiện click cho mỗi nút
buttons.forEach((button) => {
  button.addEventListener("click", () => {
    // Lấy giá trị của nút được nhấn
    const rstp = button.value;
    startStream(rstp);
    fetchRecognizedPersons();
    setInterval(fetchRecognizedPersons, 5000);
  });
});

async function startStream(rstp) {
  const response = await fetch("/face_recog_cam", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ rstp: rstp }),
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value);

    let frameStart = buffer.indexOf("--frame");
    while (frameStart !== -1) {
      const frameEnd = buffer.indexOf("--frame", frameStart + 1);
      if (frameEnd === -1) break;

      const frame = buffer.slice(frameStart + 8, frameEnd);
      const base64Image = frame.split("\r\n")[2];

      const imgCam = document.getElementById("img_cam");
      imgCam.src = `data:image/jpeg;base64,${base64Image}`;

      buffer = buffer.slice(frameEnd);
      frameStart = buffer.indexOf("--frame");
    }
  }
}

async function fetchRecognizedPersons() {
  const response = await fetch("/recognized_persons", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.ok) {
    const data = await response.json();
    const personsList = document.getElementById("persons_list");
    const existingPersons = new Set();
    // Thu thập những người đã có trong danh sách
    personsList.querySelectorAll("li").forEach((li) => {
      existingPersons.add(li.textContent);
    });

    data.persons.forEach((person) => {
      // Chỉ thêm nếu người này chưa có trong danh sách
      if (!existingPersons.has(person)) {
        const li = document.createElement("li");
        li.textContent = person;
        personsList.appendChild(li);
      }
    });
  } else {
    console.error("Failed to fetch recognized persons");
  }
}
