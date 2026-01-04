import React from 'react';
import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <p className="footer-text">
          &copy; 2025 Hawkington Technologies, Inc. All rights reserved.
        </p>
        <a 
          href="https://hawkington-tech.com" 
          target="_blank" 
          rel="noopener noreferrer"
          className="footer-link"
        >
          hawkington-tech.com
        </a>
      </div>
    </footer>
  );
};

export default Footer;
