// JavaScript Client Example for Abraxas Hybrid WebSocket Server
// Works in modern browsers and Node.js (with 'ws' package)

const WS_URL = 'ws://localhost:8000/ws';

// Connect to the hybrid server
function connectToHybridServer() {
  const socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log('Connected to Abraxas Hybrid Server');

    // Example 1: Send a valid signal
    const validSignal = {
      type: 'signal',
      features: [0.85, 0.72, 0.41, 0.55],
      target: 0.3
    };
    socket.send(JSON.stringify(validSignal));

    // Example 2: Send invalid data (will trigger validation)
    setTimeout(() => {
      const invalidSignal = {
        type: 'signal',
        features: [] // Empty array - will fail validation
      };
      socket.send(JSON.stringify(invalidSignal));
    }, 1500);

    // Example 3: Send ping
    setTimeout(() => {
      socket.send(JSON.stringify({ type: 'ping' }));
    }, 3000);
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    if (data.error) {
      console.warn('Server returned error:', data.error, data.details || '');
    }
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  socket.onclose = () => {
    console.log('Disconnected from server');
  };

  return socket;
}

// Usage in browser:
// const socket = connectToHybridServer();

// For Node.js, use: const WebSocket = require('ws');
// Then replace new WebSocket(...) with new WebSocket(WS_URL)

export { connectToHybridServer };
