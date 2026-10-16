"""
opencivil/projekt/skript.py -- ein Python-Skript der App «Python», wie es
gespeichert wird.

VERANTWORTUNG:
Kennung, Name und Code. Ausgeführt wird es nicht im Rechenkern, sondern in
der Konsole der Oberfläche (:mod:`opencivil.konsole`); was es ausgibt, steht
in keinem Bericht. Gespeichert wird es mit dem Projekt, damit es beim
nächsten Öffnen wieder da ist (Benutzer, 2026-10-15).
"""

from __future__ import annotations

from dataclasses import dataclass

from opencivil.projekt.eintraege import Beschreibung

#: Was ein neues Skript schon enthält: ein Diagramm ohne Download -- numpy
#: und pandas kosten beim ersten Einbinden ein paar Megabyte.
VORLAGE = '''# Python im Browser: die Standardbibliothek, numpy, pandas und opencivil.
# Strg+Enter führt aus; die Variablen stehen rechts.
import zeichnen as plt

x = [i / 10 for i in range(31)]
y = [v ** 2 for v in x]

plt.plot(x, y, label="y = x²")
plt.xlabel("x")
plt.ylabel("y")
plt.grid()
plt.legend()
'''


@dataclass
class SkriptEintrag(Beschreibung):
    """Ein Skript: Name und Code."""

    BEZEICHNUNG = "Skript"

    kennung: str
    name: str = ""
    code: str = ""

    @classmethod
    def neu(cls, kennung: str, name: str) -> "SkriptEintrag":
        """Ein neues Skript, mit der :data:`VORLAGE` darin."""
        return cls(kennung=kennung, name=name, code=VORLAGE)
