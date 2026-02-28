/**
 * Response utilities for consistent API responses.
 */

const ALLOWED_ORIGINS = [
  'https://snapchat-organizer.machive.dev',
];

/**
 * Return CORS headers. When a request is provided, validates the Origin
 * against an allowlist. Desktop HTTP clients send no Origin header and
 * are allowed through. Browser requests from unknown origins are blocked.
 */
export function corsHeaders(request = null) {
  const origin = request?.headers?.get?.('Origin') ?? null;
  // Desktop apps send no Origin header — allow those requests.
  // For browser requests, check against allowlist.
  const allowOrigin = (!origin || ALLOWED_ORIGINS.includes(origin))
    ? (origin || 'https://snapchat-organizer.machive.dev')
    : null;

  return {
    'Access-Control-Allow-Origin': allowOrigin || '',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
    ...(origin ? { 'Vary': 'Origin' } : {}),
  };
}

export function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(),
    },
  });
}

export function errorResponse(message, status = 400) {
  return jsonResponse({ error: message, success: false }, status);
}

export function successResponse(data, message = 'Success') {
  return jsonResponse({ success: true, message, data });
}
