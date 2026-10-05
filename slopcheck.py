#!/usr/bin/env python3
"""Lint prose for AI-slop tells and give it a score.

    ./slopcheck.py                 # score this repo
    ./slopcheck.py --list          # show every hit
    ./slopcheck.py FILE [FILE...]  # score specific files

Scans Markdown prose and Python docstrings/comments. Skips fenced code, ASCII
diagrams and inline code, because a literal "many flows" in a sentence about
many flows is not the same claim as "many developers". Also skips .venv and
other vendored trees, which are nobody's prose.

Every rule carries both English and Spanish patterns, because this repo's code
is English and its essays are Spanish, and slop sounds the same in both.

Calibration, measured with this script:

    Beej's Guide to C           1.6 em-dash/1k,  3.0 hits/1k
    Bert Hubert, SO_LINGER      0.0 em-dash/1k,  1.7 hits/1k
    this repo, first draft     11.1 em-dash/1k,  4.2 hits/1k
"""

import re
import sys
import pathlib

# Each rule is (name, pattern, why). Patterns are matched case-insensitively
# against prose lines only.
RULES = [
    ("fake_insight", r"\b(this is what (trips|confuses)|trips (most )?people"
                     r"|confuses (most )?people|catches (you|people) out"
                     r"|worth (knowing|noting|remembering)|be warned"
                     r"|it is important to (note|remember)|crucial to note"
                     r"|at its core|in essence|simply put|the key insight"
                     r"|needless to say"
                     r"|aquí (está|viene) (el truco|la clave|lo)"
                     r"|(ahí|aquí) está la clave|la clave (está|es) en"
                     r"|lo esencial es|en esencia|en el fondo"
                     r"|cabe (destacar|señalar|notar)"
                     r"|es importante (notar|señalar|recordar|destacar)"
                     r"|conviene (notar|señalar|recordar)"
                     r"|merece la pena (notar|destacar|señalar|ver)"
                     r"|ni que decir|el detalle que)\b",
     "insight signalled rather than delivered"),

    ("dramatic_signoff", r"\b(in conclusion|ultimately|the bottom line"
                         r"|at the end of the day|the whole (point|trick|lesson|story)"
                         r"|if you (remember|take) (only )?one thing"
                         r"|that is the (entire|whole) point|earns its keep"
                         r"|en conclusión|en resumen|a fin de cuentas"
                         r"|al final del día|la moraleja|y ya está|eso es todo"
                         r"|es todo\.|todo el (asunto|secreto)"
                         r"|si te llevas (una sola|sólo una|solo una) cosa"
                         r"|ahí está(,| el| la)|ese es (todo el|el) (punto|truco))\b",
     "summary flourish instead of a stop"),

    ("unsourced_claim", r"\b(half (of )?the \w+|most people|many (experts|developers|people)"
                        r"|the most common \w+|the biggest \w+|everyone knows"
                        r"|the classic (error|mistake|bug)|notoriously|famously"
                        r"|better than most|read better than"
                        r"|casi (todas?|todos?) (las|los) \w+"
                        r"|la mayoría de (la gente|las personas)"
                        r"|todo el mundo (sabe|lee|cree)|a todo el mundo le"
                        r"|es (muy )?común (leer|oír|escuchar)"
                        r"|se suele (contar|decir|leer)"
                        r"|el (error|fallo) más común|la confusión más común"
                        r"|notoriamente|célebre|famoso por)\b",
     "claim about the world with no source"),

    ("prophecy", r"\b(you will find out|you'?ll (spend|end up|discover|regret)"
                 r"|sooner or later|trust me|mark my words"
                 r"|ya lo verás|tarde o temprano|créeme"
                 r"|te vas a (encontrar|dar cuenta)|acabarás)\b",
     "predicting the reader's future"),

    ("counting_frame", r"\b(two|three|four|five) (things|words|reasons|ways|points"
                       r"|rules|facts|lessons|takeaways)"
                       r"|\b(dos|tres|cuatro|cinco) (cosas|palabras|razones|maneras"
                       r"|formas|puntos|reglas|hechos|lecciones|ideas|motivos|claves)\b",
     "makes the reader count; say the thing instead"),

    ("filler", r"\b(genuinely|obviously|of course|arguably|essentially|basically"
               r"|in practice|needless|it goes without saying|quite frankly"
               r"|obviamente|por supuesto|evidentemente|básicamente"
               r"|esencialmente|sin duda|la verdad es que|ciertamente"
               r"|francamente|en la práctica|desde luego|como es sabido)\b",
     "adds no information"),

    ("warmup", r"^(here is|here's) (a|an|the) (breakdown|overview|rundown|summary)"
               r"|^(in today'?s|in the world of|let'?s (dive|talk|explore))"
               r"|^(first,? )?(a )?(quick )?(word|note) (about|on)\b"
               r"|^(en el mundo de|hoy en día|vamos a (hablar|ver|contar)"
               r"|antes de (nada|empezar)|empecemos por"
               r"|una (nota|palabra) sobre|nota sobre)\b",
     "clears its throat before starting"),
]

# Trees that hold no prose of ours.
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__",
             ".pytest_cache", ".mypy_cache", "site-packages"}

FENCE = re.compile(r"^\s*```")
DIAGRAM = re.compile(r"[┌┐└┘├┤┬┴┼│─►▼▲╔╗╚╝║═╢╟⏰]")
INLINE_CODE = re.compile(r"`[^`]*`")
MD_LINK = re.compile(r"\]\([^)]*\)")

# Hits that are correct as written. Each entry is (file, rule, snippet, why).
ALLOW = [
    ("slopcheck.py", None, None, "the linter quotes the patterns it bans"),
    ("README.md", "unsourced_claim", "half the synodic",
     "literal: 14.77 d really is half of the 29.53 d synodic month"),
    ("docs/06-de-la-teoria-al-puerto.md", "fake_insight", "~16 m en el fondo",
     "literal: the head of the bay, not a rhetorical 'deep down'"),
    ("docs/07-el-solent.md", "counting_frame", "dos razones que se refuerzan",
     "literal: both are named on the next two lines"),
    ("docs/08-el-teorema-virial.md", "counting_frame", "tres formas de convencerse",
     "literal: all three follow immediately"),
    ("docs/09-estabilidad.md", "counting_frame", "dos hechos independientes",
     "literal: both are named in the same sentence"),
]


def allowed(path, rule, line):
    for f, r, snip, _ in ALLOW:
        if not path.endswith(f):
            continue
        if r is None:
            return True
        if r == rule and snip and snip.lower() in line.lower():
            return True
    return False


def prose_lines(path):
    """Yield (lineno, text) for lines that are prose, not code or diagrams."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    md = path.endswith(".md")
    in_fence = False
    in_doc = False
    for n, raw in enumerate(text.splitlines(), 1):
        if md:
            if FENCE.match(raw):
                in_fence = not in_fence
                continue
            if in_fence or DIAGRAM.search(raw):
                continue
            line = raw
        else:
            # Python: docstrings and comments only.
            stripped = raw.strip()
            if stripped.count('"""') == 1:
                in_doc = not in_doc
                line = stripped.replace('"""', "")
            elif in_doc:
                line = raw
            elif stripped.startswith("#"):
                line = stripped.lstrip("# ")
            else:
                continue
        line = MD_LINK.sub("", INLINE_CODE.sub("", line))
        if line.strip():
            yield n, line


def scan(paths):
    hits, words, emdash = [], 0, 0
    for p in paths:
        for n, line in prose_lines(p):
            words += len(line.split())
            emdash += line.count("—")
            for name, pat, why in RULES:
                for m in re.finditer(pat, line, re.I | re.M):
                    if allowed(p, name, line):
                        continue
                    hits.append((p, n, name, m.group(0).strip(), line.strip(), why))
    return hits, words, emdash


def report(paths, show_all=False):
    hits, words, emdash = scan(paths)
    per_k = lambda x: round(x / words * 1000, 1) if words else 0.0

    by_rule = {}
    for h in hits:
        by_rule.setdefault(h[2], []).append(h)

    print(f"prose words scanned: {words}")
    print(f"em-dash per 1k:      {per_k(emdash)}   (Beej 1.6, Hubert 0.0)")
    print(f"slop hits per 1k:    {per_k(len(hits))}   (Beej 3.0, Hubert 1.7)")
    print()
    for name, _, why in RULES:
        got = by_rule.get(name, [])
        mark = "   " if not got else "!! "
        print(f"  {mark}{name:18} {len(got):3}   {why}")
    if hits and (show_all or len(hits) <= 20):
        print()
        for p, n, name, frag, line, _ in hits:
            print(f"  {p}:{n}  [{name}] {frag!r}")
            print(f"      {line[:96]}")
    return len(hits), per_k(len(hits)), per_k(emdash)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    show = "--list" in sys.argv
    if args:
        paths = args
    else:
        root = pathlib.Path(__file__).parent
        paths = sorted(
            p.as_posix() for p in list(root.rglob("*.md")) + list(root.rglob("*.py"))
            if not any(part in SKIP_DIRS for part in p.parts))
    n, rate, em = report(paths, show)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
