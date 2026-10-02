"""
routes/club.py - Club Routes
AICTE Activity & Points Management System

Handles club dashboard, event CRUD, attendee management,
and QR code generation.
"""

import os
import io
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, send_file, abort
)
import time
from functools import wraps
from typing import cast, Any
from models.user import User
from models.event import Event
from models.registration import Registration
from utils.validators import validate_event_data, sanitize_input
from utils.qr_generator import generate_event_qr, get_qr_path, get_request_base_url
from utils.pdf_generator import get_club_signature_path
from config import SIGNATURE_DIR, MAX_SIGNATURE_SIZE

club_bp = Blueprint('club', __name__, url_prefix='/club')


# =============================================================================
# Authentication Decorator
# =============================================================================
def club_required(f):
    """Decorator to ensure user is logged in as a club."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'club':
            flash('Access denied. Club accounts only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# Dashboard
# =============================================================================
@club_bp.route('/dashboard')
@club_required
def dashboard():
    """Club dashboard showing all events and statistics."""
    events = cast(list[dict[str, Any]], Event.get_club_events(session['user_id']))
    user = User.find_by_id(session['user_id'])

    # Calculate stats
    total_events = len(events)
    approved = sum(1 for e in events if e['status'] == 'approved')
    pending = sum(1 for e in events if e['status'] == 'pending')
    total_registrations = sum(e.get('registered_count', 0) for e in events)

    return render_template('club/dashboard.html',
        events=events,
        user=user,
        stats={
            'total_events': total_events,
            'approved': approved,
            'pending': pending,
            'total_registrations': total_registrations
        }
    )


# =============================================================================
# Create Event
# =============================================================================
@club_bp.route('/event/create', methods=['GET', 'POST'])
@club_required
def create_event():
    """Create a new event."""
    if request.method == 'POST':
        data = {
            'title': sanitize_input(request.form.get('title')),
            'description': sanitize_input(request.form.get('description')),
            'category': request.form.get('category'),
            'event_date': request.form.get('event_date'),
            'event_time': request.form.get('event_time'),
            'venue': sanitize_input(request.form.get('venue')),
            'points': request.form.get('points'),
            'max_participants': request.form.get('max_participants'),
        }

        # Validate
        is_valid, errors = validate_event_data(data)
        if not is_valid:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('club/create_event.html', data=data)

        try:
            event = Event(
                title=data['title'],
                description=data['description'],
                category=data['category'],
                event_date=data['event_date'],
                event_time=data['event_time'],
                venue=data['venue'],
                points=int(data['points'] or 0),
                max_participants=int(data['max_participants'] or 0),
                club_id=session['user_id'],
                status='pending'
            )
            event_id = event.save()

            # Generate QR code using current request origin (supports localhost & Cloudflare tunnels)
            base_url = get_request_base_url()
            qr_path = generate_event_qr(event_id, event.qr_token, base_url=base_url)

            flash('Event created! It will be visible after admin approval.', 'success')
            return redirect(url_for('club.dashboard'))
        except Exception as e:
            flash(f'Error creating event: {str(e)}', 'error')
            return render_template('club/create_event.html', data=data)

    return render_template('club/create_event.html', data={})


# =============================================================================
# Edit Event
# =============================================================================
@club_bp.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@club_required
def edit_event(event_id):
    """Edit an existing event."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    if request.method == 'POST':
        data = {
            'title': sanitize_input(request.form.get('title')),
            'description': sanitize_input(request.form.get('description')),
            'category': request.form.get('category'),
            'event_date': request.form.get('event_date'),
            'event_time': request.form.get('event_time'),
            'venue': sanitize_input(request.form.get('venue')),
            'points': request.form.get('points'),
            'max_participants': request.form.get('max_participants'),
        }

        # Validate
        is_valid, errors = validate_event_data(data)
        if not is_valid:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('club/edit_event.html', event=event, data=data)

        try:
            event.title = data['title']
            event.description = data['description']
            event.category = data['category']
            event.event_date = data['event_date']
            event.event_time = data['event_time']
            event.venue = data['venue']
            event.points = int(data['points'] or 0)
            event.max_participants = int(data['max_participants'] or 0)
            # Reset to pending if it was rejected
            if event.status == 'rejected':
                event.status = 'pending'
            event.update()

            flash('Event updated successfully!', 'success')
            return redirect(url_for('club.dashboard'))
        except Exception as e:
            flash(f'Error updating event: {str(e)}', 'error')
            return render_template('club/edit_event.html', event=event, data=data)

    return render_template('club/edit_event.html', event=event, data=event.to_dict())


# =============================================================================
# Delete Event
# =============================================================================
@club_bp.route('/event/delete/<int:event_id>', methods=['POST'])
@club_required
def delete_event(event_id):
    """Delete an event."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    try:
        event.delete()
        flash('Event deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting event: {str(e)}', 'error')

    return redirect(url_for('club.dashboard'))


# =============================================================================
# View Event Attendees
# =============================================================================
@club_bp.route('/event/<int:event_id>/attendees')
@club_required
def event_attendees(event_id):
    """View registered students and manage attendance."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    students = event.get_registered_students()
    stats = Registration.get_event_stats(event_id)

    # Dynamically generate/refresh QR code for current request origin (supports localhost & Cloudflare tunnels)
    base_url = get_request_base_url()
    qr_path = generate_event_qr(event_id, event.qr_token, base_url=base_url)
    qr_timestamp = int(time.time())

    return render_template('club/attendance.html',
        event=event,
        students=students,
        stats=stats,
        qr_path=qr_path,
        qr_timestamp=qr_timestamp
    )


# =============================================================================
# Mark Attendance
# =============================================================================
@club_bp.route('/event/<int:event_id>/mark-attendance', methods=['POST'])
@club_required
def mark_attendance(event_id):
    """Mark attendance for selected students."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Event not found or access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    # Get list of student IDs from form checkboxes
    student_ids = request.form.getlist('student_ids')

    if not student_ids:
        flash('No students selected.', 'warning')
        return redirect(url_for('club.event_attendees', event_id=event_id))

    try:
        student_ids = [int(sid) for sid in student_ids]
        Registration.mark_attendance_bulk(event_id, student_ids, event.points)
        flash(f'Attendance marked for {len(student_ids)} student(s). Points awarded!', 'success')
    except Exception as e:
        flash(f'Error marking attendance: {str(e)}', 'error')

    return redirect(url_for('club.event_attendees', event_id=event_id))


# =============================================================================
# Toggle Individual Attendance
# =============================================================================
@club_bp.route('/event/<int:event_id>/toggle-attendance/<int:student_id>', methods=['POST'])
@club_required
def toggle_attendance(event_id, student_id):
    """Toggle attendance for a single student."""
    event = Event.find_by_id(event_id)

    if not event or event.club_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('club.dashboard'))

    reg = Registration.find(student_id, event_id)
    if not reg:
        flash('Registration not found.', 'error')
        return redirect(url_for('club.event_attendees', event_id=event_id))

    try:
        if reg.attended:
            Registration.unmark_attendance(student_id, event_id)
            flash('Attendance unmarked.', 'info')
        else:
            Registration.mark_attendance(student_id, event_id, event.points)
            flash('Attendance marked. Points awarded!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('club.event_attendees', event_id=event_id))


# =============================================================================
# Certificate Settings & Signature Management
# =============================================================================
@club_bp.route('/certificate-settings')
@club_required
def certificate_settings():
    """Manage authorized certificate signatures for club activities."""
    club_id = session['user_id']
    user = User.find_by_id(club_id)
    has_organizer = get_club_signature_path(club_id, 'organizer') is not None
    has_admin = get_club_signature_path(club_id, 'administration') is not None

    return render_template(
        'club/certificate_settings.html',
        user=user,
        has_organizer=has_organizer,
        has_admin=has_admin
    )


@club_bp.route('/certificate-settings/preview/<sig_type>')
@club_required
def preview_signature(sig_type):
    """Securely stream club signature preview image."""
    club_id = session['user_id']
    if sig_type not in ('organizer', 'administration'):
        abort(404)

    sig_path = get_club_signature_path(club_id, sig_type)
    if not sig_path or not os.path.isfile(sig_path):
        abort(404)

    with open(sig_path, 'rb') as f:
        img_bytes = f.read()

    return send_file(io.BytesIO(img_bytes), mimetype='image/png', max_age=0)


@club_bp.route('/certificate-settings/upload', methods=['POST'])
@club_required
def upload_signature():
    """Upload or replace an authorized certificate signature."""
    club_id = session['user_id']
    sig_type = request.form.get('sig_type', '').strip().lower()

    if sig_type not in ('organizer', 'administration'):
        flash('Invalid signature role specified.', 'error')
        return redirect(url_for('club.certificate_settings'))

    if 'signature_file' not in request.files or not request.files['signature_file'].filename:
        flash('Please select an image file to upload.', 'error')
        return redirect(url_for('club.certificate_settings'))

    file = request.files['signature_file']
    filename = file.filename or ''
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext not in ('png', 'jpg', 'jpeg'):
        flash('Unsupported file extension. Only PNG and JPG/JPEG files are accepted.', 'error')
        return redirect(url_for('club.certificate_settings'))

    file_bytes = file.read()
    if len(file_bytes) == 0:
        flash('Uploaded file is empty.', 'error')
        return redirect(url_for('club.certificate_settings'))

    if len(file_bytes) > MAX_SIGNATURE_SIZE:
        flash('File size exceeds the 2MB limit. Please upload a smaller image.', 'error')
        return redirect(url_for('club.certificate_settings'))

    try:
        from PIL import Image as PILImage
        file_stream = io.BytesIO(file_bytes)
        with PILImage.open(file_stream) as im:
            im.verify()

        file_stream.seek(0)
        with PILImage.open(file_stream) as im:
            format_name = (im.format or '').upper()
            if format_name not in ('PNG', 'JPEG'):
                flash('Invalid image content. Only genuine PNG and JPEG files are allowed.', 'error')
                return redirect(url_for('club.certificate_settings'))

            club_dir = os.path.join(SIGNATURE_DIR, f"club_{int(club_id)}")
            os.makedirs(club_dir, exist_ok=True)
            dest_path = os.path.join(club_dir, f"{sig_type}.png")

            # Convert palette/CMYK modes if necessary to ensure clean PNG output
            if im.mode in ('CMYK', 'P'):
                im = im.convert('RGBA' if 'transparency' in im.info else 'RGB')
            im.save(dest_path, 'PNG', optimize=True)

        role_label = 'Event Organizer' if sig_type == 'organizer' else 'Administration'
        flash(f"{role_label} signature saved successfully.", 'success')
    except Exception:
        flash('Failed to process image file. Please ensure it is a valid PNG or JPEG image.', 'error')

    return redirect(url_for('club.certificate_settings'))


@club_bp.route('/certificate-settings/remove', methods=['POST'])
@club_required
def remove_signature():
    """Remove a previously configured signature."""
    club_id = session['user_id']
    sig_type = request.form.get('sig_type', '').strip().lower()

    if sig_type not in ('organizer', 'administration'):
        flash('Invalid signature role specified.', 'error')
        return redirect(url_for('club.certificate_settings'))

    sig_path = os.path.join(SIGNATURE_DIR, f"club_{int(club_id)}", f"{sig_type}.png")
    if os.path.isfile(sig_path):
        try:
            os.remove(sig_path)
            role_label = 'Event Organizer' if sig_type == 'organizer' else 'Administration'
            flash(f"{role_label} signature removed. Blank line will be used on certificates.", 'info')
        except Exception:
            flash('Error removing signature file.', 'error')
    else:
        flash('Signature not found or already removed.', 'warning')

    return redirect(url_for('club.certificate_settings'))
