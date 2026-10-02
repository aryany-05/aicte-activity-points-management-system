"""
utils/qr_generator.py - QR Code Generator
AICTE Activity & Points Management System

Generates QR codes for event attendance tracking.
"""

import os
import qrcode
import qrcode.constants
from flask import has_request_context, request
from config import QR_CODE_DIR


def get_request_base_url():
    """
    Dynamically determine the external base URL (scheme + host) from current request.
    Handles reverse proxies and tunnels like Cloudflare Quick Tunnel (X-Forwarded-Proto, X-Forwarded-Host).
    """
    if has_request_context():
        # Scheme: check X-Forwarded-Proto header, CF-Visitor, or request.scheme
        proto = request.headers.get('X-Forwarded-Proto')
        if not proto and 'CF-Visitor' in request.headers:
            import json
            try:
                proto = json.loads(request.headers['CF-Visitor']).get('scheme')
            except Exception:
                proto = None
        if not proto:
            proto = request.scheme or 'http'

        # Host: check X-Forwarded-Host or Host header
        host = request.headers.get('X-Forwarded-Host') or request.host

        return f"{proto}://{host}".rstrip('/')
    return 'http://localhost:5000'


def generate_event_qr(event_id, qr_token, base_url=None):
    """
    Generate a QR code for an event's attendance URL.

    Args:
        event_id: The event's database ID
        qr_token: Unique token for this event's QR code
        base_url: The application's base URL (e.g. from request or tunnel)

    Returns:
        str: Path to the generated QR code image (relative to static/)
    """
    if not base_url:
        base_url = get_request_base_url()

    # Build the attendance URL that the QR code will encode
    clean_base = base_url.rstrip('/')
    attendance_url = f"{clean_base}/student/attend/{qr_token}"

    # Create QR code instance with settings for good readability
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(attendance_url)
    qr.make(fit=True)

    # Create the QR code image with custom colors
    img = qr.make_image(fill_color="#1a1a2e", back_color="#ffffff")

    # Save the image
    filename = f"event_{event_id}_{qr_token}.png"
    filepath = os.path.join(QR_CODE_DIR, filename)
    with open(filepath, "wb") as f:
        img.save(f)

    # Return relative path for use in templates
    return f"qrcodes/{filename}"


def get_qr_path(event_id, qr_token):
    """
    Get the path to an existing QR code image.
    Returns the path if it exists, None otherwise.
    """
    filename = f"event_{event_id}_{qr_token}.png"
    filepath = os.path.join(QR_CODE_DIR, filename)
    if os.path.exists(filepath):
        return f"qrcodes/{filename}"
    return None
