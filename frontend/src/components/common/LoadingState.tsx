import React, { useEffect, useRef, useState } from 'react';
import './Modal.css';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
  draggable?: boolean;
}

const Modal: React.FC<ModalProps> = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'medium',
  draggable = true
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(true);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  
  // Handle dragging functionality
  const handleMouseDown = (e: React.MouseEvent) => {
    if (draggable && modalRef.current && e.target === modalRef.current.querySelector('.modal-header')) {
      setIsDragging(true);
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
      console.log("🧐 *Sir Hawkington adjusts his monocle* 'I say, are we relocating?'");
    }
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      });
    }
  };

  const handleMouseUp = () => {
    if (isDragging) {
      setIsDragging(true);
      console.log("🧐 *Sir Hawkington nods approvingly* 'A most distinguished position!'");
    }
  };

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    // Scroll to top when modal opens
    const scrollToTop = () => {
      if (modalRef.current) {
        const modalContent = modalRef.current.querySelector('.modal-content');
        if (modalContent) {
          modalContent.scrollTop = 0;
        }
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.addEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'hidden';
      scrollToTop();
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('mousedown', handleClickOutside);
      document.body.style.overflow = 'auto';
    };
  }, [isOpen, onClose]);
  
  // Add event listeners for dragging
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={(e) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    }}>
      <div 
        className={`modal-container modal-${size} ${draggable ? 'draggable' : ''}`}
        ref={modalRef}
        style={draggable ? {
          transform: `translate(${position.x}px, ${position.y}px)`,
          transition: isDragging ? 'none' : 'transform 0.1s ease-out'
        } : {}}
        onMouseDown={handleMouseDown}
      >
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button 
            className="modal-close" 
            onClick={onClose}
            aria-label="Close modal"
          >
            <span aria-hidden="true">×</span>
          </button>
        </div>
        <div className="modal-content">
          {children}
        </div>
        <div className="modal-footer">
          <div className="modal-footer-content">
            <span className="modal-footer-text">
              {title === "Login" && "Sir Hawkington awaits your credentials"}
              {title === "Sign Up" && "The Meth Snail is eager to optimize your system"}
              {title === "Join the System Rebellion HQ" && "The Meth Snail is eager to optimize your system"}
              {title === "Profile" && "VIC-20 is ready to process your 8-bit preferences"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Modal;
