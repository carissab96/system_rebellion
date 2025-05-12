// System Rebellion Authentication Reset Utility
// Created by Sir Hawkington and the Meth Snail

console.log('%c🔐 System Rebellion Authentication Reset Utility 🔐', 'color: #00ff00; font-size: 16px; font-weight: bold;');
console.log('%cThe Quantum Shadow People shall not interfere!', 'color: #ff00ff; font-style: italic;');

// Clear all authentication tokens
localStorage.removeItem('token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('username');

// Also clear any session storage items that might be related
sessionStorage.removeItem('token');
sessionStorage.removeItem('refresh_token');
sessionStorage.removeItem('username');

// Clear any WebSocket related data
localStorage.removeItem('websocket_session');
sessionStorage.removeItem('websocket_session');

// Add a small delay before redirecting to login
console.log('%c✅ Authentication tokens cleared successfully!', 'color: #00ff00; font-weight: bold;');
console.log('%c⏱️ Redirecting to login page in 2 seconds...', 'color: #0088ff;');

// Redirect to login page after a short delay
setTimeout(() => {
  console.log('%c🚀 Redirecting now...', 'color: #0088ff;');
  window.location.href = '/login';
}, 2000);
