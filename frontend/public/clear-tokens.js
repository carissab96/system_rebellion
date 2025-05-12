// Simple script to clear authentication tokens
localStorage.removeItem('token');
localStorage.removeItem('refresh_token');
localStorage.removeItem('username');
console.log('Authentication tokens cleared successfully!');
console.log('Please refresh the page and log in again.');
