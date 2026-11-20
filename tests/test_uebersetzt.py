"""
Das Übersetzte des Kerns für den nächsten Start (opencivil/web/uebersetzt.py):
Python nimmt ein eingesetztes .pyc, solange es zu seiner Quelle passt -- und
nur dann, auch wenn die Quelle gleich gross und gleich alt bleibt.
"""

import importlib.util
import marshal
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from opencivil.web.uebersetzt import einsetzen, packen

#: Zwei Zeitpunkte, zu denen die Seite startet, in Sekunden seit 1970.
FRUEHER, SPAETER = 1_700_000_000, 1_800_000_000


def anlegen(wurzel: Path, quellen: dict, zeit: int) -> None:
    """Legt die Quellen an, wie der Faden der Seite bei jedem Start, alle zur selben Zeit."""
    for name, text in quellen.items():
        pfad = wurzel / name
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(text, encoding="utf-8")
        os.utime(pfad, (zeit, zeit))


def uebersetzen(wurzel: Path, *namen: str) -> None:
    """Wie Python beim Einbinden: je Quelle ein .pyc, an Zeit und Grösse geprüft."""
    for quelle in [wurzel / name for name in namen] or sorted(wurzel.rglob("*.py")):
        py_compile.compile(
            str(quelle), cfile=pyc_von(quelle), doraise=True,
            invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)


def pyc_von(quelle: Path) -> str:
    return importlib.util.cache_from_source(str(quelle))


def einbinden(wurzel: Path, modul: str) -> tuple:
    """
    Bindet ``modul`` in einem frischen Python ein, ohne etwas zu schreiben:
    was es von ``WERT`` druckt, und ob es dafür das .pyc nahm.
    """
    lauf = subprocess.run(
        [sys.executable, "-v", "-c",
         f"import sys; sys.path.insert(0, {str(wurzel)!r}); import {modul}; print({modul}.WERT)"],
        capture_output=True, text=True, check=True, cwd=wurzel,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return lauf.stdout.strip(), f"{pyc_von(wurzel / f'{modul}.py')} matches" in lauf.stderr


class TestUebersetzt(unittest.TestCase):

    def setUp(self):
        ordner = tempfile.TemporaryDirectory()
        self.addCleanup(ordner.cleanup)
        self.ordner = Path(ordner.name)
        self.stueck = self.ordner / "stueck"

    def besuch(self, name: str, quellen: dict, zeit: int) -> Path:
        """Ein Start der Seite: die Quellen frisch angelegt, noch nichts eingebunden."""
        wurzel = self.ordner / name
        anlegen(wurzel, quellen, zeit)
        return wurzel

    def namen_im_stueck(self) -> list:
        with open(self.stueck, "rb") as datei:
            return sorted(marshal.load(datei))

    def test_dieselbe_quelle_nimmt_das_uebersetzte_vom_letzten_besuch(self):
        """Auch wenn die Quelle beim zweiten Besuch eine andere Zeit trägt."""
        erster = self.besuch("erster", {"probe.py": "WERT = 1\n"}, FRUEHER)
        uebersetzen(erster)
        self.assertTrue(packen(self.stueck, erster))
        zweiter = self.besuch("zweiter", {"probe.py": "WERT = 1\n"}, SPAETER)
        self.assertEqual(einsetzen(self.stueck, zweiter), 1)
        self.assertEqual(einbinden(zweiter, "probe"), ("1", True))

    def test_eine_geaenderte_ziffer_wird_neu_uebersetzt(self):
        """Gleich gross, gleich alt: an Zeit und Grösse geprüft, liefe still der alte Code."""
        erster = self.besuch("erster", {"probe.py": "WERT = 1\n"}, FRUEHER)
        uebersetzen(erster)
        packen(self.stueck, erster)
        zweiter = self.besuch("zweiter", {"probe.py": "WERT = 2\n"}, FRUEHER)
        einsetzen(self.stueck, zweiter)
        self.assertEqual(einbinden(zweiter, "probe"), ("2", False))

    def test_ins_stueck_kommt_nur_was_zu_den_quellen_passt(self):
        wurzel = self.besuch("baum", {
            "bleibt.py": "WERT = 1\n", "geaendert.py": "WERT = 1\n",
            "geloescht.py": "WERT = 1\n", "paket/__init__.py": "",
        }, FRUEHER)
        uebersetzen(wurzel)
        (wurzel / "geaendert.py").write_text("WERT = 22\n", encoding="utf-8")
        (wurzel / "geloescht.py").unlink()
        # Übersetzt von einer anderen Fassung von Python: ein anderer Anfang.
        fremd = Path(pyc_von(wurzel / "bleibt.py")).with_name("bleibt.cpython-299.pyc")
        fremd.write_bytes(b"\0\0\r\n" + Path(pyc_von(wurzel / "bleibt.py")).read_bytes()[4:])
        packen(self.stueck, wurzel)
        self.assertEqual(self.namen_im_stueck(), sorted(
            Path(pyc_von(wurzel / name)).relative_to(wurzel).as_posix()
            for name in ("bleibt.py", "paket/__init__.py")))

    def test_unveraendert_gibt_es_nichts_abzulegen(self):
        erster = self.besuch("erster", {"probe.py": "WERT = 1\n"}, FRUEHER)
        uebersetzen(erster)
        self.assertTrue(packen(self.stueck, erster))
        self.assertFalse(packen(self.stueck, erster))
        zweiter = self.besuch("zweiter", {"probe.py": "WERT = 1\n"}, SPAETER)
        einsetzen(self.stueck, zweiter)
        self.assertFalse(packen(self.stueck, zweiter))
        anlegen(zweiter, {"neu.py": "WERT = 3\n"}, SPAETER)
        uebersetzen(zweiter, "neu.py")
        self.assertTrue(packen(self.stueck, zweiter))
        self.assertEqual(len(self.namen_im_stueck()), 2)

    def test_ein_unlesbares_stueck_wird_neu_geschrieben(self):
        wurzel = self.besuch("baum", {"probe.py": "WERT = 1\n"}, FRUEHER)
        uebersetzen(wurzel)
        self.stueck.write_bytes(b"kein marshal")
        self.assertTrue(packen(self.stueck, wurzel))
        self.assertEqual(len(self.namen_im_stueck()), 1)


if __name__ == "__main__":
    unittest.main()
