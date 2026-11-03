from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Iterable, List, Optional


class JsonRepair:
    """Try to repair broken JSON config files and explain why repair was not possible."""

    def __init__(self):
        self.last_reason = ""

    def repair_text(self, text: str) -> Optional[Any]:
        if not text or not text.strip():
            return None

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            self.last_reason = self._describe_error(exc)

        for candidate in self._candidate_variants(text):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

            try:
                parsed = ast.literal_eval(candidate)
                return json.loads(json.dumps(parsed))
            except (ValueError, TypeError, SyntaxError):
                pass

        print(f"JSON repair failed: {self.last_reason}")
        return None

    def repair_file(self, path: str | Path) -> Optional[Any]:
        file_path = Path(path)

        try:
            raw_text = file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"JSON repair failed: file not found: {file_path}")
            return None

        repaired = self.repair_text(raw_text)
        if repaired is None:
            print(f"JSON repair failed for {file_path}: {self.last_reason}")
            return None

        file_path.write_text(json.dumps(repaired, indent=2, ensure_ascii=False), encoding="utf-8")
        return repaired

    def _describe_error(self, exc: json.JSONDecodeError) -> str:
        return f"{exc.msg} at line {exc.lineno}, column {exc.colno}"

    def _candidate_variants(self, text: str) -> List[str]:
        variants = []
        cleaned = text.strip()

        variants.append(cleaned)
        variants.append(re.sub(r"//.*?$", "", cleaned, flags=re.MULTILINE))
        variants.append(re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL))

        no_comments = re.sub(r"//.*?$", "", cleaned, flags=re.MULTILINE)
        no_comments = re.sub(r"/\*.*?\*/", "", no_comments, flags=re.DOTALL)
        variants.append(no_comments)

        for candidate in list(variants):
            fixed = re.sub(r",\s*([}\]])", r"\1", candidate)
            fixed = re.sub(r"(?<!['\"])(\b[A-Za-z_][A-Za-z0-9_]*\b)\s*:", r'"\1":', fixed)
            fixed = re.sub(r"\btrue\b", "true", fixed)
            fixed = re.sub(r"\bfalse\b", "false", fixed)
            fixed = re.sub(r"\bnull\b", "null", fixed)
            fixed = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', fixed)
            variants.append(fixed)

        deduped: List[str] = []
        seen = set()
        for variant in variants:
            if variant not in seen:
                deduped.append(variant)
                seen.add(variant)
        return deduped
