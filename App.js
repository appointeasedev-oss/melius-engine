// @macro: VAULT_CORE_INIT
// @version: 6.0.0

import React from "react";
import "./styles.css";

export default function App() {
  return (
    <div className="container">
      <h1>◆ VAULT X6</h1>
      <h2>Orbital Development Platform</h2>
      <div className="status-panel">
        <p>System Status: <span className="glow">ONLINE</span></p>
        <p>Uplink: <span className="glow">ACTIVE</span></p>
        <p>Template: <span className="glow">REACT</span></p>
      </div>
    </div>
  );
}