"""Make the research bundle for sending by email (R74), from the files in docs/research.

Usage: python3 -I build/tools/research_bundle.py OUT_DIR
Needs pandoc and LibreOffice (soffice). Writes OUT_DIR/ghrac-research-bundle.zip with:
  0 Invitation email.txt             the email, ready to paste into a new message (subject first)
  1 Introducing the catalogue        .docx and .pdf
  2 Participant information          .docx and .pdf
  3 Consent form                     .docx and .pdf
  4 Screener                         for whoever arranges sessions, .docx
  5 Session guides                   for facilitators, .docx
The Word files use Arial 12 point, British English, real headings and tables, so screen readers can navigate them.
Nothing here contains an email address of ours: people reply to whoever sent the invitation.
"""
import os, re, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "docs", "research")
PARTS = [("1 Introducing the catalogue", "introducing-the-catalogue.md", True), ("2 Participant information", "participant-information.md", True),
         ("3 Consent form", "consent-form.md", True), ("4 Screener, for whoever arranges sessions", "screener.md", False),
         ("5 Session guides, for facilitators", "session-guides.md", False)]


def reference_docx(tmp):
    """Pandoc's reference document, restyled: Arial 12 point body, bold Arial headings, British English."""
    ref = os.path.join(tmp, "ref.docx")
    subprocess.run(["pandoc", "-o", ref, "--print-default-data-file", "reference.docx"], check=True)
    d = os.path.join(tmp, "ref"); zipfile.ZipFile(ref).extractall(d)
    sp = os.path.join(d, "word", "styles.xml"); s = open(sp, encoding="utf-8").read()
    s = re.sub(r'w:ascii="[^"]*"', 'w:ascii="Arial"', s); s = re.sub(r'w:hAnsi="[^"]*"', 'w:hAnsi="Arial"', s)
    s = re.sub(r'w:asciiTheme="[^"]*"', "", s); s = re.sub(r'w:hAnsiTheme="[^"]*"', "", s)
    s = s.replace('<w:lang w:val="en-US"', '<w:lang w:val="en-GB"')
    s = re.sub(r'<w:rFonts (?![^>]*w:ascii=)', '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" ', s)   # every style, including the document default, gets Arial
    open(sp, "w", encoding="utf-8").write(s)
    tp = os.path.join(d, "word", "theme", "theme1.xml")   # the theme's own fonts, which headings and some readers use
    if os.path.exists(tp):
        t = open(tp, encoding="utf-8").read(); t = re.sub(r'<a:latin typeface="[^"]*"', '<a:latin typeface="Arial"', t); open(tp, "w", encoding="utf-8").write(t)
    os.remove(ref)
    with zipfile.ZipFile(ref, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(d):
            for fn in files:
                p = os.path.join(base, fn); z.write(p, os.path.relpath(p, d))
    return ref


def email_text():
    md = open(os.path.join(SRC, "invitation-email.md"), encoding="utf-8").read()
    body = md[md.index("**Subject:**"):]
    body = body.replace("**Subject:**", "Subject:").replace("**", "")
    body = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", body)
    return body.strip() + "\n"


def main(out):
    os.makedirs(out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        ref = reference_docx(tmp); pack = os.path.join(tmp, "pack"); os.makedirs(pack)
        open(os.path.join(pack, "0 Invitation email.txt"), "w", encoding="utf-8").write(email_text())
        for name, src, pdf in PARTS:
            md = open(os.path.join(SRC, src), encoding="utf-8").read()
            md = re.sub(r"\n\*\*For teams who might use it\.\*\*", "\n**For teams who might use it.**", md)
            title = re.search(r"^# (.+)$", md, re.M).group(1)
            md = re.sub(r"^# .+\n", "", md, count=1, flags=re.M)
            mp = os.path.join(tmp, src); open(mp, "w", encoding="utf-8").write(md)
            dx = os.path.join(pack, name + ".docx")
            subprocess.run(["pandoc", mp, "-o", dx, "--reference-doc", ref, "-M", "title=" + title, "-M", "lang=en-GB", "-M", "author=GitHub Repos Asset Catalogue maintainers"], check=True)
            if pdf:
                subprocess.run(["soffice", "--headless", "--convert-to", 'pdf:writer_pdf_Export:{"UseTaggedPDF":{"type":"boolean","value":"true"}}', "--outdir", pack, dx], check=True, capture_output=True)
        text = "".join(open(os.path.join(pack, f), encoding="utf-8").read() for f in os.listdir(pack) if f.endswith(".txt"))
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text): sys.exit("The email contains an email address; refusing to make the bundle.")
        zp = os.path.join(out, "ghrac-research-bundle.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(os.listdir(pack)): z.write(os.path.join(pack, f), "GitHub Repos Asset Catalogue research bundle/" + f)
        for f in sorted(os.listdir(pack)): shutil.copy(os.path.join(pack, f), out)
    print("Wrote", zp)


if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(sys.argv[1])
