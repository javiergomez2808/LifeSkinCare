from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# Where you want to receive bookings
BOOKING_TO_EMAIL = "lifeskincare@outlook.com"

# SMTP settings (recommended: environment variables)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.office365.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")          # e.g. lifeskincare@outlook.com
SMTP_PASS = os.environ.get("SMTP_PASS")          # app password or mailbox password (see notes)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/book", methods=["POST"])
def book():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    service = request.form.get("service", "").strip()
    date = request.form.get("date", "").strip()
    time = request.form.get("time", "").strip()
    notes = request.form.get("notes", "").strip()

    # Basic validation
    if not all([name, phone, email, service, date, time]):
        flash("Please fill out all required fields.", "error")
        return redirect(url_for("home") + "#contact")

    if not SMTP_USER or not SMTP_PASS:
        # Avoid silently failing in production
        flash("Email sending is not configured on the server (missing SMTP credentials).", "error")
        return redirect(url_for("home") + "#contact")

    msg = EmailMessage()
    msg["Subject"] = f"New Booking Request — {service} — {name}"
    msg["From"] = SMTP_USER
    msg["To"] = BOOKING_TO_EMAIL
    msg["Reply-To"] = email  # so you can reply directly to the client

    body = f"""New booking request received:

Name: {name}
Phone: {phone}
Client Email: {email}
Service: {service}
Preferred Date: {date}
Preferred Time: {time}

Notes:
{notes if notes else "(none)"}
"""
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

        flash("Booking request sent! We will contact you soon.", "success")
    except Exception as e:
        flash(f"Could not send booking email. Error: {e}", "error")

    return redirect(url_for("home") + "#contact")


if __name__ == "__main__":
    app.run(debug=True)
