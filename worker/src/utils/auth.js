/**
 * Authentication utilities - password hashing and JWT-like token management.
 * Uses Web Crypto API available in Cloudflare Workers.
 */

const encoder = new TextEncoder();

/**
 * Hash a password using PBKDF2 with SHA-256.
 */
export async function hashPassword(password, salt = null) {
  if (!salt) {
    const saltBytes = new Uint8Array(16);
    crypto.getRandomValues(saltBytes);
    salt = btoa(String.fromCharCode(...saltBytes));
  }

  const keyMaterial = await crypto.subtle.importKey(
    'raw', encoder.encode(password), 'PBKDF2', false, ['deriveBits']
  );

  const derivedBits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', salt: encoder.encode(salt), iterations: 100000, hash: 'SHA-256' },
    keyMaterial, 256
  );

  const hash = btoa(String.fromCharCode(...new Uint8Array(derivedBits)));
  return `${salt}:${hash}`;
}

/**
 * Verify a password against a stored hash.
 */
export async function verifyPassword(password, storedHash) {
  const [salt] = storedHash.split(':');
  const computed = await hashPassword(password, salt);
  return computed === storedHash;
}

/**
 * Generate a secure session token.
 */
export function generateToken() {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Generate a license key in format: SNAP-XXXX-XXXX-XXXX-XXXX
 */
export function generateLicenseKey() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // Removed ambiguous chars
  const segments = [];
  for (let s = 0; s < 4; s++) {
    let segment = '';
    for (let i = 0; i < 4; i++) {
      const bytes = new Uint8Array(1);
      crypto.getRandomValues(bytes);
      segment += chars[bytes[0] % chars.length];
    }
    segments.push(segment);
  }
  return `SNAP-${segments.join('-')}`;
}

/**
 * Authenticate a request by extracting and validating the session token.
 * Returns the user object or null.
 */
export async function authenticateRequest(request, db) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }

  const token = authHeader.substring(7);
  
  const session = await db.prepare(
    `SELECT s.user_id, s.expires_at, u.id, u.email, u.name, u.is_active, u.stripe_customer_id
     FROM sessions s
     JOIN users u ON s.user_id = u.id
     WHERE s.token = ? AND s.is_valid = 1`
  ).bind(token).first();

  if (!session) return null;

  // Check expiry
  if (new Date(session.expires_at) < new Date()) {
    await db.prepare('UPDATE sessions SET is_valid = 0 WHERE token = ?').bind(token).run();
    return null;
  }

  return {
    id: session.user_id,
    email: session.email,
    name: session.name,
    is_active: session.is_active,
    stripe_customer_id: session.stripe_customer_id,
  };
}
