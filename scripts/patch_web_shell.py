from pathlib import Path
import re


FULL_VIEWPORT_STYLE = """
<style id="full-viewport-shell">
html, body {
    width: 100vw !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    background: #171717 !important;
}
#canvas {
    width: 100vw !important;
    height: 100vh !important;
    max-width: none !important;
    max-height: none !important;
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
}
</style>
"""

RESIZE_SCRIPT = """
<script id="full-viewport-resize">
function syncFullViewport() {
    if (typeof config !== "undefined") {
        config.fb_width = String(window.innerWidth);
        config.fb_height = String(window.innerHeight);
        config.fb_ar = window.innerWidth / Math.max(1, window.innerHeight);
    }
    const canvas = document.getElementById("canvas");
    if (canvas) {
        canvas.style.width = "100vw";
        canvas.style.height = "100vh";
    }
    if (typeof window_resize === "function") {
        window_resize();
    }
}
window.addEventListener("resize", syncFullViewport);
window.addEventListener("orientationchange", syncFullViewport);
window.addEventListener("load", syncFullViewport);
</script>
"""


def patch_web_shell(index_path: Path) -> None:
    text = index_path.read_text(encoding="utf-8")

    text = text.replace(
        'platform.document.body.style.background = "#7f7f7f"',
        'platform.document.body.style.background = "#171717"',
    )
    text = re.sub(
        r"fb_ar\s*:\s*[^,]+,",
        "fb_ar   :  window.innerWidth / Math.max(1, window.innerHeight),",
        text,
        count=1,
    )
    text = re.sub(
        r'fb_width\s*:\s*"[^"]+"',
        'fb_width : String(window.innerWidth)',
        text,
        count=1,
    )
    text = re.sub(
        r'fb_height\s*:\s*"[^"]+"',
        'fb_height : String(window.innerHeight)',
        text,
        count=1,
    )

    if 'id="full-viewport-shell"' not in text:
        text = text.replace("</head>", FULL_VIEWPORT_STYLE + RESIZE_SCRIPT + "\n</head>", 1)

    index_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    import sys

    patch_web_shell(Path(sys.argv[1]))
