import express from 'express';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const publicDir = path.join(__dirname, '..', 'public');

/**
 * Given a message, return the Marco Polo style reply.
 * "marco" (case/whitespace-insensitive) is answered with "Polo!".
 * Anything else is echoed back so callers can tell they were heard.
 */
export function reply(message) {
  const normalized = String(message ?? '').trim().toLowerCase();
  if (normalized === 'marco') {
    return { match: true, reply: 'Polo!' };
  }
  return { match: false, reply: `I only answer to "Marco". You said: "${message ?? ''}"` };
}

export function createApp() {
  const app = express();
  app.use(express.json());
  app.use(express.static(publicDir));

  app.get('/api/health', (_req, res) => {
    res.json({ status: 'ok', service: 'marco' });
  });

  app.post('/api/marco', (req, res) => {
    const { message } = req.body ?? {};
    if (typeof message !== 'string') {
      res.status(400).json({ error: 'Expected a string "message" field.' });
      return;
    }
    res.json(reply(message));
  });

  return app;
}
