const fs = require('fs');

// File paths
const envPath = '.env';
const examplePath = '.env.example';

// Read both files
const envContent = fs.readFileSync(envPath, 'utf-8');
const exampleContent = fs.existsSync(examplePath) ? fs.readFileSync(examplePath, 'utf-8') : '';

// Parse both files into objects
const parseEnv = (content) =>
  Object.fromEntries(content.split('\n').filter(Boolean).map(line => line.split('=')));

const env = parseEnv(envContent);
const example = parseEnv(exampleContent);

// Merge keys from .env into .env.example
const merged = { ...example, ...Object.fromEntries(Object.keys(env).map(key => [key, example[key] || ''])) };

// Write updated .env.example
const updatedContent = Object.entries(merged).map(([key, value]) => `${key}=${value}`).join('\n');
fs.writeFileSync(examplePath, updatedContent);

console.log('.env.example is updated!');
