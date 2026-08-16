import React from 'react';
import './LoadingBall.css';

export default function LoadingBall() {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="ball">
        <div className="inner">
          <div className="line"></div>
          <div className="line line--two"></div>
          <div className="oval"></div>
          <div className="oval oval--two"></div>
        </div>
      </div>
      <div className="shadow"></div>
    </div>
  );
}
