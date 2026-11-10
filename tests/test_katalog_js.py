"""
Was die Oberflaeche im Katalog liest, gibt es dort: jeder Pfad, den
``web/js`` an ``katalog(...)`` gibt, jede Art, nach der ``feldangabe`` und
``ausVorlage`` fragen, und je Liste des Projekts die Vorlage, die
``nachVorlage`` nimmt.

Die Oberflaeche wirft, wenn ein Schluessel fehlt (``katalog`` in
``web/js/zustand.js``), statt still einen leeren Schalter zu zeigen. Damit
das nicht erst beim Klicken auffaellt, liest dieser Test die Aufrufe aus dem
Quelltext und schlaegt jeden Pfad im Katalog des Kerns nach -- so weit er aus
festen Texten besteht. Ein umbenannter Schluessel im Kern faellt hier auf.
"""

import re
import unittest
from pathlib import Path

from opencivil.web.api import katalog

WURZEL = Path(__file__).resolve().parents[1]

#: Ein Aufruf mit seinen Argumenten bis zur schliessenden Klammer -- ohne
#: verschachtelte Klammern, die stehen bei diesen Aufrufen nicht.
AUFRUF = r"(?<![.\w]){name}\(([^()]*)\)"


def aufrufe(name):
    """Je Datei und Aufruf die Argumente, als Liste von Texten."""
    for pfad in sorted((WURZEL / "web" / "js").glob("*.js")):
        quelltext = re.sub(r"//[^\n]*|/\*.*?\*/", "", pfad.read_text(encoding="utf-8"),
                           flags=re.S)
        for m in re.finditer(AUFRUF.format(name=name), quelltext):
            yield pfad.name, [a.strip() for a in m.group(1).split(",") if a.strip()]


def feste_teile(argumente):
    """Die Argumente von vorn, solange sie feste Texte sind."""
    teile = []
    for a in argumente:
        m = re.fullmatch(r"'([^']*)'", a)
        if not m:
            break
        teile.append(m.group(1))
    return teile


class TestKatalogpfade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.katalog = katalog()

    def nachschlagen(self, pfad):
        wert = self.katalog
        for i, schluessel in enumerate(pfad):
            self.assertIsInstance(wert, dict, f"{'.'.join(pfad[:i])} ist kein Verzeichnis")
            self.assertIn(schluessel, wert, f"Im Katalog fehlt {'.'.join(pfad[:i + 1])}")
            wert = wert[schluessel]

    def test_jeder_pfad_von_katalog(self):
        gefunden = list(aufrufe("katalog"))
        self.assertGreater(len(gefunden), 30)
        for datei, argumente in gefunden:
            pfad = feste_teile(argumente)
            with self.subTest(datei=datei, pfad=pfad):
                self.nachschlagen(pfad)

    def test_feldangaben_und_vorlagen(self):
        """Die Art als festes Argument -- dazu die Vorlagen, die ein Ort nennt (`vorlage: '…'`)."""
        for muster, wurzel in ((r"(?<![.\w])feldangabe\(\s*'(\w+)'", "felder"),
                               (r"(?<![.\w])ausVorlage\(\s*'(\w+)'", "vorlagen"),
                               (r"\bvorlage: '(\w+)'", "vorlagen")):
            arten = {(pfad.name, m.group(1))
                     for pfad in (WURZEL / "web" / "js").glob("*.js")
                     for m in re.finditer(muster, pfad.read_text(encoding="utf-8"))}
            self.assertTrue(arten, muster)
            for datei, art in sorted(arten):
                with self.subTest(datei=datei, art=art):
                    self.nachschlagen([wurzel, art])

    def test_jede_liste_hat_ihre_vorlage(self):
        """Ein neuer Eintrag nimmt die Vorlage seiner Liste (`nachVorlage`, apps.js)."""
        from opencivil.projekt.aufbau import BAUTEILE
        self.assertEqual(set(self.katalog["neu"]),
                         {art.liste for art in BAUTEILE} | {"skripte"})


if __name__ == "__main__":
    unittest.main()
