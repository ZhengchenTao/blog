"""Convert ASCII punctuation to Chinese punctuation in CJK context.

Strategy:
  - Skip fenced code blocks entirely.
  - Mask out inline code, markdown links, bare URLs as opaque blobs (placeholder
    char from the Private Use Area), so paren matching can span them.
  - Process YAML front matter only by converting `description:` / `title:` /
    `summary:` string values — leaves `tags: [...]` arrays alone.
  - For each prose line in the body, decide if it's "Chinese-flavored" (>= 3 CJK
    chars). On Chinese lines, convert ASCII , . : ; ? ! ( ) → Chinese
    counterparts where it makes sense.

Preservation rules (kept as ASCII):
  - Number lists / decimals: `1,234`, `RS(255, 239)`, `1:8` (ratio).
  - Math context: a comma/colon between two math expressions (one of `∇ ∂ √
    ≡ ≈ ± ¹²³⁴⁵⁶⁷⁸⁹⁰ ₀₁₂₃₄₅₆₇₈₉` or Greek letters within a 20-char window
    on each side).
  - Nested inside an existing Chinese paren: only converts prose-like content
    (no math/digit indicator), preserving notation like `（GF(2⁸) 列混合）`.
  - English-attached parens: `DNS(Domain Name System)` (the `(` immediately
    follows an English letter/digit) stays ASCII.
  - Inside ASCII parens we chose to keep ASCII (e.g. `cookie(Ch8, Ch9)`),
    inner punctuation stays ASCII.

Usage:
  python scripts/cn-punct.py path/to/file1.md path/to/file2.md ...

This is the one-shot conversion script used in the 2026-05 blog cleanup. It is
deliberately conservative; if you re-run it on already-converted files it
should be a near no-op.
"""
import re
import sys

CJK_RE = re.compile(r'[一-鿿]')
PLACEHOLDER = ''  # private-use char for opaque blobs

# Walk past these to find the "real" neighbor of a punctuation mark.
WEAK = set(' \t*_"\'`)]}>“”‘’')

# Punctuation that signals Chinese context for adjacent ASCII punctuation.
CHINESE_PUNCT = set(
    '，。：；？！、（）'
    '【】「」『』'
    '“”‘’…—《》〈〉'
)

# Math-specific characters: superscript / subscript digits, operators, Greek
# letters that almost only appear in formulas. Used to detect comma/colon
# sitting between two math expressions (where it must stay ASCII).
MATH_CHARS = set(
    '∇∂√≡≈±'
    '¹²³⁴⁵⁶⁷⁸⁹⁰'
    '₀₁₂₃₄₅₆₇₈₉'
    'αβγδεζηθικ'
    'λμνξπρστυφ'
    'χψω'
    'ΓΔΘΛΞΠΣΦΨΩ'
    '∞∑∏∫·×÷'
)


def is_cjk(ch: str) -> bool:
    return bool(ch and CJK_RE.match(ch))


def is_chinese_context(ch: str) -> bool:
    return is_cjk(ch) or (ch in CHINESE_PUNCT)


def is_ascii_alnum(ch: str) -> bool:
    return bool(ch) and ord(ch) < 128 and ch.isalnum()


def find_strong_neighbor(text: str, idx: int, direction: int) -> str:
    """Walk past WEAK chars to find the nearest 'strong' character, or '' if
    we hit a boundary."""
    n = len(text)
    i = idx + direction
    while 0 <= i < n:
        ch = text[i]
        if ch in WEAK:
            i += direction
            continue
        return ch
    return ''


def looks_like_math_context(text: str, idx: int, window: int = 20) -> bool:
    """Heuristic: comma at idx is between two math expressions if both sides
    contain math-specific characters within a small window."""
    left_window = text[max(0, idx - window):idx]
    right_window = text[idx + 1:idx + 1 + window]
    return (
        any(c in MATH_CHARS for c in left_window)
        and any(c in MATH_CHARS for c in right_window)
    )


def convert_parens(text: str, aggressive: bool, depth_offset: int = 0) -> str:
    """Convert ( ) to （ ） when in Chinese context.

    Tracks Chinese-paren depth so that a paren nested inside an outer Chinese
    paren only converts if its own content contains CJK — preserves math
    notation like `（GF(2⁸) 列混合）`.

    Skips conversion when the immediate preceding char is an English letter or
    digit (e.g. `DNS(Domain Name System)`), since such parens behave like a
    function call / abbreviation expansion in the source language.
    """
    n = len(text)
    out = []
    i = 0
    cn_depth = depth_offset
    while i < n:
        ch = text[i]
        if ch == '（':  # （
            cn_depth += 1
            out.append(ch)
            i += 1
            continue
        if ch == '）':  # ）
            cn_depth = max(0, cn_depth - 1)
            out.append(ch)
            i += 1
            continue
        if ch == '(':
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if text[j] == '(':
                    depth += 1
                elif text[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth == 0:
                content = text[i + 1:j]
                left = find_strong_neighbor(text, i, -1)
                right = find_strong_neighbor(text, j, +1)
                immediate_prev = text[i - 1] if i > 0 else ''
                content_has_cjk = bool(CJK_RE.search(content))
                neighbor_chinese = (
                    is_chinese_context(left) or is_chinese_context(right)
                )
                content_has_math = bool(re.search(
                    r'[\d=+\-*/×÷^¹²³⁴-⁹⁰₀-₉]',
                    content,
                ))

                if cn_depth > 0:
                    # Nested inside Chinese paren — convert prose-like content
                    should_convert = content_has_cjk or not content_has_math
                elif is_ascii_alnum(immediate_prev):
                    # Attached to English identifier — leave ASCII
                    should_convert = content_has_cjk
                else:
                    should_convert = (
                        content_has_cjk
                        or (aggressive and neighbor_chinese)
                    )

                inner_offset = cn_depth + (1 if should_convert else 0)
                converted_content = convert_parens(content, aggressive, inner_offset)

                if should_convert:
                    out.append('（')
                    out.append(converted_content)
                    out.append('）')
                else:
                    out.append('(')
                    out.append(converted_content)
                    out.append(')')
                i = j + 1
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def convert_punct(text: str, aggressive: bool) -> str:
    """Convert ASCII , . : ; ? ! to Chinese counterparts.

    Tracks both Chinese-paren depth and ASCII-paren depth:
      - Inside `（...）` → aggressive (those are Chinese parentheticals).
      - Inside `(...)` → conservative (the surviving ASCII parens were kept
        ASCII for a reason — likely English-attached or notation).
    """
    chars = list(text)
    n = len(chars)
    out = []
    cn_paren_depth = 0
    ascii_paren_depth = 0
    for i, ch in enumerate(chars):
        if ch == '（':
            cn_paren_depth += 1
            out.append(ch)
            continue
        if ch == '）':
            cn_paren_depth = max(0, cn_paren_depth - 1)
            out.append(ch)
            continue
        if ch == '(':
            ascii_paren_depth += 1
            out.append(ch)
            continue
        if ch == ')':
            ascii_paren_depth = max(0, ascii_paren_depth - 1)
            out.append(ch)
            continue

        prev = chars[i - 1] if i > 0 else ''
        nxt = chars[i + 1] if i + 1 < n else ''
        in_cn_paren = cn_paren_depth > 0
        in_ascii_paren = ascii_paren_depth > 0

        if ch == ',':
            # Number-list separator: digit, [space,] digit → keep ASCII
            prev_is_digit = prev.isascii() and prev.isdigit()
            after_space_nxt = chars[i + 2] if (nxt == ' ' and i + 2 < n) else nxt
            nxt_is_digit = (
                after_space_nxt
                and after_space_nxt.isascii()
                and after_space_nxt.isdigit()
            )
            if prev_is_digit and nxt_is_digit:
                out.append(ch)
                continue
            if looks_like_math_context(text, i):
                out.append(ch)
                continue
            if is_chinese_context(prev) or is_chinese_context(nxt):
                out.append('，')
                continue
            if in_ascii_paren:
                out.append(ch)
                continue
            if in_cn_paren or aggressive:
                out.append('，')
                continue
        elif ch == '.':
            if is_ascii_alnum(nxt):
                pass  # decimal / file ext / version
            elif is_chinese_context(prev):
                out.append('。')
                continue
            elif prev in WEAK:
                left = find_strong_neighbor(text, i, -1)
                if is_chinese_context(left):
                    out.append('。')
                    continue
        elif ch in (':', ';', '?', '!'):
            mapping = {':': '：', ';': '；', '?': '？', '!': '！'}
            if ch == ':':
                # Ratio / time notation like "1:8" or "12:34" → keep ASCII colon
                prev_is_digit = prev.isascii() and prev.isdigit()
                nxt_is_digit = nxt.isascii() and nxt.isdigit()
                if prev_is_digit and nxt_is_digit:
                    out.append(ch)
                    continue
            if ch in (':', ';') and looks_like_math_context(text, i):
                out.append(ch)
                continue
            left = find_strong_neighbor(text, i, -1)
            right = find_strong_neighbor(text, i, +1)
            if is_chinese_context(left) or is_chinese_context(right):
                out.append(mapping[ch])
                continue
            if in_ascii_paren:
                out.append(ch)
                continue
            if in_cn_paren or aggressive:
                out.append(mapping[ch])
                continue
        out.append(ch)
    return ''.join(out)


def line_is_chinese(line: str) -> bool:
    """Heuristic: does this line have enough CJK to call it 'Chinese-flavored'?"""
    cjk_count = sum(1 for c in line if is_cjk(c))
    return cjk_count >= 3


def process_text(text: str, aggressive: bool) -> str:
    return convert_punct(convert_parens(text, aggressive), aggressive)


# Markdown image, markdown link, bare URL, or inline code (in this priority)
OPAQUE_RE = re.compile(
    r'!?\[[^\]]*\]\([^\)]+\)'
    r'|https?://[^\s\)\]\>]+'
    r'|`[^`\n]+`'
)
FENCE_RE = re.compile(r'(```[\s\S]*?```)')


def process_segment(segment: str, aggressive: bool) -> str:
    """Mask opaque blobs, run conversions, restore (recursively processing
    markdown link text)."""
    saved = []

    def stash(m: re.Match) -> str:
        saved.append(m.group(0))
        return PLACEHOLDER

    masked = OPAQUE_RE.sub(stash, segment)
    converted = process_text(masked, aggressive)

    out = []
    idx = 0
    for ch in converted:
        if ch == PLACEHOLDER:
            tok = saved[idx]
            idx += 1
            m = re.match(r'(!?\[)([^\]]*)(\]\()([^\)]+)(\))', tok)
            if m:
                inside = process_text(m.group(2), aggressive)
                tok = m.group(1) + inside + m.group(3) + m.group(4) + m.group(5)
            out.append(tok)
        else:
            out.append(ch)
    return ''.join(out)


def process_body_segment(segment: str) -> str:
    """Process a non-fenced body segment line by line, choosing aggressive mode
    based on whether each logical line is Chinese-flavored."""
    lines = segment.split('\n')
    out_lines = []
    for line in lines:
        out_lines.append(process_segment(line, aggressive=line_is_chinese(line)))
    return '\n'.join(out_lines)


def process_yaml_frontmatter(text: str) -> str:
    """Convert only quoted string values for description / title / summary keys.
    Leaves list/array values like `tags: [...]` alone."""
    def replace_value(m: re.Match) -> str:
        prefix, value, suffix = m.group(1), m.group(2), m.group(3)
        return prefix + process_segment(value, aggressive=line_is_chinese(value)) + suffix

    return re.sub(
        r'^(\s*(?:description|title|summary):\s*")([^"\n]*)(")',
        replace_value,
        text,
        flags=re.MULTILINE,
    )


def process_markdown(content: str) -> str:
    front = ''
    body = content
    if content.startswith('---\n') or content.startswith('---\r\n'):
        m = re.match(r'(---\r?\n[\s\S]*?\r?\n---\r?\n)', content)
        if m:
            front = m.group(1)
            body = content[m.end():]

    front = process_yaml_frontmatter(front)

    parts = FENCE_RE.split(body)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # fenced code block
            out.append(part)
        else:
            out.append(process_body_segment(part))
    return front + ''.join(out)


def main() -> None:
    changed = []
    for path in sys.argv[1:]:
        with open(path, encoding='utf-8', newline='') as f:
            content = f.read()
        new_content = process_markdown(content)
        if new_content != content:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                f.write(new_content)
            changed.append(path)
            print(f'updated {path}')
        else:
            print(f'unchanged {path}')
    print(f'\nTotal updated: {len(changed)}')


if __name__ == '__main__':
    main()
