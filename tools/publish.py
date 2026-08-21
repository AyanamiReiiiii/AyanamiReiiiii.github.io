#!/usr/bin/env python3
"""Local writing tool for AyanamiReiiiii.github.io

Run from anywhere:
    python3 tools/publish.py

It opens a writing form in your browser. Fill in title/date/category,
write Markdown (with $LaTeX$ and images), hit Publish — the tool writes a
formatted HTML page into the right folder (math/ cs/ thoughts/) and adds
the entry to writings.js, so it appears on the home page automatically.
Python standard library only; nothing leaves your laptop.
"""

import datetime
import json
import os
import re
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8844
CATEGORIES = {"math": "Math", "cs": "CS", "thoughts": "Thoughts"}

POST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} &middot; Yifan Mo</title>
    <link rel="stylesheet" href="../style.css">
    <script>
    MathJax = {{
        tex: {{ inlineMath: [['$','$'],['\\\\(','\\\\)']], displayMath: [['$$','$$'],['\\\\[','\\\\]']] }},
        options: {{ skipHtmlTags: ['pre','code','script','style','textarea'] }}
    }};
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body class="no-loader">

    <header class="site">
        <span class="name"><a href="../index.html">Yifan Mo</a></span>
        <nav class="site">
            <a href="../index.html">Home</a>
            <a href="../math.html">Math</a>
            <a href="../cs.html">CS</a>
            <a href="../thoughts.html">Thoughts</a>
            <a href="../friends.html">Friends</a>
        </nav>
    </header>

    <main>
        <div class="post-header">
            <h1>{title}</h1>
            <div class="meta">{date}</div>
        </div>

        <div class="post-body">
{body}
        </div>

        <p style="margin-top: 40px;"><a class="back" href="../{category}.html">&larr; Back to {label}</a></p>
    </main>

</body>
</html>
"""


def slugify(title):
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:60].rstrip("-") or "untitled"


def unique_path(folder, filename):
    """Return folder/filename, appending -2, -3... if it already exists."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(folder, filename)
    n = 2
    while os.path.exists(candidate):
        candidate = os.path.join(folder, f"{base}-{n}{ext}")
        n += 1
    return candidate


def load_writings():
    """Parse writings.js back into a Python list."""
    path = os.path.join(ROOT, "writings.js")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    start = text.index("[")
    end = text.rindex("]") + 1
    return path, json.loads(text[start:end])


def save_writings(path, entries):
    header = (
        "/* All writings on the site. The local writing tool (tools/publish.py) updates\n"
        "   this file automatically when you publish; you can also edit it by hand.\n"
        "   Fields: title, date (YYYY-MM-DD), category (math | cs | thoughts),\n"
        "           file (path from repo root), desc (optional, shown under the title). */\n\n"
        "window.WRITINGS = "
    )
    entries.sort(key=lambda w: w["date"], reverse=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + json.dumps(entries, indent=2, ensure_ascii=False) + ";\n")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet

    # ---- pages ----

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html", "/editor"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            # Browsers love caching this page; never serve a stale editor
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            with open(os.path.join(ROOT, "tools", "editor.html"), "rb") as f:
                self.wfile.write(f.read())
        elif parsed.path == "/writings":
            _, entries = load_writings()
            self.reply({"ok": True, "writings": entries})
        elif parsed.path == "/source":
            self.handle_source(parsed)
        else:
            super().do_GET()  # serve site files, so "View the page" works

    def handle_source(self, parsed):
        """Return the saved markdown source for an existing writing."""
        qs = parse_qs(parsed.query)
        f = qs.get("file", [""])[0]
        md_file = f if f.endswith(".md") else os.path.splitext(f)[0] + ".md"
        path = os.path.realpath(os.path.join(ROOT, md_file))
        if not (path == ROOT or path.startswith(ROOT + os.sep)):
            return self.reply({"ok": False, "error": "bad path"})
        if not os.path.isfile(path):
            return self.reply({"ok": False, "error": "no saved source for this writing"})

        with open(path, encoding="utf-8") as fh:
            text = fh.read()

        meta, body = {}, text
        lines = text.split("\n")
        if lines and lines[0].strip() == "---":
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    for ml in lines[1:i]:
                        if ":" in ml:
                            k, v = ml.split(":", 1)
                            meta[k.strip()] = v.strip()
                    body = "\n".join(lines[i + 1:]).lstrip("\n")
                    break
        self.reply({"ok": True, "meta": meta, "markdown": body})

    # ---- api ----

    def reply(self, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/upload":
                self.handle_upload(parsed)
            elif parsed.path == "/publish":
                self.handle_publish()
            else:
                self.reply({"ok": False, "error": "unknown endpoint"})
        except Exception as e:  # noqa: BLE001
            self.reply({"ok": False, "error": str(e)})

    def handle_upload(self, parsed):
        qs = parse_qs(parsed.query)
        name = unquote(qs.get("name", ["image.png"])[0])
        category = qs.get("category", ["thoughts"])[0]
        if category not in CATEGORIES:
            category = "thoughts"

        ext = os.path.splitext(name)[1].lower()
        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
            ext = ".png"

        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        folder = os.path.join(ROOT, category, "images")
        os.makedirs(folder, exist_ok=True)

        path = unique_path(folder, stamp + ext)
        length = int(self.headers.get("Content-Length", 0))
        with open(path, "wb") as f:
            f.write(self.rfile.read(length))

        rel = os.path.relpath(path, os.path.join(ROOT, category))
        self.reply({"ok": True, "path": rel})

    def handle_publish(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length).decode("utf-8"))

        title = data.get("title", "").strip()
        date = data.get("date") or datetime.date.today().isoformat()
        category = data.get("category", "thoughts")
        desc = data.get("desc", "").strip()
        body_html = data.get("html", "").strip()
        markdown = data.get("markdown", "")

        if not title:
            return self.reply({"ok": False, "error": "title is required"})
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            return self.reply({"ok": False, "error": "date must look like 2026-08-20"})
        if category not in CATEGORIES:
            return self.reply({"ok": False, "error": "unknown category"})
        if not body_html:
            return self.reply({"ok": False, "error": "content is empty"})

        folder = os.path.join(ROOT, category)
        os.makedirs(folder, exist_ok=True)

        overwrite = data.get("overwrite")  # manifest file path being edited, if any
        if overwrite:
            html_path = os.path.realpath(os.path.join(ROOT, overwrite))
            if not (html_path == ROOT or html_path.startswith(ROOT + os.sep)):
                return self.reply({"ok": False, "error": "bad overwrite path"})
            if not os.path.isfile(html_path):
                return self.reply({"ok": False, "error": "the file to overwrite no longer exists"})
        else:
            html_path = unique_path(folder, f"{date}-{slugify(title)}.html")
        md_path = os.path.splitext(html_path)[0] + ".md"

        # Indent body to match the template
        indented = "\n".join("            " + line if line.strip() else ""
                             for line in body_html.split("\n"))
        page = POST_TEMPLATE.format(
            title=title, date=date, category=category,
            label=CATEGORIES[category], body=indented,
        )
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page)
        with open(md_path, "w", encoding="utf-8") as f:  # keep the source
            f.write(f"---\ntitle: {title}\ndate: {date}\ncategory: {category}\n---\n\n{markdown}\n")

        rel = os.path.relpath(html_path, ROOT)
        entry = {"title": title, "date": date, "category": category, "file": rel}
        if desc:
            entry["desc"] = desc

        wpath, entries = load_writings()
        if overwrite:
            # Update the existing manifest entry in place (keeps its position fields fresh)
            norm = os.path.normpath(os.path.join(ROOT, overwrite))
            for e in entries:
                if os.path.normpath(os.path.join(ROOT, e.get("file", ""))) == norm:
                    e.update(entry)
                    entry = e
                    break
            else:
                entries.append(entry)
        else:
            entries.append(entry)
        save_writings(wpath, entries)

        action = "update" if overwrite else "publish"
        print(f"[{action}] {rel}")
        self.reply({"ok": True, "file": rel})


def main():
    url = f"http://127.0.0.1:{PORT}/"
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        print(f"Port {PORT} is busy — is the writing tool already running at {url}?")
        webbrowser.open(url)
        return

    print("Writing tool running at", url)
    print("Write something, hit Publish, then Ctrl-C here when done.")
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDone!")
        print("If you published anything, ship it from VS Code:")
        print("  1. Source Control panel -> click + to stage all -> type a message -> Commit")
        print("  2. ... menu -> Push   (the live site updates from the 'main' branch)")


if __name__ == "__main__":
    main()
