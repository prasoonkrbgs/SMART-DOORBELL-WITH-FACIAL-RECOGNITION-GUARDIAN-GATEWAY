import React, { useState, useEffect } from "react";
import axios from "axios";
import CameraCapture from "./CameraCapture";
import "./App.css";

const API_BASE = "http://localhost:8000";

function Dashboard() {
  const [faces, setFaces] = useState([]);
  const [logs, setLogs] = useState([]);
  const [newFaceName, setNewFaceName] = useState("");
  const [newFaceFile, setNewFaceFile] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const [message, setMessage] = useState("");
  const [cameraOn, setCameraOn] = useState(false);

  const fetchFaces = async () => {
    try {
      const res = await axios.get(`${API_BASE}/faces`);
      setFaces(res.data.faces);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await axios.get(`${API_BASE}/logs`);
      setLogs(res.data.logs);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchFaces();
    fetchLogs();
  }, []);

  // 📸 Handle camera capture
  const handleFaceCapture = (blob) => {
    setNewFaceFile(blob);
    const url = URL.createObjectURL(blob);
    setPreviewURL(url);
  };

  // ❌ Remove captured image
  const removeCapturedPhoto = () => {
    setNewFaceFile(null);
    setPreviewURL(null);
  };

  const addFace = async () => {
    if (!newFaceName || !newFaceFile) {
      setMessage("Name and photo are required.");
      return;
    }

    const formData = new FormData();
    formData.append("name", newFaceName);
    formData.append("file", newFaceFile);

    try {
      await axios.post(`${API_BASE}/faces/add`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage("Face added successfully!");
      setNewFaceName("");
      setNewFaceFile(null);
      setPreviewURL(null);
      fetchFaces();
    } catch (err) {
      console.error(err);
      setMessage("Error adding face.");
    }
  };

  const deleteFace = async (name) => {
    try {
      await axios.delete(`${API_BASE}/faces/${name}`);
      setMessage("Face deleted!");
      fetchFaces();
    } catch (err) {
      console.error(err);
      setMessage("Error deleting face.");
    }
  };

  const refreshLogs = () => {
    fetchLogs();
  };

  const logout = () => {
    localStorage.removeItem("isLoggedIn");
    window.location.href = "/";
  };

  return (
    <div className="container dashboard">

      {/* HEADER */}
      <div className="header">
        <h1 className="title">Face Recognition Dashboard</h1>
        <button className="btn red" onClick={logout}>Logout</button>
      </div>

      {message && <p className="message">{message}</p>}

      {/* ADD FACE SECTION */}
      <div className="section card">
        <h2>Add New Face</h2>

        <input
          type="text"
          placeholder="Enter Name"
          value={newFaceName}
          onChange={(e) => setNewFaceName(e.target.value)}
          className="input"
        />

        <input
          type="file"
          onChange={(e) => {
            const file = e.target.files[0];
            setNewFaceFile(file);
            setPreviewURL(URL.createObjectURL(file));
          }}
          className="input"
        />

        {/* CAMERA TOGGLE */}
        <div className="camera-controls">
          <button
            className={`btn ${cameraOn ? "red" : "green"}`}
            onClick={() => setCameraOn(!cameraOn)}
          >
            {cameraOn ? "Turn Off Camera" : "Turn On Camera"}
          </button>
        </div>

        {/* CAMERA COMPONENT */}
        {cameraOn && (
          <CameraCapture onCapture={handleFaceCapture} />
        )}

        {/* IMAGE PREVIEW */}
        {previewURL && (
          <div className="preview-box">
            <h3>Preview</h3>
            <img src={previewURL} alt="Preview" className="preview-img" />

            <button className="btn red small" onClick={removeCapturedPhoto}>
              Remove Photo
            </button>
          </div>
        )}

        <button className="btn blue" onClick={addFace}>
          Add Face
        </button>
      </div>

      {/* KNOWN FACES */}
      <div className="section card">
        <h2>Known Faces</h2>
        <ul className="face-list">
          {faces.map((face) => (
            <li key={face} className="face-item">
              <span>{face}</span>
              <button className="btn red small" onClick={() => deleteFace(face)}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* LOGS */}
      <div className="section card">
        <div className="logs-header">
          <h2>Visitor Logs</h2>
          <button className="btn green small" onClick={refreshLogs}>
            Refresh
          </button>
        </div>

        <table className="logs-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Timestamp</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td>{log.id}</td>
                <td>{log.name}</td>
                <td>{log.timestamp}</td>
                <td>
                  <span className={log.name === "Unknown" ? "status denied" : "status granted"}>
                    {log.name === "Unknown" ? "Denied" : "Granted"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default Dashboard;
