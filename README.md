# marco

A tiny **Marco → Polo** web app used to demonstrate a working Cloud Agent
development environment. Type `Marco`, and the server answers `Polo!`.

## Requirements

- Node.js >= 20

## Getting started

```bash
npm install      # install dependencies
npm run dev      # start the dev server with auto-reload
```

Then open http://localhost:3000 and call out `Marco`.

## Scripts

| Command        | Description                                  |
| -------------- | -------------------------------------------- |
| `npm start`    | Start the server (`src/server.js`).          |
| `npm run dev`  | Start the server with `--watch` auto-reload. |
| `npm test`     | Run the test suite (`node --test`).          |
| `npm run lint` | Lint the project with ESLint.                |

## API

| Method | Path          | Description                                   |
| ------ | ------------- | --------------------------------------------- |
| `GET`  | `/api/health` | Health check → `{ "status": "ok" }`.          |
| `POST` | `/api/marco`  | Body `{ "message": "Marco" }` → `{ "match": true, "reply": "Polo!" }`. |

## Project layout

```
src/         Express app (app.js) and server entrypoint (server.js)
public/      Static frontend (HTML, CSS, JS)
test/        Node test-runner tests
```

## Cloud Agent environment

`.cursor/environment.json` runs `npm install`, exposes port `3000`, and starts
the dev server in a persistent terminal named `dev-server`.
