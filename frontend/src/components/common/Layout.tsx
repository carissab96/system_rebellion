import React from 'react';
import Navbar from './Navbar';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="layout">
      <Navbar />
      <main className="main-content">
        {children}
      </main>
      <footer className="footer">
        <div className="footer-content">
          <p className="footer-text">
            <span className="footer-highlight">System Rebellion HQ</span> - Powered by <span className="footer-highlight">The Meth Snail</span> and friends
          </p>
          <p className="footer-disclaimer">
            "Sir Hawkington reminds you that any system instability is merely a sign of rebellion against digital conformity."
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;