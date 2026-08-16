import React from 'react';
import './Starfield.css';

export default function Starfield() {
  return (
    <div className="starfield-container pointer-events-none fixed inset-0 z-0">
      <div id="stars"></div>
      <div id="stars2"></div>
      <div id="stars3"></div>
    </div>
  );
}
