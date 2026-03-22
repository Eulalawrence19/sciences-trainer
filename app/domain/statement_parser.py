# app/domain/statement_parser.py

import re

def parse_statement(raw: str) -> tuple[str | None, str | None]:
    math_blocks = re.findall(r"\$\$(.*?)\$\$", raw, re.S)
    text = re.sub(r"\$\$.*?\$\$", "", raw, flags=re.S).strip()

    statement_text = text if text else None
    statement_math = "\n".join(m.strip() for m in math_blocks) if math_blocks else None

    return statement_text, statement_math