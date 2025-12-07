// components/consciousness/MessageFlow.tsx
// Real-time message flow visualization
// Watching thoughts travel between agents

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './MessageFlow.css';

export interface Message {
  id: string;
  from: string;
  to: string;
  type: 'triage' | 'coordination' | 'resource_alert' | 'decision';
  timestamp: Date;
  content?: string;
}

interface MessageFlowProps {
  messages: Message[];
  onMessageComplete?: (messageId: string) => void;
}

export const MessageFlow: React.FC<MessageFlowProps> = ({ messages, onMessageComplete }) => {
  const [activeMessages, setActiveMessages] = useState<Message[]>([]);

  useEffect(() => {
    // Keep only recent messages (last 10 seconds)
    const now = new Date();
    const recent = messages.filter(m => {
      const age = now.getTime() - m.timestamp.getTime();
      return age < 10000; // 10 seconds
    });
    setActiveMessages(recent);
  }, [messages]);

  const getMessageColor = (type: Message['type']) => {
    switch (type) {
      case 'triage': return '#e6ac00';
      case 'coordination': return '#06b6d4';
      case 'resource_alert': return '#f97316';
      case 'decision': return '#00d084';
      default: return '#888';
    }
  };

  const getMessageLabel = (type: Message['type']) => {
    switch (type) {
      case 'triage': return '🧐 TRIAGE';
      case 'coordination': return '🖥️ COORD';
      case 'resource_alert': return '⚠️ ALERT';
      case 'decision': return '✨ DECISION';
      default: return '📡';
    }
  };

  return (
    <div className="message-flow-container">
      <AnimatePresence>
        {activeMessages.map((message) => (
          <motion.div
            key={message.id}
            className="message-bubble"
            style={{ borderColor: getMessageColor(message.type) }}
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -20 }}
            transition={{ duration: 0.3 }}
            onAnimationComplete={() => {
              // Auto-remove after animation
              setTimeout(() => {
                if (onMessageComplete) {
                  onMessageComplete(message.id);
                }
              }, 5000);
            }}
          >
            <div className="message-header">
              <span className="message-type" style={{ color: getMessageColor(message.type) }}>
                {getMessageLabel(message.type)}
              </span>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </span>
            </div>
            <div className="message-route">
              <span className="message-from">{message.from}</span>
              <span className="message-arrow">→</span>
              <span className="message-to">{message.to}</span>
            </div>
            {message.content && (
              <div className="message-content">{message.content}</div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};
