"""Test updated subscription model: no trial, free/pro/premium tiers, device limits."""

import sys
sys.path.insert(0, '.')

from src.license.license_manager import LicenseManager
from src.utils.config import (
    FEATURE_ACCESS, TIER_FREE, TIER_PRO, TIER_PREMIUM,
    DEVICE_LIMITS, can_access_feature,
)

# 1. Verify feature matrix
print("=== Feature Access Matrix ===")
for tier in [TIER_FREE, TIER_PRO, TIER_PREMIUM]:
    limit = FEATURE_ACCESS[tier]['max_files_per_month']
    limit_str = "Unlimited" if limit == -1 else str(limit)
    print(f"\n{tier.upper()} ({limit_str} downloads/month):")
    for feature in ['download_memories', 'organize_chat_media', 'overlay_compositing',
                     'gps_embedding', 'remove_duplicates', 'organize_by_year', 'fix_timestamps']:
        access = can_access_feature(tier, feature)
        print(f"  {feature}: {'YES' if access else 'NO'}")

# 2. Verify device limits
print("\n=== Device Limits ===")
assert DEVICE_LIMITS[TIER_FREE] == 1, f"Free should be 1 device, got {DEVICE_LIMITS[TIER_FREE]}"
assert DEVICE_LIMITS[TIER_PRO] == 2, f"Pro should be 2 devices, got {DEVICE_LIMITS[TIER_PRO]}"
assert DEVICE_LIMITS[TIER_PREMIUM] == 3, f"Premium should be 3 devices, got {DEVICE_LIMITS[TIER_PREMIUM]}"
print(f"  Free:    {DEVICE_LIMITS[TIER_FREE]} device(s)")
print(f"  Pro:     {DEVICE_LIMITS[TIER_PRO]} device(s)")
print(f"  Premium: {DEVICE_LIMITS[TIER_PREMIUM]} device(s)")

# 3. Test LicenseManager device properties (offline, no server)
print("\n=== LicenseManager Device Properties ===")
lm = LicenseManager()
# Default (not logged in) should show free tier limits
print(f"  Tier: {lm.current_tier}")
print(f"  Max devices: {lm.max_devices}")
print(f"  Active devices: {lm.active_devices}")
assert lm.max_devices == DEVICE_LIMITS[TIER_FREE], f"Expected {DEVICE_LIMITS[TIER_FREE]}, got {lm.max_devices}"
assert lm.active_devices == 0, f"Expected 0 active devices, got {lm.active_devices}"

# 4. Test registration (should create FREE account, no trial)
print("\n=== Register (expect FREE, no trial) ===")
import time
email = f"sub_test_{int(time.time())}@example.com"
result = lm.register(email, 'password123', 'Sub Test')
print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")
print(f"Tier: {lm.current_tier}")
print(f"Is trial: {lm.is_trial}")
assert lm.current_tier == 'free', f"Expected free, got {lm.current_tier}"
assert not lm.is_trial, "Expected no trial"

# 5. Test mock upgrade to Pro
print("\n=== Upgrade to Pro ===")
upgrade = lm.confirm_upgrade('pro')
print(f"Success: {upgrade.get('success')}")
print(f"Tier: {lm.current_tier}")
print(f"Max devices: {lm.max_devices}")
assert lm.current_tier == 'pro', f"Expected pro, got {lm.current_tier}"
assert lm.max_devices == 2, f"Pro should have max 2 devices, got {lm.max_devices}"

# 6. Test mock upgrade to Premium
print("\n=== Upgrade to Premium ===")
upgrade = lm.confirm_upgrade('premium')
print(f"Success: {upgrade.get('success')}")
print(f"Tier: {lm.current_tier}")
print(f"Max devices: {lm.max_devices}")
assert lm.current_tier == 'premium', f"Expected premium, got {lm.current_tier}"
assert lm.max_devices == 3, f"Premium should have max 3 devices, got {lm.max_devices}"

# 7. Logout and login - should retain premium
print("\n=== Logout & Login ===")
lm.logout()
assert lm.current_tier == 'free', "Should be free after logout"

result = lm.login(email, 'password123')
print(f"Tier after login: {lm.current_tier}")
assert lm.current_tier == 'premium', f"Expected premium, got {lm.current_tier}"
assert not lm.is_trial, "No trial after login"

print("\n=== ALL TESTS PASSED ===")
