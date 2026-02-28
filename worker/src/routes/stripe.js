/**
 * Stripe / payment routes - Handle checkout and webhooks.
 * 
 * Supports a MOCK_STRIPE mode for testing without a real Stripe account.
 * When env.MOCK_STRIPE === "true":
 *   - create-checkout returns a mock confirmation URL (API endpoint)
 *   - mock-confirm simulates a successful subscription payment
 * 
 * POST /api/stripe/webhook          - Stripe webhook endpoint (real mode)
 * POST /api/stripe/create-checkout   - Create Stripe Checkout session URL
 * POST /api/stripe/mock-confirm      - Simulate successful payment (mock mode)
 */

import { authenticateRequest, generateLicenseKey } from '../utils/auth.js';
import { errorResponse, successResponse } from '../utils/response.js';

export async function handleStripe(request, env, path) {
  const db = env.DB;

  if (path === '/api/stripe/create-checkout' && request.method === 'POST') {
    return await createCheckout(request, env, db);
  }
  if (path === '/api/stripe/mock-confirm' && request.method === 'POST') {
    return await mockConfirmPayment(request, env, db);
  }
  if (path === '/api/stripe/webhook' && request.method === 'POST') {
    return await stripeWebhook(request, env, db);
  }

  return errorResponse('Not found', 404);
}

function isMockMode(env) {
  return env.MOCK_STRIPE === 'true' || env.MOCK_STRIPE === true;
}

/**
 * Create a Stripe Checkout session.
 * In mock mode, returns a mock-confirm API URL instead.
 */
async function createCheckout(request, env, db) {
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

  const { tier } = body;
  if (!tier || !['pro', 'premium'].includes(tier)) {
    return errorResponse('Valid tier required: pro or premium');
  }

  // ── Mock mode ──
  if (isMockMode(env)) {
    // Return a mock checkout URL that the desktop app will call to confirm
    const mockUrl = new URL(request.url);
    mockUrl.pathname = '/api/stripe/mock-confirm';

    return successResponse({
      checkout_url: mockUrl.toString(),
      mock: true,
      tier,
      user_id: user.id,
      message: 'Mock mode: call POST /api/stripe/mock-confirm with your auth token and {tier} to simulate payment.',
    }, 'Mock checkout session created');
  }

  // ── Real Stripe mode ──
  const STRIPE_SECRET = env.STRIPE_SECRET_KEY;
  if (!STRIPE_SECRET) {
    return errorResponse('Payment system not configured', 503);
  }

  const priceId = tier === 'pro' ? env.STRIPE_PRICE_PRO : env.STRIPE_PRICE_PREMIUM;
  if (!priceId) {
    return errorResponse(`Price not configured for tier: ${tier}`, 503);
  }

  // Create or reuse Stripe customer
  let customerId = user.stripe_customer_id;
  if (!customerId) {
    const customerResp = await fetch('https://api.stripe.com/v1/customers', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        email: user.email,
        name: user.name,
        'metadata[user_id]': String(user.id),
      }),
    });
    const customer = await customerResp.json();
    if (customer.error) {
      return errorResponse('Failed to create payment profile: ' + customer.error.message);
    }
    customerId = customer.id;

    await db.prepare('UPDATE users SET stripe_customer_id = ? WHERE id = ?')
      .bind(customerId, user.id).run();
  }

  // Create Checkout Session
  const params = new URLSearchParams({
    'customer': customerId,
    'mode': 'subscription',
    'line_items[0][price]': priceId,
    'line_items[0][quantity]': '1',
    'success_url': env.CHECKOUT_SUCCESS_URL || 'https://snapchat-organizer.machive.dev/success',
    'cancel_url': env.CHECKOUT_CANCEL_URL || 'https://snapchat-organizer.machive.dev/cancel',
    'metadata[user_id]': String(user.id),
    'metadata[tier]': tier,
    'subscription_data[metadata][user_id]': String(user.id),
    'subscription_data[metadata][tier]': tier,
  });

  const sessionResp = await fetch('https://api.stripe.com/v1/checkout/sessions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${STRIPE_SECRET}`,
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params,
  });
  const session = await sessionResp.json();

  if (session.error) {
    return errorResponse('Failed to create checkout: ' + session.error.message);
  }

  return successResponse({ checkout_url: session.url }, 'Checkout session created');
}

/**
 * Mock payment confirmation - simulates a successful Stripe payment.
 * Only available when MOCK_STRIPE=true.
 * 
 * Accepts: { tier: "pro" | "premium" }
 * Does the same work as webhook checkout.session.completed:
 *   - Expires old licenses
 *   - Creates a new paid license for the given tier
 *   - Returns the new license details
 */
async function mockConfirmPayment(request, env, db) {
  if (!isMockMode(env)) {
    return errorResponse('Mock mode is not enabled', 403);
  }

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

  const { tier } = body;
  if (!tier || !['pro', 'premium'].includes(tier)) {
    return errorResponse('Valid tier required: pro or premium');
  }

  // Expire old active licenses
  await db.prepare(
    "UPDATE licenses SET status = 'replaced' WHERE user_id = ? AND status = 'active'"
  ).bind(user.id).run();

  // Create new paid license
  const licenseKey = generateLicenseKey();
  // Device limits: free=1, pro=2, premium=3
  const maxDevices = tier === 'premium' ? 3 : 2;

  // Subscription lasts 30 days from now (mock)
  const expiresAt = new Date();
  expiresAt.setDate(expiresAt.getDate() + 30);

  await db.prepare(
    `INSERT INTO licenses (user_id, license_key, tier, status, is_trial, max_devices, expires_at, stripe_subscription_id)
     VALUES (?, ?, ?, 'active', 0, ?, ?, ?)`
  ).bind(
    user.id, licenseKey, tier, maxDevices,
    expiresAt.toISOString(),
    `mock_sub_${Date.now()}`  // fake subscription ID
  ).run();

  return successResponse({
    tier,
    license_key: licenseKey,
    is_trial: false,
    expires_at: expiresAt.toISOString(),
    max_devices: maxDevices,
    mock: true,
  }, `Mock payment successful! Upgraded to ${tier}.`);
}

/**
 * Stripe webhook handler (real mode only).
 * Verifies signature and processes payment events.
 */
async function stripeWebhook(request, env, db) {
  const STRIPE_SECRET = env.STRIPE_SECRET_KEY;
  const WEBHOOK_SECRET = env.STRIPE_WEBHOOK_SECRET;

  if (!STRIPE_SECRET || !WEBHOOK_SECRET) {
    return errorResponse('Webhook not configured', 503);
  }

  const signature = request.headers.get('stripe-signature');
  if (!signature) {
    return errorResponse('Missing stripe-signature header', 400);
  }

  const rawBody = await request.text();

  const isValid = await verifyStripeSignature(rawBody, signature, WEBHOOK_SECRET);
  if (!isValid) {
    return errorResponse('Invalid webhook signature', 400);
  }

  const event = JSON.parse(rawBody);

  switch (event.type) {
    case 'checkout.session.completed':
      await handleCheckoutComplete(event.data.object, db);
      break;
    case 'customer.subscription.updated':
      await handleSubscriptionUpdated(event.data.object, db);
      break;
    case 'customer.subscription.deleted':
      await handleSubscriptionDeleted(event.data.object, db);
      break;
    case 'invoice.payment_failed':
      await handlePaymentFailed(event.data.object, db);
      break;
  }

  return successResponse(null, 'Webhook processed');
}

async function handleCheckoutComplete(session, db) {
  const userId = parseInt(session.metadata?.user_id);
  const tier = session.metadata?.tier || 'pro';

  if (!userId) return;

  await db.prepare(
    "UPDATE licenses SET status = 'replaced' WHERE user_id = ? AND status = 'active'"
  ).bind(userId).run();

  const licenseKey = generateLicenseKey();
  // Device limits: free=1, pro=2, premium=3
  const maxDevices = tier === 'premium' ? 3 : 2;

  await db.prepare(
    `INSERT INTO licenses (user_id, license_key, tier, status, is_trial, max_devices, stripe_subscription_id)
     VALUES (?, ?, ?, 'active', 0, ?, ?)`
  ).bind(userId, licenseKey, tier, maxDevices, session.subscription || null).run();
}

async function handleSubscriptionUpdated(subscription, db) {
  const subId = subscription.id;

  if (subscription.cancel_at_period_end) {
    await db.prepare(
      "UPDATE licenses SET expires_at = ? WHERE stripe_subscription_id = ? AND status = 'active'"
    ).bind(new Date(subscription.current_period_end * 1000).toISOString(), subId).run();
  }
}

async function handleSubscriptionDeleted(subscription, db) {
  const subId = subscription.id;

  await db.prepare(
    "UPDATE licenses SET status = 'expired' WHERE stripe_subscription_id = ?"
  ).bind(subId).run();

  const license = await db.prepare(
    'SELECT user_id FROM licenses WHERE stripe_subscription_id = ?'
  ).bind(subId).first();

  if (license) {
    const freeKey = generateLicenseKey();
    await db.prepare(
      `INSERT INTO licenses (user_id, license_key, tier, status, is_trial, max_devices)
       VALUES (?, ?, 'free', 'active', 0, 1)`
    ).bind(license.user_id, freeKey).run();
  }
}

async function handlePaymentFailed(invoice, db) {
  console.error('Payment failed for invoice:', invoice.id);
}

async function verifyStripeSignature(payload, sigHeader, secret) {
  const parts = sigHeader.split(',').reduce((acc, part) => {
    const [key, value] = part.split('=');
    acc[key] = value;
    return acc;
  }, {});

  const timestamp = parts['t'];
  const signatures = Object.entries(parts)
    .filter(([k]) => k === 'v1')
    .map(([, v]) => v);

  if (!timestamp || signatures.length === 0) return false;

  const age = Math.abs(Date.now() / 1000 - parseInt(timestamp));
  if (age > 300) return false;

  const signedPayload = `${timestamp}.${payload}`;
  const encoder = new TextEncoder();

  const key = await crypto.subtle.importKey(
    'raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  );
  const mac = await crypto.subtle.sign('HMAC', key, encoder.encode(signedPayload));
  const expected = Array.from(new Uint8Array(mac)).map(b => b.toString(16).padStart(2, '0')).join('');

  return signatures.some(sig => sig === expected);
}
