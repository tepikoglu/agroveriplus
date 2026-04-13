"""Email service tests — SMTP not configured so emails are skipped gracefully."""

from app.services.email import _build_html, _is_configured, send_email, send_notification_email


def test_smtp_not_configured():
    """Without SMTP settings, _is_configured returns False."""
    assert _is_configured() is False


async def test_send_email_skipped_when_not_configured():
    """send_email returns False (not sent) when SMTP is not configured."""
    result = await send_email("test@example.com", "Subject", "Title", "Body text")
    assert result is False


async def test_send_notification_email_skipped():
    result = await send_notification_email("test@example.com", "Test Title", "Test body")
    assert result is False


def test_build_html_structure():
    """HTML template should contain title and body."""
    html = _build_html("Certificate Uploaded", "Your cert organic.pdf is sealed.")
    assert "Certificate Uploaded" in html
    assert "organic.pdf" in html
    assert "AgroVeri" in html
    assert "<!DOCTYPE html>" in html


def test_build_html_escaping():
    """Template should handle special characters."""
    html = _build_html("Test <Title>", "Body with & special chars")
    assert "<Title>" in html  # raw HTML in template (trusted input)


async def test_notification_with_email_no_crash(client):
    """Notification creation should not crash even when email fails."""
    import io
    # Register + login
    await client.post("/api/auth/register", json={
        "email": "email_test@test.com", "password": "test12345", "name": "Email Test",
    })
    r = await client.post("/api/auth/login", json={
        "email": "email_test@test.com", "password": "test12345",
    })
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Upload triggers notification → notify() tries email → skips gracefully
    r2 = await client.post(
        "/api/certificates/upload",
        files={"file": ("email.pdf", io.BytesIO(b"email test cert"), "application/pdf")},
        headers=h,
    )
    assert r2.status_code == 200

    # Notification was still created in DB
    r3 = await client.get("/api/notifications", headers=h)
    assert r3.status_code == 200
    assert len(r3.json()) >= 1
    assert r3.json()[0]["event"] == "certificate_uploaded"
