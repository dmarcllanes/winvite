"""Reusable FastHTML UI components for the Wedding E-Invite Engine."""

import os
import urllib.parse
from datetime import datetime, timezone

from fasthtml.common import *

from db import format_phone

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5001")


# ---------------------------------------------------------------------------
# Book / Church-Door Opening Overlay
# ---------------------------------------------------------------------------

def _door_svg(side: str) -> FT:
    """Floral-cross SVG ornament placed on each door panel."""
    # Flipped horizontally for right door
    flip = 'transform="scale(-1,1) translate(-120,0)"' if side == 'right' else ''
    return NotStr(f"""
    <svg viewBox="0 0 120 200" xmlns="http://www.w3.org/2000/svg"
         class="door-cross w-full max-w-[90px] md:max-w-[120px] opacity-75"
         aria-hidden="true">
      <g {flip}>
        <!-- Vertical bar -->
        <rect x="55" y="20" width="10" height="160" rx="3"
              fill="none" stroke="#D4AF37" stroke-width="1.2"/>
        <!-- Horizontal bar -->
        <rect x="20" y="70" width="80" height="10" rx="3"
              fill="none" stroke="#D4AF37" stroke-width="1.2"/>
        <!-- Centre diamond -->
        <polygon points="60,55 68,70 60,85 52,70"
                 fill="none" stroke="#D4AF37" stroke-width="1"/>
        <!-- Petal motifs at cross tips -->
        <circle cx="60" cy="22" r="4" fill="none" stroke="#E8B4BC" stroke-width="1"/>
        <circle cx="60" cy="178" r="4" fill="none" stroke="#E8B4BC" stroke-width="1"/>
        <circle cx="22" cy="75" r="4" fill="none" stroke="#E8B4BC" stroke-width="1"/>
        <circle cx="98" cy="75" r="4" fill="none" stroke="#E8B4BC" stroke-width="1"/>
        <!-- Small filigree lines -->
        <line x1="60" y1="30" x2="60" y2="50" stroke="#D4AF37" stroke-width="0.8" stroke-dasharray="2,2"/>
        <line x1="60" y1="90" x2="60" y2="165" stroke="#D4AF37" stroke-width="0.8" stroke-dasharray="2,2"/>
        <line x1="30" y1="75" x2="50" y2="75" stroke="#D4AF37" stroke-width="0.8" stroke-dasharray="2,2"/>
        <line x1="70" y1="75" x2="90" y2="75" stroke="#D4AF37" stroke-width="0.8" stroke-dasharray="2,2"/>
      </g>
    </svg>
    """)


def _petal_span(i: int) -> FT:
    """Single rose petal with randomised trajectory via CSS vars."""
    colors = [
        '#E8B4BC', '#C4687A', '#F5C6CE', '#D4AF37', '#FFF0F3',
        '#FDEEF2', '#E8B4BC', '#C4687A', '#F5C6CE', '#FAD4DA',
        '#E8B4BC', '#D4AF37'
    ]
    txs = [-180, -120, -80, -30, 30, 80, 120, 180, -150, 150, -60, 60]
    tys = [-280, -220, -260, -300, -310, -250, -270, -230, -180, -200, -320, -240]
    rots = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
    durs = [1.4, 1.6, 1.8, 1.5, 2.0, 1.7, 1.9, 1.6, 1.8, 1.5, 2.1, 1.7]
    delays = [0, 0.05, 0.1, 0.15, 0.08, 0.12, 0.03, 0.18, 0.07, 0.14, 0.11, 0.06]
    color = colors[i % len(colors)]
    tx    = txs[i % len(txs)]
    ty    = tys[i % len(tys)]
    rot   = rots[i % len(rots)]
    dur   = durs[i % len(durs)]
    delay = delays[i % len(delays)]
    return Span(
        cls="petal",
        style=(
            f"background:{color};"
            f"--tx:{tx}px;--ty:{ty}px;"
            f"--rot:{rot}deg;--dur:{dur}s;--delay:{delay}s;"
        ),
    )


def _dust_particle(i: int) -> FT:
    sizes = [6, 8, 5, 10, 7, 4, 9, 6, 8, 5, 7, 11]
    ls    = [10, 25, 40, 55, 70, 80, 90, 15, 60, 35, 45, 75]
    ts    = [15, 30, 50, 20, 65, 45, 10, 80, 35, 55, 25, 70]
    mxs   = [15, -20, 12, -18, 20, -14, 16, -22, 18, -16, 22, -10]
    mys   = [-25, -18, -30, -22, -28, -20, -35, -15, -32, -24, -19, -26]
    durs  = [5, 7, 6, 8, 5.5, 7.5, 6.5, 9, 5, 7, 6.5, 8]
    dels  = [0, 1.2, 2.4, 0.6, 1.8, 3.0, 0.3, 2.1, 1.5, 0.9, 2.7, 1.1]
    s = sizes[i % len(sizes)]
    return Div(
        cls="dust",
        style=(
            f"width:{s}px;height:{s}px;"
            f"left:{ls[i % len(ls)]}%;top:{ts[i % len(ts)]}%;"
            f"--fmx:{mxs[i % len(mxs)]}px;--fmy:{mys[i % len(mys)]}px;"
            f"--fdur:{durs[i % len(durs)]}s;--fdelay:{dels[i % len(dels)]}s;"
        ),
    )


def BookOpeningOverlay(name: str | None = None) -> FT:
    """Full-screen church-door / book-opening overlay."""
    # Greeting shown inside the overlay
    names_display = "Nikolai & Valentina"
    greeting = f"Dear {name.split()[0]}," if name else "You are invited"

    dust = [_dust_particle(i) for i in range(12)]
    petals = [_petal_span(i) for i in range(12)]

    door_shared_inner_content = lambda side: (
        Div(cls="corner-ornament tl"),
        Div(cls="corner-ornament tr"),
        Div(cls="corner-ornament bl"),
        Div(cls="corner-ornament br"),
        Div(
            Div(cls="door-rule"),
            _door_svg(side),
            Div(cls="door-rule"),
            cls="door-inner",
        ),
    )

    return Div(
        # Floating gold dust (behind panels)
        *dust,
        # ── Left door panel ──
        Div(
            *door_shared_inner_content('left'),
            cls="door-panel door-left",
        ),
        # ── Right door panel ──
        Div(
            *door_shared_inner_content('right'),
            cls="door-panel door-right",
        ),
        # ── Centre spine ──
        Div(cls="book-spine"),
        # ── Central names (between panels, above) ──
        Div(
            P(
                greeting,
                cls="font-sans text-[9px] uppercase tracking-[0.45em] text-[#A89090] mb-2 text-center",
            ),
            Div(
                Div(
                    Span("◆", style="font-size:0.6rem; color: #D4AF37;"),
                    cls="floral-ring-inner",
                ),
                cls="floral-ring mb-4",
            ),
            P(names_display, cls="overlay-names mb-3"),
            P("August 24, 2026", cls="overlay-date"),
            style="""
                position:absolute;top:50%;left:50%;
                transform:translate(-50%,-50%);
                z-index:5;pointer-events:none;
                display:flex;flex-direction:column;align-items:center;
                width:90%;max-width:380px;text-align:center;
            """,
        ),
        # ── Petal burst ──
        Div(*petals, cls="petal-burst"),
        # ── Tap-to-open prompt ──
        Div(
            Div(
                Div(cls="tap-ring"),
                Div(cls="tap-dot"),
                style="position:relative;width:54px;height:54px;",
            ),
            P("Click to Open", cls="tap-label"),
            P("↓", style="font-family:serif;font-size:1.4rem;color:#C4687A;opacity:0.5;margin-top:0.25rem;animation:breathe 2.4s ease-in-out infinite;"),
            id="tap-prompt",
        ),
        # ── JS trigger ──
        Script("""
(function() {
    var overlay = document.getElementById('book-overlay');
    if (!overlay) return;
    var opened = false;

    function openBook() {
        if (opened) return;
        opened = true;
        overlay.classList.add('open');
        // Reveal invite sections with stagger once overlay is done
        setTimeout(function() {
            var sections = document.querySelectorAll('.invite-section');
            sections.forEach(function(el, idx) {
                setTimeout(function() {
                    el.classList.add('visible');
                }, idx * 160);
            });
        }, 950);
    }

    overlay.addEventListener('click', openBook, { once: true });
    overlay.addEventListener('touchstart', openBook, { once: true, passive: true });

    // NO auto-open — guest must click/tap.
})();
        """),
        id="book-overlay",
    )

CATEGORY_MESSAGES = {
    "Friends": (
        "You're one of the people who makes life more fun and memorable — "
        "we wouldn't have it any other way than celebrating this day with you! 🎉"
    ),
    "Family": (
        "With all our love and gratitude, we would be deeply honored "
        "to have you celebrate this joyful milestone with us."
    ),
    "VIP": (
        "It is with the greatest pleasure and heartfelt sincerity that "
        "we request the honor of your presence on our wedding day."
    ),
    "Work": (
        "We would be truly delighted to have you join us as we celebrate "
        "the beginning of our new chapter together."
    ),
    "General": (
        "We joyfully invite you to share in the celebration of our "
        "wedding day and create beautiful memories together."
    ),
}

RSVP_STATUS_STYLES = {
    "pending":   ("bg-gray-100 text-gray-600",  "Clock"),
    "attending": ("bg-green-100 text-green-700", "CheckCircle"),
    "declined":  ("bg-red-100 text-red-600",     "XCircle"),
}

CATEGORY_STYLES = {
    "Friends": "bg-purple-100 text-purple-700",
    "Family":  "bg-amber-100 text-amber-700",
    "VIP":     "bg-yellow-100 text-yellow-800",
    "Work":    "bg-blue-100 text-blue-700",
    "General": "bg-gray-100 text-gray-600",
}


# ---------------------------------------------------------------------------
# Pastel palette tokens (reference)
# --blush:     #E8B4BC   --blush-deep: #C4687A
# --sage:      #B8D0B4   --ivory:      #FDF8F5
# --petal:     #FFF0F3   --mist:       #F5EEF8
# --text-dark: #5C4A4A   --text-mid:   #8C7070   --text-soft: #A89090
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Shared decorative helpers
# ---------------------------------------------------------------------------

def _ornament() -> FT:
    """Horizontal blush-rose ornamental divider."""
    return Div(
        Span(cls="flex-1 h-px bg-[#E8B4BC]/50"),
        Span("✦", cls="text-[#C4687A]/60 mx-5 text-xs tracking-widest"),
        Span(cls="flex-1 h-px bg-[#E8B4BC]/50"),
        cls="flex items-center max-w-[200px] mx-auto",
    )


def _countdown_unit(el_id: str, label: str) -> FT:
    return Div(
        Span("00", id=el_id,
             cls="font-serif text-4xl md:text-5xl text-[#C4687A] tabular-nums block"),
        Span(label,
             cls="font-sans text-[9px] uppercase tracking-[0.25em] text-[#A89090] mt-1 block"),
        cls="text-center min-w-[56px]",
    )


_COUNTDOWN_JS = Script("""
(function() {
    var target = new Date('2026-08-24T16:00:00+08:00');
    function tick() {
        var diff = target - new Date();
        if (diff < 0) diff = 0;
        var d = Math.floor(diff / 86400000);
        var h = Math.floor((diff % 86400000) / 3600000);
        var m = Math.floor((diff % 3600000) / 60000);
        var s = Math.floor((diff % 60000) / 1000);
        var pad = function(n){ return String(n).padStart(2,'0'); };
        [['cd-days',d],['cd-hours',h],['cd-mins',m],['cd-secs',s]].forEach(function(p){
            var el = document.getElementById(p[0]);
            if (el) el.textContent = pad(p[1]);
        });
    }
    tick();
    setInterval(tick, 1000);
})();
""")


# ---------------------------------------------------------------------------
# Music Player — floating, bottom-right
# Browsers block autoplay; we unlock on the very first user interaction.
# ---------------------------------------------------------------------------

def MusicPlayer() -> FT:
    return Div(
        Audio(
            Source(src="/static/invite.mp3", type="audio/mpeg"),
            id="bg-music",
            loop=True,
            preload="auto",
        ),
        # Outer: fixed positioning only
        Div(
            # Inner: relative for pulse absolute positioning
            Div(
                # Pulsing ring — visible until music starts
                Div(
                    cls=(
                        "absolute inset-0 rounded-full bg-[#E8B4BC] "
                        "animate-ping opacity-50 pointer-events-none"
                    ),
                    id="music-pulse",
                ),
                Button(
                    Div(I(data_lucide="music",   cls="w-5 h-5"), id="music-icon-on"),
                    Div(I(data_lucide="volume-x", cls="w-5 h-5 opacity-30"),
                        id="music-icon-off", cls="hidden"),
                    id="music-btn",
                    title="Tap to play music",
                    cls=(
                        "flex items-center justify-center w-12 h-12 rounded-full "
                        "bg-white border border-[#E8B4BC] shadow-md text-[#C4687A] "
                        "hover:shadow-lg hover:scale-105 transition-all duration-200 "
                        "disabled:opacity-30 disabled:cursor-not-allowed disabled:scale-100"
                    ),
                ),
                cls="relative",
            ),
            cls="fixed bottom-20 right-6 z-[8500]",
        ),
        Script("""
(function(){
    var audio   = document.getElementById('bg-music');
    var btn     = document.getElementById('music-btn');
    var pulse   = document.getElementById('music-pulse');
    var iconOn  = document.getElementById('music-icon-on');
    var iconOff = document.getElementById('music-icon-off');
    var playing = false;

    if (!audio || !btn) return;
    audio.volume = 0.5;

    // If the file can't be loaded, disable the button gracefully
    audio.addEventListener('error', function() {
        btn.disabled = true;
        btn.title = 'No music file — add invite.mp3 to the /static/ folder';
        if (pulse) pulse.classList.add('hidden');
    }, { once: true });

    function setPlaying(val) {
        playing = val;
        if (iconOn)  iconOn.classList.toggle('hidden', !val);
        if (iconOff) iconOff.classList.toggle('hidden', val);
        if (pulse)   pulse.classList.toggle('hidden', val);
        lucide.createIcons();
    }

    function tryPlay() {
        audio.play()
            .then(function() { setPlaying(true); })
            .catch(function() { setPlaying(false); });
    }

    // Button: toggle play / pause
    btn.addEventListener('click', function() {
        if (playing) { audio.pause(); setPlaying(false); }
        else         { tryPlay(); }
    });

    // Also start on the very first interaction anywhere on the page
    // (handles browsers that block autoplay until a gesture occurs)
    function onFirstGesture() {
        if (!playing) tryPlay();
    }
    document.addEventListener('click',      onFirstGesture, { once: true, passive: true });
    document.addEventListener('touchstart', onFirstGesture, { once: true, passive: true });
    document.addEventListener('keydown',    onFirstGesture, { once: true });

    // Attempt immediate autoplay (works after page reload on some browsers)
    tryPlay();
})();
        """),
    )


# ---------------------------------------------------------------------------
# Wedding Decoration Helpers
# ---------------------------------------------------------------------------

def _section_petals(n: int = 7, colors: list | None = None) -> FT:
    """Drifting background petals for any section."""
    if colors is None:
        colors = ['#E8B4BC', '#C4687A', '#FFF0F3', '#FAD4DA', '#F5C6CE']
    lefts  = [4, 14, 28, 52, 68, 82, 92, 8, 44]
    delays = [0, 1.8, 3.6, 1.0, 2.6, 4.4, 0.4, 3.0, 2.2]
    durs   = [15, 12, 17, 13, 11, 14, 16, 10, 18]
    drifts = [28, -22, 38, -28, 18, -38, 24, -18, 32]
    rots   = [360, -360, 480, -480, 300, 420, -420, 360, -300]
    sizes  = [8, 10, 7, 11, 9, 10, 7, 8, 12]
    items = []
    for i in range(n):
        s = sizes[i % len(sizes)]
        items.append(Div(
            cls='section-bg-petal',
            style=(
                f"left:{lefts[i%len(lefts)]}%;"
                f"width:{s}px;height:{int(s*1.4)}px;"
                f"background:{colors[i%len(colors)]};"
                f"--petal-dur:{durs[i%len(durs)]}s;"
                f"--petal-delay:{delays[i%len(delays)]}s;"
                f"--drift:{drifts[i%len(drifts)]}px;"
                f"--petal-rot:{rots[i%len(rots)]}deg;"
            )
        ))
    return Div(*items, cls='petal-field')


def _deco_flower(emoji: str, top: int | str, left: int | str,
                size: float = 2.0, opacity: float = 0.10,
                dur: float = 8, delay: float = 0,
                rot_start: int = -8, rot_end: int = 8, fy: int = -16) -> FT:
    """Absolutely-positioned decorative flower emoji."""
    return Span(
        emoji,
        cls='deco-flower',
        style=(
            f"top:{top}%;left:{left}%;"
            f"--fl-size:{size}rem;--fl-opacity:{opacity};"
            f"--fl-dur:{dur}s;--fl-delay:{delay}s;"
            f"--fl-rs:{rot_start}deg;--fl-re:{rot_end}deg;"
            f"--fl-fy:{fy}px;"
        )
    )


def _sparkle_svg(top: int, left: int, dur: float = 2.5,
                 delay: float = 0, size: int = 12) -> FT:
    """Soft pastel 4-pointed star sparkle."""
    # Alternate between lavender and blush sparkles
    fills = ['#CDB8EC', '#F2C4CE', '#A8DCC8', '#F7C8A0']
    fill = fills[(top + left) % 4]
    return NotStr(
        f'<svg class="sparkle" style="top:{top}%;left:{left}%;'
        f'width:{size}px;height:{size}px;'
        f'--sp-dur:{dur}s;--sp-delay:{delay}s;" '
        f'viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">'
        f'<path d="M10 0L11.5 8.5L20 10L11.5 11.5L10 20L8.5 11.5L0 10L8.5 8.5Z"'
        f' fill="{fill}" opacity="0.6"/>'
        f'</svg>'
    )


def _rsvp_heart(i: int) -> FT:
    """One floating heart for the RSVP section."""
    lefts  = [8, 22, 40, 58, 74, 88]
    delays = [0, 1.4, 2.8, 0.7, 2.1, 3.5]
    durs   = [3.5, 4.2, 3.0, 4.5, 3.8, 4.0]
    sizes  = ['0.85rem', '1.1rem', '0.75rem', '1rem', '0.9rem', '1.15rem']
    return Span(
        '♡',
        cls='rsvp-heart',
        style=(
            f"left:{lefts[i%6]}%;bottom:12%;"
            f"--h-delay:{delays[i%6]}s;"
            f"--h-dur:{durs[i%6]}s;"
            f"--h-size:{sizes[i%6]};"
        )
    )


def WeddingEffects() -> FT:
    """Global JS: IntersectionObserver scroll-reveal + falling petals on scroll."""
    return Script("""
(function(){
  // ── Scroll-reveal via IntersectionObserver ──
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting){
        e.target.classList.add('sr-visible');
        var vines = e.target.querySelectorAll('.vine-wrap');
        vines.forEach(function(v){ v.classList.add('sr-visible'); });
      }
    });
  }, { threshold: 0.10, rootMargin: '0px 0px -30px 0px' });
  document.querySelectorAll('.scroll-reveal').forEach(function(el){
    io.observe(el);
  });

  // ── Polaroid reveal (mem-reveal → mem-in) ────────────────
  var memIO = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(e.isIntersecting) e.target.classList.add('mem-in');
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -20px 0px' });
  document.querySelectorAll('.mem-reveal').forEach(function(el){
    memIO.observe(el);
  });

  // ── Falling petals on scroll ── full pastel rainbow
  var petalColors = [
    '#F2C4CE','#D47896',  // blush
    '#CDB8EC','#B89CD8',  // lavender
    '#A8DCC8','#7EC4AE',  // mint
    '#F7C8A0','#F0A878',  // peach
    '#A8CCEC','#80B4DC',  // sky
    '#FDEEF5','#EEF0FD'   // pale mixed
  ];
  var lastDrop = 0, lastY = 0;
  window.addEventListener('scroll', function(){
    var now = Date.now();
    var delta = Math.abs(window.scrollY - lastY);
    if(now - lastDrop < 220 || delta < 25) return;
    lastDrop = now; lastY = window.scrollY;
    var count = Math.min(4, Math.floor(delta / 35) + 1);
    for(var j = 0; j < count; j++){
      (function(off){
        setTimeout(function(){
          var p = document.createElement('div');
          p.className = 'scroll-petal';
          var color = petalColors[Math.floor(Math.random() * petalColors.length)];
          var drift = (Math.random() * 130 - 65);
          var spr   = Math.floor(Math.random() * 360);
          var sz    = Math.floor(Math.random() * 9 + 7);
          p.style.cssText =
            'left:'+(Math.random()*94+2)+'vw;'
            +'width:'+sz+'px;height:'+Math.round(sz*1.4)+'px;'
            +'background:'+color+';'
            +'--drift:'+drift+'px;'
            +'--spr:'+spr+'deg;';
          document.body.appendChild(p);
          setTimeout(function(){ p.remove(); }, 3400);
        }, off * 90);
      })(j);
    }
  }, { passive: true });

  // ── Gentle parallax on deco flowers ──
  window.addEventListener('scroll', function(){
    var sy = window.scrollY;
    document.querySelectorAll('.deco-flower[data-par="slow"]').forEach(function(el){
      el.style.transform = 'translateY('+(sy*0.035)+'px)';
    });
    document.querySelectorAll('.deco-flower[data-par="fast"]').forEach(function(el){
      el.style.transform = 'translateY('+(-sy*0.055)+'px)';
    });
  }, { passive: true });
})();
    """)


# ---------------------------------------------------------------------------
# Invite Page Components — Pastel Light Mode
# ---------------------------------------------------------------------------

def InviteHero(name: str | None = None) -> FT:
    """Full-screen blush-ivory hero with sparkles and drifting petals."""
    sparkles = [
        _sparkle_svg(10, 8,  2.2, 0.0, 11), _sparkle_svg(18, 90, 2.8, 0.8, 9),
        _sparkle_svg(32, 6,  2.0, 1.5, 13), _sparkle_svg(42, 94, 1.9, 0.3, 8),
        _sparkle_svg(58, 10, 2.5, 2.2, 10), _sparkle_svg(24, 86, 2.1, 1.0, 9),
        _sparkle_svg(70, 88, 2.4, 0.5, 11), _sparkle_svg(78, 8,  2.0, 1.8, 8),
        _sparkle_svg(88, 50, 2.3, 0.9, 10), _sparkle_svg(12, 48, 2.6, 1.4, 12),
    ]
    flowers = [
        _deco_flower('🌸', 4,  2,  4.5, 0.08, 9,  0.0, -10, 10, -22),
        _deco_flower('🌸', 6,  88, 4.0, 0.07, 11, 1.5, -8,  8,  -18),
        _deco_flower('🌸', 74, 4,  5.5, 0.06, 10, 0.8, -6,  6,  -14),
        _deco_flower('🌸', 78, 88, 4.5, 0.07, 8,  2.2, -12, 12, -24),
        _deco_flower('✿',  50, 1,  3.0, 0.10, 7,  1.2, -5,  5,  -12),
        _deco_flower('✿',  28, 95, 2.8, 0.09, 9,  0.4, -7,  7,  -15),
    ]
    # Gold accent dots
    gold_dots = [
        Div(cls='gold-dot', style='width:4px;height:4px;top:22%;left:22%;--gd-dur:3.5s;--gd-delay:0s;'),
        Div(cls='gold-dot', style='width:3px;height:3px;top:38%;right:19%;--gd-dur:4.5s;--gd-delay:1s;'),
        Div(cls='gold-dot', style='width:5px;height:5px;top:63%;left:17%;--gd-dur:4s;--gd-delay:0.5s;'),
        Div(cls='gold-dot', style='width:3px;height:3px;top:74%;right:23%;--gd-dur:5.5s;--gd-delay:1.5s;'),
    ]
    return Section(
        # Radial blush glow
        Div(cls="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_50%_40%,_#FFF0F3_0%,_#FDF8F5_70%)]"),
        # Section petals
        _section_petals(10, ['#F2C4CE','#CDB8EC','#FFF0F3','#FAD4DA','#E8B8D4']),
        # Decorative flowers
        Div(*flowers, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
        # Sparkle stars
        Div(*sparkles, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
        # Gold dots
        Div(*gold_dots, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
        # Corner accent marks
        Div(
            Span(cls="absolute top-0 left-0 block w-8 h-px bg-[#E8B4BC]/70"),
            Span(cls="absolute top-0 left-0 block w-px h-8 bg-[#E8B4BC]/70"),
            cls="absolute top-6 left-6",
        ),
        Div(
            Span(cls="absolute bottom-0 right-0 block w-8 h-px bg-[#E8B4BC]/70"),
            Span(cls="absolute bottom-0 right-0 block w-px h-8 bg-[#E8B4BC]/70"),
            cls="absolute bottom-6 right-6",
        ),
        # Main content - 3D Perspective Wrapper
        Div(
            Div(
                # ── Left: Text ──────────────────────────────────────
                Div(
                    P(
                        "You are cordially invited to the wedding of",
                        cls=(
                            "font-sans text-[10px] uppercase tracking-[0.45em] text-[#A89090] mb-8 "
                            "animate__animated animate__fadeIn"
                        ),
                        style="transform: translateZ(30px);"
                    ),
                    H1(
                        "Nikolai",
                        Span(" & ", cls="text-[#D4AF37] mx-2 font-serif font-light opacity-90"),
                        "Valentina",
                        cls=(
                            "font-serif text-[3.2rem] sm:text-6xl lg:text-[4rem] xl:text-[5rem] leading-[1.1] mb-2 "
                            "text-transparent bg-clip-text bg-gradient-to-b from-[#C4687A] to-[#8A4854] "
                            "drop-shadow-[0_2px_12px_rgba(196,104,122,0.4)] "
                            "animate__animated animate__fadeInUp animate__delay-1s"
                        ),
                        style="transform: translateZ(60px);"
                    ),
                    Div(
                        Div(cls="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-8 bg-[#D4AF37]/20 blur-xl rounded-full mix-blend-screen"),
                        Span(cls="block w-20 sm:w-28 h-[1px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent opacity-80"),
                        Span("✧", cls="text-[#D4AF37] text-2xl mx-4 drop-shadow-[0_0_8px_rgba(212,175,55,1)] animate-pulse"),
                        Span(cls="block w-20 sm:w-28 h-[1px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent opacity-80"),
                        cls="relative flex items-center justify-center lg:justify-start max-w-md mx-auto lg:mx-0 my-8 animate__animated animate__fadeIn animate__delay-2s",
                        style="transform: translateZ(40px);"
                    ),
                    P(
                        "Party: August 24, 2026",
                        cls="font-serif text-xl text-[#5C4A4A] tracking-wide animate__animated animate__fadeInUp animate__delay-2s",
                        style="transform: translateZ(25px);"
                    ),
                    P(
                        "Location: Eje Cafetero (Coffee Triangle)",
                        cls="font-sans text-[10px] uppercase tracking-[0.35em] text-[#A89090] mt-3 animate__animated animate__fadeInUp animate__delay-2s",
                        style="transform: translateZ(15px);"
                    ),
                    P(
                        "Address: Finca Hotel Nuevo Futuro",
                        cls="font-sans text-[10px] uppercase tracking-[0.35em] text-[#A89090] mt-1 animate__animated animate__fadeInUp animate__delay-2s",
                        style="transform: translateZ(15px);"
                    ),
                    *([
                        Div(
                            P(f"for {name}", cls="font-serif italic text-[#C4687A]/50 text-base mt-6"),
                            cls="animate__animated animate__fadeIn animate__delay-3s",
                            style="transform: translateZ(45px);"
                        )
                    ] if name else []),
                    Div(
                        I(data_lucide="chevrons-down", cls="w-5 h-5 text-[#E8B4BC] animate-bounce"),
                        cls="mt-10 lg:mt-14 animate__animated animate__fadeIn animate__delay-3s",
                        style="transform: translateZ(10px);"
                    ),
                    cls="hero-text-col",
                ),
                # ── Right: Couple Photo ──────────────────────────────
                Div(
                    Div(
                        Img(
                            src="/static/images/main/main.jpeg",
                            alt="Nikolai & Valentina",
                            cls="hero-main-img",
                            loading="eager",
                        ),
                        Div("Nikolai & Valentina ♡", cls="hero-photo-badge"),
                        cls="hero-main-frame js-lightbox",
                        data_src="/static/images/main/main.jpeg",
                    ),
                    cls="hero-photo-col animate__animated animate__fadeInRight animate__delay-2s",
                ),
                id="hero-3d-content",
                cls="relative z-10 hero-split-grid min-h-screen w-full",
                style="transform-style: preserve-3d; transition: transform 0.1s ease-out;",
            ),
            id="hero-3d-wrapper",
            cls="absolute inset-0 z-10 pointer-events-auto",
            style="perspective: 1000px;",
        ),
        
        # JS for Interactive Parallax 3D Animation
        Script(NotStr("""
            document.addEventListener('DOMContentLoaded', () => {
                const wrapper = document.getElementById('hero-3d-wrapper');
                const content = document.getElementById('hero-3d-content');
                if(!wrapper || !content) return;
                
                // Mouse parallax (desktop)
                wrapper.addEventListener('mousemove', (e) => {
                    const rect = wrapper.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    
                    const centerX = rect.width / 2;
                    const centerY = rect.height / 2;
                    
                    // Calculate rotation (max 10 degrees to keep it classy)
                    const rotateX = ((y - centerY) / centerY) * -10; 
                    const rotateY = ((x - centerX) / centerX) * 10;
                    
                    content.style.transition = 'none'; // Snappy follow
                    content.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
                });
                
                // Smooth reset when mouse leaves
                wrapper.addEventListener('mouseleave', () => {
                    content.style.transition = 'transform 0.8s cubic-bezier(0.2, 0.8, 0.2, 1)';
                    content.style.transform = `rotateX(0deg) rotateY(0deg)`;
                });
                
                // Gyroscope parallax (mobile/tablet)
                window.addEventListener('deviceorientation', (e) => {
                    if(e.beta === null || e.gamma === null) return;
                    
                    // e.beta (front-to-back), e.gamma (left-to-right)
                    let rotateX = -(e.beta - 45) * 0.3; // Assume typical phone viewing angle of 45deg
                    let rotateY = e.gamma * 0.4;
                    
                    // Clamp rotations to keep it elegant and readable
                    rotateX = Math.max(-12, Math.min(12, rotateX));
                    rotateY = Math.max(-12, Math.min(12, rotateY));
                    
                    content.style.transition = 'transform 0.1s ease-out';
                    content.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
                });
            });
        """)),
        
        cls="relative min-h-screen bg-[#FDF8F5] overflow-hidden section-canvas hero-canvas",
    )


def InviteDetails() -> FT:
    """Save-the-date: dramatic date + live countdown + interactive map cards + Google Calendar."""
    vine_svg = NotStr("""
    <svg class="vine-wrap scroll-reveal" viewBox="0 0 600 40" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;max-width:400px;height:40px;margin:0 auto;display:block;overflow:visible">
      <path class="draw-path" d="M0 20 Q50 5, 100 20 Q150 35, 200 20 Q250 5, 300 20 Q350 35, 400 20 Q450 5, 500 20 Q550 35, 600 20"
            fill="none" stroke="#CDB8EC" stroke-width="1.2" stroke-linecap="round"/>
      <circle cx="100" cy="20" r="3" fill="#CDB8EC" opacity="0.6"/>
      <circle cx="200" cy="20" r="2" fill="#9070C0" opacity="0.5"/>
      <circle cx="300" cy="20" r="3" fill="#CDB8EC" opacity="0.6"/>
      <circle cx="400" cy="20" r="2" fill="#9070C0" opacity="0.5"/>
      <circle cx="500" cy="20" r="3" fill="#CDB8EC" opacity="0.6"/>
    </svg>
    """)
    deco_flowers = [
        _deco_flower('🌸', 10, 2,  3.5, 0.09, 9,  0.0, -8, 8, -18),
        _deco_flower('🌸', 15, 90, 3.0, 0.08, 11, 1.2, -6, 6, -14),
        _deco_flower('✿',  70, 3,  3.5, 0.08, 8,  0.6, -9, 9, -20),
        _deco_flower('✿',  75, 88, 3.0, 0.07, 10, 2.0, -7, 7, -16),
    ]
    gcal_url = (
        "https://calendar.google.com/calendar/render?action=TEMPLATE"
        "&text=Nikolai+%26+Valentina+Wedding"
        "&dates=20260824%2F20260825"
        "&details=You%27re+cordially+invited+to+celebrate+the+wedding+of+Nikolai+%26+Valentina%21"
        "%0AFinca+Hotel+Nuevo+Futuro%2C+Eje+Cafetero%2C+Colombia"
        "&location=Finca+Hotel+Nuevo+Futuro%2C+Eje+Cafetero%2C+Colombia"
    )
    gmaps_url = (
        "https://www.google.com/maps/search/?api=1"
        "&query=Finca+Hotel+Nuevo+Futuro+Eje+Cafetero+Colombia"
    )
    gmaps_embed = (
        "https://maps.google.com/maps?q=Finca+Hotel+Nuevo+Futuro,+Eje+Cafetero,+Colombia"
        "&t=&z=14&ie=UTF8&iwloc=&output=embed"
    )

    def _map_card(icon, label, value, sub, extra_cls, sr_cls):
        return Div(
            Div(
                I(data_lucide=icon, cls="w-6 h-6 text-[#9070C0] mx-auto mb-3"),
                P(label, cls="std-card-label"),
                P(value,  cls="std-card-value"),
                P(sub,    cls="std-card-sub"),
                Div(
                    I(data_lucide="chevron-down", cls="w-4 h-4 std-chevron"),
                    P("Tap to view map", cls="text-[9px] text-[#9070C0] tracking-widest uppercase"),
                    cls="std-map-hint",
                ),
                cls="std-card-body",
            ),
            Div(
                NotStr(f'<iframe src="{gmaps_embed}" class="std-map-iframe" loading="lazy" frameborder="0" allowfullscreen=""></iframe>'),
                A(
                    I(data_lucide="navigation", cls="w-3.5 h-3.5 mr-1.5"),
                    "Get Directions",
                    href=gmaps_url, target="_blank", rel="noopener noreferrer",
                    cls="std-dir-btn",
                ),
                cls="std-map-panel",
            ),
            cls=f"std-card std-card-map {extra_cls} scroll-reveal {sr_cls}",
            data_mapcard="1",
        )

    return Section(
        _section_petals(8, ['#CDB8EC','#B89CD8','#E8D8F8','#D8C8F0','#F2C4CE']),
        Div(*deco_flowers, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
        Div(
            # ── Header ────────────────────────────────────────────────
            P(
                "Save the Date",
                cls="font-sans text-[10px] uppercase tracking-[0.5em] text-[#9070C0] mb-4 text-center scroll-reveal",
            ),
            vine_svg,
            Div(cls="h-6"),

            # ── Dramatic date display ──────────────────────────────────
            Div(
                Span("August", cls="std-date-month"),
                Span("24",     cls="std-date-day"),
                Span("2026",   cls="std-date-year"),
                cls="std-date-hero scroll-reveal sr-d1",
            ),

            # ── Live countdown ─────────────────────────────────────────
            Div(
                Div(Span("—", id="std-days",  cls="std-cnt-num"), P("Days",    cls="std-cnt-lbl"), cls="std-cnt-unit"),
                Div(cls="std-cnt-sep"),
                Div(Span("—", id="std-hours", cls="std-cnt-num"), P("Hours",   cls="std-cnt-lbl"), cls="std-cnt-unit"),
                Div(cls="std-cnt-sep"),
                Div(Span("—", id="std-mins",  cls="std-cnt-num"), P("Minutes", cls="std-cnt-lbl"), cls="std-cnt-unit"),
                Div(cls="std-cnt-sep"),
                Div(Span("—", id="std-secs",  cls="std-cnt-num"), P("Seconds", cls="std-cnt-lbl"), cls="std-cnt-unit"),
                cls="std-countdown scroll-reveal sr-d2",
            ),

            # ── Gold ornament divider ──────────────────────────────────
            Div(
                Span(cls="block w-16 h-px bg-gradient-to-r from-transparent via-[#CDB8EC] to-transparent"),
                Span("✦", cls="text-[#CDB8EC] text-xs mx-3 opacity-80"),
                Span(cls="block w-16 h-px bg-gradient-to-r from-transparent via-[#CDB8EC] to-transparent"),
                cls="flex items-center justify-center my-8 scroll-reveal sr-d3",
            ),

            # ── Info cards ─────────────────────────────────────────────
            Div(
                # Party / Date — static card
                Div(
                    I(data_lucide="calendar-heart", cls="w-6 h-6 text-[#9070C0] mx-auto mb-3"),
                    P("Party",           cls="std-card-label"),
                    P("August 24, 2026", cls="std-card-value"),
                    P("Monday",          cls="std-card-sub"),
                    cls="std-card scroll-reveal from-left sr-d4",
                ),
                # Location — interactive map card
                _map_card("map",     "Location", "Eje Cafetero",          "Coffee Triangle, Colombia",    "", "zoom-in sr-d5"),
                # Venue — interactive map card
                _map_card("map-pin", "Venue",    "Finca Hotel Nuevo Futuro", "Eje Cafetero, Colombia",   "", "from-right sr-d6"),
                cls="std-cards-grid",
            ),

            # ── Google Calendar CTA ────────────────────────────────────
            Div(
                A(
                    I(data_lucide="calendar-plus", cls="w-5 h-5 mr-2 flex-shrink-0"),
                    Span("Add to Google Calendar"),
                    href=gcal_url, target="_blank", rel="noopener noreferrer",
                    cls="std-gcal-btn scroll-reveal sr-d6",
                ),
                cls="flex justify-center mt-10 mb-2",
            ),

            cls="max-w-3xl mx-auto px-6 py-16 section-inner text-center",
        ),
        # ── Inline JS: countdown + map toggle ─────────────────────────
        Script(NotStr("""
(function(){
  // Live countdown to August 24 2026
  var target = new Date('2026-08-24T00:00:00');
  function pad(n){ return String(n).padStart(2,'0'); }
  function tick(){
    var diff = Math.max(0, target - new Date());
    var d = Math.floor(diff/86400000);
    var h = Math.floor((diff%86400000)/3600000);
    var m = Math.floor((diff%3600000)/60000);
    var s = Math.floor((diff%60000)/1000);
    var dEl=document.getElementById('std-days');
    var hEl=document.getElementById('std-hours');
    var mEl=document.getElementById('std-mins');
    var sEl=document.getElementById('std-secs');
    if(dEl) dEl.textContent = d;
    if(hEl) hEl.textContent = pad(h);
    if(mEl) mEl.textContent = pad(m);
    if(sEl) sEl.textContent = pad(s);
  }
  tick(); setInterval(tick, 1000);

  // Map card accordion toggle
  document.querySelectorAll('[data-mapcard]').forEach(function(card){
    card.addEventListener('click', function(e){
      if(e.target.closest('a') || e.target.tagName==='IFRAME') return;
      var opening = !card.classList.contains('std-card-open');
      document.querySelectorAll('[data-mapcard]').forEach(function(c){ c.classList.remove('std-card-open'); });
      if(opening) card.classList.add('std-card-open');
    });
  });
})();
""")),
        cls="bg-transparent relative section-canvas",
    )


def PersonalMessage(guest: dict) -> FT:
    first_name = guest["name"].split()[0]
    msg = guest.get("custom_message") or CATEGORY_MESSAGES.get(guest["category"], CATEGORY_MESSAGES["General"])
    return Section(
        _section_petals(6, ['#A8DCC8','#7EC4AE','#C8F0E4','#B8E8D4','#F2C4CE']),
        Span('🌹', cls='floral-watermark', style='top:5%;left:-2%;--fw-size:10rem;--fw-op:0.04;--fw-dur:16s;--fw-delay:0s;'),
        Span('🌸', cls='floral-watermark', style='bottom:5%;right:-2%;--fw-size:9rem;--fw-op:0.04;--fw-dur:14s;--fw-delay:2s;'),
        Span('🌺', cls='side-petal-l'),
        Span('🌸', cls='side-petal-r'),
        Div(
            Div(_ornament(), cls='scroll-reveal'),
            Div(cls="h-10"),
            P(
                f"Dear {first_name},",
                cls="font-serif text-2xl text-[#3A6A56] mb-5 scroll-reveal sr-d1",
            ),
            P(
                f'"{msg}"',
                cls="font-serif italic text-xl md:text-2xl text-[#5A7A68] leading-relaxed scroll-reveal sr-d2",
            ),
            Div(cls="h-10"),
            Div(_ornament(), cls='scroll-reveal sr-d3'),
            cls="max-w-2xl mx-auto text-center px-8 py-20 section-inner",
        ),
        cls="bg-transparent relative section-canvas",
    )


def RSVPForm(guest: dict) -> FT:
    hearts = [_rsvp_heart(i) for i in range(6)]
    corner_flowers = [
        _deco_flower('🌸', 2,  2,  2.5, 0.10, 8,  0.0, -8, 8, -16),
        _deco_flower('✿',  2,  86, 2.0, 0.09, 10, 1.4, -6, 6, -14),
        _deco_flower('🌸', 80, 4,  2.5, 0.09, 9,  0.7, -9, 9, -18),
        _deco_flower('✿',  80, 88, 2.0, 0.10, 7,  2.0, -7, 7, -14),
    ]
    return Div(
        Section(
            _section_petals(7, ['#F7C8A0','#F0A878','#F4D8BC','#F2C4CE','#CDB8EC']),
            Div(*hearts, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
            Div(*corner_flowers, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
            Div(
                Div(_ornament(), cls='scroll-reveal'),
                Div(cls="h-10"),
                H2(
                    "Will you join us?",
                    cls="font-serif text-4xl md:text-5xl text-[#6A3A28] mb-4 text-center scroll-reveal sr-d1",
                ),
                P(
                    "Kindly reply by August 10, 2026",
                    cls="font-sans text-[10px] uppercase tracking-[0.35em] text-[#A88060] text-center mb-8 scroll-reveal sr-d2",
                ),
                P(
                    guest["name"],
                    cls="font-serif italic text-[#C07840] text-xl text-center mb-10 scroll-reveal sr-d2",
                ),
                Form(
                    Input(type="hidden", name="slug", value=guest["slug"]),
                    Div(
            Div(
                Input(type="radio", name="attending", value="attending",
                      cls="sr-only peer", required=True),
                Div(
                    Span("♡", cls="text-3xl block mb-2 text-[#F7C8A0]"),
                    Span("Joyfully Accepts",
                         cls="font-sans text-xs uppercase tracking-widest"),
                    cls=(
                        "flex flex-col items-center justify-center px-8 py-6 h-full "
                        "rounded-2xl border-2 border-[#F4D0B0] cursor-pointer "
                        "text-[#A88060] transition-all duration-300 "
                        "peer-checked:border-[#C07840] peer-checked:bg-[#FEF6EF] "
                        "peer-checked:text-[#C07840] hover:border-[#F7C8A0]"
                    ),
                ),
                cls="cursor-pointer w-full",
            ),
            Label(
                Input(type="radio", name="attending", value="declined",
                      cls="sr-only peer"),
                Div(
                    Span("✗", cls="text-3xl block mb-2 text-[#D4C8EC]"),
                    Span("Regretfully Declines",
                         cls="font-sans text-xs uppercase tracking-widest"),
                    cls=(
                        "flex flex-col items-center justify-center px-8 py-6 h-full "
                        "rounded-2xl border-2 border-[#D4C8EC] cursor-pointer "
                        "text-[#8070A8] transition-all duration-300 "
                        "peer-checked:border-[#9070C0] peer-checked:bg-[#F6F0FD] "
                        "peer-checked:text-[#7050A8] hover:border-[#CDB8EC]"
                    ),
                ),
                cls="cursor-pointer w-full",
            ),
            cls="grid grid-cols-2 gap-4 mb-8 scroll-reveal zoom-in sr-d3",
        ),
        Label(
            Input(type="checkbox", name="plus_one", value="on",
                  cls="w-4 h-4 accent-[#C07840] mr-3"),
            "I'll be bringing a guest (+1)",
            cls="flex items-center justify-center text-xs text-[#A88060] uppercase tracking-widest mb-10 cursor-pointer",
        ),
        Button(
            "Confirm My Attendance",
            type="submit",
            cls=(
                "w-full py-4 rounded-2xl font-sans font-semibold text-sm "
                "uppercase tracking-[0.25em] text-white "
                "bg-[#C07840] hover:bg-[#A86030] "
                "shadow-md shadow-[#F7C8A0]/50 "
                "transition-all duration-200 active:scale-[0.98] "
                "scroll-reveal sr-d4"
            ),
        ),
                    hx_post="/rsvp",
                    hx_target="#rsvp-section",
                    hx_swap="outerHTML",
                    cls="max-w-sm mx-auto",
                ),
                cls="max-w-lg mx-auto px-8 py-20 text-center section-inner",
            ),
            cls="bg-transparent relative section-canvas",
        ),
        id="rsvp-section",
    )


def AttendanceSection(guest: dict) -> FT:
    slug = guest["slug"]
    hearts = [_rsvp_heart(i) for i in range(6)]
    corner_flowers = [
        _deco_flower('🌸', 2,  2,  2.5, 0.10, 8,  0.0, -8, 8, -16),
        _deco_flower('✿',  2,  86, 2.0, 0.09, 10, 1.4, -6, 6, -14),
        _deco_flower('🌸', 80, 4,  2.5, 0.09, 9,  0.7, -9, 9, -18),
        _deco_flower('✿',  80, 88, 2.0, 0.10, 7,  2.0, -7, 7, -14),
    ]

    css = Style("""
#att-backdrop {
  position:fixed;inset:0;z-index:9000;
  background:rgba(20,10,30,0.55);backdrop-filter:blur(10px);
  display:flex;align-items:flex-end;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity 0.3s ease;
}
#att-backdrop.att-open { opacity:1;pointer-events:all; }
#att-sheet {
  width:100%;max-width:520px;
  background:linear-gradient(160deg,#FEFAF8,#F6F0FD);
  border-radius:1.75rem 1.75rem 0 0;
  box-shadow:0 -20px 60px rgba(120,80,120,0.18);
  transform:translateY(100%);
  transition:transform 0.38s cubic-bezier(.34,1.56,.64,1);
  max-height:92vh;overflow-y:auto;overscroll-behavior:contain;
}
#att-backdrop.att-open #att-sheet { transform:translateY(0); }
@media(min-width:600px){
  #att-backdrop{align-items:center;}
  #att-sheet{border-radius:1.75rem;max-height:88vh;transform:scale(0.9) translateY(20px);}
  #att-backdrop.att-open #att-sheet{transform:scale(1) translateY(0);}
}
.att-handle{width:40px;height:4px;background:#DDD;border-radius:2px;margin:.8rem auto 0;display:block;}
.att-dots{display:flex;gap:.45rem;justify-content:center;margin:.75rem 0 .25rem;}
.att-dot{width:8px;height:8px;border-radius:50%;background:#DDD;transition:background .3s,transform .3s;}
.att-dot.active{background:#C4687A;transform:scale(1.35);}
.att-dot.done{background:#C4687A;opacity:.45;}
.att-step{display:none;animation:attIn .3s ease;padding:0 1.5rem .5rem;}
.att-step.active{display:block;}
@keyframes attIn{from{opacity:0;transform:translateX(28px)}to{opacity:1;transform:translateX(0)}}
.att-field{margin-bottom:1rem;}
.att-field label{display:block;font-family:sans-serif;font-size:.65rem;text-transform:uppercase;
  letter-spacing:.22em;color:#B09090;margin-bottom:.35rem;}
.att-field input,.att-field textarea,.att-field select{
  width:100%;padding:.7rem 1rem;border-radius:.75rem;border:1.5px solid #E8D8EC;
  background:rgba(255,255,255,.72);font-family:sans-serif;font-size:.88rem;color:#5C4A4A;
  outline:none;transition:border-color .2s,box-shadow .2s;-webkit-appearance:none;}
.att-field input:focus,.att-field textarea:focus,.att-field select:focus{
  border-color:#C4687A;box-shadow:0 0 0 3px rgba(196,104,122,.12);}
.att-field textarea{resize:none;}
.att-actions{display:flex;gap:.75rem;padding:.5rem 1.5rem 1.5rem;}
.att-btn-next,.att-btn-submit{
  flex:1;padding:.85rem;border-radius:.85rem;border:none;cursor:pointer;
  background:linear-gradient(135deg,#C4687A,#D47896);color:white;
  font-family:sans-serif;font-size:.82rem;text-transform:uppercase;letter-spacing:.2em;
  box-shadow:0 4px 16px rgba(196,104,122,.25);transition:transform .15s;touch-action:manipulation;}
.att-btn-next:active,.att-btn-submit:active{transform:scale(.97);}
.att-btn-back{
  padding:.85rem 1.1rem;border-radius:.85rem;border:1.5px solid #E8D8EC;
  background:white;color:#A89090;font-family:sans-serif;font-size:.82rem;
  cursor:pointer;touch-action:manipulation;}
""")

    js = Script("""
(function(){
  var bd = document.getElementById('att-backdrop');
  if(!bd) return;
  var STEPS = bd.querySelectorAll('.att-step');
  var DOTS  = bd.querySelectorAll('.att-dot');
  var btnNext   = bd.querySelector('.att-btn-next');
  var btnSubmit = bd.querySelector('.att-btn-submit');
  var btnBack   = bd.querySelector('.att-btn-back');
  var cur = 0;

  function isDeclined(){
    var r = bd.querySelector('[name="attending"]:checked');
    return r && r.value === 'declined';
  }

  function open(){
    bd.classList.add('att-open');
    document.body.style.overflow='hidden';
    go(0);
  }
  function close(){
    bd.classList.remove('att-open');
    document.body.style.overflow='';
  }
  function go(n){
    cur = n;
    STEPS.forEach(function(s,i){
      s.classList.toggle('active', i===n);
    });
    DOTS.forEach(function(d,i){
      d.classList.remove('active','done');
      if(i<n) d.classList.add('done');
      else if(i===n) d.classList.add('active');
    });
    // On step 0 with declined: show Submit immediately, hide Next
    if(n === 0 && isDeclined()){
      btnNext.style.display   = 'none';
      btnSubmit.style.display = '';
    } else {
      var isLast = (n === STEPS.length-1);
      btnNext.style.display   = isLast ? 'none' : '';
      btnSubmit.style.display = isLast ? '' : 'none';
    }
    btnBack.style.display = (n===0) ? 'none' : '';
  }

  // Re-evaluate buttons when attending choice changes
  bd.querySelectorAll('[name="attending"]').forEach(function(r){
    r.addEventListener('change', function(){ go(cur); });
  });

  btnNext.addEventListener('click', function(){ if(cur < STEPS.length-1) go(cur+1); });
  btnBack.addEventListener('click', function(){ if(cur > 0) go(cur-1); });
  bd.addEventListener('click', function(e){ if(e.target===bd) close(); });
  document.getElementById('att-close').addEventListener('click', close);
  window._attOpen = open;
})();
""")

    def _field(label, name, placeholder="", tag="input", input_type="text"):
        if tag == "textarea":
            el = Textarea(placeholder=placeholder, name=name, rows="3")
        elif tag == "select":
            el = NotStr(
                f'<select name="{name}">'
                '<option value="">Select…</option>'
                '<option value="1">Just me</option>'
                '<option value="2">2 guests</option>'
                '<option value="3">3 guests</option>'
                '<option value="4">4 guests</option>'
                '<option value="5+">5 or more</option>'
                '</select>'
            )
        else:
            el = Input(type=input_type, placeholder=placeholder, name=name)
        return Div(NotStr(f'<label>{label}</label>'), el, cls="att-field")

    total_steps = 4
    dots = Div(*[Div(cls="att-dot" + (" active" if i == 0 else "")) for i in range(total_steps)], cls="att-dots")

    form = Form(
        Input(type="hidden", name="slug", value=slug),
        # Step 1 — Attendance
        Div(
            P(guest["name"], cls="font-serif italic text-[#C07840] text-xl text-center mb-6"),
            Div(
                Label(
                    Input(type="radio", name="attending", value="attending", cls="sr-only peer", required=True),
                    Div(
                        Span("♡", cls="text-3xl block mb-2 text-[#F7C8A0]"),
                        Span("Joyfully Accepts", cls="font-sans text-xs uppercase tracking-widest"),
                        cls="flex flex-col items-center justify-center px-6 py-5 rounded-2xl border-2 border-[#F4D0B0] cursor-pointer text-[#A88060] transition-all peer-checked:border-[#C07840] peer-checked:bg-[#FEF6EF] peer-checked:text-[#C07840] hover:border-[#F7C8A0]",
                    ),
                    cls="cursor-pointer w-full",
                ),
                Label(
                    Input(type="radio", name="attending", value="declined", cls="sr-only peer"),
                    Div(
                        Span("✗", cls="text-3xl block mb-2 text-[#D4C8EC]"),
                        Span("Regretfully Declines", cls="font-sans text-xs uppercase tracking-widest"),
                        cls="flex flex-col items-center justify-center px-6 py-5 rounded-2xl border-2 border-[#D4C8EC] cursor-pointer text-[#8070A8] transition-all peer-checked:border-[#9070C0] peer-checked:bg-[#F6F0FD] peer-checked:text-[#7050A8] hover:border-[#CDB8EC]",
                    ),
                    cls="cursor-pointer w-full",
                ),
                cls="grid grid-cols-2 gap-3 mb-5",
            ),
            cls="att-step active", data_step="0",
        ),
        # Step 2 — Guest count
        Div(
            P("How many seats should we reserve?", cls="font-serif text-lg text-[#5C4A4A] text-center mb-5"),
            _field("Number of guests", "guest_count", tag="select"),
            cls="att-step", data_step="1",
        ),
        # Step 3 — Dietary & notes
        Div(
            P("Any special needs?", cls="font-serif text-lg text-[#5C4A4A] text-center mb-5"),
            _field("Dietary restrictions", "dietary", "Vegetarian, gluten-free, allergies…", tag="textarea"),
            _field("Extra notes", "notes", "Anything else we should know? 🌸", tag="textarea"),
            cls="att-step", data_step="2",
        ),
        # Step 4 — Song request
        Div(
            P("Request a song 🎵", cls="font-serif text-lg text-[#5C4A4A] text-center mb-1"),
            P("Would you like to request a song?", cls="font-sans text-xs text-[#B09090] text-center mb-4"),
            Div(
                Label(
                    Input(type="radio", name="song_opt", value="yes",
                          cls="w-4 h-4 accent-[#C4687A] mr-2",
                          onchange="document.getElementById('song-fields').style.display='block'"),
                    "Yes, I have a request 🎶",
                    cls="flex items-center text-sm text-[#5C4A4A] cursor-pointer",
                ),
                Label(
                    Input(type="radio", name="song_opt", value="no", checked=True,
                          cls="w-4 h-4 accent-[#B09090] mr-2",
                          onchange="document.getElementById('song-fields').style.display='none'"),
                    "No, skip this step",
                    cls="flex items-center text-sm text-[#B09090] cursor-pointer",
                ),
                cls="flex flex-col gap-2 mb-4 px-1",
            ),
            Div(
                _field("Song title", "song_title", "e.g. Perfect"),
                _field("Artist / band", "song_artist", "e.g. Ed Sheeran"),
                _field("Dedication", "song_message", "A message for the couple? 🌹", tag="textarea"),
                id="song-fields", style="display:none;",
            ),
            cls="att-step", data_step="3",
        ),
        id="att-form",
        hx_post="/attend",
        hx_target="#attendance-section",
        hx_swap="outerHTML",
    )

    modal = Div(
        Div(
            Div(cls="att-handle"),
            Button("✕", id="att-close",
                   style="position:absolute;top:1rem;right:1rem;width:34px;height:34px;"
                         "border-radius:50%;border:none;background:rgba(0,0,0,.07);"
                         "color:#999;font-size:1rem;cursor:pointer;"),
            Div(
                Div("💌", style="font-size:2rem;filter:drop-shadow(0 0 8px #C4687A44);margin-bottom:.4rem;text-align:center;"),
                P("Confirm My Attendance", style="font-family:serif;font-size:1.3rem;color:#5C4A4A;text-align:center;margin:.3rem 0 .1rem;"),
                P("RSVP · Reservation · Song Request", style="font-family:sans-serif;font-size:.65rem;text-transform:uppercase;letter-spacing:.25em;color:#B09090;text-align:center;"),
                dots,
                style="padding:1.25rem 1.5rem .5rem;",
            ),
            form,
            Div(
                Button("← Back", cls="att-btn-back", type="button", style="display:none;"),
                Button("Next →", cls="att-btn-next", type="button"),
                Button("Confirm My Attendance ✓", cls="att-btn-submit", type="submit", form="att-form", style="display:none;"),
                cls="att-actions",
            ),
            id="att-sheet", style="position:relative;",
        ),
        id="att-backdrop",
    )

    status = guest["rsvp_status"]
    already_responded = status != "pending"
    is_attending = status == "attending"

    if already_responded:
        # Build their response summary
        res_rows = []
        if is_attending:
            if guest.get("guest_count"):
                res_rows.append(("Seats reserved", guest["guest_count"]))
            if guest.get("dietary"):
                res_rows.append(("Dietary", guest["dietary"]))
            if guest.get("special_notes"):
                res_rows.append(("Notes", guest["special_notes"]))

        response_detail = Div(
            *[
                Div(
                    Span(lbl, cls="text-xs text-[#B09090] uppercase tracking-wider w-28 shrink-0"),
                    Span(val, cls="text-sm text-[#5C4A4A]"),
                    cls="flex gap-3 items-start border-b border-[#F0E8E4] py-1.5 last:border-0",
                )
                for lbl, val in res_rows
            ],
            id="resp-detail",
            style="display:none;margin-top:1rem;text-align:left;",
        )

        cta = Div(
            P(
                ("✓ You're on the list!" if is_attending else "✗ You've declined the invitation"),
                cls=f"font-serif text-xl {'text-[#22A05A]' if is_attending else 'text-[#C4687A]'} mb-2",
            ),
            P(
                ("We can't wait to celebrate with you! 🎉" if is_attending else "We'll miss you on our special day."),
                cls="font-sans text-xs text-[#B09090] mb-6",
            ),
            Button(
                "View My Response",
                onclick="var d=document.getElementById('resp-detail');var b=this;if(d.style.display==='none'){d.style.display='block';b.textContent='Hide Response';}else{d.style.display='none';b.textContent='View My Response';}",
                type="button",
                cls="px-6 py-2.5 rounded-2xl border border-[#E8D8D0] bg-white text-[#8C7070] text-xs font-semibold uppercase tracking-widest hover:bg-[#FDF8F5] transition-all",
            ) if (res_rows) else "",
            response_detail,
            cls="max-w-sm mx-auto text-center",
        )
    else:
        cta = Div(
            Button(
                "Confirm My Attendance",
                onclick="window._attOpen()",
                type="button",
                cls="w-full max-w-sm mx-auto block py-4 rounded-2xl font-sans font-semibold text-sm uppercase tracking-[.25em] text-white bg-[#C07840] hover:bg-[#A86030] shadow-md shadow-[#F7C8A0]/50 transition-all duration-200 active:scale-[.98] scroll-reveal sr-d4",
            ),
        )

    return Div(
        Section(
            css,
            _section_petals(7, ['#F7C8A0','#F0A878','#F4D8BC','#F2C4CE','#CDB8EC']),
            Div(*hearts, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
            Div(*corner_flowers, style='position:absolute;inset:0;pointer-events:none;overflow:hidden;'),
            modal if not already_responded else "",
            Div(
                Div(_ornament(), cls='scroll-reveal'),
                Div(cls="h-10"),
                H2("Will you join us?", cls="font-serif text-4xl md:text-5xl text-[#6A3A28] mb-4 text-center scroll-reveal sr-d1"),
                P("Kindly reply by August 10, 2026", cls="font-sans text-[10px] uppercase tracking-[0.35em] text-[#A88060] text-center mb-8 scroll-reveal sr-d2"),
                P(guest["name"], cls="font-serif italic text-[#C07840] text-xl text-center mb-10 scroll-reveal sr-d2"),
                cta,
                Div(cls="h-16"),
                cls="max-w-lg mx-auto px-8 py-20 text-center section-inner",
            ),
            cls="bg-transparent relative section-canvas",
        ),
        js if not already_responded else "",
        id="attendance-section",
    )


def RSVPSuccess(attending: str) -> FT:
    if attending == "attending":
        symbol, title, msg, symbol_cls = (
            "♡", "We can't wait to see you!",
            "Your RSVP has been received. We're so thrilled you'll be celebrating with us.",
            "text-[#C4687A]",
        )
    else:
        symbol, title, msg, symbol_cls = (
            "✦", "We'll miss you dearly.",
            "Thank you for letting us know. You'll be in our hearts on our special day.",
            "text-[#B8D0B4]",
        )
    return Div(
        Section(
            Div(
                P(symbol, cls=f"text-5xl {symbol_cls} mb-8 animate__animated animate__zoomIn"),
                H2(title, cls="font-serif text-3xl text-[#5C4A4A] mb-4"),
                P(msg, cls="font-sans text-sm text-[#8C7070] leading-relaxed max-w-xs mx-auto"),
                cls="max-w-lg mx-auto px-8 py-24 text-center",
            ),
            cls="bg-transparent relative",
        ),
        id="attendance-section",
    )


# ---------------------------------------------------------------------------
# Reservation & Song Request Section
# ---------------------------------------------------------------------------

def ReservationSongSection(guest: dict) -> FT:
    """One CTA button that opens a PWA-friendly multi-step wizard modal."""
    slug = guest.get("slug", "")
    petals = _section_petals(5, ['#CDB8EC','#F2C4CE','#A8DCC8','#A8CCEC','#F2C4CE'])

    wizard_css = NotStr("""<style>
/* ── Wizard Modal ─────────────────────────────────── */
#wizard-backdrop {
  position: fixed; inset: 0; z-index: 9000;
  background: rgba(20,10,30,0.55);
  backdrop-filter: blur(10px);
  display: flex; align-items: flex-end;
  justify-content: center;
  opacity: 0; pointer-events: none;
  transition: opacity 0.3s ease;
}
#wizard-backdrop.wiz-open {
  opacity: 1; pointer-events: all;
}
#wizard-sheet {
  width: 100%; max-width: 520px;
  background: linear-gradient(160deg,#FEFAF8,#F6F0FD);
  border-radius: 1.75rem 1.75rem 0 0;
  padding: 0 0 env(safe-area-inset-bottom,0);
  box-shadow: 0 -20px 60px rgba(120,80,120,0.18);
  transform: translateY(100%);
  transition: transform 0.38s cubic-bezier(.34,1.56,.64,1);
  max-height: 92vh; overflow-y: auto;
  overscroll-behavior: contain;
  -webkit-overflow-scrolling: touch;
}
#wizard-backdrop.wiz-open #wizard-sheet {
  transform: translateY(0);
}
/* on tablet/desktop: center as modal */
@media (min-width: 600px) {
  #wizard-backdrop { align-items: center; }
  #wizard-sheet {
    border-radius: 1.75rem;
    max-height: 88vh;
    transform: scale(0.9) translateY(20px);
  }
  #wizard-backdrop.wiz-open #wizard-sheet {
    transform: scale(1) translateY(0);
  }
}
.wiz-handle {
  width: 40px; height: 4px;
  background: #DDD; border-radius: 2px;
  margin: 0.8rem auto 0; display: block;
}
.wiz-header { padding: 1.25rem 1.5rem 0.5rem; text-align: center; }
.wiz-title {
  font-family: serif; font-size: 1.3rem;
  color: #5C4A4A; margin: 0.4rem 0 0.15rem;
}
.wiz-subtitle {
  font-family: sans-serif; font-size: 0.68rem;
  text-transform: uppercase; letter-spacing: 0.25em; color: #B09090;
}
/* Progress dots */
.wiz-dots {
  display: flex; gap: 0.45rem;
  justify-content: center; margin: 1rem 0 0.25rem;
}
.wiz-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #DDD; transition: background 0.3s, transform 0.3s;
}
.wiz-dot.active { background: var(--wiz-color,#C4687A); transform: scale(1.35); }
.wiz-dot.done   { background: var(--wiz-color,#C4687A); opacity: 0.45; }
/* Steps */
.wiz-body { padding: 0.5rem 1.5rem 1.25rem; }
.wiz-step { display: none; animation: wizIn 0.3s ease; }
.wiz-step.active { display: block; }
@keyframes wizIn {
  from { opacity:0; transform: translateX(28px); }
  to   { opacity:1; transform: translateX(0); }
}
.wiz-step.back-anim { animation: wizBack 0.3s ease; }
@keyframes wizBack {
  from { opacity:0; transform: translateX(-28px); }
  to   { opacity:1; transform: translateX(0); }
}
/* Fields */
.wiz-field { margin-bottom: 1rem; }
.wiz-field label {
  display: block;
  font-family: sans-serif; font-size: 0.65rem;
  text-transform: uppercase; letter-spacing: 0.22em;
  color: #B09090; margin-bottom: 0.35rem;
}
.wiz-field input, .wiz-field textarea, .wiz-field select {
  width: 100%; padding: 0.7rem 1rem;
  border-radius: 0.75rem;
  border: 1.5px solid #E8D8EC;
  background: rgba(255,255,255,0.72);
  font-family: sans-serif; font-size: 0.88rem; color: #5C4A4A;
  outline: none; transition: border-color 0.2s, box-shadow 0.2s;
  -webkit-appearance: none;
}
.wiz-field input:focus, .wiz-field textarea:focus {
  border-color: var(--wiz-color,#C4687A);
  box-shadow: 0 0 0 3px rgba(196,104,122,0.12);
}
.wiz-field textarea { resize: none; }
/* Buttons */
.wiz-actions {
  display: flex; gap: 0.75rem;
  padding: 0.5rem 1.5rem 1.25rem;
}
.wiz-btn-next {
  flex: 1; padding: 0.85rem;
  border-radius: 0.85rem; border: none; cursor: pointer;
  background: var(--wiz-grad, linear-gradient(135deg,#C4687A,#D47896));
  color: white; font-family: sans-serif; font-size: 0.82rem;
  text-transform: uppercase; letter-spacing: 0.2em;
  box-shadow: 0 4px 16px rgba(196,104,122,0.25);
  transition: transform 0.15s, box-shadow 0.15s;
  touch-action: manipulation;
}
.wiz-btn-next:active { transform: scale(0.97); }
.wiz-btn-back {
  padding: 0.85rem 1.1rem;
  border-radius: 0.85rem;
  border: 1.5px solid #E8D8EC;
  background: white; color: #A89090;
  font-family: sans-serif; font-size: 0.82rem;
  cursor: pointer; touch-action: manipulation;
  transition: background 0.2s;
}
.wiz-btn-back:active { background: #F9F5F5; }
/* Finish screen */
.wiz-finish {
  text-align: center; padding: 2rem 1.5rem 2.5rem;
  display: none;
}
.wiz-finish.active { display: block; animation: wizIn 0.4s ease; }
.wiz-finish-emoji { font-size: 3.5rem; margin-bottom: 0.75rem; }
.wiz-finish-title {
  font-family: serif; font-size: 1.4rem; color: #5C4A4A; margin-bottom: 0.4rem;
}
.wiz-finish-sub {
  font-family: sans-serif; font-size: 0.82rem; color: #B09090;
  margin-bottom: 1.5rem;
}
/* CTA buttons in section */
.wiz-cta-btn {
  display: flex; align-items: center; gap: 0.9rem;
  padding: 1rem 1.5rem; border-radius: 1.25rem; border: none;
  cursor: pointer; width: 100%; text-align: left;
  background: rgba(255,255,255,0.72);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.07);
  transition: transform 0.2s, box-shadow 0.2s;
  touch-action: manipulation;
  border: 1.5px solid rgba(255,255,255,0.9);
}
.wiz-cta-btn:active { transform: scale(0.98); }
.wiz-cta-icon {
  width: 48px; height: 48px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; flex-shrink: 0;
}
.wiz-cta-text p:first-child {
  font-family: serif; font-size: 1rem; color: #5C4A4A;
  margin: 0 0 0.1rem;
}
.wiz-cta-text p:last-child {
  font-family: sans-serif; font-size: 0.7rem;
  color: #B09090; margin: 0;
  text-transform: uppercase; letter-spacing: 0.15em;
}
.wiz-cta-chevron { margin-left: auto; color: #CCC; font-size: 1.1rem; }
</style>""")

    wizard_js = Script("""
(function(){
  var backdrop = document.getElementById('wizard-backdrop');
  var sheet    = document.getElementById('wizard-sheet');
  if(!backdrop) return;

  function openWiz(){
    document.documentElement.style.setProperty('--wiz-color', '#C4687A');
    document.documentElement.style.setProperty('--wiz-grad',  'linear-gradient(135deg,#C4687A,#D47896)');
    document.querySelector('.wiz-panel').style.display = '';
    backdrop.classList.add('wiz-open');
    document.body.style.overflow = 'hidden';
    activateStep(0, false);
  }

  function closeWiz(){
    backdrop.classList.remove('wiz-open');
    document.body.style.overflow = '';
  }

  backdrop.addEventListener('click', function(e){
    if(e.target===backdrop) closeWiz();
  });
  document.getElementById('wiz-close-btn').addEventListener('click', closeWiz);

  // ── Step engine ──────────────────────────────────────────
  function activateStep(idx, back){
    var panel = document.querySelector('.wiz-panel');
    var steps = panel.querySelectorAll('.wiz-step');
    var dots  = panel.querySelectorAll('.wiz-dot');
    var finish= panel.querySelector('.wiz-finish');
    var actns = panel.querySelector('.wiz-actions');

    // hide finish, show steps
    if(finish){ finish.classList.remove('active'); finish.style.display='none'; }
    if(actns)  actns.style.display='';

    steps.forEach(function(s,i){
      s.classList.remove('active','back-anim');
      if(i===idx){
        s.classList.add('active');
        if(back) s.classList.add('back-anim');
      }
    });
    dots.forEach(function(d,i){
      d.classList.remove('active','done');
      if(i<idx) d.classList.add('done');
      else if(i===idx) d.classList.add('active');
    });
    panel.dataset.step = idx;
  }

  function showFinish(){
    var panel = document.querySelector('.wiz-panel');
    panel.querySelectorAll('.wiz-step').forEach(function(s){ s.classList.remove('active'); });
    var finish= panel.querySelector('.wiz-finish');
    var actns = panel.querySelector('.wiz-actions');
    if(finish){ finish.style.display=''; finish.classList.add('active'); }
    if(actns)  actns.style.display='none';
    var dots=panel.querySelectorAll('.wiz-dot');
    dots.forEach(function(d){ d.classList.remove('active'); d.classList.add('done'); });
  }

  // Next button handler
  document.querySelectorAll('.wiz-btn-next').forEach(function(btn){
    btn.addEventListener('click', function(){
      var panel = btn.closest('.wiz-panel');
      var steps = panel.querySelectorAll('.wiz-step');
      var cur   = parseInt(panel.dataset.step||'0');
      var next  = cur+1;
      if(next >= steps.length){
        // last step — show finish
        showFinish();
      } else {
        activateStep(next, false);
      }
    });
  });

  // Back button handler
  document.querySelectorAll('.wiz-btn-back').forEach(function(btn){
    btn.addEventListener('click', function(){
      var panel = btn.closest('.wiz-panel');
      var cur   = parseInt(panel.dataset.step||'0');
      if(cur>0) activateStep(cur-1, true);
    });
  });

  // Close from finish
  document.querySelectorAll('.wiz-close-finish').forEach(function(btn){
    btn.addEventListener('click', closeWiz);
  });

  // Expose openWiz globally for inline onclick
  window._wizOpen = openWiz;
})();
""")

    # ── Wizard modal markup ────────────────────────────────────────────────
    def _field(label, name, placeholder, tag="input", input_type="text"):
        if tag == "textarea":
            el = Textarea(placeholder=placeholder, name=name, rows="3")
        elif tag == "select":
            el = NotStr(f'<select name="{name}"><option value="">Select…</option>'
                        '<option value="1">1 guest</option><option value="2">2 guests</option>'
                        '<option value="3">3 guests</option><option value="4">4 guests</option>'
                        '<option value="5+">5+ guests</option></select>')
        else:
            el = Input(type=input_type, placeholder=placeholder, name=name)
        return Div(NotStr(f'<label>{label}</label>'), el, cls="wiz-field")

    def _dots(n):
        return Div(*[Div(cls="wiz-dot" + (" active" if i == 0 else "")) for i in range(n)], cls="wiz-dots")

    # Unified Reservation wizard panel
    res_panel = Div(
        # Header
        Div(
            Div("💌", style="font-size:2.2rem; filter:drop-shadow(0 0 8px #C4687A44); margin-bottom: 0.5rem;"),
            P("Reserve Your Seat", cls="wiz-title"),
            P("RSVP & Song Request", cls="wiz-subtitle"),
            _dots(5),
            cls="wiz-header",
        ),
        # Steps
        Div(
            # Step 1: Guests
            Div(
                P("How many people will be joining you?",
                  style="font-family:serif;font-size:1.1rem;color:#5C4A4A;margin-bottom:1.5rem;text-align:center;"),
                _field("Number of Guests", "guest_count", "", tag="select"),
                cls="wiz-step active", data_step="0",
            ),
            # Step 2: Dietary
            Div(
                P("Any dietary needs or special requests?",
                  style="font-family:serif;font-size:1.1rem;color:#5C4A4A;margin-bottom:1.5rem;text-align:center;"),
                _field("Dietary Restrictions", "dietary", "Vegetarian, gluten-free, allergies…", tag="textarea"),
                _field("Extra Notes", "notes", "Anything else we should know? 🌸", tag="textarea"),
                cls="wiz-step", data_step="1",
            ),
            # Step 3: Song
            Div(
                P("What song should we play?",
                  style="font-family:serif;font-size:1.1rem;color:#5C4A4A;margin-bottom:1.5rem;text-align:center;"),
                _field("Song Title", "song_title", "e.g. Perfect"),
                _field("Artist / Band", "song_artist", "e.g. Ed Sheeran"),
                cls="wiz-step", data_step="2",
            ),
            # Step 4: Dedication
            Div(
                P("Add a personal touch 🎶",
                  style="font-family:serif;font-size:1.1rem;color:#5C4A4A;margin-bottom:1.5rem;text-align:center;"),
                _field("Dedication (optional)", "song_message",
                       "For who? A special message?", tag="textarea"),
                cls="wiz-step", data_step="3",
            ),
            # Step 5: Review
            Div(
                P("All set?",
                  style="font-family:serif;font-size:1.1rem;color:#5C4A4A;margin-bottom:0.6rem;text-align:center;"),
                P("Tap confirm to save your reservation and song request.",
                  style="font-family:sans-serif;font-size:0.85rem;color:#B09090;margin-bottom:1.5rem;text-align:center;"),
                Input(type="hidden", name="slug", value=slug),
                Input(type="hidden", name="form_type", value="reservation_and_song"),
                cls="wiz-step", data_step="4",
            ),
            cls="wiz-body",
        ),
        # Actions
        Div(
            Button("← Back", cls="wiz-btn-back"),
            Button("Next →", cls="wiz-btn-next"),
            cls="wiz-actions",
        ),
        # Finish screen
        Div(
            Div("🌸", cls="wiz-finish-emoji"),
            P("You're on the list!", cls="wiz-finish-title"),
            P("Reservation & Song Request saved.", cls="wiz-finish-sub", style="color:#A89090;"),
            P("We can't wait to celebrate with you.", cls="wiz-finish-sub"),
            Button("Close  ✓", cls="wiz-btn-next wiz-close-finish"),
            cls="wiz-finish",
            style="display:none;",
        ),
        cls="wiz-panel", data_step="0",
        style="display:none;",
    )

    # The full modal backdrop + sheet
    modal = Div(
        Div(
            # Drag handle + close
            Div(
                Div(cls="wiz-handle"),
                style="position:relative;",
            ),
            Button("✕", id="wiz-close-btn",
                   style="position:absolute;top:1rem;right:1rem;width:34px;height:34px;"
                         "border-radius:50%;border:none;background:rgba(0,0,0,0.07);"
                         "color:#999;font-size:1rem;cursor:pointer;touch-action:manipulation;"),
            res_panel,
            id="wizard-sheet",
            style="position:relative;",
        ),
        id="wizard-backdrop",
    )

    return Section(
        petals,
        wizard_css,
        modal,
        Div(
            # Section heading
            Div(
                P("♡  Make it Memorable  ♡",
                  style="font-family:sans-serif;font-size:0.65rem;text-transform:uppercase;"
                        "letter-spacing:0.38em;color:#A89090;margin-bottom:0.6rem;",
                  cls="scroll-reveal"),
                P("Your Details & Music",
                  style="font-family:serif;font-size:clamp(1.5rem,5vw,2rem);"
                        "color:#5C4A4A;margin:0 0 0.4rem;",
                  cls="scroll-reveal sr-d1"),
                P("Help us make this day perfect for everyone.",
                  style="font-family:sans-serif;font-size:0.82rem;color:#B09090;",
                  cls="scroll-reveal sr-d2"),
                style="text-align:center;margin-bottom:2rem;",
            ),
            # CTA Buttons
            Div(
                # Single Unified Button
                Button(
                    Div("💌",
                        style="background:linear-gradient(135deg,#FADADD,#F2C4CE); transform: translateZ(20px);",
                        cls="wiz-cta-icon"),
                    Div(
                        P("Reserve Your Seat"),
                        P("RSVP & Song Request Inside"),
                        cls="wiz-cta-text",
                        style="transform: translateZ(10px);"
                    ),
                    Div("›", cls="wiz-cta-chevron", style="transform: translateZ(15px);"),
                    cls="wiz-cta-btn scroll-reveal js-tilt transform-preserve-3d transition-transform",
                    style="box-shadow:0 15px 35px rgba(212,120,150,0.25); background: rgba(255,255,255,0.85) backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.6);",
                    onclick="window._wizOpen()",
                ),
                style="display:flex;flex-direction:column;gap:1rem;max-width:480px;margin:0 auto;",
            ),
            cls="section-inner",
            style="padding:3.5rem 1.5rem 4rem;max-width:600px;margin:0 auto;",
        ),
        wizard_js,
        id="reservation-song-section",
        cls="section-canvas",
        style="background:linear-gradient(160deg,#F6F0FD 0%,#FEF4EB 50%,#F0FAF6 100%);",
    )




    # ── shared decorative petals ───────────────────────────────────────────
    petals = _section_petals(6, ['#CDB8EC','#F2C4CE','#A8DCC8','#F7C8A0','#A8CCEC','#F2C4CE'])

    def _card_header(emoji: str, title: str, subtitle: str, color: str) -> FT:
        return Div(
            Div(emoji, style=f"font-size:2rem;filter:drop-shadow(0 0 8px {color}44);"),
            P(title,
              style=f"font-family:serif;font-size:1.25rem;font-weight:600;color:{color};margin:0.5rem 0 0.15rem;"),
            P(subtitle,
              style="font-family:sans-serif;font-size:0.65rem;text-transform:uppercase;"
                    "letter-spacing:0.28em;color:#A89090;"),
            style="text-align:center;margin-bottom:1.5rem;",
        )

    def _field(label: str, name: str, placeholder: str, tag: str = "input",
               input_type: str = "text", extra_style: str = "") -> FT:
        field_style = (
            "width:100%;padding:0.65rem 1rem;border-radius:0.75rem;"
            "border:1.5px solid #E8D8EC;background:rgba(255,255,255,0.7);"
            "font-family:sans-serif;font-size:0.85rem;color:#5C4A4A;"
            "outline:none;transition:border-color 0.2s;"
            f"{extra_style}"
        )
        input_el = (
            Textarea(placeholder=placeholder, name=name, rows="3",
                     style=field_style + "resize:none;")
            if tag == "textarea"
            else Input(type=input_type, placeholder=placeholder, name=name,
                       style=field_style)
        )
        return Div(
            P(label, style="font-family:sans-serif;font-size:0.68rem;text-transform:uppercase;"
                           "letter-spacing:0.22em;color:#A89090;margin-bottom:0.35rem;"),
            input_el,
            style="margin-bottom:1rem;",
        )

    # ── Card 1: Reservation ────────────────────────────────────────────────
    reservation_card = Div(
        _card_header("🌹", "Reserve Your Seat", "Confirm your attendance details", "#C4687A"),
        Div(
            _field("Number of Guests", "guest_count", "How many seats?", input_type="number"),
            _field("Dietary Restrictions", "dietary", "Vegetarian, gluten-free, allergies…", tag="textarea"),
            _field("Special Notes", "notes", "Any other requests for us?", tag="textarea"),
            Input(type="hidden", name="slug", value=slug),
            Input(type="hidden", name="form_type", value="reservation"),
            Button(
                "🌸 Confirm Reservation",
                hx_post="/guest-form",
                hx_target="#reservation-msg",
                hx_swap="outerHTML",
                style=(
                    "width:100%;padding:0.8rem;border-radius:0.75rem;"
                    "background:linear-gradient(135deg,#C4687A,#D47896);"
                    "color:white;font-family:sans-serif;font-size:0.8rem;"
                    "text-transform:uppercase;letter-spacing:0.2em;"
                    "border:none;cursor:pointer;"
                    "box-shadow:0 4px 16px rgba(196,104,122,0.3);"
                    "transition:transform 0.2s,box-shadow 0.2s;"
                ),
            ),
            Div(id="reservation-msg"),
            style="display:flex;flex-direction:column;",
            hx_on__submit="",
        ),
        style=(
            "background:rgba(255,255,255,0.65);backdrop-filter:blur(12px);"
            "border-radius:1.5rem;padding:2rem;"
            "border:1.5px solid rgba(212,120,150,0.18);"
            "box-shadow:0 8px 32px rgba(212,120,150,0.12);"
            "flex:1;min-width:0;"
        ),
        cls="scroll-reveal",
    )

    # ── Card 2: Song Request ───────────────────────────────────────────────
    song_card = Div(
        _card_header("🎵", "Request a Song", "What should we play at the reception?", "#7A6AAA"),
        Div(
            _field("Song Title", "song_title", "e.g. Perfect — Ed Sheeran"),
            _field("Artist / Band", "song_artist", "e.g. Ed Sheeran"),
            _field("Dedication Message", "song_message", "Optional — who's this for? 🎶", tag="textarea"),
            Input(type="hidden", name="slug", value=slug),
            Input(type="hidden", name="form_type", value="song_request"),
            Button(
                "🎶 Submit Song Request",
                hx_post="/guest-form",
                hx_target="#song-msg",
                hx_swap="outerHTML",
                style=(
                    "width:100%;padding:0.8rem;border-radius:0.75rem;"
                    "background:linear-gradient(135deg,#7A6AAA,#9A88CC);"
                    "color:white;font-family:sans-serif;font-size:0.8rem;"
                    "text-transform:uppercase;letter-spacing:0.2em;"
                    "border:none;cursor:pointer;"
                    "box-shadow:0 4px 16px rgba(122,106,170,0.3);"
                    "transition:transform 0.2s,box-shadow 0.2s;"
                ),
            ),
            Div(id="song-msg"),
            style="display:flex;flex-direction:column;",
        ),
        style=(
            "background:rgba(255,255,255,0.65);backdrop-filter:blur(12px);"
            "border-radius:1.5rem;padding:2rem;"
            "border:1.5px solid rgba(122,106,170,0.18);"
            "box-shadow:0 8px 32px rgba(122,106,170,0.12);"
            "flex:1;min-width:0;"
        ),
        cls="scroll-reveal sr-d1",
    )

    return Section(
        petals,
        Div(
            # Section header
            Div(
                P("♡  Make it Memorable  ♡",
                  style="font-family:sans-serif;font-size:0.65rem;text-transform:uppercase;"
                        "letter-spacing:0.38em;color:#A89090;margin-bottom:0.6rem;",
                  cls="scroll-reveal"),
                P("Your Details & Music",
                  style="font-family:serif;font-size:clamp(1.6rem,5vw,2.2rem);"
                        "color:#5C4A4A;margin:0 0 0.5rem;",
                  cls="scroll-reveal sr-d1"),
                P("Reserve your seat and help us curate the perfect soundtrack for our celebration.",
                  style="font-family:sans-serif;font-size:0.85rem;color:#A89090;max-width:420px;margin:0 auto;",
                  cls="scroll-reveal sr-d2"),
                style="text-align:center;margin-bottom:2.5rem;",
            ),
            # Cards row
            Div(
                reservation_card,
                song_card,
                style=(
                    "display:flex;gap:1.5rem;align-items:flex-start;"
                    "flex-wrap:wrap;"
                ),
            ),
            cls="section-inner",
            style="padding:4rem 1.5rem;max-width:900px;margin:0 auto;",
        ),
        id="reservation-song-section",
        cls="section-canvas",
        style="background:linear-gradient(160deg,#F6F0FD 0%,#FEF4EB 50%,#F0FAF6 100%);",
    )


def InviteFooter() -> FT:
    """Elegant closing footer — monogram, date, venue, and closing message."""
    return Footer(
        # Ambient floating petals
        _section_petals(10, ['#E8B4BC','#CDB8EC','#A8DCC8','#F2C4CE','#FFF0F3','#E8B4BC']),
        # Top vine divider
        Div(
            Span(cls="ftw-vine ftw-vine-l"),
            Span("✦", cls="ftw-diamond"),
            Span(cls="ftw-vine ftw-vine-r"),
            cls="ftw-divider scroll-reveal",
        ),
        # Large blush monogram N & V
        Div(
            Span("N", cls="ftw-mono-letter"),
            Span("&", cls="ftw-mono-amp"),
            Span("V", cls="ftw-mono-letter"),
            cls="ftw-monogram scroll-reveal sr-d1",
        ),
        # Ornamental fleuron
        Span("❦", cls="ftw-fleuron scroll-reveal sr-d1"),
        # Wedding date
        P("August 24, 2026", cls="ftw-date scroll-reveal sr-d2"),
        # Thin ornament rule
        Div(
            Span(cls="flex-1 h-px bg-[#E8B4BC]/40"),
            Span("✦", cls="text-[#C4687A]/35 text-[9px] mx-4"),
            Span(cls="flex-1 h-px bg-[#E8B4BC]/40"),
            cls="ftw-rule flex items-center max-w-[160px] mx-auto my-5 scroll-reveal sr-d2",
        ),
        # Venue
        P("Finca Hotel Nuevo Futuro", cls="ftw-venue-name scroll-reveal sr-d3"),
        P("Eje Cafetero · Colombia", cls="ftw-venue-loc scroll-reveal sr-d3"),
        # Spacer
        Div(cls="h-12"),
        # Closing message
        P("We can\u2019t wait to celebrate with you.", cls="ftw-closing scroll-reveal sr-d4"),
        # Bottom bar
        Div(
            Span("With love,", cls="ftw-bottom-pre"),
            Span("Nikolai & Valentina \u2665", cls="ftw-bottom-names"),
            cls="ftw-bottom scroll-reveal sr-d5",
        ),
        cls="ftw-canvas relative text-center overflow-hidden",
    )


# ---------------------------------------------------------------------------
# Interactive Image Sections
# ---------------------------------------------------------------------------

def _lightbox() -> FT:
    """Global fullscreen lightbox overlay."""
    return Div(
        Button("✕", id="lightbox-close", aria_label="Close"),
        Div(id="lightbox-img-wrap"),
        id="lightbox",
        aria_hidden="true",
    )


def HeroPhotoSection() -> FT:
    """Main couple photo with 3D tilt frame and animated badge."""
    return Div(
        Div(
            Div(
                Img(
                    src="/static/images/main/main.jpeg",
                    alt="Nikolai & Valentina",
                    cls="w-full",
                    loading="eager",
                ),
                Div("Nikolai & Valentina ♡", cls="hero-photo-badge"),
                cls="hero-photo-frame js-tilt",
                data_src="/static/images/main/main.jpeg",
            ),
            cls="hero-photo-wrap scroll-reveal zoom-in",
        ),
        cls="max-w-xl mx-auto px-6 pb-10",
    )


def VenueSection() -> FT:
    """Full-bleed parallax venue image with animated overlay text."""
    return Div(
        Div(
            cls="venue-bg js-parallax-bg",
            style="background-image:url('/static/images/main/main.jpeg');",
        ),
        Div(cls="venue-overlay"),
        Div(
            P(
                "Join Us At",
                cls="font-sans text-[10px] uppercase tracking-[0.5em] text-white/70 mb-3 scroll-reveal",
            ),
            Div(
                "Finca Hotel Nuevo Futuro",
                cls="font-serif text-4xl md:text-5xl text-white mb-3 scroll-reveal sr-d1",
                style="text-shadow:0 2px 20px rgba(0,0,0,0.4);",
            ),
            Div(
                Div(cls="w-16 h-px bg-white/50 mx-auto mb-3"),
                P(
                    "Location: Eje Cafetero (Coffee Triangle)",
                    cls="font-sans text-sm text-white/85 tracking-wide scroll-reveal sr-d2",
                ),
                P(
                    "Party: August 24, 2026",
                    cls="font-sans text-sm text-white/85 tracking-wide scroll-reveal sr-d3 mt-1",
                ),
                Div(cls="w-16 h-px bg-white/50 mx-auto mt-3"),
            ),
        ),
        cls="venue-section section-canvas invite-section",
    )


def MemoriesSection() -> FT:
    """Scattered polaroid wall — staggered drop-in entry, hover lift, heart burst."""
    imgs = [
        ("/static/images/memories/mem1.jpeg", "A Beautiful Beginning"),
        ("/static/images/memories/mem2.jpeg", "Our Journey"),
        ("/static/images/memories/mem3.jpeg", "Together Always"),
        ("/static/images/memories/mem4.jpeg", "True Love"),
        ("/static/images/memories/mem5.jpeg", "Forever Yours"),
    ]
    # Per-photo: (rotation, vertical-offset, stagger-delay)
    scatter = [
        ("-6deg", "8px",  "0s"),
        ( "4deg", "-6px", "0.15s"),
        ("-2deg", "14px", "0.3s"),
        ( "7deg", "-4px", "0.45s"),
        ("-5deg", "10px", "0.6s"),
    ]
    cells = [
        Div(
            Div(cls="polaroid-tape"),
            Div(cls="polaroid-pin"),
            Div(
                Img(src=src, alt=label, loading="lazy", cls="polaroid-img"),
                Div(cls="polaroid-shine"),
                Div(cls="polaroid-hearts"),
                cls="polaroid-frame",
            ),
            P(label, cls="polaroid-caption"),
            cls="polaroid mem-reveal js-lightbox",
            data_src=src,
            data_caption=label,
            style=f"--rot:{rot}; --yo:{yo}; --entry-delay:{delay};",
        )
        for (src, label), (rot, yo, delay) in zip(imgs, scatter)
    ]
    return Section(
        _section_petals(6, ['#CDB8EC','#F2C4CE','#A8DCC8','#F7C8A0','#A8CCEC']),
        Div(
            P(
                "Memories",
                cls="font-sans text-[10px] uppercase tracking-[0.5em] text-[#9070C0] mb-2 text-center scroll-reveal",
            ),
            P(
                "Moments We'll Cherish Forever",
                cls="font-serif text-3xl md:text-4xl text-[#5C4A5E] mb-2 text-center scroll-reveal sr-d1",
            ),
            P(
                "Tap a photo to open · Hover for love",
                cls="font-sans text-[10px] text-[#B090C0] tracking-[0.3em] uppercase text-center mb-12 scroll-reveal sr-d2",
            ),
            Div(*cells, cls="memories-board"),
            cls="max-w-5xl mx-auto px-6 py-16 section-inner",
        ),
        cls="bg-transparent relative section-canvas memories-section-canvas",
    )


def DressCodeSection() -> FT:
    """Cinematic fashion editorial lookbook — portrait cards with overlay text."""
    cards = [
        (
            "/static/images/dress_code/bd1.jpeg",
            "The Groom",
            "Suit & Tie",
            ["#1A2A4A", "#4A4A5A", "#C8C8D8"],
            "01",
        ),
        (
            "/static/images/dress_code/gd1.jpeg",
            "The Bride",
            "Wedding Gown",
            ["#F5ECD7", "#D4AF37", "#E8B4BC"],
            "02",
        ),
        (
            "/static/images/dress_code/gd2.jpeg",
            "Our Guests",
            "Cocktail Attire",
            ["#E8C8A0", "#A8DCC8", "#F2C4CE"],
            "03",
        ),
    ]
    card_els = []
    for i, (src, who, wear, palette_colors, num) in enumerate(cards):
        swatches = [
            Span(
                style=(
                    f"display:inline-block;width:13px;height:13px;"
                    f"border-radius:50%;background:{c};"
                    f"box-shadow:0 1px 4px rgba(0,0,0,0.3),"
                    f"inset 0 1px 1px rgba(255,255,255,0.25);"
                )
            )
            for c in palette_colors
        ]
        card_els.append(
            Div(
                # Gold corner bracket — top-left
                Div(
                    Span(cls="dc-cl dc-cl-h"),
                    Span(cls="dc-cl dc-cl-v"),
                    cls="dc-corner-tl",
                ),
                # Gold corner bracket — bottom-right (rotated 180°)
                Div(
                    Span(cls="dc-cl dc-cl-h"),
                    Span(cls="dc-cl dc-cl-v"),
                    cls="dc-corner-br",
                ),
                # Full-bleed photo
                Img(src=src, alt=f"{who} dress code", loading="lazy", cls="dc-photo"),
                # Cinematic gradient overlay
                Div(cls="dc-overlay"),
                # Sweep shimmer on hover
                Div(cls="dc-scan"),
                # Overlaid text info
                Div(
                    Span(num, cls="dc-num"),
                    P(who, cls="dc-who"),
                    Div(cls="dc-rule"),
                    P(wear, cls="dc-wear"),
                    Div(*swatches, cls="dc-swatches"),
                    cls="dc-info",
                ),
                cls=(
                    "dc-card js-lightbox scroll-reveal zoom-in js-tilt"
                    + (" dc-card-mid" if i == 1 else "")
                ),
                data_src=src,
                data_caption=f"{who} — {wear}",
            )
        )
    return Section(
        _section_petals(5, ['#F7C8A0', '#CDB8EC', '#A8DCC8', '#F2C4CE']),
        Div(
            P(
                "Dress Code",
                cls="font-sans text-[10px] uppercase tracking-[0.5em] text-[#C07840] mb-3 text-center scroll-reveal",
            ),
            P(
                "Look & Feel the Part",
                cls="font-serif text-3xl md:text-4xl text-[#6A3A28] mb-3 text-center scroll-reveal sr-d1",
            ),
            Div(
                Span(cls="block w-12 h-px bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent"),
                Span("✦", cls="text-[#D4AF37] text-xs mx-3 opacity-70"),
                Span(cls="block w-12 h-px bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent"),
                cls="flex items-center justify-center mb-4 scroll-reveal sr-d2",
            ),
            P(
                "Dress to impress — help set the scene for our most beautiful day",
                cls="font-sans text-[10px] italic text-[#B09090] tracking-widest text-center mb-14 scroll-reveal sr-d3",
            ),
            Div(*card_els, cls="dc-grid"),
            cls="max-w-4xl mx-auto px-6 py-16 section-inner",
        ),
        cls="bg-transparent relative section-canvas",
    )

def _nav_cd_unit(el_id: str, label: str) -> FT:
    """Countdown unit specifically for the white-text sticky navbar."""
    return Div(
        Span(
            "00",
            id=el_id,
            style=(
                "display:block;font-family:serif;font-size:1.6rem;line-height:1;"
                "color:#ffffff;font-weight:600;letter-spacing:0.04em;"
                "text-shadow:0 0 12px rgba(255,200,230,0.8),0 0 4px rgba(255,255,255,0.6);"
                "tabular-nums;"
            ),
        ),
        Span(
            label,
            style=(
                "display:block;font-family:sans-serif;font-size:0.6rem;"
                "text-transform:uppercase;letter-spacing:0.25em;"
                "color:rgba(255,220,235,0.85);margin-top:2px;"
            ),
        ),
        style="text-align:center;min-width:44px;",
    )


def CountdownNavbar() -> FT:
    """Sticky bottom artistic countdown bar — always visible, fully white text."""
    colon = Span(
        ":",
        style=(
            "font-family:serif;font-size:1.3rem;color:rgba(255,200,230,0.7);"
            "align-self:flex-start;margin-top:3px;margin-left:2px;margin-right:2px;"
        ),
    )
    return Div(
        # Shimmer top border
        Div(style=(
            "position:absolute;top:0;left:0;right:0;height:1px;"
            "background:linear-gradient(90deg,transparent,rgba(255,200,230,0.6),rgba(255,240,200,0.8),"
            "rgba(255,200,230,0.6),transparent);"
        )),
        # Content row
        Div(
            # Left: ring icon + label
            Div(
                Div(
                    "💍",
                    style="font-size:1.1rem;line-height:1;margin-bottom:2px;filter:drop-shadow(0 0 6px rgba(255,200,230,0.9));",
                ),
                Div(
                    "Until We Say I Do",
                    style=(
                        "font-family:sans-serif;font-size:0.58rem;text-transform:uppercase;"
                        "letter-spacing:0.3em;color:rgba(255,220,235,0.9);"
                    ),
                ),
                style="display:none;flex-direction:column;align-items:center;margin-right:1.1rem;",
                id="cd-left-label",
            ),
            # Vertical divider
            Div(style="width:1px;height:2rem;background:rgba(255,200,230,0.25);margin-right:1.1rem;display:none;",
                id="cd-divider-l"),
            # Countdown digits
            Div(
                _nav_cd_unit("cd-days",  "Days"),
                colon,
                _nav_cd_unit("cd-hours", "Hrs"),
                colon,
                _nav_cd_unit("cd-mins",  "Min"),
                colon,
                _nav_cd_unit("cd-secs",  "Sec"),
                style="display:flex;align-items:flex-start;gap:2px;",
            ),
            # Right divider + date
            Div(
                Div(style="width:1px;height:2rem;background:rgba(255,200,230,0.25);margin-left:1.1rem;margin-right:1.1rem;"),
                Div(
                    Div(
                        "🌸 Aug 24",
                        style=(
                            "font-family:serif;font-size:0.85rem;color:#ffffff;"
                            "font-weight:600;line-height:1;"
                            "text-shadow:0 0 8px rgba(255,180,210,0.7);"
                        ),
                    ),
                    Div(
                        "2026",
                        style=(
                            "font-family:sans-serif;font-size:0.55rem;text-transform:uppercase;"
                            "letter-spacing:0.3em;color:rgba(255,220,235,0.75);margin-top:2px;"
                        ),
                    ),
                    style="text-align:center;",
                ),
                style="display:none;align-items:center;",
                id="cd-right-block",
            ),
            style="display:flex;align-items:center;justify-content:center;",
        ),
        # Show hidden elements on sm+ via JS
        Script("""
(function(){
  var mq = window.matchMedia('(min-width:640px)');
  function applyMq(e){
    var show=e.matches?'flex':'none';
    ['cd-left-label','cd-divider-l','cd-right-block'].forEach(function(id){
      var el=document.getElementById(id);
      if(el) el.style.display=show;
    });
  }
  applyMq(mq);
  mq.addEventListener('change',applyMq);
})();
"""),
        _COUNTDOWN_JS,
        id="countdown-bar",
        style=(
            "position:fixed;bottom:0;left:0;right:0;z-index:8000;"
            "padding:0.65rem 1.5rem;"
            "background:linear-gradient(105deg,"
            "rgba(60,20,80,0.88) 0%,"
            "rgba(130,40,100,0.88) 35%,"
            "rgba(180,60,120,0.88) 60%,"
            "rgba(60,20,80,0.88) 100%);"
            "backdrop-filter:blur(20px);"
            "-webkit-backdrop-filter:blur(20px);"
            "box-shadow:0 -6px 40px rgba(150,50,120,0.35),0 -1px 0 rgba(255,200,230,0.12);"
            "overflow:hidden;"
        ),
    )



def InteractiveEffects() -> FT:
    """Global JS: cursor flower trail, click burst, 3D tilt, lightbox, venue parallax."""
    return Script("""
(function(){
  // ── Cursor flower trail ──────────────────────────────────
  var trailEmojis = ['🌸','✿','🌺','🌹','💮','✦'];
  var lastTrail = 0;
  document.addEventListener('mousemove', function(e){
    var now = Date.now();
    if(now - lastTrail < 80) return;
    lastTrail = now;
    var el = document.createElement('span');
    el.className = 'cursor-petal';
    el.textContent = trailEmojis[Math.floor(Math.random()*trailEmojis.length)];
    el.style.left = e.clientX + 'px';
    el.style.top  = e.clientY + 'px';
    el.style.setProperty('--cx', (Math.random()*60-30)+'px');
    el.style.setProperty('--cy', (Math.random()*-60-20)+'px');
    el.style.setProperty('--cr', (Math.random()*360)+'deg');
    document.body.appendChild(el);
    setTimeout(function(){ el.remove(); }, 1050);
  }, {passive:true});

  // ── Click heart burst ────────────────────────────────────
  var burstEmojis = ['♡','🌸','✦','💗','🌺','✿','💕'];
  document.addEventListener('click', function(e){
    if(e.target.closest('#book-overlay') || e.target.closest('.dc-card') || e.target.closest('.polaroid')) return;
    var count = 7;
    for(var i=0;i<count;i++){
      (function(idx){
        setTimeout(function(){
          var el = document.createElement('span');
          el.className = 'click-burst';
          el.textContent = burstEmojis[Math.floor(Math.random()*burstEmojis.length)];
          el.style.left = e.clientX + 'px';
          el.style.top  = e.clientY + 'px';
          var angle = (360/count * idx) * Math.PI / 180;
          var dist  = 50 + Math.random()*50;
          el.style.setProperty('--bx', (Math.cos(angle)*dist)+'px');
          el.style.setProperty('--by', (Math.sin(angle)*dist - 40)+'px');
          el.style.setProperty('--br', (Math.random()*360)+'deg');
          document.body.appendChild(el);
          setTimeout(function(){ el.remove(); }, 1200);
        }, idx * 35);
      })(i);
    }
  });

  // ── 3D Tilt on .js-tilt ──────────────────────────────────
  document.querySelectorAll('.js-tilt').forEach(function(card){
    card.addEventListener('mousemove', function(e){
      var r = card.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width  - 0.5;
      var y = (e.clientY - r.top)  / r.height - 0.5;
      card.style.transform = 'rotateY('+(x*18)+'deg) rotateX('+(-y*12)+'deg) scale(1.03)';
    });
    card.addEventListener('mouseleave', function(){
      card.style.transform = 'rotateY(0) rotateX(0) scale(1)';
      card.style.transition = 'transform 0.6s ease';
    });
    card.addEventListener('mouseenter', function(){
      card.style.transition = 'transform 0.1s ease';
    });
  });

  // ── Tilt on gallery cards ────────────────────────────────
  document.querySelectorAll('.tilt-card').forEach(function(card){
    card.addEventListener('mousemove', function(e){
      var r = card.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width  - 0.5;
      var y = (e.clientY - r.top)  / r.height - 0.5;
      card.style.transform = 'rotateY('+(x*20)+'deg) rotateX('+(-y*14)+'deg) translateZ(8px)';
    });
    card.addEventListener('mouseleave', function(){
      card.style.transform = 'rotateY(0) rotateX(0) translateZ(0)';
      card.style.transition = 'transform 0.5s ease';
    });
    card.addEventListener('mouseenter', function(){
      card.style.transition = 'transform 0.08s ease';
    });
  });

  // ── Venue parallax bg ────────────────────────────────────
  var venueBg = document.querySelector('.js-parallax-bg');
  if(venueBg){
    window.addEventListener('scroll', function(){
      var section = venueBg.parentElement;
      var rect = section.getBoundingClientRect();
      if(rect.bottom < 0 || rect.top > window.innerHeight) return;
      var prog = 1 - (rect.top + rect.height/2) / window.innerHeight;
      venueBg.style.transform = 'translateY('+(prog*40-20)+'px) scale(1.12)';
    }, {passive:true});
  }

  // ── Lightbox ─────────────────────────────────────────────
  var lb = document.getElementById('lightbox');
  var lbClose = document.getElementById('lightbox-close');
  var lbWrap = document.getElementById('lightbox-img-wrap');
  function openLightbox(src) {
    lbWrap.innerHTML = '<img src="'+src+'" alt="Photo"/>';
    lb.setAttribute('aria-hidden','false');
    lb.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeLightbox() {
    lb.classList.remove('open');
    lb.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
    setTimeout(function(){ lbWrap.innerHTML=''; }, 360);
  }
  if(lbClose) lbClose.addEventListener('click', closeLightbox);
  if(lb) lb.addEventListener('click', function(e){ if(e.target === lb) closeLightbox(); });
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeLightbox(); });

  document.querySelectorAll('.js-lightbox').forEach(function(el){
    el.addEventListener('click', function(){
      var src = el.dataset.src;
      if(src) openLightbox(src);
    });
  });

  // ── Polaroid heart burst on hover ────────────────────────
  var heartEmojis = ['♡','💗','🌸','💕','✦','🌺'];
  document.querySelectorAll('.polaroid').forEach(function(card){
    card.addEventListener('mouseenter', function(){
      var container = card.querySelector('.polaroid-hearts');
      if(!container) return;
      for(var i=0;i<5;i++){
        (function(idx){
          setTimeout(function(){
            var h = document.createElement('span');
            h.className = 'mem-heart';
            h.textContent = heartEmojis[Math.floor(Math.random()*heartEmojis.length)];
            h.style.left  = (15 + Math.random()*70) + '%';
            h.style.bottom = (8 + Math.random()*18) + 'px';
            h.style.animationDelay = (idx * 0.1) + 's';
            container.appendChild(h);
            setTimeout(function(){ h.remove(); }, 1600);
          }, idx * 80);
        })(i);
      }
    });
  });

})();
""")


def _section_separator() -> FT:
    return Div(
        _ornament(),
        cls="flex justify-center items-center py-12 md:py-16 opacity-60 w-full relative z-10"
    )

def InvitePage(guest: dict) -> FT:
    return (
        Title(f"You're Invited · {guest['name']}"),
        Main(
            TopMarqueeBanner(),
            BookOpeningOverlay(name=guest["name"]),
            Div(InviteHero(name=guest["name"]), cls="invite-section"),
            _section_separator(),
            Div(InviteDetails(), cls="invite-section"),
            
            Div(VenueSection(), cls="invite-section"),
            _section_separator(),
            Div(MemoriesSection(), cls="invite-section"),
            _section_separator(),
            Div(DressCodeSection(), cls="invite-section"),
            _section_separator(),
            Div(PersonalMessage(guest), cls="invite-section"),
            _section_separator(),
            Div(AttendanceSection(guest), cls="invite-section"),
            Div(InviteFooter(), cls="invite-section"),
        ),
        _lightbox(),
        CountdownNavbar(),
        MusicPlayer(),
        WeddingEffects(),
        InteractiveEffects(),
        Script("lucide.createIcons();"),
    )


# ---------------------------------------------------------------------------
# Admin Dashboard Components
# ---------------------------------------------------------------------------

def StatusBadge(status: str) -> FT:
    style, icon = RSVP_STATUS_STYLES.get(status, RSVP_STATUS_STYLES["pending"])
    return Span(
        I(data_lucide=icon, cls="w-3 h-3 mr-1 inline"),
        status.capitalize(),
        cls=f"inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {style}",
    )


def CategoryBadge(category: str) -> FT:
    style = CATEGORY_STYLES.get(category, CATEGORY_STYLES["General"])
    return Span(
        category,
        cls=f"inline-flex px-2 py-0.5 rounded-full text-xs font-medium {style}",
    )


def WhatsAppButton(guest: dict) -> FT:
    first_name = guest["name"].split()[0]
    invite_url = f"{BASE_URL}/invite/{guest['slug']}"
    custom = guest.get("custom_message")
    if custom:
        msg = f"Hi {first_name}! 💌 {custom}\n\nYour personal wedding invitation: {invite_url}"
    else:
        msg = (
            f"Hi {first_name}! 🎊 Your personalized wedding invitation from Nikolai & Valentina "
            f"is ready. Tap to open: {invite_url}"
        )
    phone = format_phone(guest.get("phone", ""))
    wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
    return A(
        I(data_lucide="message-circle", cls="w-4 h-4"),
        href=wa_url,
        target="_blank",
        cls=(
            "inline-flex items-center justify-center w-8 h-8 rounded-lg "
            "bg-green-50 text-green-600 hover:bg-green-100 transition-colors"
        ),
        title="Send via WhatsApp",
    )


def OpenedAt(ts) -> FT:
    if ts is None:
        return Span("Not opened", cls="text-xs text-[#D4B8B0] italic")
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts)
        except ValueError:
            return Span(ts, cls="text-xs text-[#B09090]")
    return Span(
        ts.strftime("%b %d, %Y %H:%M"),
        cls="text-xs text-[#B09090]",
    )


def SharePanel(guest: dict) -> FT:
    """Full-width share row inserted below the guest row via HTMX."""
    slug      = guest["slug"]
    first     = guest["name"].split()[0]
    url       = f"{BASE_URL}/invite/{slug}"
    custom    = guest.get("custom_message") or ""
    wa_text   = f"Hi {first}! 💌 {custom}\n\nYour personal wedding invitation: {url}" if custom else \
                f"Hi {first}! 🎊 Your personalized wedding invitation is ready. Tap to open: {url}"

    copy_btn = Button(
        I(data_lucide="copy", cls="w-4 h-4 mr-2"),
        Span("Copy Link", cls="text-sm font-medium"),
        type="button",
        onclick=f"navigator.clipboard.writeText('{url}');this.querySelector('span').textContent='✓ Copied!';setTimeout(()=>this.querySelector('span').textContent='Copy Link',2000)",
        cls=(
            "inline-flex items-center px-4 py-2.5 rounded-xl "
            "bg-[#F5EEEA] hover:bg-[#EAD8D0] text-[#6A5A5A] transition-colors cursor-pointer"
        ),
    )

    return Tr(
        Td(
            Div(
                # URL display
                Div(
                    Span(guest["name"], cls="text-xs font-semibold text-[#B09090] uppercase tracking-wider mr-2"),
                    Span("Personalized invite link:", cls="text-xs text-[#C0A8A8]"),
                    cls="flex items-center mb-2",
                ),
                Div(
                    Input(
                        type="text", value=url, readonly=True,
                        cls=(
                            "flex-1 px-3 py-2 text-sm rounded-lg border border-[#E8D8D0] "
                            "bg-[#FDF8F5] text-[#8C7070] font-mono select-all cursor-text"
                        ),
                        onclick="this.select()",
                    ),
                    cls="flex gap-2 mb-4",
                ),
                Div(copy_btn, cls="flex"),
                # Close
                Div(
                    Button(
                        I(data_lucide="x", cls="w-3.5 h-3.5 mr-1"), "Close",
                        cls=(
                            "inline-flex items-center text-xs text-[#C0A8A8] "
                            "hover:text-[#8C7070] transition-colors mt-3"
                        ),
                        hx_get=f"/admin/guests/{slug}/row",
                        hx_target="closest tr",
                        hx_swap="outerHTML",
                    ),
                    cls="flex justify-end",
                ),
                cls="p-4",
            ),
            colspan="6",
            cls="bg-[#FAF3F0] border-b border-[#E8D8D0] px-4",
        ),
        id=f"guest-row-{slug}",
    )


def _icon_btn(icon: str, title: str, cls_extra: str, **attrs) -> FT:
    return Button(
        I(data_lucide=icon, cls="w-3.5 h-3.5"),
        title=title,
        cls=(
            "inline-flex items-center justify-center w-7 h-7 rounded-lg "
            f"transition-colors {cls_extra}"
        ),
        **attrs,
    )


def AdminRow(guest: dict) -> FT:
    slug = guest["slug"]

    actions = Div(
        # Preview — opens invite in new tab
        A(
            I(data_lucide="eye", cls="w-3.5 h-3.5"),
            href=f"/invite/{slug}",
            target="_blank",
            title="Preview invite",
            cls=(
                "inline-flex items-center justify-center w-7 h-7 rounded-lg "
                "bg-[#FDF8F5] text-[#B09090] hover:bg-[#F5EEEA] transition-colors"
            ),
        ),
        # Share — expands platform panel below row
        _icon_btn(
            "share-2", "Share invite link",
            "bg-[#D4AF37]/10 text-[#B8960C] hover:bg-[#D4AF37]/20",
            hx_get=f"/admin/guests/{slug}/share",
            hx_target="closest tr",
            hx_swap="outerHTML",
        ),
        # Edit — swap row with edit form
        _icon_btn(
            "pencil", "Edit guest",
            "bg-[#D4AF37]/10 text-[#B8960C] hover:bg-[#D4AF37]/25",
            hx_get=f"/admin/guests/{slug}/edit-form",
            hx_target="closest tr",
            hx_swap="outerHTML",
        ),
        # Delete
        _icon_btn(
            "trash-2", "Delete guest",
            "bg-[#F2C4CE]/40 text-[#C4687A] hover:bg-[#F2C4CE]/70",
            hx_delete=f"/admin/guests/{slug}",
            hx_target="closest tr",
            hx_swap="outerHTML swap:300ms",
            hx_confirm=f"Remove {guest['name']} from the guest list?",
        ),
        cls="flex items-center gap-1.5",
    )

    has_custom = bool(guest.get("custom_message"))
    return Tr(
        Td(
            P(guest["name"], cls="font-medium text-[#5C4A4A] text-sm"),
            P(guest.get("phone", "—"), cls="text-xs text-[#C0A8A8] mt-0.5"),
            cls="px-4 py-3",
        ),
        Td(
            CategoryBadge(guest["category"]),
            Span("✎ custom msg", cls="ml-2 text-[10px] text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded-full") if has_custom else "",
            cls="px-4 py-3",
        ),
        Td(StatusBadge(guest["rsvp_status"]), cls="px-4 py-3"),
        Td(
            "✓" if guest["plus_one"] else "—",
            cls="px-4 py-3 text-sm text-[#B09090] text-center",
        ),
        Td(OpenedAt(guest.get("opened_at")), cls="px-4 py-3"),
        Td(actions, cls="px-4 py-3"),
        id=f"guest-row-{slug}",
        data_rsvp=guest["rsvp_status"],
        cls="border-b border-[#F0E8E4] hover:bg-[#FEF6F3] transition-colors",
    )


def EditGuestRow(guest: dict) -> FT:
    slug = guest["slug"]
    input_cls = (
        "w-full px-2 py-1 rounded border border-[#E8D8D0] text-[#5C4A4A] text-sm"
        "focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37]"
    )
    select_cls = input_cls + " bg-white"
    category_default = CATEGORY_MESSAGES.get(guest["category"], CATEGORY_MESSAGES["General"])
    # Build JS map of all category defaults for live textarea update
    cat_map_js = "{" + ",".join(
        f'"{k}": {repr(v)}' for k, v in CATEGORY_MESSAGES.items()
    ) + "}"
    textarea_id = f"msg-{slug}"
    select_id   = f"cat-{slug}"
    return Tr(
        # Col 1: name
        Td(
            Input(type="text", name="name", value=guest["name"],
                  required=True, cls=input_cls, form=f"edit-{slug}"),
            Input(type="hidden", name="phone", value=guest.get("phone", ""),
                  form=f"edit-{slug}"),
            cls="px-4 py-3",
        ),
        # Col 2: category — updates textarea on change
        Td(
            Select(
                Option("General", value="General", selected=guest["category"] == "General"),
                Option("Family",  value="Family",  selected=guest["category"] == "Family"),
                Option("Friends", value="Friends", selected=guest["category"] == "Friends"),
                Option("VIP",     value="VIP",     selected=guest["category"] == "VIP"),
                Option("Work",    value="Work",    selected=guest["category"] == "Work"),
                name="category", id=select_id, cls=select_cls, form=f"edit-{slug}",
                onchange=(
                    f"(function(){{var m={cat_map_js};"
                    f"var ta=document.getElementById('{textarea_id}');"
                    f"ta.value=m[this.value]||'';}}).call(this)"
                ),
            ),
            cls="px-4 py-3",
        ),
        # Col 3: personal message — pre-filled with category default
        Td(
            P("Personal message (shown on their invite):",
              cls="text-xs text-[#C0A8A8] mb-1"),
            Textarea(
                guest.get("custom_message") or category_default,
                name="custom_message",
                id=textarea_id,
                rows="3",
                cls=f"{input_cls} resize-none",
                form=f"edit-{slug}",
            ),
            colspan="3",
            cls="px-4 py-3",
        ),
        # Col 6: save/cancel
        Td(
            Form(
                Button(
                    I(data_lucide="check", cls="w-3.5 h-3.5 mr-1"), "Save",
                    type="submit",
                    cls=(
                        "inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold "
                        "bg-[#D4AF37] text-[#0A0A0A] hover:bg-amber-400 transition-colors"
                    ),
                ),
                Button(
                    "Cancel",
                    type="button",
                    cls=(
                        "inline-flex items-center px-3 py-1 rounded-lg text-xs "
                        "bg-[#F5EEEA] text-[#8C7070] hover:bg-[#E8D8D0] transition-colors"
                    ),
                    hx_get=f"/admin/guests/{slug}/row",
                    hx_target="closest tr",
                    hx_swap="outerHTML",
                ),
                id=f"edit-{slug}",
                hx_post=f"/admin/guests/{slug}/edit",
                hx_target="closest tr",
                hx_swap="outerHTML",
                cls="flex flex-col gap-2",
            ),
            cls="px-4 py-3",
        ),
        id=f"guest-row-{slug}",
        cls="border-b border-amber-100 bg-amber-50/40",
    )


def AdminResponsePanel(guest: dict, songs: list[dict]) -> FT:
    slug = guest["slug"]
    status = guest["rsvp_status"]
    is_attending = status == "attending"

    status_color = "#22A05A" if is_attending else "#C4687A"
    status_label = "✓ Attending" if is_attending else "✗ Declined"

    def _row(label, value):
        if not value:
            return None
        return Div(
            Span(label, cls="text-xs text-[#B09090] uppercase tracking-wider w-28 shrink-0"),
            Span(value, cls="text-sm text-[#5C4A4A]"),
            cls="flex gap-3 items-start py-1.5 border-b border-[#F0E8E4] last:border-0",
        )

    details = [
        _row("Status", status_label),
        _row("Guest count", guest.get("guest_count")),
        _row("Dietary", guest.get("dietary")),
        _row("Notes", guest.get("special_notes")),
    ]
    details = [d for d in details if d is not None]

    song_items = []
    for s in songs:
        song_items.append(
            Div(
                Span(f"🎵 {s['song']}", cls="text-sm font-medium text-[#5C4A4A]"),
                Span(f" — {s['artist']}", cls="text-sm text-[#A08080]"),
                Span(f'  "{s["dedication"]}"', cls="text-xs text-[#B09090] block mt-0.5") if s.get("dedication") else "",
            )
        )

    return Tr(
        Td(
            Div(
                Div(
                    Div(
                        Span(guest["name"], cls="text-xs font-semibold text-[#B09090] uppercase tracking-wider"),
                        Span(" · Response Details", cls="text-xs text-[#C0A8A8]"),
                        cls="flex items-center mb-3",
                    ),
                    Div(
                        Div(
                            status_label,
                            style=f"display:inline-block;padding:.3rem .85rem;border-radius:2rem;"
                                  f"background:{'#EDFBF3' if is_attending else '#FFF0F3'};"
                                  f"color:{status_color};font-size:.8rem;font-weight:600;"
                                  f"margin-bottom:.75rem;",
                        ),
                        *details,
                        cls="mb-3",
                    ) if details else "",
                    Div(
                        P("Song Request", cls="text-xs text-[#B09090] uppercase tracking-wider mb-2"),
                        *song_items,
                        cls="mt-2",
                    ) if song_items else "",
                    cls="flex-1",
                ),
                Div(
                    Button(
                        I(data_lucide="x", cls="w-3.5 h-3.5 mr-1"), "Close",
                        cls="inline-flex items-center text-xs text-[#C0A8A8] hover:text-[#8C7070] transition-colors",
                        onclick="this.closest('tr').remove()",
                        type="button",
                    ),
                    cls="flex justify-end pt-1",
                ),
                cls="p-4",
            ),
            colspan="6",
            cls="bg-[#F7F2EF] border-b border-[#E8D8D0]",
        ),
        id=f"response-row-{slug}",
    )


def GuestTable(guests: list[dict]) -> FT:
    rows = [AdminRow(g) for g in guests] if guests else [
        Tr(
            Td(
                "No guests yet. Add your first guest above.",
                colspan="6",
                cls="text-center text-[#C0A8A8] text-sm py-12",
            )
        )
    ]
    attending = sum(1 for g in guests if g["rsvp_status"] == "attending")
    pending   = sum(1 for g in guests if g["rsvp_status"] == "pending")
    declined  = sum(1 for g in guests if g["rsvp_status"] == "declined")

    # Filter tabs
    filter_tabs = Div(
        Button("All", onclick="filterGuests('all')",   id="tab-all",      cls="tab-btn tab-active"),
        Button("✓ Attending", onclick="filterGuests('attending')", id="tab-attending", cls="tab-btn"),
        Button("✗ Declined",  onclick="filterGuests('declined')",  id="tab-declined",  cls="tab-btn"),
        Button("⏳ Pending",   onclick="filterGuests('pending')",   id="tab-pending",   cls="tab-btn"),
        cls="flex gap-2 mb-4 flex-wrap",
    )

    filter_js = Script("""
function filterGuests(status) {
    document.querySelectorAll('#guest-table tr').forEach(function(tr) {
        var badge = tr.querySelector('[data-rsvp]');
        if (!badge) return;
        tr.style.display = (status === 'all' || badge.dataset.rsvp === status) ? '' : 'none';
    });
    document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('tab-active'); });
    document.getElementById('tab-' + status).classList.add('tab-active');
}
""")

    tab_css = Style("""
.tab-btn {
    padding: .4rem 1rem; border-radius: .65rem; border: 1.5px solid #E8D8D0;
    background: white; color: #A89090; font-size: .75rem; font-family: sans-serif;
    cursor: pointer; transition: all .15s;
}
.tab-btn:hover { background: #FAF3F0; }
.tab-btn.tab-active { background: #5C4A4A; color: white; border-color: #5C4A4A; }
""")

    return Div(
        tab_css,
        filter_js,
        # Stats bar
        Div(
            _stat("Users", str(len(guests)), "Total Guests"),
            _stat("CheckCircle", str(attending), "Attending"),
            _stat("Clock", str(pending), "Pending"),
            _stat("XCircle", str(declined), "Declined"),
            cls="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6",
        ),
        filter_tabs,
        # Table
        Div(
            Table(
                Thead(
                    Tr(
                        *[
                            Th(h, cls="px-4 py-3 text-left text-xs font-semibold text-[#B09090] uppercase tracking-wider")
                            for h in ["Guest", "Category", "RSVP", "+1", "Opened", "Actions"]
                        ],
                        cls="bg-[#FAF3F0] border-b border-[#E8D8D0]",
                    )
                ),
                Tbody(*rows, id="guest-table"),
                cls="w-full",
            ),
            cls="overflow-x-auto rounded-xl border border-[#E8D8D0] bg-white shadow-[0_2px_12px_rgba(92,74,74,0.06)]",
        ),
    )


def _stat(icon: str, value: str, label: str) -> FT:
    return Div(
        Div(
            I(data_lucide=icon, cls="w-5 h-5 text-[#D4AF37]"),
            cls="mb-2",
        ),
        P(value, cls="font-serif text-3xl text-[#5C4A4A]"),
        P(label, cls="text-xs text-[#B09090] uppercase tracking-wider mt-0.5"),
        cls="bg-white rounded-xl border border-[#E8D8D0] px-5 py-4 shadow-[0_2px_12px_rgba(92,74,74,0.06)]",
    )


def AddGuestForm() -> FT:
    return Form(
        Div(
            Input(
                type="text", name="name", placeholder="Full Name",
                required=True,
                cls=(
                    "w-full px-4 py-2.5 rounded-lg border border-[#E8D8D0] text-[#5C4A4A] text-sm"
                    "focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37] "
                    "transition-colors"
                ),
            ),
            Input(type="hidden", name="phone", value=""),
            Select(
                Option("General", value="General"),
                Option("Family",  value="Family"),
                Option("Friends", value="Friends"),
                Option("VIP",     value="VIP"),
                Option("Work",    value="Work"),
                name="category",
                cls=(
                    "w-full px-4 py-2.5 rounded-lg border border-[#E8D8D0] text-[#5C4A4A] text-sm"
                    "focus:outline-none focus:border-[#D4AF37] bg-white "
                    "transition-colors"
                ),
            ),
            Button(
                I(data_lucide="user-plus", cls="w-4 h-4 mr-2"),
                "Add Guest",
                type="submit",
                cls=(
                    "inline-flex items-center px-5 py-2.5 bg-[#D4AF37] text-[#0A0A0A] "
                    "rounded-lg text-sm font-semibold hover:bg-amber-400 "
                    "transition-colors active:scale-95"
                ),
            ),
            cls="flex flex-wrap gap-3 items-end",
        ),
        hx_post="/admin/guests",
        hx_target="#guest-table",
        hx_swap="afterbegin",
        hx_on__after_request="this.reset()",
    )


def ReservationsPanel(reservations: list[dict]) -> FT:
    if not reservations:
        return Div(
            P("No responses yet.",
              cls="text-sm text-[#C0A8A8] italic text-center py-8"),
        )

    attending = [r for r in reservations if r["rsvp_status"] == "attending"]
    declined  = [r for r in reservations if r["rsvp_status"] == "declined"]

    def _detail(label, value):
        if not value:
            return None
        return Div(
            Span(label, cls="text-[10px] text-[#B09090] uppercase tracking-wider"),
            Span(value, cls="text-xs text-[#6A5A5A] mt-0.5 block"),
            cls="flex flex-col",
        )

    def _card(r):
        is_att = r["rsvp_status"] == "attending"
        details = [
            _detail("Seats", r.get("guest_count")),
            _detail("Dietary", r.get("dietary")),
            _detail("Notes", r.get("special_notes")),
        ]
        details = [d for d in details if d is not None]
        return Div(
            Div(
                Div(
                    P(r["name"], cls="font-medium text-[#5C4A4A] text-sm"),
                    CategoryBadge(r["category"]),
                    cls="flex items-center gap-2 mb-2",
                ),
                Span(
                    "✓ Attending" if is_att else "✗ Declined",
                    cls=(
                        "inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full "
                        + ("bg-[#EDFBF3] text-[#22A05A]" if is_att else "bg-[#FFF0F3] text-[#C4687A]")
                    ),
                ),
            ),
            Div(*details, cls="flex flex-wrap gap-4 mt-3") if details else "",
            cls=(
                "bg-white rounded-xl border px-4 py-3 shadow-[0_1px_6px_rgba(92,74,74,0.07)] "
                + ("border-[#C8EDD8]" if is_att else "border-[#F2C4CE]")
            ),
        )

    cards_att = [_card(r) for r in attending]
    cards_dec = [_card(r) for r in declined]

    sections = []
    if cards_att:
        sections.append(Div(
            P(f"✓ Attending ({len(attending)})",
              cls="text-xs font-semibold text-[#22A05A] uppercase tracking-wider mb-3"),
            Div(*cards_att, cls="grid grid-cols-1 md:grid-cols-2 gap-3"),
        ))
    if cards_dec:
        sections.append(Div(
            P(f"✗ Declined ({len(declined)})",
              cls="text-xs font-semibold text-[#C4687A] uppercase tracking-wider mb-3 mt-5"),
            Div(*cards_dec, cls="grid grid-cols-1 md:grid-cols-2 gap-3"),
        ))

    return Div(*sections)


def SongRequestsPanel(songs: list[dict]) -> FT:
    if not songs:
        return Div(
            P("No song requests yet.",
              cls="text-sm text-[#C0A8A8] italic text-center py-8"),
        )
    rows = []
    for s in songs:
        submitted = ""
        if s.get("submitted_at"):
            ts = s["submitted_at"]
            if hasattr(ts, "strftime"):
                submitted = ts.strftime("%b %d, %H:%M")
        rows.append(Tr(
            Td(
                P(s.get("name") or "Unknown", cls="font-medium text-[#5C4A4A] text-sm"),
                P(submitted, cls="text-xs text-[#C0A8A8]"),
                cls="px-4 py-3",
            ),
            Td(
                P(s["song"], cls="text-sm font-medium text-[#6A5A5A]"),
                P(f"by {s['artist']}", cls="text-xs text-[#C0A8A8]"),
                cls="px-4 py-3",
            ),
            Td(s.get("dedication") or "—", cls="px-4 py-3 text-sm text-[#B09090] max-w-xs"),
            cls="border-b border-[#F0E8E4] hover:bg-[#FEF6F3]",
        ))
    return Div(
        Table(
            Thead(Tr(
                *[Th(h, cls="px-4 py-3 text-left text-xs font-semibold text-[#B09090] uppercase tracking-wider")
                  for h in ["Requested By", "Song", "Dedication"]],
                cls="bg-[#FAF3F0] border-b border-[#E8D8D0]",
            )),
            Tbody(*rows),
            cls="w-full",
        ),
        cls="overflow-x-auto rounded-xl border border-[#E8D8D0] bg-white shadow-[0_2px_12px_rgba(92,74,74,0.06)]",
    )


def AdminPage(guests: list[dict], reservations: list[dict] = None, songs: list[dict] = None) -> FT:
    reservations = reservations or []
    songs = songs or []
    return (
        Title("Admin · Winvite"),
        Main(
            # Header
            Div(
                Div(
                    H1("Admin Dashboard", cls="font-serif text-3xl text-[#5C4A4A]"),
                    P("Manage your guest list and send personalized invitations.",
                      cls="text-sm text-[#B09090] mt-1"),
                    cls="flex-1",
                ),
                Div(I(data_lucide="heart", cls="w-8 h-8 text-[#D4AF37]"), cls="flex items-center"),
                cls="flex items-start justify-between mb-8",
            ),
            # Add guest
            Div(
                H2("Add Guest", cls="text-sm font-semibold text-[#B09090] uppercase tracking-wider mb-3"),
                AddGuestForm(),
                cls="bg-white border border-[#E8D8D0] rounded-xl p-5 mb-8 shadow-[0_2px_12px_rgba(92,74,74,0.06)]",
            ),
            # Guest table
            GuestTable(guests),
            # Reservations
            Div(
                Div(
                    I(data_lucide="calendar-check", cls="w-5 h-5 text-[#D4AF37] mr-2"),
                    H2(f"Reservation Responses ({len(reservations)})",
                       cls="text-base font-semibold text-[#5C4A4A]"),
                    cls="flex items-center mb-4",
                ),
                ReservationsPanel(reservations),
                cls="mt-10",
            ),
            # Song requests
            Div(
                Div(
                    I(data_lucide="music", cls="w-5 h-5 text-[#D4AF37] mr-2"),
                    H2(f"Song Requests ({len(songs)})",
                       cls="text-base font-semibold text-[#5C4A4A]"),
                    cls="flex items-center mb-4",
                ),
                SongRequestsPanel(songs),
                cls="mt-10 mb-16",
            ),
            cls="max-w-5xl mx-auto px-4 py-10",
            style="background:#FDF8F5;min-height:100vh;",
        ),
        Script("lucide.createIcons();"),
    )


def NewGuestRow(guest: dict) -> FT:
    """Partial response: single <tr> to prepend into #guest-table via HTMX."""
    return (
        AdminRow(guest),
        Script("lucide.createIcons();"),
    )


# ---------------------------------------------------------------------------
# Public landing / preview page (no personalization, reuses invite components)
# ---------------------------------------------------------------------------

def TopMarqueeBanner() -> FT:
    """Animated, artistic moving banner at the very top of the invitation."""
    anim_css = Style("""
    .marquee-container { overflow: hidden; white-space: nowrap; width: 100%; border-bottom: 1px solid rgba(255,255,255,0.1); }
    .marquee-content { display: inline-block; animation: marquee 60s linear infinite; }
    .marquee-content span { padding-right: 2.5rem; }
    @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
    """)
    msg = "✧ PARTY: AUGUST 24, 2026 ✧ LOCATION: EJE CAFETERO (COFFEE TRIANGLE) ✧ ADDRESS: FINCA HOTEL NUEVO FUTURO ✧"
    
    return Div(
        anim_css,
        Div(
            Span(msg), Span(msg), Span(msg), Span(msg),
            Span(msg), Span(msg), Span(msg), Span(msg),
            cls="marquee-content",
        ),
        cls="marquee-container sticky top-0 w-full bg-[#5C4A5E] text-[#FADADD] font-sans text-[9px] md:text-[11px] tracking-[0.35em] uppercase py-2 md:py-2.5 z-[8900] shadow-[0_4px_20px_rgba(92,74,94,0.3)]",
    )

def InvitationQuoteSection() -> FT:
    """Dramatic full-bleed cinematic quote proclamation section."""
    return Section(
        # Scattered gold glint sparkles in corners
        Span(cls="iq-glint", style="--gx:8%;--gy:25%;--gd:0s;--gs:0.8"),
        Span(cls="iq-glint", style="--gx:92%;--gy:20%;--gd:1.4s;--gs:1.2"),
        Span(cls="iq-glint", style="--gx:85%;--gy:75%;--gd:0.6s;--gs:0.6"),
        Span(cls="iq-glint", style="--gx:15%;--gy:80%;--gd:2.1s;--gs:1"),
        Span(cls="iq-glint", style="--gx:50%;--gy:8%;--gd:1.8s;--gs:0.7"),
        Span(cls="iq-glint", style="--gx:30%;--gy:92%;--gd:0.3s;--gs:0.9"),
        Span(cls="iq-glint", style="--gx:65%;--gy:15%;--gd:2.5s;--gs:0.5"),
        Span(cls="iq-glint", style="--gx:75%;--gy:85%;--gd:1.1s;--gs:0.7"),
        # Ambient glow orbs
        Div(cls="iq-orb iq-orb-l"),
        Div(cls="iq-orb iq-orb-r"),
        # Main centred content
        Div(
            # Giant decorative typographic open-quote mark
            Div("\u201c", cls="iq-big-quote"),
            # Expanding gold rule — top
            Div(cls="iq-rule scroll-reveal sr-d1"),
            # Quote text, each line staggered
            Div(
                P("We joyfully invite you", cls="iq-line scroll-reveal sr-d2"),
                P("to share in the celebration", cls="iq-line scroll-reveal sr-d3"),
                P("of our wedding day", cls="iq-line scroll-reveal sr-d4"),
                P("and create beautiful memories together.", cls="iq-line scroll-reveal sr-d5"),
                cls="iq-text",
            ),
            # Expanding gold rule — bottom
            Div(cls="iq-rule scroll-reveal sr-d5"),
            # Signature
            P("\u2014 Nikolai & Valentina", cls="iq-sig scroll-reveal sr-d6"),
            cls="iq-inner",
        ),
        cls="iq-canvas",
    )


def PreviewInvitePage() -> FT:
    """Generic invite shown at / — no guest record needed."""
    return (
        Title("Nikolai & Valentina · Wedding Invitation"),
        Main(
            TopMarqueeBanner(),
            BookOpeningOverlay(),
            Div(InviteHero(), cls="invite-section"),
            _section_separator(),
            Div(InviteDetails(), cls="invite-section"),
            Div(VenueSection(), cls="invite-section"),
            _section_separator(),
            Div(MemoriesSection(), cls="invite-section"),
            _section_separator(),
            Div(DressCodeSection(), cls="invite-section"),
            _section_separator(),
            Div(InvitationQuoteSection(), cls="invite-section"),

            Div(ReservationSongSection({"slug": "", "name": "Guest"}), cls="invite-section"),
            Div(InviteFooter(), cls="invite-section"),
        ),
        _lightbox(),
        CountdownNavbar(),
        MusicPlayer(),
        WeddingEffects(),
        InteractiveEffects(),
        Script("lucide.createIcons();"),
    )
