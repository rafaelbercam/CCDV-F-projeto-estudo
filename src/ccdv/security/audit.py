"""Módulo 05 — audit log em JSON Lines, sem conteúdo sensível.

Regras:
- Nunca grave a conversa inteira. Grave metadados: quem (hash), o quê, quando, tamanhos.
- ID de usuário entra como hash truncado, para correlacionar eventos sem expor o identificador.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Any


class AuditLog:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def record(self, user_id: str, action: str, **metadata: Any) -> None:
        entry = {
            "ts": time.time(),
            "user": hashlib.sha256(user_id.encode()).hexdigest()[:16],
            "action": action,
            **metadata,
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
