from fasthtml.common import *
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv

from db import init_db, get_guest, mark_opened, update_rsvp, get_all_guests, add_guest
from components import InvitePage, AdminPage, RSVPSuccess, NewGuestRow, PreviewInvitePage

load_dotenv()

import logging
class _ASGIMutedFilter(logging.Filter):
    def filter(self, record):
        return "ASGI callable returned without completing response" not in record.getMessage()

logging.getLogger("uvicorn.error").addFilter(_ASGIMutedFilter())

# ---------------------------------------------------------------------------
# Global CDN headers
# ---------------------------------------------------------------------------

_hdrs = (
    # Viewport — REQUIRED for mobile
    Meta(name="viewport", content="width=device-width, initial-scale=1, viewport-fit=cover"),
    # PWA
    Meta(name="theme-color", content="#E8B4BC"),
    Meta(name="apple-mobile-web-app-capable", content="yes"),
    Meta(name="apple-mobile-web-app-status-bar-style", content="default"),
    Meta(name="apple-mobile-web-app-title", content="Winvite"),
    Meta(name="mobile-web-app-capable", content="yes"),
    Link(rel="manifest", href="/static/manifest.json"),
    Link(rel="apple-touch-icon", href="/static/icon.svg"),
    # Google Fonts: Playfair Display + Inter
    Link(rel="preconnect", href="https://fonts.googleapis.com"),
    Link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=""),
    Link(
        rel="stylesheet",
        href=(
            "https://fonts.googleapis.com/css2?"
            "family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400"
            "&family=Inter:wght@300;400;500;600&display=swap"
        ),
    ),
    # Animate.css
    Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css",
    ),
    # Custom animation styles
    Link(rel="stylesheet", href="/static/invite.css"),
    # Tailwind Play CDN
    Script(src="https://cdn.tailwindcss.com"),
    # Lucide Icons
    Script(src="https://unpkg.com/lucide@latest"),
    # Tailwind config
    Script("""
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        serif: ['Playfair Display', 'Georgia', 'serif'],
                        sans:  ['Inter', 'system-ui', 'sans-serif'],
                    },
                }
            }
        }
    """),
    # Global styles
    Style("""
        body { font-family: 'Inter', system-ui, sans-serif; background: #FDF8F5; color: #5C4A4A; }
        html { scroll-behavior: smooth; }
        section { width: 100%; }
        .tabular-nums { font-variant-numeric: tabular-nums; }
        .animate__delay-4s { animation-delay: 4s; }
        .htmx-request .htmx-indicator { display: inline-block; }
        .htmx-indicator { display: none; }
    """),
    # Service worker registration
    Script("""
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js')
                    .catch(function(e) { console.warn('SW reg failed:', e); });
            });
        }
    """),
)

original_app, rt = fast_app(hdrs=_hdrs, live=False)

# Suppress harmless client disconnect TimeoutErrors (Errno 60)
async def app(scope, receive, send):
    try:
        await original_app(scope, receive, send)
    except TimeoutError:
        pass
    except RuntimeError as e:
        if "shorter than Content-Length" in str(e) or "ASGI callable returned" in str(e):
            pass
        else:
            raise
import os as _os
_static_dir = _os.path.join(_os.path.dirname(__file__), "static")
_os.makedirs(_static_dir, exist_ok=True)
original_app.mount("/static", StaticFiles(directory=_static_dir), name="static")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@rt("/sw.js")
def get():
    """Serve service worker from root scope so it can control all pages."""
    return FileResponse("static/sw.js", media_type="application/javascript")

@rt("/favicon.ico")
def get():
    return Response(content=b"", media_type="image/x-icon")
    from starlette.responses import FileResponse
    return FileResponse(
        _os.path.join(_static_dir, "sw.js"),
        media_type="application/javascript",
    )


@rt("/")
def get():
    return PreviewInvitePage()


@rt("/invite/{slug}")
def get(slug: str):
    guest = get_guest(slug)
    if not guest:
        return (
            Title("Not Found"),
            Main(
                Div(
                    I(data_lucide="frown", cls="w-12 h-12 text-stone-300 mx-auto mb-4"),
                    H1("Invitation Not Found",
                       cls="font-serif text-2xl text-stone-700 mb-2"),
                    P("This link may be invalid or expired.",
                      cls="text-sm text-stone-400"),
                    cls="text-center py-24 px-4",
                ),
                cls="min-h-screen bg-[#FAFAF9] flex items-center justify-center",
            ),
            Script("lucide.createIcons();"),
        )
    mark_opened(slug)
    return InvitePage(guest)


@rt("/rsvp")
def post(slug: str, attending: str, plus_one: str = "off"):
    is_plus_one = plus_one == "on"
    # Sanitize: only allow valid statuses
    if attending not in ("attending", "declined"):
        attending = "declined"
    update_rsvp(slug, attending, is_plus_one)
    return RSVPSuccess(attending)


@rt("/guest-form")
def post(
    slug: str = "",
    form_type: str = "",
    # Reservation fields
    guest_count: str = "",
    dietary: str = "",
    notes: str = "",
    # Song request fields
    song_title: str = "",
    song_artist: str = "",
    song_message: str = "",
):
    """Handle reservation details and song request form submissions."""
    import sqlite3, os as _os, json as _json
    db_path = _os.path.join(_os.path.dirname(__file__), "guests.db")

    def _ok(msg: str, color: str = "#7A6AAA") -> FT:
        return Div(
            P(f"✓  {msg}",
              style=f"color:{color};font-family:sans-serif;font-size:0.82rem;"
                    "padding:0.65rem 1rem;background:rgba(255,255,255,0.8);"
                    "border-radius:0.6rem;border:1px solid rgba(0,0,0,0.06);"
                    "text-align:center;margin-top:0.5rem;"),
            id="reservation-msg" if form_type == "reservation" else "song-msg",
        )

    try:
        if form_type == "reservation":
            # Store as a JSON note appended to the guest record
            with sqlite3.connect(db_path) as con:
                con.execute(
                    "UPDATE guests SET notes=? WHERE slug=?",
                    (_json.dumps({
                        "guest_count": guest_count,
                        "dietary": dietary,
                        "special_notes": notes,
                    }), slug)
                )
            return _ok(f"Reservation confirmed for {guest_count or '?'} guest(s)! 🌸", "#C4687A")

        elif form_type == "song_request":
            # Append song request to a simple text log, or store in DB notes
            with sqlite3.connect(db_path) as con:
                # Try to upsert into a song_requests table
                con.execute("""CREATE TABLE IF NOT EXISTS song_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug TEXT, song TEXT, artist TEXT, dedication TEXT
                )""")
                con.execute(
                    "INSERT INTO song_requests (slug,song,artist,dedication) VALUES (?,?,?,?)",
                    (slug, song_title, song_artist, song_message)
                )
            return _ok(f'🎵 "{song_title}" by {song_artist} added to the playlist!', "#7A6AAA")

    except Exception as e:
        return Div(
            P(f"⚠ Something went wrong — please try again.",
              style="color:#C4687A;font-family:sans-serif;font-size:0.8rem;"
                    "padding:0.65rem 1rem;background:#FFF5F5;"
                    "border-radius:0.6rem;text-align:center;margin-top:0.5rem;"),
            id="reservation-msg" if form_type == "reservation" else "song-msg",
        )


@rt("/admin")
def get():
    guests = get_all_guests()
    return AdminPage(guests)


@rt("/admin/guests")
def post(name: str, phone: str, category: str = "General"):
    guest = add_guest(name, phone, category)
    return NewGuestRow(guest)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

init_db()
import os, uvicorn
_raw_port = int(os.environ.get("PORT", 5001))
# Privileged ports (<1024) fail for non-root users; fall back to 5001
port = _raw_port if _raw_port >= 1024 else 5001
uvicorn.run(app, host="0.0.0.0", port=port)
