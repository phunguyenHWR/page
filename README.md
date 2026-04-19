# Personal Research Website

Single-source-of-truth academic website. **Edit one file → push → website and CV update automatically.**

```
data/publications.bib  ──►  Website   (rendered live in the browser via JS)
                       ──►  cv.pdf    (compiled by GitHub Actions)
```

---

## File Structure

```
your-github.io/
├── index.html                   ← website (edit CONFIG block once)
├── data/
│   └── publications.bib         ← ✏️  THE ONLY FILE YOU REGULARLY EDIT
├── scripts/
│   └── generate_cv.py           ← CV generator (edit CONFIG block once)
├── assets/
│   └── photo.jpg                ← add your photo here
├── cv.pdf                       ← auto-generated, committed by CI
└── .github/
    └── workflows/
        └── generate-cv.yml      ← GitHub Action (no edits needed)
```

---

## One-Time Setup

### 1. Create the GitHub repository

```bash
# On GitHub: create a repo named  yourusername.github.io
git clone https://github.com/yourusername/yourusername.github.io
cd yourusername.github.io
```

### 2. Copy all these files in

```bash
# Copy the entire contents of this folder into the cloned repo
cp -r researcher-site/* yourusername.github.io/
```

### 3. Fill in your personal details (edit once)

Open **`index.html`** and edit the `CONFIG` block at the top of the `<script>` section:

```js
const CONFIG = {
  name:        "Your Full Name",
  title:       "Your Title",
  institution: "Your Institution",
  email:       "you@example.com",
  scholar:     "https://scholar.google.com/citations?user=YOURID",
  linkedin:    "https://linkedin.com/in/yourhandle",
  github:      "https://github.com/yourhandle",
  ...
};
```

Open **`scripts/generate_cv.py`** and edit the same `CONFIG` dict.

### 4. Add your photo

Drop your photo at `assets/photo.jpg` (portrait orientation works best).

### 5. Enable GitHub Pages

Go to **Settings → Pages** in your GitHub repository.  
Set **Source → Deploy from a branch → main / (root)**.  
Your site will be live at `https://yourusername.github.io` within a minute.

### 6. Push everything

```bash
git add .
git commit -m "initial site"
git push
```

The GitHub Action will run automatically and commit `cv.pdf` within ~2 minutes.

---

## Daily Workflow (the only thing you ever do)

```bash
# 1. Edit your bib file
nano data/publications.bib

# 2. Push
git add data/publications.bib
git commit -m "add APMS 2025 paper"
git push
```

That's it. In ~2 minutes:
- ✅ Website sections update (on next page load)
- ✅ `cv.pdf` is regenerated and committed back

---

## BibTeX Keyword Reference

| `keywords=` | Where it appears |
|-------------|-----------------|
| `J`         | Journal Articles |
| `C`         | Conference Papers |
| `B`         | Books & Book Chapters |
| `R`         | Working Papers (set `howpublished={Under Review}` or `In Progress`) |
| `T`         | Talks & Presentations |
| `P`         | Posters |
| `D`         | Demonstrations & Tutorials |
| `Teach`     | Teaching Experience |
| `Award`     | Awards & Grants |
| `News`      | News & Blog (website only) |

### Self-author highlighting
Wrap your name in `\textbf{}` and it will be **bold** on the website:
```bibtex
author = {\textbf{Nguyen, P.} and Ivanov, Dmitry},
```

### Equal contribution
```bibtex
author = {\textbf{Nguyen, P.$^{\dagger}$} and Smith, J.$^{\dagger}$},
```

### Adding a link to a paper
```bibtex
url = {https://doi.org/10.1000/yourpaper},
```

---

## Adding New Section Types

To add a Teaching entry (for example):

```bibtex
@misc{teach_scm2024,
    title    = {Supply Chain Management},
    author   = {\textbf{Nguyen, P.}},
    note     = {Teaching Assistant — HWR Berlin},
    year     = {2024},
    keywords = {Teach}
}
```

Push → Teaching section appears on the website and in the CV.

---

## Local Preview

```bash
# Python one-liner — open http://localhost:8000
python -m http.server 8000
```

---

## Custom Domain (optional)

1. Buy a domain (e.g. `phuongnguyen.com`)
2. In repo root, create a file named `CNAME` containing just your domain:
   ```
   phuongnguyen.com
   ```
3. In your domain registrar, point DNS to GitHub Pages IPs:
   ```
   185.199.108.153
   185.199.109.153
   185.199.110.153
   185.199.111.153
   ```
