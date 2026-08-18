#!/usr/bin/env python3
"""Build the two v2 pages from their sources.

Two modes, because the same markup has to serve two very different hosts:

  artifact  every asset inlined as a data URI, because the artifact viewer's CSP
            blocks requests to any external host
  site      videos and posters left as ordinary files under assets/, because a
            5MB base64 blob in the HTML is a terrible way to ship a video

Images stay inlined in both modes; they are small and it keeps the page one file.
"""
import base64, mimetypes, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).parent          # <repo>/v2
REPO = HERE.parent
SP   = HERE / "src-assets"                     # images inlined into both pages
VID  = REPO / "assets/video"                   # clips, shipped as files on the real site
OUT  = HERE / "build"

def datauri(path: pathlib.Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

# Images are always inlined. Two of them were pre-encoded to .b64 sidecars.
IMAGES = {
    "__ABBAS__":    lambda: datauri(SP / "abbas.webp"),
    "__WK__":       lambda: datauri(SP / "wk.webp"),
    "__GOOGLE__":   lambda: (SP / "google.b64").read_text(),
    "__HARDROCK__": lambda: (SP / "hardrock.b64").read_text(),
}

# Posters are small enough to inline in either mode.
POSTERS = {
    "__FOUNDERPOSTER__": ("founder-poster.webp", "assets/video/founder-poster.webp"),
    "__YCPOSTER__":      ("yc-poster.webp",      "assets/video/yc-poster.webp"),
}

# Videos never become data: URIs — Chrome will not stream media from one, and a 5MB
# data: URI parks the element at readyState 0 indefinitely. For the artifact the clip
# ships as a base64 payload the page turns into a Blob URL on click.
VIDEOS = {
    "__FOUNDERVID__": ("founder-pitch.mp4", "assets/video/founder-pitch.mp4", "p-founder"),
    "__YCVID__":      ("yc-pitch.mp4",      "assets/video/yc-pitch.mp4",      "p-yc"),
}

def render(src: pathlib.Path, mode: str) -> str:
    t = src.read_text()
    for token, fn in IMAGES.items():
        if token in t:
            t = t.replace(token, fn())
    for token, (fname, relpath) in POSTERS.items():
        if token in t:
            t = t.replace(token, datauri(VID / fname) if mode == "artifact" else relpath)

    payloads = []
    for token, (fname, relpath, pid) in VIDEOS.items():
        if token not in t:
            continue
        if mode == "artifact":
            t = t.replace(token, f"b64:{pid}")
            b64 = base64.b64encode((VID / fname).read_bytes()).decode()
            payloads.append(f'<script id="{pid}" type="text/plain">{b64}</script>')
        else:
            t = t.replace(token, relpath)
    t = t.replace("__PAYLOADS__", "\n".join(payloads))

    left = re.findall(r"__[A-Z]+__", t)
    if left:
        raise SystemExit(f"{src.name}: unresolved placeholders {sorted(set(left))}")
    return t

def check_js(html: str, label: str) -> None:
    # Strip only genuine base64 payloads. A looser pattern eats prose that merely
    # mentions "data:" and hands node a truncated script to choke on.
    clean = re.sub(r"data:[a-z]+/[a-z0-9.+-]+;base64,[A-Za-z0-9+/=]+", "", html)
    clean = re.sub(r'(<script id="p-[a-z]+" type="text/plain">)[A-Za-z0-9+/=]+', r"\1", clean)
    for n, js in enumerate(re.findall(r"<script>(.*?)</script>", clean, re.S)):
        r = subprocess.run(["node", "--check", "/dev/stdin"],
                           input=js, capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f"{label} script {n} failed to parse:\n{r.stderr[:400]}")
    for n, css in enumerate(re.findall(r"<style>(.*?)</style>", clean, re.S)):
        if css.count("{") != css.count("}"):
            raise SystemExit(f"{label} style {n} has unbalanced braces")

SKEL = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '%s</head><body>%s</body></html>')

def main(mode: str = "artifact", out: str | None = None) -> None:
    global OUT
    OUT = pathlib.Path(out) if out else OUT
    OUT.mkdir(parents=True, exist_ok=True)
    home = render(HERE / "az-v2-src.html", mode)
    check_js(home, "home")
    (OUT / "az-v2.html").write_text(home)
    # The artifact host supplies the document skeleton; the local harness does not.
    i = home.index("<nav>")
    (OUT / "test-home.html").write_text(SKEL % (home[:i], home[i:]))

    inv = render(HERE / "az-investors-src.html", mode)
    check_js(inv, "investors")
    (OUT / "az-investors.html").write_text(inv)
    j = inv.index("<nav>")
    (OUT / "test-investors.html").write_text(SKEL % (inv[:j], inv[j:]))

    for name in ("az-v2.html", "az-investors.html"):
        mb = (OUT / name).stat().st_size / 1e6
        flag = "  OVER 16MB LIMIT" if mb > 16 else ""
        print(f"  {name:22} {mb:6.2f} MB{flag}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "artifact",
         sys.argv[2] if len(sys.argv) > 2 else None)
