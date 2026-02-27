"""Device fingerprinting for license validation.

This module generates unique hardware identifiers for the current device
to support device-based license activation and validation.
"""

import hashlib
import platform
import socket
import uuid
from typing import Dict, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


def get_mac_address() -> str:
    """Get the MAC address of the first network interface.
    
    Returns:
        MAC address as a hex string, or "unknown" if not available
    """
    try:
        mac = uuid.getnode()
        # Check if we got a real MAC or a random one
        if (mac >> 40) % 2:
            # Random MAC (multicast bit set), not reliable
            return "unknown"
        mac_hex = ':'.join(('%012x' % mac)[i:i+2] for i in range(0, 12, 2))
        return mac_hex
    except Exception as e:
        logger.warning(f"Failed to get MAC address: {e}")
        return "unknown"


def get_cpu_id() -> str:
    """Get a CPU identifier.
    
    Returns:
        CPU identifier string
    """
    try:
        # This works on most platforms
        return platform.processor() or platform.machine() or "unknown"
    except Exception as e:
        logger.warning(f"Failed to get CPU ID: {e}")
        return "unknown"


def get_hostname() -> str:
    """Get the system hostname.
    
    Returns:
        Hostname string
    """
    try:
        return socket.gethostname() or "unknown"
    except Exception as e:
        logger.warning(f"Failed to get hostname: {e}")
        return "unknown"


def get_platform_info() -> Dict[str, str]:
    """Get detailed platform information.
    
    Returns:
        Dictionary with platform details
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }


def get_windows_machine_guid() -> Optional[str]:
    """Get the Windows MachineGuid from registry.
    
    This is a stable identifier that persists across reboots.
    
    Returns:
        Machine GUID string, or None if not on Windows or unavailable
    """
    if platform.system() != 'Windows':
        return None
    
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        return machine_guid
    except Exception as e:
        logger.warning(f"Failed to get Windows MachineGuid: {e}")
        return None


def get_macos_hardware_uuid() -> Optional[str]:
    """Get the macOS Hardware UUID.
    
    This is a stable identifier unique to each Mac.
    
    Returns:
        Hardware UUID string, or None if not on macOS or unavailable
    """
    if platform.system() != 'Darwin':
        return None
    
    try:
        import subprocess
        result = subprocess.run(
            ['system_profiler', 'SPHardwareDataType'],
            capture_output=True,
            text=True,
            timeout=5
        )
        for line in result.stdout.split('\n'):
            if 'Hardware UUID' in line:
                return line.split(':')[1].strip()
    except Exception as e:
        logger.warning(f"Failed to get macOS Hardware UUID: {e}")
    
    return None


def get_linux_machine_id() -> Optional[str]:
    """Get the Linux machine-id.
    
    This is a stable identifier set during OS installation.
    
    Returns:
        Machine ID string, or None if not on Linux or unavailable
    """
    if platform.system() != 'Linux':
        return None
    
    for path in ['/etc/machine-id', '/var/lib/dbus/machine-id']:
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except Exception:
            continue
    
    logger.warning("Failed to get Linux machine-id")
    return None


def get_hardware_id() -> str:
    """Generate a unique hardware identifier for the current device.
    
    This combines multiple hardware identifiers to create a stable,
    unique fingerprint for the device. The ID is hashed for privacy.
    
    Returns:
        64-character hex string (SHA-256 hash)
    """
    components = []
    
    # Platform-specific stable identifier
    system = platform.system()
    if system == 'Windows':
        machine_id = get_windows_machine_guid()
    elif system == 'Darwin':
        machine_id = get_macos_hardware_uuid()
    else:
        machine_id = get_linux_machine_id()
    
    if machine_id:
        components.append(machine_id)
    
    # Fallback components
    components.append(get_mac_address())
    components.append(get_cpu_id())
    components.append(platform.machine())
    components.append(platform.system())
    
    # Combine and hash
    fingerprint = '|'.join(components)
    hardware_id = hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()
    
    logger.debug(f"Generated hardware ID: {hardware_id[:16]}...")
    return hardware_id


def get_device_name() -> str:
    """Get a user-friendly device name.
    
    Returns:
        Device name string (e.g., "John's MacBook Pro")
    """
    hostname = get_hostname()
    system = platform.system()
    
    # Clean up hostname
    if hostname.endswith('.local'):
        hostname = hostname[:-6]
    if hostname.endswith('.lan'):
        hostname = hostname[:-4]
    
    return f"{hostname} ({system})"


def get_platform_name() -> str:
    """Get a friendly platform name.
    
    Returns:
        Platform name (e.g., "macOS 14.0", "Windows 11", "Linux")
    """
    system = platform.system()
    
    if system == 'Darwin':
        version = platform.mac_ver()[0]
        return f"macOS {version}" if version else "macOS"
    elif system == 'Windows':
        version = platform.version()
        release = platform.release()
        return f"Windows {release}"
    elif system == 'Linux':
        try:
            # Try to get distribution info
            import distro
            return f"{distro.name()} {distro.version()}"
        except ImportError:
            return f"Linux {platform.release()}"
    
    return system


def get_device_info() -> Dict[str, str]:
    """Get comprehensive device information.
    
    Returns:
        Dictionary with device details for registration
    """
    return {
        'hardware_id': get_hardware_id(),
        'device_name': get_device_name(),
        'platform': get_platform_name(),
        'hostname': get_hostname(),
        'mac_address': get_mac_address(),
        'system': platform.system(),
        'machine': platform.machine(),
    }
