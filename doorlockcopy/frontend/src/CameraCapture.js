import React, { useRef, useState } from "react";

function CameraCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);

 const startCamera = async () => {
  try {
    setCameraActive(true);
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    videoRef.current.srcObject = stream;
    videoRef.current.play();
  } catch (err) {
    console.error("Camera access failed:", err);
    alert(
      "Could not access camera. Make sure you are on HTTPS or localhost and granted permissions."
    );
  }
};

  const capturePhoto = () => {
    const context = canvasRef.current.getContext("2d");
    context.drawImage(videoRef.current, 0, 0, 300, 200);
    canvasRef.current.toBlob((blob) => {
      onCapture(blob);
    }, "image/jpeg");
  };

  return (
    <div>
      {!cameraActive && (
        <button className="btn blue" onClick={startCamera}>
          Open Camera
        </button>
      )}
      {cameraActive && (
        <div>
          <video ref={videoRef} width="300" height="200"></video>
          <br />
          <button className="btn green" onClick={capturePhoto}>
            Capture
          </button>
        </div>
      )}
      <canvas ref={canvasRef} width="300" height="200" style={{ display: "none" }}></canvas>
    </div>
  );
}

export default CameraCapture;
