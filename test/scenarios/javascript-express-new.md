---
id: javascript-express-new
language: JS
framework: Express
state: new
phase: 1
priority: medium
fixture: javascript-express
---

# JS Express — New Project

## Project Description
A new Express.js API server using plain JavaScript (not TypeScript), with a minimal server entry point and package.json.

## Fixture Contents
- package.json
- src/index.js
- src/routes/

## /generate Evaluation Focus
- node start command (e.g., `node src/index.js`)
- nodemon dev command for development
- Express-specific security guidance (helmet middleware, rate limiting, CORS)
- Recommended src/ directory structure (routes, middleware, controllers)

## /audit Evaluation Focus
- Test command detection (npm test, jest, or mocha)
- Security middleware suggestions (helmet, express-rate-limit, cors)
- Correct identification as plain JavaScript (not TypeScript)
