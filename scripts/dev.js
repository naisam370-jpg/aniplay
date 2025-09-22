#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

console.log('Starting AniPlay in development mode...');

const electron = spawn('electron', ['.', '--development'], {
  cwd: path.join(__dirname, '..'),
  stdio: 'inherit'
});

electron.on('close', (code) => {
  console.log(`Electron exited with code ${code}`);
});
