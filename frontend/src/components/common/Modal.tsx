import React, { useState, useRef, useEffect, ReactNode } from 'react';
import ReactDOM from 'react-dom';
import './Modal.css';
import '../optimization/modal-fix.css';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: 'small' | 'medium' | 'large';
  draggable?: boolean;
}

const Modal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  size = 'medium',
  draggable = false
}: ModalProps) => {
  console.log('Modal render called with isOpen:', isOpen);
  const modalRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!draggable || !modalRef.current) return;
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    });
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || !modalRef.current) return;
    const newX = e.clientX - dragOffset.x;
    const newY = e.clientY - dragOffset.y;
    setPosition({ x: newX, y: newY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

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

  if (!isOpen) {
    console.log('Modal not rendering because isOpen is false');
    return null;
  }
  
  console.log('Modal will render with title:', title);

  // Force any existing modal elements to be removed to prevent stacking
  useEffect(() => {
    if (isOpen) {
      // Ensure the modal is visible by forcing styles after a small delay
      setTimeout(() => {
        const existingOverlay = document.querySelector('.modal-overlay');
        if (existingOverlay) {
          (existingOverlay as HTMLElement).style.display = 'flex';
          (existingOverlay as HTMLElement).style.zIndex = '9999999';
          console.log('Modal visibility enforced via useEffect');
        }
      }, 50);
    }
    
    return () => {
      console.log('Modal component unmounting');
    };
  }, [isOpen]);
  
  // Using React Portal to render the modal outside the normal DOM hierarchy
  // This ensures it's not affected by parent component styles or z-index issues
  const modalContent = (
    <div className="modal-overlay" onClick={onClose}>
      <div
        ref={modalRef}
        className={`modal-content ${size} ${draggable ? 'draggable' : ''}`}
        onClick={(e) => e.stopPropagation()}
        onMouseDown={handleMouseDown}
      >
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="close-button" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
  
  // Create a portal to render the modal at the end of the document body
  return ReactDOM.createPortal(
    modalContent,
    document.body
  );
};

export default Modal;
