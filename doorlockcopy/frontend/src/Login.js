import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://localhost:8000";

function Login({ setIsLoggedIn }) {
  const [otp, setOtp] = useState("");
  const [message, setMessage] = useState("");

  const requestOtp = async () => {
    try {
      await axios.post(`${API_BASE}/request-otp`);
      setMessage("OTP sent to admin email!");
    } catch (err) {
      setMessage("Error sending OTP.");
    }
  };

  const verifyOtp = async () => {
    try {
      const res = await axios.post(`${API_BASE}/verify-otp`, null, {
        params: { otp },
      });
      if (res.data.status === "success") {
        setIsLoggedIn(true);
        localStorage.setItem("isLoggedIn", "true");
      } else {
        setMessage("Invalid OTP.");
      }
    } catch (err) {
      setMessage("Error verifying OTP.");
    }
  };

  return (
    <div className="container center">
      <h1 className="title">Admin Login</h1>
      <button className="btn blue" onClick={requestOtp}>
        Send OTP
      </button>
      <input
        type="text"
        placeholder="Enter OTP"
        value={otp}
        onChange={(e) => setOtp(e.target.value)}
        className="input"
      />
      <button className="btn green" onClick={verifyOtp}>
        Verify OTP
      </button>
      {message && <p className="message">{message}</p>}
    </div>
  );
}

export default Login;
