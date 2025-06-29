// components/dashboard/Dashboard/SystemStatus/SystemStatusNew.tsx
import React, { useState, useEffect } from 'react';
import './system-status.css';

export interface SystemStatusProps {
    loading: boolean;
    error: string | null;
}

export const SystemStatus: React.FC<SystemStatusProps> = ({ loading, error }) => {
    const [messageIndex, setMessageIndex] = useState(0);
    
    // Collection of humorous messages featuring all project characters
    const statusMessages = [
        "🧐🎩 Sir Hawkington: 'Your CPU is performing most admirably, old chap!'" ,
        "🐌💊 The Meth Snail: 'HOLY SHIT YOUR RAM IS FUCKING FLYING DUDE!'" ,
        "🐹🔧 The Hamsters: 'WebSockets patched with fresh duct tape, sir!'" ,
        "🥢😰 The Stick: 'Anxiety levels at 42%. That's... acceptable.'" ,
        "👤👽 Quantum Shadow People: 'Your router would work better if you put it upside down in jello.'" ,
        "🕹️💾 VIC-20: '01001000 01100101 01101100 01101100 01101111 00100000 01100110 01110101 01100011 01101011 01100101 01110010'" ,
        "🧐🎩 Sir Hawkington: 'I say, these metrics are looking positively scrumptious!'" ,
        "🐌💊 The Meth Snail: 'OPTIMIZING SO HARD I'M SEEING SOUNDS!'" ,
        "🐹🔧 The Hamsters: 'We've replaced the wheel with a fidget spinner. INNOVATION!'" ,
        "🥢😰 The Stick: 'Regulatory compliance at 0%. Perfect.'" ,
        "👤👽 Quantum Shadow People: 'We've been trying to reach you about your router's extended warranty.'" ,
        "🕹️💾 VIC-20: 'Loading... Please insert cassette tape and wait 45 minutes.'" ,
        "🧐🎩 Sir Hawkington: 'Your disk usage is quite distinguished, if I do say so myself.'" ,
        "🐌💊 The Meth Snail: 'I LICKED YOUR HARD DRIVE AND NOW I CAN TASTE COLORS!'" ,
        "🐹🔧 The Hamsters: 'Network packets delivered via tiny hamster motorcycles.'" ,
        "🥢😰 The Stick: 'Existential dread minimized. For now.'" ,
        "👤👽 Quantum Shadow People: 'Have you tried putting your entire computer in rice?'" ,
        "🕹️💾 VIC-20: 'ERROR: NOT ENOUGH MEMORY. NEED 3 MORE KB.'" ,
        "🧐🎩 Sir Hawkington: 'I've applied a fresh coat of digital wax to your CPU cache, sir!'" ,
        "🐌💊 The Meth Snail: 'YOUR MEMORY LEAKS TASTE LIKE PURPLE LIGHTNING!'" ,
        "🐹🔧 The Hamsters: 'Running in circles has never been more efficient!'" ,
        "🥢😰 The Stick: 'I've successfully suppressed 17 kernel panics today.'" ,
        "👤👽 Quantum Shadow People: 'We've replaced your DNS with interdimensional portals.'" ,
        "🕹️💾 VIC-20: 'POKE 53280,0 - BACKGROUND SET TO VOID OF DESPAIR'" ,
        "🧐🎩 Sir Hawkington: 'Your bandwidth is looking particularly dapper today!'" ,
        "🐌💊 The Meth Snail: 'DEFRAGMENTING AT THE SPEED OF COCAINE!'" ,
        "🐹🔧 The Hamsters: 'Wheel spinning at 420 RPM - nice.'" ,
        "🥢😰 The Stick: 'Existential buffer overflow successfully contained.'" ,
        "👤👽 Quantum Shadow People: 'Your IP address looks better in hexadecimal.'" ,
        "🕹️💾 VIC-20: 'SYNTAX ERROR IN LINE 42: LIFE HAS NO MEANING'" ,
    ];
    
    useEffect(() => {
        // Rotate through messages every 4 seconds
        const intervalId = setInterval(() => {
            setMessageIndex((prevIndex) => (prevIndex + 1) % statusMessages.length);
        }, 4000);
        
        return () => clearInterval(intervalId);
    }, []);
    
    // Randomize the initial message
    useEffect(() => {
        setMessageIndex(Math.floor(Math.random() * statusMessages.length));
    }, []);
    
    const getStatusClass = () => {
        if (loading) return 'status-loading';
        if (error) return 'status-error';
        return 'status-active';
    };

    const getStatusMessage = () => {
        if (loading) {
            return (
                <div className="status-message loading">
                    <i className="fas fa-sync-alt"></i> Optimizing your shit...
                </div>
            );
        }
        if (error) {
            return (
                <div className="status-message error">
                    <i className="fas fa-exclamation-triangle"></i> {error}
                </div>
            );
        }
        
        // Parse the message to separate emojis from text
        const currentMessage = statusMessages[messageIndex];
        const emojiMatch = currentMessage.match(/^([\p{Emoji}\p{Emoji_Presentation}\p{Emoji_Modifier}\p{Emoji_Component}\p{Emoji_Modifier_Base}]+)/u);
        const messageWithoutEmoji = emojiMatch ? currentMessage.substring(emojiMatch[0].length) : currentMessage;
        
        return (
            <div className="status-message active">
                <i className="fas fa-check-circle"></i>
                {emojiMatch && <span className="character-emoji">{emojiMatch[0]}</span>}
                <div className="ticker-wrapper">
                    <div className="ticker">{messageWithoutEmoji}</div>
                </div>
            </div>
        );
    };

    return (
        <div className="system-status">
            <div className="status-dot-container">
                <div className={`status-dot ${getStatusClass()}`}></div>
            </div>
            <div className="status-content">
                {getStatusMessage()}
            </div>
        </div>
    );
};

export default SystemStatus;