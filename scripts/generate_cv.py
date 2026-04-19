#!/usr/bin/env python3
"""
generate_cv.py
─────────────────────────────────────────────────────────────
Parses data/publications.bib and generates cv.tex.
Run locally:  python scripts/generate_cv.py
GitHub Actions then compiles cv.tex → cv.pdf automatically.

KEYWORD MAP  (same as website)
  J     → Journal Articles
  C     → Conference Papers
  B     → Books & Book Chapters
  R     → Working Papers
  T     → Talks & Presentations
  P     → Posters
  D     → Demonstrations & Tutorials
  Teach → Teaching Experience
  Award → Awards & Grants
  News  → (skipped in CV)
─────────────────────────────────────────────────────────────
"""

import os
import re
from datetime import datetime

# ── Paths ─────────────────────────────────────────────────────
BIB_IN  = os.path.join(os.path.dirname(__file__), '..', 'data', 'publications.bib')
TEX_OUT = os.path.join(os.path.dirname(__file__), '..', 'cv.tex')

# ══════════════════════════════════════════════════════════════
#  ✏️  PERSONAL CONFIG  — keep in sync with index.html CONFIG
# ══════════════════════════════════════════════════════════════
CONFIG = {
    "name":        "Phuong Nguyen",
    "title":       "PhD Researcher in Supply Chain \\& Operations Management",
    "institution": "Berlin School of Economics and Law (HWR Berlin)",
    "email":       "p.nguyen@hwr-berlin.de",
    "scholar":     "https://scholar.google.com/",
    "linkedin":    "https://linkedin.com/in/example",
    "github":      "https://github.com/example",
    "orcid":       "",
    "address":     "Berlin, Germany",
    # Optional sections
    "about": (
        "PhD researcher specialising in supply chain resilience, network science, "
        "and digital twin methods. Research focuses on quantitative frameworks for "
        "understanding disruption propagation and designing robust supply chains."
    ),
    "research_interests": [
        "Supply Chain Resilience", "Network Science", "Digital Twins",
        "Agent-Based Simulation", "Disruption Management",
    ],
}

# ══════════════════════════════════════════════════════════════
#  BIBTEX PARSER  (brace-depth-aware)
# ══════════════════════════════════════════════════════════════
def parse_bib(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    # Strip % comments
    text = re.sub(r"%[^\n]*", "", text)

    entries = []
    i = 0
    n = len(text)

    while i < n:
        while i < n and text[i] != "@":
            i += 1
        if i >= n:
            break
        i += 1

        # Entry type
        t0 = i
        while i < n and (text[i].isalnum() or text[i] == "_"):
            i += 1
        etype = text[t0:i].strip().lower()
        if not etype:
            continue

        # Opening brace
        while i < n and text[i] != "{":
            i += 1
        if i >= n:
            break
        i += 1

        # Citation key
        k0 = i
        while i < n and text[i] not in (",", "}"):
            i += 1
        key = text[k0:i].strip()
        if i < n and text[i] == ",":
            i += 1

        # Fields
        fields: dict[str, str] = {}

        while i < n:
            while i < n and text[i] in " \t\n\r":
                i += 1
            if i >= n:
                break
            if text[i] == "}":
                i += 1
                break

            # Field name
            fn0 = i
            while i < n and text[i] not in ("=", "}", ","):
                i += 1
            fname = text[fn0:i].strip().lower()

            if i >= n or text[i] != "=":
                if i < n:
                    if text[i] == "}":
                        i += 1
                        break
                    i += 1
                continue
            i += 1  # skip =

            while i < n and text[i] in " \t\n\r":
                i += 1

            # Value
            value = ""
            if i < n and text[i] == "{":
                d = 1
                i += 1
                while i < n and d > 0:
                    if text[i] == "{":
                        d += 1
                    elif text[i] == "}":
                        d -= 1
                        if d == 0:
                            i += 1
                            break
                    if d > 0:
                        value += text[i]
                    i += 1
            elif i < n and text[i] == '"':
                i += 1
                while i < n and text[i] != '"':
                    value += text[i]
                    i += 1
                if i < n:
                    i += 1
            else:
                while i < n and text[i] not in (",", "}", "\n"):
                    value += text[i]
                    i += 1
                value = value.strip()

            if fname:
                fields[fname] = value

            while i < n and text[i] in " \t\n\r":
                i += 1
            if i < n and text[i] == ",":
                i += 1

        entry = {"type": etype, "key": key}
        entry.update(fields)
        entries.append(entry)

    return entries


# ══════════════════════════════════════════════════════════════
#  LATEX FORMATTER  (entries → LaTeX \item lines)
# ══════════════════════════════════════════════════════════════
def _yr(e: dict) -> str:
    y = e.get("year", "n.d.")
    return str(y).strip()


def fmt_journal(e: dict) -> str:
    author = e.get("author", "")
    title  = e.get("title", "").strip().rstrip(".")
    jrnl   = e.get("journal", "")
    vol    = e.get("volume", "")
    num    = e.get("number", "")
    pages  = e.get("pages", "")
    url    = e.get("url", "")
    year   = _yr(e)

    venue = f"\\textit{{{jrnl}}}"
    if vol:
        venue += f", {vol}"
    if num:
        venue += f"({num})"
    if pages:
        venue += f", pp.~{pages}"

    link = f" \\href{{{url}}}{{[link]}}" if url else ""
    return f"  \\item {author}. ``{title}.'' {venue}, {year}.{link}"


def fmt_conf(e: dict) -> str:
    author    = e.get("author", "")
    title     = e.get("title", "").strip().rstrip(".")
    booktitle = e.get("booktitle", "")
    note      = e.get("note", "")
    pages     = e.get("pages", "")
    org       = e.get("organization", "")
    year      = _yr(e)

    venue = note if note else booktitle
    if pages:
        venue += f", pp.~{pages}"
    if org:
        venue += f". {org}"

    return f"  \\item {author}. ``{title}.'' \\textit{{{venue}}}, {year}."


def fmt_book(e: dict) -> str:
    author    = e.get("author", "")
    title     = e.get("title", "").strip().rstrip(".")
    publisher = e.get("publisher", "")
    year      = _yr(e)
    edition   = e.get("edition", "")
    series    = e.get("series", "")
    url       = e.get("url", "")

    ed_str = f", {edition}~ed." if edition else ""
    link   = f" \\href{{{url}}}{{[link]}}" if url else ""
    ser_str = f" ({series})" if series else ""
    return f"  \\item {author}. \\textit{{{title}}}{ed_str}{ser_str}. {publisher}, {year}.{link}"


def fmt_inbook(e: dict) -> str:
    author    = e.get("author", "")
    title     = e.get("title", "").strip().rstrip(".")
    booktitle = e.get("booktitle", "")
    editor    = e.get("editor", "")
    publisher = e.get("publisher", "")
    year      = _yr(e)

    ed_str = f"Eds.~{editor}. " if editor else ""
    return f"  \\item {author}. ``{title}.'' In \\textit{{{booktitle}}}. {ed_str}{publisher}, {year}."


def fmt_working(e: dict) -> str:
    author       = e.get("author", "")
    title        = e.get("title", "").strip().rstrip(".")
    howpublished = e.get("howpublished", "")
    return f"  \\item {author}. ``{title}.'' \\textit{{{howpublished}}}."


def fmt_talk(e: dict) -> str:
    title        = e.get("title", "").strip().rstrip(".")
    howpublished = e.get("howpublished", "")
    month        = e.get("month", "")
    year         = _yr(e)
    when         = f"{month.capitalize()} {year}" if month else year
    return f"  \\item ``{title}.'' {howpublished}. {when}."


def fmt_poster(e: dict) -> str:
    title        = e.get("title", "").strip().rstrip(".")
    howpublished = e.get("howpublished", "")
    month        = e.get("month", "")
    year         = _yr(e)
    when         = f"{month.capitalize()} {year}" if month else year
    return f"  \\item ``{title}.'' Poster at {howpublished}. {when}."


def fmt_demo(e: dict) -> str:
    title        = e.get("title", "").strip().rstrip(".")
    howpublished = e.get("howpublished", "")
    note         = e.get("note", "")
    month        = e.get("month", "")
    year         = _yr(e)
    when         = f"{month.capitalize()} {year}" if month else year
    venue        = note if note else howpublished
    return f"  \\item ``{title}.'' {venue}. {when}."


def fmt_teach(e: dict) -> str:
    title = e.get("title", "").strip().rstrip(".")
    note  = e.get("note", "")
    year  = _yr(e)
    return f"  \\item \\textit{{{title}}}. {note}, {year}."


def fmt_award(e: dict) -> str:
    title = e.get("title", "").strip().rstrip(".")
    note  = e.get("note", "")
    year  = _yr(e)
    return f"  \\item {title}. {note}, {year}."


FORMATTERS = {
    "J":     fmt_journal,
    "C":     fmt_conf,
    "R":     fmt_working,
    "T":     fmt_talk,
    "P":     fmt_poster,
    "D":     fmt_demo,
    "Teach": fmt_teach,
    "Award": fmt_award,
}

BOOK_TYPES = {"book": fmt_book, "inbook": fmt_inbook}


def format_entry(e: dict) -> str:
    kw   = e.get("keywords", "").strip()
    etype = e.get("type", "")

    if kw == "B":
        formatter = BOOK_TYPES.get(etype, fmt_book)
        return formatter(e)
    if kw in FORMATTERS:
        return FORMATTERS[kw](e)
    return ""


def cv_section(heading: str, entries: list[dict]) -> str:
    if not entries:
        return ""
    # Sort by year descending; n.d. entries go first
    def sort_key(e):
        y = e.get("year", "n.d.")
        try:
            return -int(y)
        except (ValueError, TypeError):
            return 9999

    items = []
    for e in sorted(entries, key=sort_key):
        line = format_entry(e)
        if line.strip():
            items.append(line)

    if not items:
        return ""

    return (
        f"\\section{{{heading}}}\n"
        f"\\begin{{enumerate}}[leftmargin=*, itemsep=3pt, parsep=0pt, topsep=4pt]\n"
        + "\n".join(items)
        + "\n\\end{enumerate}\n"
    )


# ══════════════════════════════════════════════════════════════
#  DOCUMENT TEMPLATE
# ══════════════════════════════════════════════════════════════
TEX_PREAMBLE = r"""\documentclass[11pt, a4paper]{article}

\usepackage[margin=2.4cm, top=1.8cm, bottom=1.8cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{parskip}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{hyperref}

\definecolor{navy}{RGB}{27, 58, 107}

\hypersetup{
  colorlinks = true,
  urlcolor   = navy,
  linkcolor  = navy,
  citecolor  = navy,
}

% Section style: small caps label + rule
\titleformat{\section}
  {\large\bfseries\color{navy}}
  {}{0em}{}
  [{\color{navy}\titlerule[0.5pt]}]
\titlespacing*{\section}{0pt}{2ex plus .5ex minus .3ex}{0.8ex plus .2ex}

\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}

% Tighter list spacing by default
\setlist[enumerate]{topsep=2pt, itemsep=3pt, parsep=0pt}
"""


def build_document(cfg: dict, by_kw: dict[str, list]) -> str:
    name    = cfg["name"]
    title   = cfg["title"]
    inst    = cfg["institution"]
    email   = cfg["email"]
    scholar = cfg.get("scholar", "")
    linkedin= cfg.get("linkedin", "")
    github  = cfg.get("github", "")
    orcid   = cfg.get("orcid", "")
    now     = datetime.now().strftime("%B %Y")

    # Contact line
    contact_parts = [f"\\href{{mailto:{email}}}{{{email}}}"]
    if scholar:
        contact_parts.append(f"\\href{{{scholar}}}{{Google Scholar}}")
    if linkedin:
        contact_parts.append(f"\\href{{{linkedin}}}{{LinkedIn}}")
    if github:
        contact_parts.append(f"\\href{{{github}}}{{GitHub}}")
    if orcid:
        contact_parts.append(f"\\href{{{orcid}}}{{ORCID}}")
    contact_line = " $\\cdot$ ".join(contact_parts)

    # Research interests line
    interests = cfg.get("research_interests", [])
    interests_line = " $\\cdot$ ".join(interests) if interests else ""

    # About paragraph
    about_tex = cfg.get("about", "")

    # Build all sections
    sections = [
        cv_section("Journal Articles",          by_kw.get("J",     [])),
        cv_section("Conference Papers",          by_kw.get("C",     [])),
        cv_section("Books \\& Book Chapters",   by_kw.get("B",     [])),
        cv_section("Working Papers",             by_kw.get("R",     [])),
        cv_section("Talks \\& Presentations",   by_kw.get("T",     [])),
        cv_section("Posters",                    by_kw.get("P",     [])),
        cv_section("Demonstrations \\& Tutorials", by_kw.get("D",  [])),
        cv_section("Teaching Experience",        by_kw.get("Teach", [])),
        cv_section("Awards \\& Grants",          by_kw.get("Award", [])),
    ]
    body = "\n".join(s for s in sections if s)

    about_section = ""
    if about_tex:
        about_section = f"""
\\section{{Research Profile}}
{about_tex}

"""
    interests_section = ""
    if interests_line:
        interests_section = f"""
\\noindent\\textbf{{Research Interests:}} {interests_line}

"""

    return (
        TEX_PREAMBLE
        + f"""
\\begin{{document}}

% ─── HEADER ──────────────────────────────────────────────────
\\begin{{center}}
  {{\\LARGE\\bfseries\\color{{navy}} {name}}}\\\\[5pt]
  {{\\large {title}}}\\\\[3pt]
  {{\\normalsize {inst}}}\\\\[6pt]
  {{\\small {contact_line}}}
\\end{{center}}

\\vspace{{6pt}}
\\noindent{{\\color{{navy}}\\rule{{\\linewidth}}{{1.2pt}}}}
\\vspace{{4pt}}

{about_section}{interests_section}{body}

% ─── FOOTER ──────────────────────────────────────────────────
\\vspace{{1.5em}}
\\begin{{center}}
  {{\\small\\color{{gray}} Last updated: {now}}}
\\end{{center}}

\\end{{document}}
"""
    )


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    bib_path = os.path.normpath(BIB_IN)
    tex_path = os.path.normpath(TEX_OUT)

    print(f"Reading  {bib_path}")
    entries = parse_bib(bib_path)
    print(f"Parsed   {len(entries)} entries")

    # Group by keyword
    by_kw: dict[str, list] = {}
    for e in entries:
        kw = e.get("keywords", "?").strip()
        by_kw.setdefault(kw, []).append(e)

    # Summary
    for kw, lst in sorted(by_kw.items()):
        print(f"  [{kw}] {len(lst)} entries")

    tex = build_document(CONFIG, by_kw)

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex)
    print(f"Written  {tex_path}")
    print("Done — compile with: pdflatex cv.tex")


if __name__ == "__main__":
    main()
