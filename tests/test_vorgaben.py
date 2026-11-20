"""
Die Vorgaben eines Nachweises stehen einmal (opencivil/core/vorgaben.py): die
Herleitung zeigt sie in ihren Kästen, die Maske in ihren Karten. Bis
2026-11-20 schrieben die Masken die Tafeln ab -- ein neues Feld des Kerns
erschien dort nie, und die Zeichen liefen auseinander.
"""

import unittest

from opencivil.core.berechnung import Vorgabe
from opencivil.core.einheiten import M
from opencivil.core.vorgaben import Feld, Gruppe, mit_index
from opencivil.geotechnik.verhalten import Verhalten
from opencivil.projekt import Projekt
from opencivil.web.api import katalog


def herleitung(rechnung):
    """Die Vorgaben einer Rechnung, wie die Herleitung sie zeigt: Kasten und Kurzname."""
    return [(b.gruppe, b.ausgabe.kurzname) for b in rechnung.berechnungen
            if isinstance(b, Vorgabe)]


def maske(klasse, eintrag, gelesen=None):
    """Was die Maske eines Eintrags zeigt, wie `eingabekarten` es auswählt: Karte und Feld."""
    return [(g["titel"], f["feld"]) for g in katalog()["vorgaben"][klasse]
            for f in g["felder"]["|".join(str(eintrag[n]) for n in g["nach"])]
            if gelesen is None or f["feld"] in gelesen]


class TestBausteine(unittest.TestCase):
    def test_die_nummer_einer_schicht_kommt_in_den_index(self):
        for zeichen, erwartet in (("d", "d_{2}"), ("M_E", "M_{E,2}"), ("M'_E", "M'_{E,2}"),
                                  ("s_{u,k}", "s_{u,k,2}"), (r"\varphi'_k", r"\varphi'_{k,2}"),
                                  (r"\gamma", r"\gamma_{2}")):
            with self.subTest(zeichen=zeichen):
                self.assertEqual(mit_index(zeichen, 2), erwartet)

    def test_eine_gruppe_je_stellung_ihrer_wahlen(self):
        gruppe = Gruppe("Boden", lambda verhalten: (
            Feld("a", "a", M, "Ein Mass", beschriftung="Mass"),
            *((Feld("b", "b", M, "Dicke der #"),) if verhalten is Verhalten.DRAINIERT else ()),
        ), nach=("verhalten",))
        ausgeschrieben = gruppe.als_dict({"verhalten": tuple(Verhalten)})
        self.assertEqual({w: [f["feld"] for f in fs] for w, fs in ausgeschrieben["felder"].items()},
                         {"drainiert": ["a", "b"], "undrainiert": ["a"]})
        a, b = ausgeschrieben["felder"]["drainiert"]
        self.assertEqual((a["beschriftung"], b["beschriftung"]), ("Mass", "Dicke der Schicht"))
        self.assertEqual((a["feld"], b["feld"]), ("a", "b"))
        eintrag = type("E", (), {"verhalten": Verhalten.UNDRAINIERT})()
        self.assertEqual([f.kurz for f in gruppe.fuer(eintrag)], ["a"])
        self.assertEqual(Feld("b", "b", M, "Dicke der #").nummeriert(3).beschreibung,
                         "Dicke der Schicht 3")


class TestMaskeWieHerleitung(unittest.TestCase):
    """Die Maske zeigt genau die Vorgaben der Herleitung, in denselben Gruppen und derselben Folge."""

    def test_grundbruch(self):
        for verhalten in Verhalten:
            with self.subTest(verhalten=verhalten):
                p = Projekt(name="Probe")
                g = p.grundbruch("F", verhalten=verhalten.value)
                aufbau = p.aufbauen()
                self.assertEqual(maske("grundbruch", g.als_dict()),
                                 herleitung(aufbau.grundbrueche[g.kennung]))

    def test_setzung(self):
        """Die Schichten zeigt die Maske je in einer Zeile, die Herleitung je in einem Kasten."""
        p = Projekt(name="Probe")
        s = p.setzung("F")
        s.schicht("Lehm", d=2.0, M_E=10.0, M_E_strich=40.0)
        s.schicht("Kies", d=3.0, M_E=60.0, M_E_strich=180.0)
        eintrag = s.als_dict()
        erwartet = maske("setzung", eintrag)
        for i, schicht in enumerate(eintrag["schichten"], start=1):
            erwartet += [(f"Schicht {i}: {schicht['name']}", f"{feld}_{i}")
                         for _, feld in maske("schicht", schicht)]
        self.assertEqual(erwartet, herleitung(p.aufbauen().setzungen[s.kennung]))


if __name__ == "__main__":
    unittest.main()
