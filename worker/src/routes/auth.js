/**
 * Auth routes - Register, Login, Logout, Profile
 * 
 * POST /api/auth/register  - Create account + free license + 7-day trial
 * POST /api/auth/login     - Login and get session token
 * POST /api/auth/logout    - Invalidate session
 * GET  /api/auth/profile   - Get current user profile + license info
 */

import { hashPassword, verifyPassword, generateToken, generateLicenseKey } from '../utils/auth.js';
import { jsonResponse, errorResponse, successResponse } from '../utils/response.js';
import { authenticateRequest } from '../utils/auth.js';

const SESSION_DURATION_DAYS = 30;
const TRIAL_DURATION_DAYS = 7;

export async function handleAuth(request, env, path) {
  const db = env.DB;

  if (path === '/api/auth/register' && request.method === 'POST') {
    return await register(request, db);
  }
  if (path === '/api/auth/login' && request.method === 'POST') {
    return await login(request, db);
  }
  if (path === '/api/auth/logout' && request.method === 'POST') {
    return await logout(request, db);
  }
  if (path === '/api/auth/profile' && request.method === 'GET') {
    return await getProfile(request, db);
  }

  return errorResponse('Not found', 404);
}

async function register(request, db) {
  let body;
  try {
    body = await request.json();
  } catch {
    return errorResponse('Invalid JSON body');
  }

  const { email, password, name } = body;

  if (!email || !password || !name) {
    return errorResponse('Email, password, and name are required');
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return errorResponse('Invalid email format');
  }

  // Validate password strength
  if (password.length < 8) {
    return errorResponse('Password must be at least 8 characters');
  }

  // Check if user already exists
  const existing = await db.prepare('SELECT id FROM users WHERE email = ?')
    .bind(email.toLowerCase()).first();
  if (existing) {
    return errorResponse('An account with this email already exists');
  }

  // Hash password
  const passwordHash = await hashPassword(password);

  // Create user
  const userResult = await db.prepare(
    'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?) RETURNING id'
  ).bind(email.toLowerCase(), passwordHash, name).first();

  const userId = userResult.id;

  // Generate trial license (Pro tier for 7 days)
  const licenseKey = generateLicenseKey();
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + TRIAL_DURATION_DAYS);

  await db.prepare(
    `INSERT INTO licenses (user_id, license_key, tier, status, is_trial, expires_at, max_devices)
     VALUES (?, ?, 'pro', 'active', 1, ?, 2)`
  ).bind(userId, licenseKey, expiresAt.toISOString()).run();

  // Create session
  const token = generateToken();
  const sessionExpires = new Date();
  sessionExpires.setDate(sessionExpires.getDate() + SESSION_DURATION_DAYS);

  await db.prepare(
    'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)'
  ).bind(userId, token, sessionExpires.toISOString()).run();

  return successResponse({
    token,
    user: { id: userId, email: email.toLowerCase(), name },
    license: {
      key: licenseKey,
      tier: 'pro',
      is_trial: true,
      expires_at: expiresAt.toISOString(),
    }
  }, 'Account created with 7-day Pro trial');
}

async function login(request, db) {
  let body;
  try {
    body = await request.json();
  } catch {
    return errorResponse('Invalid JSON body');
  }

  const { email, password, device_id } = body;

  if (!email || !password) {
    return errorResponse('Email and password are required');
  }

  // Find user
  const user = await db.prepare('SELECT * FROM users WHERE email = ?')
    .bind(email.toLowerCase()).first();

  if (!user) {
    return errorResponse('Invalid email or password', 401);
  }

  if (!user.is_active) {
    return errorResponse('Account is deactivated', 403);
  }

  // Verify password
  const valid = await verifyPassword(password, user.password_hash);
  if (!valid) {
    return errorResponse('Invalid email or password', 401);
  }

  // Create session
  const token = generateToken();
  const sessionExpires = new Date();
  sessionExpires.setDate(sessionExpires.getDate() + SESSION_DURATION_DAYS);

  await db.prepare(
    'INSERT INTO sessions (user_id, token, device_id, expires_at) VALUES (?, ?, ?, ?)'
  ).bind(user.id, token, device_id || null, sessionExpires.toISOString()).run();

  // Get active license
  const license = await db.prepare(
    `SELECT * FROM licenses WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1`
  ).bind(user.id).first();

  // Check if trial expired
  let licenseInfo = null;
  if (license) {
    const isExpired = license.expires_at && new Date(license.expires_at) < new Date();
    if (isExpired && license.is_trial) {
      // Downgrade trial to free
      await db.prepare(
        "UPDATE licenses SET tier = 'free', status = 'expired', is_trial = 0 WHERE id = ?"
      ).bind(license.id).run();
      
      // Create free license
      const freeKey = generateLicenseKey();
      await db.prepare(
        `INSERT INTO licenses (user_id, license_key, tier, status, is_trial, max_devices)
         VALUES (?, ?, 'free', 'active', 0, 1)`
      ).bind(user.id, freeKey).run();
      
      licenseInfo = { key: freeKey, tier: 'free', is_trial: false, expires_at: null };
    } else {
      licenseInfo = {
        key: license.license_key,
        tier: license.tier,
        is_trial: !!license.is_trial,
        expires_at: license.expires_at,
      };
    }
  }

  return successResponse({
    token,
    user: { id: user.id, email: user.email, name: user.name },
    license: licenseInfo,
  }, 'Login successful');
}

async function logout(request, db) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return errorResponse('No session token provided', 401);
  }

  const token = authHeader.substring(7);
  await db.prepare('UPDATE sessions SET is_valid = 0 WHERE token = ?').bind(token).run();

  return successResponse(null, 'Logged out successfully');
}

async function getProfile(request, db) {
  const user = await authenticateRequest(request, db);
  if (!user) {
    return errorResponse('Authentication required', 401);
  }

  // Get active license
  const license = await db.prepare(
    `SELECT * FROM licenses WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1`
  ).bind(user.id).first();

  // Get device activations
  let devices = [];
  if (license) {
    const deviceResults = await db.prepare(
      'SELECT device_id, device_name, platform, activated_at, last_seen_at FROM device_activations WHERE license_id = ? AND is_active = 1'
    ).bind(license.id).all();
    devices = deviceResults.results || [];
  }

  return successResponse({
    user: { id: user.id, email: user.email, name: user.name },
    license: license ? {
      key: license.license_key,
      tier: license.tier,
      is_trial: !!license.is_trial,
      expires_at: license.expires_at,
      max_devices: license.max_devices,
    } : null,
    devices,
  });
}
