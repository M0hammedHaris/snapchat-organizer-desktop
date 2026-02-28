/**
 * Device management routes
 * 
 * GET  /api/device/list        - List active devices for user's license
 * POST /api/device/deactivate  - Deactivate a device
 */

import { authenticateRequest } from '../utils/auth.js';
import { errorResponse, successResponse } from '../utils/response.js';

export async function handleDevice(request, env, path) {
  const db = env.DB;

  if (path === '/api/device/list' && request.method === 'GET') {
    return await listDevices(request, db);
  }
  if (path === '/api/device/deactivate' && request.method === 'POST') {
    return await deactivateDevice(request, db);
  }

  return errorResponse('Not found', 404);
}

async function listDevices(request, db) {
  const user = await authenticateRequest(request, db);
  if (!user) return errorResponse('Authentication required', 401);

  const license = await db.prepare(
    `SELECT id, max_devices FROM licenses WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1`
  ).bind(user.id).first();

  if (!license) {
    return successResponse({ devices: [], max_devices: 0 });
  }

  const devices = await db.prepare(
    'SELECT device_id, device_name, platform, activated_at, last_seen_at FROM device_activations WHERE license_id = ? AND is_active = 1'
  ).bind(license.id).all();

  return successResponse({
    devices: devices.results || [],
    max_devices: license.max_devices,
  });
}

async function deactivateDevice(request, db) {
  const user = await authenticateRequest(request, db);
  if (!user) return errorResponse('Authentication required', 401);

  let body;
  try {
    body = await request.json();
  } catch {
    return errorResponse('Invalid JSON body');
  }

  const { device_id } = body;
  if (!device_id) return errorResponse('device_id is required');

  const license = await db.prepare(
    `SELECT id FROM licenses WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1`
  ).bind(user.id).first();

  if (!license) return errorResponse('No active license found');

  const result = await db.prepare(
    'UPDATE device_activations SET is_active = 0 WHERE license_id = ? AND device_id = ?'
  ).bind(license.id, device_id).run();

  if (result.meta.changes === 0) {
    return errorResponse('Device not found or already deactivated');
  }

  return successResponse(null, 'Device deactivated successfully');
}
