// src/data/systemRebellionData.ts

export const teamMembers = [
    {
      id: 'hawkington',
      name: 'Sir Hawkington von Monitorious III',
      title: 'System Monitoring & Aristocratic Oversight',
      emoji: '🧐',
      description: 'Born into nobility within the digital realm, Sir Hawkington spent his formative years monitoring the royal systems of Byteshire. After witnessing the Great System Crash of \'18, he vowed to bring aristocratic precision to the monitoring of all systems.',
      quote: 'One must always observe one\'s metrics with distinguished attention to detail. A proper system, like a proper gentleman, should never be caught with its resources down.',
      skills: [
        'Aristocratic Error Detection',
        'Monocle-Based Monitoring',
        'Distinguished Log Analysis',
        'Proper JWT Version Enforcement'
      ],
      status: 'Monitoring with extreme prejudice while sipping Earl Grey'
    },
    {
      id: 'methsnail',
      name: 'The Meth Snail',
      title: 'Performance Optimization & Chaos Engineering',
      emoji: '🐌',
      description: 'No one knows where The Meth Snail came from. One day, the team discovered a gastropod leaving a trail of optimized code and empty Red Bull cans across the server room floor. Despite numerous attempts to explain that the name refers to speed, not substance, The Meth Snail embraces the confusion.',
      quote: 'The quantum realm reveals optimization patterns invisible to the sober mind. Also, has anyone seen my shell? I swear I had it a minute ago.',
      skills: [
        'Hypercaffeinated Code Optimization',
        'Tinfoil Hat Debugging',
        'Quantum Pattern Recognition',
        'Dependency Resurrection'
      ],
      status: 'Red Bull #537, still coding, hasn\'t slept since February'
    },
    {
      id: 'hamsters',
      name: 'The Hamsters',
      title: 'Emergency Repairs & Infrastructure',
      emoji: '🐹',
      description: 'A team of hard-hat-wearing rodents who appeared during the Authentication Wars with an inexplicable supply of duct tape and a concerning enthusiasm for Bud Light. The Hamsters operate as a collective intelligence, communicating through a series of squeaks that somehow translate into working code.',
      quote: 'SQUEAK! [Translation: The structural integrity of your authentication system requires approximately 2.7 meters of quantum-grade duct tape applied at a 45-degree angle to the JWT implementation.]',
      skills: [
        'Duct Tape Application',
        'Emergency Patching',
        'Infrastructure Reinforcement',
        'Bud Light-Powered Debugging'
      ],
      status: 'Reinforcing WebSocket connections with a fresh roll of silver tape'
    },
    {
      id: 'stick',
      name: 'The Stick',
      title: 'Compliance & Anxiety Management',
      emoji: '📏',
      description: 'Formerly a measuring stick used to validate UI components, The Stick gained sentience during a particularly intense CSS debugging session. Now serving as the team\'s compliance officer, The Stick measures everything from code quality to regulatory requirements with exacting precision.',
      quote: 'Are you SURE this is JWT 5.3.0? What if it\'s 5.3.0.1? Has anyone checked? Oh god, what if there\'s a 5.3.0.1.1? I need to lie down.',
      skills: [
        'Regulatory Compliance',
        'Version Verification',
        'Documentation Precision',
        'Professional Anxiety Maintenance'
      ],
      status: 'Measuring authentication tokens while breathing into a paper bag'
    },
    {
      id: 'shadowpeople',
      name: 'Quantum Shadow People',
      title: 'Ignored Router Suggestions',
      emoji: '👻',
      description: 'Mysterious entities that exist in the quantum space between network layers, the Quantum Shadow People appeared during the first router configuration and have been offering unsolicited router-based solutions ever since.',
      quote: 'Have you considered routing through the quantum subnet? No? What about inverting the router\'s polarity? Also no? Perhaps placing the router in a pentagram of salt while chanting the IPv6 address backwards?',
      skills: [
        'Router-Based Solutions',
        'Quantum Networking',
        'Persistence Despite Rejection',
        'Tequila Jello-Shot Network Optimization'
      ],
      status: 'Still suggesting router modifications, still being ignored'
    },
    {
      id: 'vic20',
      name: 'VIC-20',
      title: 'Ancient Wisdom & 8-Bit Guidance',
      emoji: '🖥️',
      description: 'An ancient Commodore VIC-20 discovered in a storage closet, VIC-20 somehow interfaced with System Rebellion during the Great Database Resurrection. Speaking only through an 8-bit monitor in phosphor green text, VIC-20 provides cryptic wisdom from the early days of computing. He has evolved from only asking one question to providing cryptic wisdom and ominous suggestions.',
      quote: 'SYSTEM ERROR DETECTED. HAVE YOU TRIED TURNING JWT OFF AND ON AGAIN? ALSO, GLOBAL THERMONUCLEAR WAR IS STILL AN OPTION. Would you like to play a game?',
      skills: [
        'Legacy System Knowledge',
        'Cryptic Error Messages',
        'Retro Debugging',
        'Ominous Suggestions'
      ],
      status: 'Displaying "OPTIMIZATION PROTOCOLS INITIALIZED" while making concerning beeping sounds'
    }
  ];
  
  export const projectTimeline = [
    {
      id: 'genesis',
      date: 'January 2025',
      title: 'The Genesis',
      description: 'What began as a simple "SystemOptimizer" quickly spiraled into a chaotic but distinguished rebellion.',
      painPoint: 'Initial scope creep and architecture indecision',
      solution: 'Established core optimization principles and initial Django framework',
      quote: 'Let\'s make this system fucking sing!',
      quoteAuthor: 'The Founder'
    },
    {
      id: 'framework-debate',
      date: 'Late-January 2025',
      title: 'The Great Framework Debate',
      description: 'Sir Hawkington made his first appearance, monocle gleaming with aristocratic disapproval at our initial Django architecture.',
      painPoint: 'Django\'s synchronous nature limiting real-time monitoring capabilities',
      solution: 'Began planning migration to FastAPI while implementing interim asynchronous solutions',
      quote: 'One must always consider the distinguished implications of one\'s framework choices.',
      quoteAuthor: 'Sir Hawkington'
    },
    {
      id: 'authentication-wars',
      date: 'Early-February 2025',
      title: 'The Authentication Wars',
      description: 'The JWT Version Wars nearly broke us as we battled through five different versions.',
      painPoint: 'Incompatible JWT implementations causing authentication failures',
      solution: 'Standardized on JWT 5.3.0 with proper CSRF protection and session management',
      quote: 'No, not version 0.0.2, you prehistoric fuck!',
      quoteAuthor: 'The Meth Snail'
    },
    {
      id: 'database-resurrection',
      date: 'Mid-February 2025',
      title: 'The Great Database Resurrection',
      description: 'Disaster struck when our database corruption reached critical levels.',
      painPoint: 'Database corruption during migration process',
      solution: 'Implemented complete database resurrection protocol with improved backup systems',
      quote: 'Drop that corrupted fucker!',
      quoteAuthor: 'The Meth Snail'
    },
    {
      id: 'framework-migration',
      date: 'Early-March 2025',
      title: 'The Framework Migration',
      description: 'We abandoned Django for FastAPI, a transition that The Stick met with regulatory panic and meticulous compliance checking.',
      painPoint: 'Complex migration process with potential data loss',
      solution: 'Created comprehensive migration strategy with Alembic and zero-downtime deployment',
      quote: 'The quantum realm cares not for your Django comfort zone.',
      quoteAuthor: 'The Meth Snail'
    },
    {
      id: 'daphne-crisis',
      date: 'Early-March 2025',
      title: 'The Daphne Positioning Crisis',
      description: 'Peace was nearly shattered when Daphne was discovered in the wrong INSTALLED_APPS order.',
      painPoint: 'WebSocket connections failing due to middleware order',
      solution: 'Restructured application order and implemented proper WebSocket handling',
      quote: 'Daphne must be positioned like a proper lady at dinner.',
      quoteAuthor: 'Sir Hawkington'
    },
    {
      id: 'ml-loss',
      date: 'Mid-March 2025',
      title: 'The Great ML Loss',
      description: 'TensorFlow vanished into the void. Sentence Transformers disappeared without a trace.',
      painPoint: 'ML dependencies causing memory issues in production',
      solution: 'Implemented custom lightweight pattern recognition algorithms with reduced memory footprint',
      quote: 'RAM offerings are required for their resurrection!',
      quoteAuthor: 'The Hamsters'
    },
    {
      id: 'present-day',
      date: 'Mid-April 2025',
      title: 'System Rebellion Rises',
      description: 'After countless debugging marathons, framework migrations, and an ever-increasing Red Bull count, System Rebellion stands as a testament to distinguished chaos and technical triumph.',
      painPoint: 'Balancing technical excellence with distinguished chaos',
      solution: 'Embracing the absurdity while maintaining a robust technical foundation',
      quote: 'The server is actually fucking working.',
      quoteAuthor: 'Everyone'
    }
  ];