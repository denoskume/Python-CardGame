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
<section id="cardgame-loading" role="status" style="position:fixed;inset:0;display:grid;place-content:center;text-align:center;background:#0f1217;color:#f1eee7;font:18px system-ui;z-index:9000;pointer-events:none">
  <h1 style="color:#c73647">Rouge gagne, noir perd</h1>
  <p id="cardgame-load-status">Loading your table… First launch may take a moment.</p>
  <p style="font-size:14px;color:#99a3b1">Click or tap to activate the game.</p>
  <button id="cardgame-retry" hidden style="pointer-events:auto;padding:14px;background:#c73647;color:white;border:0;border-radius:8px" onclick="location.reload()">Try again</button>
</section>
<script>
function cardgameLoadFailed() {
  const overlay=document.getElementById('cardgame-loading');
  if (overlay && !overlay.hidden) {
    document.getElementById('cardgame-load-status').textContent='The game could not finish loading. Check your connection and try again.';
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
