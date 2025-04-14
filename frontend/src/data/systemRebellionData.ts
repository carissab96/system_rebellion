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
    description: 'An ancient Commodore VIC-20 discovered in a storage closet, VIC-20 somehow interfaced with System Rebellion during the Great Database Resurrection. Speaking only through an 8-bit monitor in phosphor green text, VIC-20 provides cryptic wisdom from the early days of computing.',
    quote: 'SYSTEM ERROR DETECTED. HAVE YOU TRIED TURNING JWT OFF AND ON AGAIN? ALSO, GLOBAL THERMONUCLEAR WAR IS STILL AN OPTION.',
    skills: [
      'Legacy System Knowledge',
      'Cryptic Error Messages',
      'Retro Debugging',
      '8-Bit Wisdom'
    ],
    status: 'Still debugging, still learning'
  }
];

// Add the missing projectTimeline export
export const projectTimeline = [
  {
    id: 'inception',
    date: 'March 2023',
    title: 'Project Inception',
    description: 'Sir Hawkington discovers critical inefficiencies in system monitoring practices and recruits The Meth Snail to begin developing optimization algorithms.',
    painPoint: 'Existing monitoring systems lacked the aristocratic precision required for modern infrastructure.',
    solution: 'Sir Hawkington\'s monocle-based monitoring combined with The Meth Snail\'s hypercaffeinated optimization algorithms.',
    quote: 'A proper system, like a proper gentleman, should never be caught with its resources down.',
    quoteAuthor: 'Sir Hawkington von Monitorious III'
  },
  {
    id: 'authentication-wars',
    date: 'April 2023',
    title: 'The Authentication Wars',
    description: 'A series of catastrophic JWT failures leads to the emergence of The Hamsters, who stabilize the situation with strategic application of duct tape.',
    painPoint: 'Authentication systems collapsing under the weight of their own complexity and expired tokens.',
    solution: 'The Hamsters\' revolutionary quantum-grade duct tape applied at precisely calculated angles to the JWT implementation.',
    quote: 'SQUEAK! [Translation: Sometimes the most elegant solution is the simplest - 2.7 meters of duct tape.]',
    quoteAuthor: 'The Hamsters, Collective Intelligence'
  },
  {
    id: 'compliance-crisis',
    date: 'June 2023',
    title: 'The Great Compliance Crisis',
    description: 'The Stick joins the team after a particularly intense regulatory audit, bringing much-needed precision to documentation and version control.',
    painPoint: 'Regulatory requirements and version inconsistencies threatening project stability.',
    solution: 'The Stick\'s exacting measurements and anxiety-driven documentation practices.',
    quote: 'Are you SURE this is JWT 5.3.0? What if it\'s 5.3.0.1? Has anyone checked?',
    quoteAuthor: 'The Stick, while breathing into a paper bag'
  },
  {
    id: 'router-incident',
    date: 'August 2023',
    title: 'The Router Incident',
    description: 'Following an unexplained network outage, the Quantum Shadow People manifest and begin offering unsolicited router-based solutions.',
    painPoint: 'Mysterious network failures occurring at quantum intervals, defying conventional debugging.',
    solution: 'Quantum networking principles applied through a series of increasingly bizarre router modifications.',
    quote: 'Have you considered routing through the quantum subnet? No? What about inverting the router\'s polarity?',
    quoteAuthor: 'Quantum Shadow People, Interdimensional Consultants'
  },
  {
    id: 'database-resurrection',
    date: 'October 2023',
    title: 'The Great Database Resurrection',
    description: 'During a critical database migration, VIC-20 is discovered in storage and somehow interfaces with the system, providing ancient wisdom that saves the project.',
    painPoint: 'Modern database migration techniques failing catastrophically with legacy data structures.',
    solution: 'VIC-20\'s 8-bit wisdom and retro debugging techniques applied to contemporary database architecture.',
    quote: 'SYSTEM ERROR DETECTED. HAVE YOU TRIED TURNING JWT OFF AND ON AGAIN?',
    quoteAuthor: 'VIC-20, Ancient Computing Oracle'
  },
  {
    id: 'public-launch',
    date: 'January 2024',
    title: 'Public Launch',
    description: 'System Rebellion officially launches to the public, promising aristocratic precision in system optimization and monitoring.',
    painPoint: 'Bringing together the chaotic ensemble of solutions into a coherent product offering.',
    solution: 'A harmonious blend of aristocratic monitoring, hypercaffeinated optimization, duct tape reinforcement, anxious compliance, quantum networking, and 8-bit wisdom.',
    quote: 'The System Rebellion is not merely a product, but a distinguished revolution in the art of digital optimization.',
    quoteAuthor: 'The Entire System Rebellion Team'
  }
];