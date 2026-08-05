import { test } from 'node:test';
import assert from 'node:assert/strict';
import request from 'supertest';
import { createApp, reply } from '../src/app.js';

test('reply() answers Marco with Polo!', () => {
  assert.deepEqual(reply('Marco'), { match: true, reply: 'Polo!' });
  assert.deepEqual(reply('  marco  '), { match: true, reply: 'Polo!' });
});

test('reply() echoes anything that is not Marco', () => {
  const result = reply('hello');
  assert.equal(result.match, false);
  assert.match(result.reply, /hello/);
});

test('GET /api/health returns ok', async () => {
  const res = await request(createApp()).get('/api/health');
  assert.equal(res.status, 200);
  assert.deepEqual(res.body, { status: 'ok', service: 'marco' });
});

test('POST /api/marco with "Marco" returns Polo!', async () => {
  const res = await request(createApp())
    .post('/api/marco')
    .send({ message: 'Marco' });
  assert.equal(res.status, 200);
  assert.deepEqual(res.body, { match: true, reply: 'Polo!' });
});

test('POST /api/marco rejects a non-string message', async () => {
  const res = await request(createApp())
    .post('/api/marco')
    .send({ message: 42 });
  assert.equal(res.status, 400);
});

test('GET / serves the web app', async () => {
  const res = await request(createApp()).get('/');
  assert.equal(res.status, 200);
  assert.match(res.text, /<title>Marco<\/title>/);
});
