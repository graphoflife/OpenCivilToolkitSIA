"""
Die Schichten des Kerns: was unten liegt, weiss nichts von dem, was darauf steht.

Der Querschnitt (``opencivil/querschnitt/``) rechnet Geometrie, Fasern und
Werkstoffgesetze; die Nachweise, das Projekt, der Dienst und die
Spannung-Dehnung-Analyse stehen darauf. Importierte der Querschnitt aus
ihnen, hinge er an Entscheidungen, die über ihm fallen -- und ein Ring von
Importen liesse sich nur mit einem Import in der Funktion umgehen, wie es
bis 2026-10-17 geschah.
"""

import ast
import pathlib
import unittest

WURZEL = pathlib.Path(__file__).resolve().parents[1]

#: Was über dem Querschnitt steht.
DARUEBER = ("opencivil.nachweis", "opencivil.projekt", "opencivil.web",
            "opencivil.spannungsanalyse", "opencivil.bericht", "opencivil.bewehrungssuche")

#: Die Schnittanalyse zieht als Nächstes zur Spannung-Dehnung-Analyse; bis
#: dahin steht sie noch hier.
NOCH_NICHT = {"schnittanalyse.py"}


def importe(pfad: pathlib.Path):
    """Jedes Modul, das die Datei importiert -- auch in Funktionen und unter TYPE_CHECKING."""
    for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
        if isinstance(knoten, ast.Import):
            yield from (a.name for a in knoten.names)
        elif isinstance(knoten, ast.ImportFrom) and knoten.module:
            yield knoten.module
            if knoten.module == "opencivil":
                yield from (f"opencivil.{a.name}" for a in knoten.names)


class TestSchichten(unittest.TestCase):
    def test_der_querschnitt_importiert_nichts_von_darueber(self):
        for pfad in sorted((WURZEL / "opencivil" / "querschnitt").glob("*.py")):
            if pfad.name in NOCH_NICHT:
                continue
            for modul in importe(pfad):
                with self.subTest(datei=pfad.name, modul=modul):
                    self.assertFalse(
                        any(modul == d or modul.startswith(d + ".") for d in DARUEBER),
                        f"{pfad.name} importiert {modul}")


if __name__ == "__main__":
    unittest.main()
