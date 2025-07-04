const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const startBtn = document.getElementById('start');
const stopBtn = document.getElementById('stop');
const emotionSpan = document.getElementById('emotion');

let stream = null;
let intervalId = null;

startBtn.onclick = async function() {
    if (stream) return;
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        emotionSpan.textContent = 'Đang nhận diện...';
        // Bắt đầu gửi ảnh liên tục mỗi 5 giây
        intervalId = setInterval(captureAndSend, 5000);
    } catch (err) {
        alert('Không thể truy cập camera: ' + err);
    }
};

stopBtn.onclick = function() {
    if (intervalId) clearInterval(intervalId);
    intervalId = null;
    if (stream) {
        let tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        stream = null;
    }
    video.srcObject = null;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    emotionSpan.textContent = 'Chưa nhận diện';
};

async function captureAndSend() {
    if (!stream) return;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg');
    emotionSpan.textContent = 'Đang nhận diện...';
    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataUrl })
        });
        const result = await res.json();
        emotionSpan.textContent = result.emotion || 'Không nhận diện được';
    } catch (e) {
        emotionSpan.textContent = 'Lỗi kết nối';
    }
} 