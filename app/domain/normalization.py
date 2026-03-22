#normalization.py
def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.upper()
    for ch in [" ", "\t", "\n", "(", ")", "[", "]"]:
        s = s.replace(ch, "")
    return s


def normalize_equation(s: str) -> str:
    if not s:
        return ""
    s = normalize_text(s)
    return (
        s.replace("*", "X")
         .replace("·", "X")
         .replace("×", "X")
    )