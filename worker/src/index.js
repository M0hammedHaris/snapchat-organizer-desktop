/**
 * Snapchat Organizer License API - Cloudflare Worker
 * 
 * Handles: User auth, license management, Stripe webhooks, device activation.
 * Backend for the Snapchat Organizer Desktop application.
 */

import { handleAuth } from './routes/auth.js';
import { handleLicense } from './routes/license.js';
import { handleStripe } from './routes/stripe.js';
import { handleDevice } from './routes/device.js';
import { corsHeaders, jsonResponse, errorResponse } from './utils/response.js';

export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(request) });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // Route requests
      if (path.startsWith('/api/auth/')) {
        return await handleAuth(request, env, path);
      }
      if (path.startsWith('/api/license/')) {
        return await handleLicense(request, env, path);
      }
      if (path.startsWith('/api/stripe/')) {
        return await handleStripe(request, env, path);
      }
      if (path.startsWith('/api/device/')) {
        return await handleDevice(request, env, path);
      }

      // Health check
      if (path === '/api/health') {
        return jsonResponse({ status: 'ok', version: '1.0.0' });
      }

      return errorResponse('Not found', 404);
    } catch (err) {
      console.error('Unhandled error:', err);
      return errorResponse('Internal server error', 500);
    }
  }
};
