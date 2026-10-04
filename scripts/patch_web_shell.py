from pathlib import Path
import re
import sys


FULL_VIEWPORT_STYLE = """
<style id=\"full-viewport-shell\">
html, body {
    width: 100vw !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    background: #181818 !important;
}
canvas.emscripten, #canvas {
    width: 100vw !important;
    height: 100vh !important;
    max-width: none !important;
    max-height: none !important;
    margin: 0 !important;
    inset: 0 !important;
}
</style>
"""

FULL_VIEWPORT_SCRIPT = """
<script id=\"full-viewport-runtime\">
function syncViewportFramebuffer() {
    const width = Math.max(320, window.innerWidth || document.documentElement.clientWidth || 1280);
    const height = Math.max(300, window.innerHeight || document.documentElement.clientHeight || 720);
    if (typeof config !== 'undefined') {
        config.fb_width = String(width);
        config.fb_height = String(height);
        config.fb_ar = width / height;
        config.user_canvas = 1;
        config.user_canvas_managed = 1;
    }
    const canvas = document.getElementById('canvas');
    if (canvas) {
        canvas.style.setProperty('width', '100vw', 'important');
        canvas.style.setProperty('height', '100vh', 'important');
        canvas.style.setProperty('max-width', 'none', 'important');
        canvas.style.setProperty('max-height', 'none', 'important');
        canvas.style.setProperty('margin', '0', 'important');
        canvas.style.setProperty('inset', '0', 'important');
    }
}
window.addEventListener('resize', syncViewportFramebuffer);
window.addEventListener('orientationchange', () => setTimeout(syncViewportFramebuffer, 50));
window.addEventListener('load', () => setTimeout(syncViewportFramebuffer, 0));
</script>
"""


LOADING_SHELL = """
<section id="cardgame-loading" role="dialog" aria-label="CardGame start" style="position:fixed;inset:0;display:grid;place-content:center;text-align:center;background:#0f1217;color:#f1eee7;font:18px system-ui;z-index:9000">
  <div style="min-width:min(86vw,360px);padding:34px 30px;border:1px solid #303946;border-radius:20px;background:#171c24;box-shadow:0 20px 60px #0008">
    <h1 style="margin:0 0 12px;color:#e0aa54;font-size:22px">Rouge gagne, noir perd</h1>
    <p id="cardgame-load-status" style="margin:0 0 22px;color:#aab4c2;font-size:14px">Loading your table… First launch may take a moment.</p>
    <button id="cardgame-start" type="button" style="display:inline-flex;align-items:center;justify-content:center;gap:10px;min-width:210px;padding:14px 24px;background:linear-gradient(180deg,#dc4658,#a92439);color:#fff;border:1px solid #f07784;border-radius:12px;box-shadow:0 8px 18px #7f1d2d88;font:700 16px system-ui;cursor:pointer" onclick="activateCardGame()"><span aria-hidden="true">▶</span> START GAME</button>
    <button id="cardgame-retry" hidden type="button" style="margin-top:14px;padding:10px 18px;background:transparent;color:#e0aa54;border:1px solid #596779;border-radius:10px;font:600 14px system-ui;cursor:pointer" onclick="location.reload()">Try again</button>
  </div>
</section>
<script>
function activateCardGame() {
  window.__cardgameStarted = true;
  const overlay=document.getElementById('cardgame-loading');
  if (overlay) overlay.remove();
  const canvas=document.getElementById('canvas');
  if (canvas) { canvas.focus(); canvas.dispatchEvent(new PointerEvent('pointerdown', {bubbles:true})); }
}
function cardgameLoadFailed() {
  const overlay=document.getElementById('cardgame-loading');
  if (overlay && !overlay.hidden) {
    document.getElementById('cardgame-load-status').textContent='The game could not finish loading. Check your connection and try again.';
    document.getElementById('cardgame-start').hidden=true;
    document.getElementById('cardgame-retry').hidden=false;
  }
}
window.addEventListener('error',cardgameLoadFailed);
window.addEventListener('unhandledrejection',cardgameLoadFailed);
setTimeout(cardgameLoadFailed,60000);
</script>
"""


def patch(index_path: Path) -> None:
    html = index_path.read_text(encoding="utf-8")

    html = html.replace(
        'platform.document.body.style.background = "#7f7f7f"',
        'platform.document.body.style.background = "#181818"',
    )
    html, count_user = re.subn(r"user_canvas\s*:\s*0", "user_canvas : 1", html, count=1)
    html, count_managed = re.subn(
        r"user_canvas_managed\s*:\s*0",
        "user_canvas_managed : 1",
        html,
        count=1,
    )
    html, count_ar = re.subn(
        r"fb_ar\s*:\s*1\.77",
        "fb_ar : window.innerWidth / Math.max(1, window.innerHeight)",
        html,
        count=1,
    )
    html, count_w = re.subn(
        r'fb_width\s*:\s*"1280"',
        'fb_width : String(window.innerWidth)',
        html,
        count=1,
    )
    html, count_h = re.subn(
        r'fb_height\s*:\s*"720"',
        'fb_height : String(window.innerHeight)',
        html,
        count=1,
    )

    if not (count_user and count_managed and count_ar and count_w and count_h):
        raise RuntimeError("Expected Pygbag canvas/framebuffer defaults were not found in index.html")

    if 'id="full-viewport-shell"' not in html:
        html = html.replace("</head>", FULL_VIEWPORT_STYLE + "\n</head>", 1)
    if 'id="full-viewport-runtime"' not in html:
        html = html.replace("</body>", FULL_VIEWPORT_SCRIPT + "\n</body>", 1)

    html = html.replace("</body>", LOADING_SHELL + "\n</body>", 1)
    index_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/patch_web_shell.py <index.html>")
    patch(Path(sys.argv[1]))
