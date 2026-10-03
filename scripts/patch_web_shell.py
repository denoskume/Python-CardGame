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
    }
    const canvas = document.getElementById('canvas');
    if (canvas) {
        canvas.style.setProperty('width', '100vw', 'important');
        canvas.style.setProperty('height', '100vh', 'important');
        canvas.style.setProperty('max-width', 'none', 'important');
        canvas.style.setProperty('max-height', 'none', 'important');
    }
    if (typeof window_resize === 'function') {
        window_resize();
    }
}
window.addEventListener('resize', syncViewportFramebuffer);
window.addEventListener('orientationchange', () => setTimeout(syncViewportFramebuffer, 50));
window.addEventListener('load', () => setTimeout(syncViewportFramebuffer, 0));
</script>
"""


def patch(index_path: Path) -> None:
    html = index_path.read_text(encoding="utf-8")

    html, count_ar = re.subn(r"fb_ar\s*:\s*1\.77", "fb_ar : window.innerWidth / Math.max(1, window.innerHeight)", html, count=1)
    html, count_w = re.subn(r'fb_width\s*:\s*"1280"', 'fb_width : String(window.innerWidth)', html, count=1)
    html, count_h = re.subn(r'fb_height\s*:\s*"720"', 'fb_height : String(window.innerHeight)', html, count=1)

    if not (count_ar and count_w and count_h):
        raise RuntimeError("Expected Pygbag framebuffer defaults were not found in index.html")

    if 'id="full-viewport-shell"' not in html:
        html = html.replace("</head>", FULL_VIEWPORT_STYLE + "\n</head>", 1)
    if 'id="full-viewport-runtime"' not in html:
        html = html.replace("</body>", FULL_VIEWPORT_SCRIPT + "\n</body>", 1)

    index_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/patch_web_shell.py <index.html>")
    patch(Path(sys.argv[1]))
