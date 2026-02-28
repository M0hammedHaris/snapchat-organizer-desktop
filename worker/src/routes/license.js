/**
 * License routes - Validate, activate key, check status
 * 
 * GET  /api/license/status   - Get current license status
 * POST /api/license/activate - Activate a license key on this account
 * POST /api/license/validate - Validate license key + device (desktop app calls this on startup)
 */

import { authenticateRequest, generateLicenseKey } from '../utils/auth.js';
import { errorResponse, successResponse } from '../utils/response.js';

export async function handleLicense(request, env, path) {
  const db = env.DB;

  if (path === '/api/license/validate' && request.method === 'POST') {
    return await validateLicense(request, db);
  }
  if (path === '/api/license/status' && request.method === 'GET') {
    return await licenseStatus(request, db);
  }
  if (path === '/api/license/activate' && request.method === 'POST') {
    return await activateLicenseKey(request, db);
  }

  return errorResponse('Not found', 404);
}

/**
 * Validate license - called by desktop app on startup.
 * Checks token + license validity + device activation.
 */
async function validateLicense(request, db) {
  const user = await authenticateRequest(request, db);
  if (!user) {
    return errorResponse('Authentication required', 401);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return errorResponse('Invalid JSON body');
  }

  const { device_id, device_name, platform } = body;
  if (!device_id) {
    return errorResponse('device_id is required');
  }

  // Get active license
  const license = await db.prepare(
    `SELECT * FROM licenses WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1`
  ).bind(user.id).first();

  if (!license) {
    return successResponse({
      valid: false,
      tier: 'free',
      reason: 'No active license found',
    });
  }

  // Check expiry
  if (license.expires_at && new Date(license.expires_at) < new Date()) {
    if (license.is_trial) {
      // Expire the trial 
      await db.prepare(
        "UPDATE licenses SET status = 'expired' WHERE id = ?"
      ).bind(license.id).run();
      
      return successResponse({
        valid: false,
        tier: 'free',
        reason: 'Trial period has expired',
        expired: true,
      });
    }
  }

  // Check/register device activation
  const existingDevice = await db.prepare(
    'SELECT * FROM device_activations WHERE license_id = ? AND device_id = ?'
  ).bind(license.id, device_id).first();

  if (existingDevice) {
    // Update last seen
    await db.prepare(
      "UPDATE device_activations SET last_seen_at = datetime('now') WHERE id = ?"
    ).bind(existingDevice.id).run();
  } else {
    // Check device limit
    const deviceCount = await db.prepare(
      'SELECT COUNT(*) as count FROM device_activations WHERE license_id = ? AND is_active = 1'
    ).bind(license.id).first();

    if (deviceCount.count >= license.max_devices) {
      return successResponse({
        valid: false,
        tier: license.tier,
        reason: `Device limit reached (${license.max_devices} devices). Deactivate a device first.`,
        device_limit_reached: true,
      });
    }

    // Register new device
    await db.prepare(
      `INSERT INTO device_activations (license_id, device_id, device_name, platform)
       VALUES (?, ?, ?, ?)`
    ).bind(license.id, device_id, device_name || 'Unknown', platform || 'Unknown').run();
  }

  return successResponse({
    valid: true,
    tier: license.tier,
    is_trial: !!license.is_trial,
    expires_at: license.expires_at,
    license_key: license.license_key,
  });
}

/**
 * Get license status for authenticated user.
 */
async function licenseStatus(request, db) {
  const user = await authenticateRequest(request, db);
  if (!user) {
    return errorResponse('Authentication required', 401);
  }

  const license = await db.prepare(
    `SELECT * FROM licenses WHERE user_id = ? ORDER BY created_at DESC LIMIT 1`
  ).bind(user.id).first();

  if (!license) {
    return successResponse({ tier: 'free', status: 'none', license: null });
  }

  // Get device count
  const deviceCount = await db.prepare(
    'SELECT COUNT(*) as count FROM device_activations WHERE license_id = ? AND is_active = 1'
  ).bind(license.id).first();

  return successResponse({
    tier: license.tier,
    status: license.status,
    license: {
      key: license.license_key,
      is_trial: !!license.is_trial,
      expires_at: license.expires_at,
      max_devices: license.max_devices,
      active_devices: deviceCount.count,
      stripe_subscription_id: license.stripe_subscription_id,
    }
  });
}

/**
 * Activate a purchased license key on the user's account.
 */
async function activateLicenseKey(request, db) {
  const user = await authenticateRequest(request, db);
  if (!user) {
    return errorResponse('Authentication required', 401);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return errorResponse('Invalid JSON body');
  }

  const { license_key } = body;
  if (!license_key) {
    return errorResponse('license_key is required');
  }

  // Find the license
  const license = await db.prepare('SELECT * FROM licenses WHERE license_key = ?')
    .bind(license_key).first();

  if (!license) {
    return errorResponse('Invalid license key');
  }

  if (license.user_id !== user.id) {
    return errorResponse('This license key belongs to another account');
  }

  if (license.status === 'active') {
    return successResponse({
      tier: license.tier,
      already_active: true,
    }, 'License is already active');
  }

  // Activate
  await db.prepare(
    "UPDATE licenses SET status = 'active', activated_at = datetime('now') WHERE id = ?"
  ).bind(license.id).run();

  return successResponse({
    tier: license.tier,
    key: license.license_key,
    expires_at: license.expires_at,
  }, 'License activated successfully');
}
