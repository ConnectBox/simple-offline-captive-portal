"""Captive portal text in the visitor's language.

The page text is kept in the box's interface translation files
(TRANSLATIONS_DIR/<code>.json, managed with the rest of the ConnectBox
interface strings by mmiLoader and shipped by connectbox-pi), under the
PORTAL_* keys below.  Each entry records the English it was translated from;
an entry whose English no longer matches is not used.

Language choice, the same rule as the ConnectBox menu: the first language in
the phone's Accept-Language header that the box has content in (exact code,
then the same base language: es-MX -> es, zh-TW -> zh), else the box's default
language (languages.json), else English.  The box's languages come from
LANGUAGES_JSON; when it cannot be read, every language with a translation
file counts.  A language with no translation for a string shows that string
in English.

Strings may hold {name} (box name), {url} (ConnectBox address) and {option}
(Android's menu item).  If a translation lost one of them, the value is added
at the end so nothing is missing.
"""
import json
import os
from markupsafe import Markup, escape

# The English page text.  Keep in step with PORTAL_* in mmiLoader.py
# (EXTRA_INTERFACE_STRINGS), which adds them to the translation files.
ENGLISH = {
    "PORTAL_TITLE": "Connected to {name} Wifi",
    "PORTAL_GO_TO": "Go to {url}",
    "PORTAL_TYPE_ADDRESS": "Type {url} in your browser",
    "PORTAL_OK": "OK",
    "PORTAL_NOT_CLOSING": "If this page does not close after OK,\ntap ⋮ (top right) and choose {option}.",
    # Android's own label for the menu item (CaptivePortalLogin
    # action_use_network): translations must use Android's wording
    "PORTAL_USE_AS_IS": "Use this network as is",
}

RTL_LANGUAGES = ("ar", "arc", "arz", "ckb", "dv", "fa", "he", "iw", "pnb", "ps", "sd", "ug", "ur", "yi")


def _base(code):
    return code.lower().split("-")[0].split("_")[0]


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _translation_files(translations_dir):
    """{lower-case code: path} of the translation files."""
    found = {}
    try:
        names = os.listdir(translations_dir)
    except OSError:
        return found
    for name in names:
        if name.endswith(".json") and not name.startswith("."):
            found[name[:-5].lower()] = os.path.join(translations_dir, name)
    return found


def _box_languages(languages_json):
    """([codes per language], default codes) from languages.json, or (None, None)."""
    data = _read_json(languages_json)
    if not isinstance(data, list):
        return None, None
    langs, default = [], None
    for entry in data:
        codes = [str(c).lower() for c in (entry.get("codes") or []) if c]
        if not codes:
            continue
        langs.append(codes)
        if entry.get("default") and default is None:
            default = codes
    if default is None and langs:
        default = langs[0]
    return langs, default


def choose_language(accept_languages, translations_dir, languages_json):
    """Return the language code to show (lower case; 'en' for English)."""
    files = _translation_files(translations_dir)
    box, default = _box_languages(languages_json)
    if box is None:                         # no menu yet: any translated language, else English
        box = [[code] for code in files] + [["en"]]
        default = ["en"]
    wanted = [str(w).lower() for w in accept_languages if w and w != "*"]
    chosen = None
    for w in wanted:
        for same in (lambda a, c: a == c, lambda a, c: _base(a) == _base(c)):
            for codes in box:
                if any(same(w, c) for c in codes):
                    chosen = (w, codes)
                    break
            if chosen:
                break
        if chosen:
            break
    if not chosen:
        chosen = (default[0], default)
    wanted_code, codes = chosen
    # A language's codes are its content folder first, then the codes phones
    # report for it (mmiLoader phone_codes: ["arb", "ar"], ["yue", "zh-HK"])
    bases = set(_base(c) for c in codes)
    if "en" in bases or "eng" in bases:
        return "en"
    # The translation file: one of the language's own codes (the most
    # specific first: zh-HK before zh), else the phone's code if it is the
    # same language, else another file of the same base language
    for candidate in sorted(codes, key=lambda c: -len(c)) + [wanted_code]:
        if candidate in files and _base(candidate) in bases:
            return candidate
    for code in sorted(files):
        if _base(code) in bases:
            return code
    return codes[0]                         # no translation file: English text, but marked with the language


def page_strings(code, translations_dir):
    """The PORTAL_* strings for a language (English where there is no current translation)."""
    strings = dict(ENGLISH)
    if code == "en":
        return strings
    path = _translation_files(translations_dir).get(code)
    data = _read_json(path) if path else None
    entries = (data or {}).get("strings") or {}
    for key, english in ENGLISH.items():
        entry = entries.get(key)
        if isinstance(entry, dict) and entry.get("en") == english and entry.get("text"):
            strings[key] = entry["text"]
    return strings


def fill(text, **values):
    """
    HTML for a string: escaped, line breaks as <br>, the menu symbol in bold,
    and each {placeholder} replaced by its (already safe) markup; a placeholder
    the translation lost is added at the end.
    """
    html = str(escape(text)).replace("\n", "<br>\n").replace("⋮", "<strong>&#8942;</strong>")
    for key, value in values.items():
        mark = "{" + key + "}"
        if mark in html:
            html = html.replace(mark, str(value))
        else:
            html = html + " " + str(value)
    return Markup(html)


def plain(text, **values):
    """Plain text for a string (title, alt text): placeholders replaced, no markup."""
    text = text.replace("\n", " ")
    for key, value in values.items():
        mark = "{" + key + "}"
        text = text.replace(mark, value) if mark in text else text + " " + value
    return text


def is_rtl(code):
    return _base(code) in RTL_LANGUAGES
