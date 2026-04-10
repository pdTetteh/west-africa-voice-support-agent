import re


WORD_RE = re.compile(r"\b[a-z0-9_]+\b")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "but",
    "by",
    "can",
    "do",
    "for",
    "from",
    "i",
    "if",
    "in",
    "is",
    "it",
    "my",
    "of",
    "on",
    "or",
    "so",
    "that",
    "the",
    "this",
    "to",
    "was",
    "with",
    "you",
    "your",
}

PHRASE_REPLACEMENTS = {
    "cash out": "cashout",
    "cash-out": "cashout",
    "log in": "login",
    "sign in": "login",
    "wrong person": "wrong_recipient",
    "wrong recipient": "wrong_recipient",
    "kyc": "identity_verification",
    "verify identity": "identity_verification",
    "identity verification": "identity_verification",
    "balance deducted": "deducted_balance",
    "money deducted": "deducted_balance",
}

TOKEN_SYNONYMS = {
    "cashout": {"cashout", "withdrawal", "withdraw", "cashout_issue"},
    "wrong_recipient": {"wrong_recipient", "recipient", "transfer", "transferred", "funds"},
    "identity_verification": {"identity_verification", "verification", "identity", "kyc"},
    "login": {"login", "signin", "access", "profile_access"},
    "locked": {"locked", "blocked", "restricted"},
    "account": {"account", "profile", "wallet"},
    "deducted_balance": {"deducted_balance", "deducted", "balance"},
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()

    for source, target in PHRASE_REPLACEMENTS.items():
        text = text.replace(source, target)

    text = re.sub(r"[^a-z0-9_\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    tokens = WORD_RE.findall(normalize_text(text))
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]


def expand_tokens(tokens: list[str]) -> list[str]:
    expanded: list[str] = []

    for token in tokens:
        expanded.append(token)
        for canonical, variants in TOKEN_SYNONYMS.items():
            if token == canonical or token in variants:
                expanded.append(canonical)
                expanded.extend(sorted(variants))

    seen: set[str] = set()
    ordered: list[str] = []

    for token in expanded:
        if token not in seen:
            seen.add(token)
            ordered.append(token)

    return ordered