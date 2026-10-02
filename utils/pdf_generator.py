"""
utils/pdf_generator.py - PDF Report & Certificate Generator
AICTE Activity & Points Management System

Generates professional AICTE points reports and participation certificates
using the reportlab library.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config import REPORT_DIR, CERTIFICATE_DIR, MAX_AICTE_POINTS, SIGNATURE_DIR


# =============================================================================
# Color Palette
# =============================================================================
PRIMARY_COLOR = colors.HexColor('#6c5ce7')
SECONDARY_COLOR = colors.HexColor('#00b894')
DARK_COLOR = colors.HexColor('#2d3436')
LIGHT_COLOR = colors.HexColor('#dfe6e9')
ACCENT_COLOR = colors.HexColor('#0984e3')


def generate_report(student, total_points, category_points, event_history):
    """
    Generate a comprehensive AICTE Points Report PDF.

    Args:
        student: User object for the student
        total_points: Total AICTE points earned
        category_points: Dict of {category: points}
        event_history: List of event participation records

    Returns:
        str: Absolute path to the generated PDF file
    """
    filename = f"report_{student.roll_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORT_DIR, filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------------------------------------------------------
    # Custom Styles
    # -------------------------------------------------------------------------
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, textColor=PRIMARY_COLOR,
        spaceAfter=6, alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=12, textColor=DARK_COLOR,
        spaceAfter=20, alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading', parent=styles['Heading2'],
        fontSize=14, textColor=PRIMARY_COLOR,
        spaceBefore=15, spaceAfter=10
    )
    normal_style = ParagraphStyle(
        'CustomNormal', parent=styles['Normal'],
        fontSize=10, textColor=DARK_COLOR, spaceAfter=4
    )
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.gray,
        alignment=TA_CENTER
    )

    # -------------------------------------------------------------------------
    # Header
    # -------------------------------------------------------------------------
    elements.append(Paragraph("AICTE Activity Points Report", title_style))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        subtitle_style
    ))
    elements.append(HRFlowable(
        width="100%", thickness=2, color=PRIMARY_COLOR,
        spaceAfter=15
    ))

    # -------------------------------------------------------------------------
    # Student Details
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Student Information", heading_style))

    student_data = [
        ['Full Name:', student.full_name, 'Roll Number:', student.roll_number or 'N/A'],
        ['Department:', student.department or 'N/A', 'Email:', student.email],
        ['Username:', student.username, 'Member Since:', 
         student.created_at.strftime('%B %Y') if student.created_at else 'N/A'],
    ]

    student_table = Table(student_data, colWidths=[90, 170, 90, 170])
    student_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('FONT', (3, 0), (3, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (0, -1), PRIMARY_COLOR),
        ('TEXTCOLOR', (2, 0), (2, -1), PRIMARY_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # Points Summary
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Points Summary", heading_style))

    progress = min((total_points / MAX_AICTE_POINTS) * 100, 100)

    summary_data = [
        ['Total AICTE Points:', f'{total_points} / {MAX_AICTE_POINTS}'],
        ['Progress:', f'{progress:.1f}%'],
        ['Status:', 'COMPLETED ✓' if total_points >= MAX_AICTE_POINTS else 'IN PROGRESS'],
    ]

    summary_table = Table(summary_data, colWidths=[150, 370])
    summary_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 11),
        ('TEXTCOLOR', (0, 0), (0, -1), DARK_COLOR),
        ('TEXTCOLOR', (1, 2), (1, 2),
         SECONDARY_COLOR if total_points >= MAX_AICTE_POINTS else ACCENT_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BOX', (0, 0), (-1, -1), 1, LIGHT_COLOR),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Category-wise Breakdown
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Category-wise Points Breakdown", heading_style))

    categories = ['technical', 'cultural', 'social', 'sports']
    cat_header = ['Category', 'Points Earned']
    cat_data = [cat_header]
    for cat in categories:
        pts = category_points.get(cat, 0)
        cat_data.append([cat.capitalize(), str(pts)])
    cat_data.append(['Total', str(total_points)])

    cat_table = Table(cat_data, colWidths=[260, 260])
    cat_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('FONT', (0, 1), (-1, -2), 'Helvetica', 10),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(cat_table)
    elements.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # Event History Table
    # -------------------------------------------------------------------------
    elements.append(Paragraph("Event Participation History", heading_style))

    if event_history:
        evt_header = ['#', 'Event', 'Category', 'Date', 'Status', 'Points']
        evt_data = [evt_header]
        for i, evt in enumerate(event_history, 1):
            status = 'Attended' if evt['attended'] else 'Registered'
            date_str = evt['event_date'].strftime('%d %b %Y') if evt['event_date'] else 'N/A'
            evt_data.append([
                str(i),
                str(evt['title'])[:35],
                str(evt['category']).capitalize(),
                date_str,
                status,
                str(evt['points_awarded'])
            ])

        evt_table = Table(evt_data, colWidths=[30, 180, 80, 80, 70, 60])
        evt_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (4, 0), (5, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_COLOR),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(evt_table)
    else:
        elements.append(Paragraph("No events participated yet.", normal_style))

    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=LIGHT_COLOR))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(
        "This is an auto-generated report from the AICTE Activity & Points Management System. "
        "For queries, contact the administration office.",
        footer_style
    ))

    # Build PDF
    doc.build(elements)
    return filepath


# =============================================================================
# Institutional Certificate Theme Constants
# =============================================================================
CERT_NAVY_DEEP = colors.HexColor('#090E1A')
CERT_NAVY_PRIMARY = colors.HexColor('#0F172A')
CERT_NAVY_SLATE = colors.HexColor('#1E293B')
CERT_BRASS_PRIMARY = colors.HexColor('#B8860B')
CERT_BRASS_ACCENT = colors.HexColor('#C59B27')
CERT_GRAPHITE_TEXT = colors.HexColor('#334155')
CERT_GRAPHITE_MUTED = colors.HexColor('#64748B')
CERT_GRAPHITE_LIGHT = colors.HexColor('#94A3B8')
CERT_BORDER_SUBTLE = colors.HexColor('#E2E8F0')
CERT_BG_CHALK = colors.HexColor('#FCFDFE')
CERT_EMERALD_VERIFIED = colors.HexColor('#059669')


def _draw_certificate_frame(canvas, doc):
    """Draw institutional academic certificate border and architectural corner detailing."""
    canvas.saveState()
    width, height = landscape(A4)

    # 1. Warm chalk background fill
    canvas.setFillColor(CERT_BG_CHALK)
    canvas.rect(0, 0, width, height, fill=True, stroke=False)

    # 2. Outer Primary Navy Border (2.5 pt)
    canvas.setStrokeColor(CERT_NAVY_PRIMARY)
    canvas.setLineWidth(2.5)
    canvas.rect(20, 20, width - 40, height - 40, fill=False, stroke=True)

    # 3. Intermediate Brass Border (0.85 pt)
    canvas.setStrokeColor(CERT_BRASS_ACCENT)
    canvas.setLineWidth(0.85)
    canvas.rect(26, 26, width - 52, height - 52, fill=False, stroke=True)

    # 4. Inner Subtle Hairline (0.5 pt)
    canvas.setStrokeColor(CERT_BORDER_SUBTLE)
    canvas.setLineWidth(0.5)
    canvas.rect(30, 30, width - 60, height - 60, fill=False, stroke=True)

    # 5. Corner Architectural Motifs (4 corners)
    corner_size = 14
    for cx, cy, x_dir, y_dir in [
        (26, height - 26, 1, -1),          # Top-Left
        (width - 26, height - 26, -1, -1), # Top-Right
        (26, 26, 1, 1),                     # Bottom-Left
        (width - 26, 26, -1, 1)             # Bottom-Right
    ]:
        canvas.setStrokeColor(CERT_BRASS_ACCENT)
        canvas.setLineWidth(1.75)
        path = canvas.beginPath()
        path.moveTo(cx, cy + y_dir * corner_size)
        path.lineTo(cx, cy)
        path.lineTo(cx + x_dir * corner_size, cy)
        canvas.drawPath(path)

        # Small decorative square at intersection
        canvas.setFillColor(CERT_BRASS_ACCENT)
        canvas.rect(cx + (0 if x_dir > 0 else -3), cy + (0 if y_dir > 0 else -3), 3, 3, fill=True, stroke=False)

    # 6. Center Top & Bottom Brass Diamond Accents
    center_x = width / 2.0
    for y_pos in [height - 26, 26]:
        canvas.setFillColor(CERT_BRASS_ACCENT)
        canvas.setStrokeColor(CERT_BRASS_ACCENT)
        p = canvas.beginPath()
        p.moveTo(center_x, y_pos + 4)
        p.lineTo(center_x + 5, y_pos)
        p.lineTo(center_x, y_pos - 4)
        p.lineTo(center_x - 5, y_pos)
        p.close()
        canvas.drawPath(p, fill=1, stroke=1)

    canvas.restoreState()


def get_club_signature_path(club_id, sig_type):
    """
    Return the filesystem path to a club's signature image if it exists, else None.
    
    Args:
        club_id: Integer club/user ID
        sig_type: 'organizer' or 'administration'
        
    Returns:
        str or None: Path to signature file
    """
    if not club_id or sig_type not in ('organizer', 'administration'):
        return None
    try:
        club_id_int = int(club_id)
    except (ValueError, TypeError):
        return None
    sig_path = os.path.join(SIGNATURE_DIR, f"club_{club_id_int}", f"{sig_type}.png")
    if os.path.isfile(sig_path):
        return sig_path
    return None


def _get_signature_flowable(path, max_w=140, max_h=36):
    """
    Return a scaled ReportLab Image flowable maintaining aspect ratio, or an empty string.
    
    Args:
        path: Filesystem path to image
        max_w: Maximum allowable width in points
        max_h: Maximum allowable height in points
        
    Returns:
        reportlab.platypus.Image or str
    """
    if not path or not os.path.isfile(path):
        return ''
    try:
        import io
        from PIL import Image as PILImage
        with open(path, 'rb') as f:
            img_data = f.read()

        with PILImage.open(io.BytesIO(img_data)) as im:
            iw, ih = im.size
        if iw <= 0 or ih <= 0:
            return ''
        scale = min(max_w / float(iw), max_h / float(ih))
        return Image(io.BytesIO(img_data), width=iw * scale, height=ih * scale)
    except Exception:
        return ''


def generate_certificate(student, event):
    """
    Generate a professional institutional participation certificate PDF.

    Args:
        student: User object for the student
        event: dict with event details

    Returns:
        str: Absolute path to the generated PDF file
    """
    filename = f"cert_{student.roll_number}_{event['id']}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(CERTIFICATE_DIR, filename)

    # Use landscape A4 for certificate with calibrated margins
    doc = SimpleDocTemplate(
        filepath, pagesize=landscape(A4),
        rightMargin=50, leftMargin=50,
        topMargin=38, bottomMargin=32
    )

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------------------------------------------------------
    # Typographic Hierarchy Styles
    # -------------------------------------------------------------------------
    inst_kicker_style = ParagraphStyle(
        'CertInstKicker', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=14,
        textColor=CERT_NAVY_PRIMARY, alignment=TA_CENTER,
        spaceAfter=6
    )

    cert_main_title = ParagraphStyle(
        'CertMainTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=28, leading=32,
        textColor=CERT_NAVY_PRIMARY, alignment=TA_CENTER,
        spaceBefore=2, spaceAfter=3
    )

    cert_sub_title = ParagraphStyle(
        'CertSubTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=16,
        textColor=CERT_BRASS_PRIMARY, alignment=TA_CENTER,
        spaceAfter=14
    )

    presentation_style = ParagraphStyle(
        'CertPresentation', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=11, leading=15,
        textColor=CERT_GRAPHITE_TEXT, alignment=TA_CENTER,
        spaceAfter=6
    )

    # Dynamic name size for long-name safety
    raw_name = getattr(student, 'full_name', '') or 'Student Participant'
    name_size = 24 if len(raw_name) < 32 else (20 if len(raw_name) < 45 else 17)
    name_leading = name_size + 4
    name_style = ParagraphStyle(
        'CertStudentName', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=name_size, leading=name_leading,
        textColor=CERT_NAVY_PRIMARY, alignment=TA_CENTER,
        spaceBefore=2, spaceAfter=4
    )

    meta_sub_style = ParagraphStyle(
        'CertStudentMeta', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13,
        textColor=CERT_GRAPHITE_TEXT, alignment=TA_CENTER,
        spaceAfter=14
    )

    participated_style = ParagraphStyle(
        'CertParticipated', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10.5, leading=14,
        textColor=CERT_GRAPHITE_TEXT, alignment=TA_CENTER,
        spaceAfter=5
    )

    # Dynamic event title size for long title safety
    raw_title = event.get('title', 'Event Title')
    event_size = 16 if len(raw_title) < 45 else (13.5 if len(raw_title) < 70 else 12)
    event_leading = event_size + 4
    event_style = ParagraphStyle(
        'CertEventTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=event_size, leading=event_leading,
        textColor=CERT_NAVY_PRIMARY, alignment=TA_CENTER,
        spaceBefore=2, spaceAfter=5
    )

    date_venue_style = ParagraphStyle(
        'CertDateVenue', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13,
        textColor=CERT_GRAPHITE_TEXT, alignment=TA_CENTER,
        spaceAfter=16
    )

    # -------------------------------------------------------------------------
    # 1. Institutional Header (Exact system name, no invented subtitle)
    # -------------------------------------------------------------------------
    elements.append(Paragraph("AICTE ACTIVITY &amp; POINTS MANAGEMENT SYSTEM", inst_kicker_style))

    # Thin divider with centered brass diamond accent
    divider_data = [['', '◆', '']]
    divider_table = Table(divider_data, colWidths=[320, 20, 320], rowHeights=[10])
    divider_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
        ('FONTSIZE', (1, 0), (1, 0), 7),
        ('TEXTCOLOR', (1, 0), (1, 0), CERT_BRASS_ACCENT),
        ('LINEBELOW', (0, 0), (0, 0), 0.5, CERT_BORDER_SUBTLE),
        ('LINEBELOW', (2, 0), (2, 0), 0.5, CERT_BORDER_SUBTLE),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(divider_table)
    elements.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 2. Certificate Title
    # -------------------------------------------------------------------------
    elements.append(Paragraph("CERTIFICATE", cert_main_title))
    elements.append(Paragraph("OF PARTICIPATION", cert_sub_title))

    # -------------------------------------------------------------------------
    # 3. Recipient Presentation
    # -------------------------------------------------------------------------
    elements.append(Paragraph("This is to certify that", presentation_style))
    elements.append(Paragraph(raw_name, name_style))

    # Subtle brass underline below student name
    name_bar = Table([['']], colWidths=[220], rowHeights=[2])
    name_bar.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEABOVE', (0, 0), (-1, -1), 1.25, CERT_BRASS_ACCENT),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(name_bar)
    elements.append(Spacer(1, 6))

    dept = getattr(student, 'department', '') or ''
    roll = getattr(student, 'roll_number', '') or ''
    dept_str = f"Department of {dept}" if dept else "Student Participant"
    roll_str = f"Roll Number: {roll}" if roll else ""
    meta_line = f"{dept_str} &nbsp;&bull;&nbsp; {roll_str}" if (dept and roll) else (dept_str or roll_str)
    elements.append(Paragraph(meta_line, meta_sub_style))

    # -------------------------------------------------------------------------
    # 4. Participation Statement & Event Details
    # -------------------------------------------------------------------------
    elements.append(Paragraph("has successfully participated in", participated_style))
    elements.append(Paragraph(raw_title, event_style))

    event_date = event.get('event_date')
    if hasattr(event_date, 'strftime'):
        date_str = event_date.strftime('%B %d, %Y')
    else:
        date_str = str(event_date or 'N/A')
    venue_str = event.get('venue') or 'Campus Venue'
    elements.append(Paragraph(f"Conducted on {date_str} &nbsp;&bull;&nbsp; Venue: {venue_str}", date_venue_style))

    # -------------------------------------------------------------------------
    # 5. Activity Metadata Strip (Domain & Points Awarded)
    # -------------------------------------------------------------------------
    cat_name = str(event.get('category', 'Technical')).capitalize()
    pts_awarded = str(event.get('points', 0))

    meta_box_data = [
        [
            Paragraph("<b>ACTIVITY DOMAIN</b>", ParagraphStyle('M1', fontName='Helvetica', fontSize=7.5, leading=10, textColor=CERT_GRAPHITE_MUTED, alignment=TA_CENTER)),
            Paragraph("<b>AICTE POINTS AWARDED</b>", ParagraphStyle('M2', fontName='Helvetica', fontSize=7.5, leading=10, textColor=CERT_BRASS_PRIMARY, alignment=TA_CENTER)),
        ],
        [
            Paragraph(f"<b>{cat_name} Activity</b>", ParagraphStyle('V1', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=CERT_NAVY_PRIMARY, alignment=TA_CENTER)),
            Paragraph(f"<b>{pts_awarded} Points</b>", ParagraphStyle('V2', fontName='Helvetica-Bold', fontSize=11.5, leading=14, textColor=CERT_BRASS_PRIMARY, alignment=TA_CENTER)),
        ]
    ]
    meta_table = Table(meta_box_data, colWidths=[240, 240], rowHeights=[15, 20])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, CERT_BORDER_SUBTLE),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, CERT_BORDER_SUBTLE),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(meta_table)

    # -------------------------------------------------------------------------
    # 6. Signature Blocks (With Optional Club Signatures)
    # -------------------------------------------------------------------------
    # Look up club ID to check for uploaded organizer / admin signatures
    club_id = event.get('club_id')
    if not club_id and event.get('id'):
        try:
            from models.event import Event
            ev = Event.find_by_id(event['id'])
            if ev:
                club_id = ev.club_id
        except Exception:
            pass

    organizer_sig_path = get_club_signature_path(club_id, 'organizer') if club_id else None
    admin_sig_path = get_club_signature_path(club_id, 'administration') if club_id else None

    organizer_flowable = _get_signature_flowable(organizer_sig_path)
    admin_flowable = _get_signature_flowable(admin_sig_path)

    elements.append(Spacer(1, 14))

    sig_data = [
        [organizer_flowable, '', admin_flowable],
        ['', '', ''],
        ['Event Organizer', '', 'Administration'],
    ]
    sig_table = Table(sig_data, colWidths=[210, 240, 210], rowHeights=[38, 1, 16])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'BOTTOM'),
        ('LINEABOVE', (0, 1), (0, 1), 1, CERT_GRAPHITE_LIGHT),
        ('LINEABOVE', (2, 1), (2, 1), 1, CERT_GRAPHITE_LIGHT),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (-1, 2), 9.5),
        ('TEXTCOLOR', (0, 2), (-1, 2), CERT_NAVY_PRIMARY),
        ('TOPPADDING', (0, 2), (-1, 2), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(sig_table)
    elements.append(Spacer(1, 14))

    # -------------------------------------------------------------------------
    # 7. Certificate Metadata Footer
    # -------------------------------------------------------------------------
    cert_id = f"AICTE-{student.id}-{event['id']}-{datetime.now().strftime('%Y%m%d')}"
    gen_date = datetime.now().strftime('%B %d, %Y')

    footer_data = [
        [
            Paragraph(f"<b>Certificate ID:</b> {cert_id}", ParagraphStyle('F1', fontName='Helvetica', fontSize=7.5, leading=10, textColor=CERT_GRAPHITE_MUTED, alignment=TA_LEFT)),
            Paragraph("AICTE Activity &amp; Points Management System", ParagraphStyle('F2', fontName='Helvetica', fontSize=7.5, leading=10, textColor=CERT_GRAPHITE_MUTED, alignment=TA_CENTER)),
            Paragraph(f"<b>Generated:</b> {gen_date}", ParagraphStyle('F3', fontName='Helvetica', fontSize=7.5, leading=10, textColor=CERT_GRAPHITE_MUTED, alignment=TA_RIGHT)),
        ]
    ]
    footer_table = Table(footer_data, colWidths=[230, 240, 230], rowHeights=[12])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, CERT_BORDER_SUBTLE),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(footer_table)

    # Build PDF with background frame
    doc.build(elements, onFirstPage=_draw_certificate_frame)
    return filepath
