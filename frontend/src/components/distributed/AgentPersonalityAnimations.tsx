import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Agent Personality Animations - Driven by REAL DATA ONLY
 * 
 * CRITICAL RULE: All animations triggered by actual backend metrics and events.
 * NO fake data, NO hardcoded triggers, NO simulated behavior.
 * 
 * Data Sources:
 * - Terry shell spins: backend shell_spin_count (increments on missing/invalid metrics)
 * - Stick anxiety: backend paper_bags_consumed (increments on Bob/errors)
 * - Hawkington monocle: backend monocle_yeet_count (increments on bad data)
 */

interface AgentPersonalityAnimationsProps {
  agentName: string;
  
  // Terry (Meth Snail) - Real data from backend
  shell_spin_count?: number;
  caffeine_level?: number;
  memory_percent?: number;
  
  // The Stick - Real data from backend
  paper_bags_consumed?: number;
  paper_bag_inventory?: number;
  bob_wild_ideas?: number;
  
  // Sir Hawkington - Real data from backend
  monocle_yeet_count?: number;
  data_quality_score?: number;
}

export function AgentPersonalityAnimations({
  agentName,
  shell_spin_count = 0,
  caffeine_level = 0,
  memory_percent = 0,
  paper_bags_consumed = 0,
  paper_bag_inventory = 0,
  bob_wild_ideas = 0,
  monocle_yeet_count = 0,
  data_quality_score = 1.0,
}: AgentPersonalityAnimationsProps) {
  
  // Track previous values to detect changes (real events)
  const [prevShellSpins, setPrevShellSpins] = useState(shell_spin_count);
  const [prevPaperBags, setPrevPaperBags] = useState(paper_bags_consumed);
  const [prevMonocleYeets, setPrevMonocleYeets] = useState(monocle_yeet_count);
  
  // Animation states (only triggered by real data changes)
  const [isShellSpinning, setIsShellSpinning] = useState(false);
  const [isBreathingIntoBag, setIsBreathingIntoBag] = useState(false);
  const [isMonocleYeeted, setIsMonocleYeeted] = useState(false);
  
  // Terry: Shell spin animation triggered by REAL shell_spin_count increment
  useEffect(() => {
    if (agentName === 'meth_snail' && shell_spin_count > prevShellSpins) {
      console.log(`🐌🔄 REAL SHELL SPIN DETECTED: ${prevShellSpins} → ${shell_spin_count}`);
      setIsShellSpinning(true);
      
      // Animation duration based on caffeine level (real data)
      const spinDuration = caffeine_level > 200 ? 2000 : 3000;
      
      setTimeout(() => setIsShellSpinning(false), spinDuration);
      setPrevShellSpins(shell_spin_count);
    }
  }, [shell_spin_count, prevShellSpins, agentName, caffeine_level]);
  
  // The Stick: Paper bag breathing triggered by REAL paper_bags_consumed increment
  useEffect(() => {
    if (agentName === 'the_stick' && paper_bags_consumed > prevPaperBags) {
      console.log(`📏😰 REAL PAPER BAG CONSUMED: ${prevPaperBags} → ${paper_bags_consumed}`);
      setIsBreathingIntoBag(true);
      
      // Animation duration: 4 seconds (realistic breathing)
      setTimeout(() => setIsBreathingIntoBag(false), 4000);
      setPrevPaperBags(paper_bags_consumed);
    }
  }, [paper_bags_consumed, prevPaperBags, agentName]);
  
  // Hawkington: Monocle yeet triggered by REAL monocle_yeet_count increment
  useEffect(() => {
    if (agentName === 'sir_hawkington' && monocle_yeet_count > prevMonocleYeets) {
      console.log(`🧐💥 REAL MONOCLE YEET DETECTED: ${prevMonocleYeets} → ${monocle_yeet_count}`);
      setIsMonocleYeeted(true);
      
      // Monocle flies off for 3 seconds
      setTimeout(() => setIsMonocleYeeted(false), 3000);
      setPrevMonocleYeets(monocle_yeet_count);
    }
  }, [monocle_yeet_count, prevMonocleYeets, agentName]);
  
  // Render animations based on agent type
  return (
    <div className="absolute inset-0 pointer-events-none">
      {/* Terry's Shell Spin Animation */}
      {agentName === 'meth_snail' && (
        <AnimatePresence>
          {isShellSpinning && (
            <motion.div
              className="absolute top-2 right-2 text-4xl"
              initial={{ rotate: 0, scale: 1 }}
              animate={{ 
                rotate: 360,
                scale: [1, 1.2, 1],
              }}
              exit={{ rotate: 720, scale: 0.8 }}
              transition={{ 
                duration: caffeine_level > 200 ? 2 : 3,
                ease: "easeInOut",
                repeat: 0
              }}
            >
              🐌
            </motion.div>
          )}
        </AnimatePresence>
      )}
      
      {/* Terry's Jitter Effect (based on REAL caffeine level) */}
      {agentName === 'meth_snail' && caffeine_level > 300 && (
        <motion.div
          className="absolute inset-0 bg-green-500/5 rounded-lg"
          animate={{
            opacity: [0.1, 0.3, 0.1],
          }}
          transition={{
            duration: 0.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}
      
      {/* Terry's Critical Memory Warning (REAL threshold: 75%) */}
      {agentName === 'meth_snail' && memory_percent >= 75 && (
        <motion.div
          className="absolute top-2 left-2 text-xs font-bold text-red-400"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
          }}
        >
          🔥 MEMORY CRITICAL
        </motion.div>
      )}
      
      {/* The Stick's Paper Bag Breathing Animation */}
      {agentName === 'the_stick' && (
        <AnimatePresence>
          {isBreathingIntoBag && (
            <motion.div
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-6xl"
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ 
                scale: [0.8, 1.2, 0.8],
                opacity: [0.8, 1, 0.8],
              }}
              exit={{ scale: 0.5, opacity: 0 }}
              transition={{ 
                duration: 4,
                ease: "easeInOut",
                times: [0, 0.5, 1]
              }}
            >
              📄😰
            </motion.div>
          )}
        </AnimatePresence>
      )}
      
      {/* The Stick's Bob Anxiety Indicator (REAL bob_wild_ideas count) */}
      {agentName === 'the_stick' && bob_wild_ideas > 0 && (
        <motion.div
          className="absolute bottom-2 right-2 text-xs font-bold text-orange-400"
          animate={{
            y: [-2, 2, -2],
          }}
          transition={{
            duration: 0.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          ⚠️ BOB DETECTED
        </motion.div>
      )}
      
      {/* Hawkington's Monocle Yeet Animation */}
      {agentName === 'sir_hawkington' && (
        <AnimatePresence>
          {isMonocleYeeted && (
            <motion.div
              className="absolute top-2 right-2 text-4xl"
              initial={{ x: 0, y: 0, rotate: 0, opacity: 1 }}
              animate={{ 
                x: 100,
                y: -50,
                rotate: 720,
                opacity: 0,
              }}
              exit={{ opacity: 0 }}
              transition={{ 
                duration: 1,
                ease: "easeOut"
              }}
            >
              🧐
            </motion.div>
          )}
        </AnimatePresence>
      )}
      
      {/* Hawkington's Data Quality Warning (REAL data_quality_score) */}
      {agentName === 'sir_hawkington' && data_quality_score < 0.7 && (
        <motion.div
          className="absolute top-2 left-2 text-xs font-bold text-yellow-400"
          animate={{
            opacity: [0.6, 1, 0.6],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
          }}
        >
          ⚠️ DATA QUALITY LOW
        </motion.div>
      )}
    </div>
  );
}
