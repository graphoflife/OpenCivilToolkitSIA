"""
Wer worauf zeigt: die Materialien und Querschnitte, die ein Bauteil braucht.

Die Oberfläche fragt den Kern, bevor sie ein Material oder Bauteil löscht
(Dienst ``verweise``). Bis 2026-10-17 hielt sie eine eigene Liste, die den
Bügelstahl nicht kannte -- er liess sich löschen, und der nächste Lauf
scheiterte am Verweis ins Leere.
"""

import unittest

from opencivil.projekt import BAUTEILE, Projekt
from opencivil.web import dienst


class TestVerweise(unittest.TestCase):

    def test_jede_bauteilart_nennt_materialien_und_bezuege(self):
        for art in BAUTEILE:
            with self.subTest(art=art.liste):
                self.assertTrue(callable(getattr(art.eintrag, "materialien", None)))
                self.assertTrue(callable(getattr(art.eintrag, "bezuege", None)))

    def test_der_stahl_der_platte_zaehlt(self):
        """Er gilt für Lagen und Bügel (Benutzer, 2026-10-24)."""
        p = Projekt.beispiel()
        zweiter = p.eigener_stahl()
        p.querschnitte[0].stahl = zweiter.kennung
        self.assertEqual([e.kennung for e in p.verweise(zweiter.kennung)], ["q1"])

    def test_ein_system_zeigt_auf_seine_querschnitte(self):
        p = Projekt.beispiel()
        self.assertEqual([e.kennung for e in p.verweise("a1")],
                         [s.kennung for s in p.balkensysteme])

    def test_was_niemand_braucht(self):
        p = Projekt.beispiel()
        self.assertEqual(p.verweise(p.eigener_beton().kennung), [])
        self.assertEqual(p.verweise("gibtesnicht"), [])

    def test_ueber_den_dienst(self):
        p = Projekt.beispiel()
        antwort = dienst.bearbeite("verweise", {"projekt": p.als_dict(), "kennung": "s1"})
        self.assertEqual(antwort.status, 200)
        self.assertIn({"kennung": "q1", "name": p.querschnitte[0].name},
                      antwort.daten["verweise"])
        ohne = dienst.bearbeite("verweise", {"projekt": p.als_dict()})
        self.assertEqual(ohne.status, 400)


if __name__ == "__main__":
    unittest.main()
