"""
scoring/keyword_extractor.py

Extracts normalized skill/keyword sets from resume or job description text,
matched against scoring/skills_dictionary.py's SKILLS_DB.

Public contract:
    extract_keywords(text: str) -> set[str]
        Returns the set of canonical skill names (as they appear in
        SKILLS_DB) detected in the input text.

Also provides a lightweight secondary signal:
    extract_secondary_terms(text: str) -> set[str]
        Returns additional capitalized/multi-word terms found in the text
        that are NOT already in SKILLS_DB.
"""

import re
from collections import Counter

from scoring.skills_dictionary import SKILLS_DB


# ---------------------------------------------------------------------------
# 1. Build the canonical skill set
# ---------------------------------------------------------------------------

def _flatten_skills_db(skills_db: dict) -> set[str]:
    """Return a flat set of every canonical skill string."""
    flat = set()

    for terms in skills_db.values():
        for term in terms:
            flat.add(term.lower().strip())

    return flat


CANONICAL_SKILLS = _flatten_skills_db(SKILLS_DB)


# ---------------------------------------------------------------------------
# 2. Alias / synonym map
# ---------------------------------------------------------------------------

ALIASES = {
    # JavaScript / Node ecosystem
    "js": "javascript",
    "nodejs": "node.js",
    "node js": "node.js",
    "node": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue.js",
    "vue": "vue.js",
    "angularjs": "angular",
    "expressjs": "express.js",
    "express": "express.js",
    "nextjs": "next.js",
    "next js": "next.js",

    # Databases
    "postgres": "postgresql",
    "mongo": "mongodb",
    "ms sql server": "sql server",
    "mssql": "sql server",
    "sql server db": "sql server",

    # Cloud / DevOps
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "k8s": "kubernetes",
    "aws cloud": "aws",

    # Frameworks
    "dotnet": ".net",
    ".net framework": ".net",
    "asp.net": ".net",
    "spring": "spring boot",

    # Data / AI-ML
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "tf": "tensorflow",
    "powerbi": "power bi",
    "power-bi": "power bi",
    "ml": "machine learning",
    "dl": "deep learning",
    "genai": "generative ai",
    "gen ai": "generative ai",
    "nlp techniques": "nlp",

    # Testing
    "pytest framework": "pytest",
    "qa testing": "qa",

    # Misc formatting variants
    "rest apis": "rest api",
    "restful api": "rest api",
    "html/css": "html",
    "c plus plus": "c++",
    "c sharp": "c#",
}


# ---------------------------------------------------------------------------
# 3. Build match table
# ---------------------------------------------------------------------------

def _build_match_table() -> list[tuple[str, str]]:
    """
    Return searchable-term / canonical-skill pairs.

    Longer terms are checked first so multi-word skills are handled correctly.
    """
    table = []

    # Canonical skills
    for skill in CANONICAL_SKILLS:
        table.append((skill, skill))

    # Aliases
    for alias, canonical in ALIASES.items():
        if canonical in CANONICAL_SKILLS:
            table.append((alias.lower().strip(), canonical))

    # Longest terms first
    table.sort(key=lambda pair: len(pair[0]), reverse=True)

    return table


_MATCH_TABLE = _build_match_table()


# ---------------------------------------------------------------------------
# 4. Regex-safe boundary matching
# ---------------------------------------------------------------------------

def _compile_term_pattern(term: str) -> re.Pattern:
    """
    Build a regex that matches a term as a standalone unit.

    Alphanumeric adjacency is used instead of \\b so terms containing
    punctuation such as c++, c#, .net, node.js and ci/cd work correctly.
    """

    escaped = re.escape(term)

    pattern = (
        r"(?<![a-zA-Z0-9])"
        + escaped
        + r"(?![a-zA-Z0-9])"
    )

    return re.compile(pattern, re.IGNORECASE)


_COMPILED_TABLE = [
    (_compile_term_pattern(term), canonical)
    for term, canonical in _MATCH_TABLE
]


# ---------------------------------------------------------------------------
# 5. Text normalization
# ---------------------------------------------------------------------------

def _normalize_text(text: str) -> str:
    """
    Lowercase the input and collapse whitespace.

    Punctuation is intentionally preserved because it matters for skills
    such as node.js, c++, c#, .net and ci/cd.
    """

    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------------------------------
# 6. Public contract
# ---------------------------------------------------------------------------

def extract_keywords(text: str) -> set[str]:
    """
    Detect and return canonical skill names found in the input text.

    Empty, None, or whitespace-only input safely returns an empty set.
    """

    normalized = _normalize_text(text)

    if not normalized:
        return set()

    found = set()

    for pattern, canonical in _COMPILED_TABLE:
        if pattern.search(normalized):
            found.add(canonical)

    return found


# ---------------------------------------------------------------------------
# 7. Secondary signal
# ---------------------------------------------------------------------------

_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "from",
    "have",
    "will",
    "are",
    "you",
    "your",
    "our",
    "their",
    "job",
    "role",
    "team",
    "work",
    "experience",
    "years",
    "using",
    "such",
    "into",
    "who",
    "able",
    "must",
    "strong",
    "good",
    "well",
    "including",
    "etc",
    "any",
    "all",
    "can",
}


def extract_secondary_terms(
    text: str,
    min_frequency: int = 1,
    max_terms: int = 15
) -> set[str]:
    """
    Extract lightweight secondary terms that are not already in SKILLS_DB.

    Uses simple regex and frequency heuristics only.
    No external NLP libraries or APIs are required.
    """

    if not text:
        return set()

    already_known = extract_keywords(text)

    # Capitalized single/multi-word terms
    capitalized_terms = re.findall(
        r"\b[A-Z][a-zA-Z0-9]*(?:\s[A-Z][a-zA-Z0-9]*){0,2}\b",
        text
    )

    # General word frequency
    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+.#/-]{2,}",
        text.lower()
    )

    word_counts = Counter(
        word for word in words
        if word not in _STOPWORDS
    )

    candidates = set()

    for term in capitalized_terms:
        norm = term.lower().strip()

        if (
            norm
            and norm not in already_known
            and len(norm) > 2
        ):
            candidates.add(term.strip())

    for word, count in word_counts.items():
        if (
            count >= min_frequency
            and word not in already_known
            and word not in _STOPWORDS
            and not word.isdigit()
        ):
            candidates.add(word)

    return set(list(candidates)[:max_terms])