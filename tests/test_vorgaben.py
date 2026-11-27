"""
Die Vorgaben eines Nachweises stehen einmal (opencivil/core/vorgaben.py): die
Herleitung zeigt sie in ihren Kästen, die Maske in ihren Karten. Bis
2026-11-20 schrieben die Masken die Tafeln ab -- ein neues Feld des Kerns
erschien dort nie, und die Zeichen liefen auseinander.
"""

import itertools
import unittest

from opencivil.core.berechnung import Vorgabe
from opencivil.core.einheiten import M
from opencivil.core.vorgaben import Feld, Gruppe, mit_index
from opencivil.durchstanzen.flaeche import Lage, Stuetzenform
from opencivil.durchstanzen.stelle import KeArt, Naeherungsstufe, Plattenart
from opencivil.geotechnik.verhalten import Verhalten
from opencivil.pfahl.boden import Mantel
from opencivil.pfahl.pfahl import Grundlage, Pfahlart, Spitze, Tragglied
from opencivil.projekt import Projekt
from opencivil.web.api import katalog


def herleitung(rechnung):
    """Die Vorgaben einer Rechnung, wie die Herleitung sie zeigt: Kasten und Kurzname."""
    return [(b.gruppe, b.ausgabe.kurzname) for b in rechnung.berechnungen
            if isinstance(b, Vorgabe)]


def maske(klasse, eintrag, gelesen=None):
    """Was die Maske eines Eintrags zeigt, wie `eingabegruppen` es auswählt: Gruppe und Feld."""
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

    def test_durchstanzen(self):
        """
        Je Stellung der Wahlen, mit dem, was der Nachweis liest: die Maske
        nimmt es aus dem Katalog, der Test von der Stelle selbst -- dass beides
        gleich ist, prüft tests/test_durchstanzen.py.
        """
        for lage, form, stufe, ke, plattenart in itertools.product(
                Lage, Stuetzenform, Naeherungsstufe, KeArt, Plattenart):
            with self.subTest(lage=lage, form=form, stufe=stufe, ke=ke, plattenart=plattenart):
                p = Projekt(name="Probe")
                d = p.durchstanzen("S", beton=p.beton().kennung, stahl=p.stahl().kennung,
                                   lage=lage.value, form=form.value, stufe=stufe.value,
                                   ke=ke.value, plattenart=plattenart.value)
                stelle = p.aufbauen().objekte("durchstanzen")[d.kennung]
                self.assertEqual(maske("durchstanz", d.als_dict(), set(stelle.eingaben())),
                                 herleitung(stelle))

    def test_grundbruch(self):
        for verhalten in Verhalten:
            with self.subTest(verhalten=verhalten):
                p = Projekt(name="Probe")
                p.fluessigkeit()
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

    def test_pfahl(self):
        """Jede Stellung der Wahlen des Pfahls, darunter je eine Schicht jeder Stellung."""
        for art, tragglied, grundlage, spitze in itertools.product(
                Pfahlart, Tragglied, Grundlage, Spitze):
            with self.subTest(art=art, tragglied=tragglied, grundlage=grundlage, spitze=spitze):
                p = Projekt(name="Probe")
                p.fluessigkeit()
                beton = p.beton().kennung if art is Pfahlart.BOHRPFAHL else ""
                t = p.pfahl("P", stahl=p.stahl().kennung, beton=beton, art=art.value,
                            tragglied=tragglied.value, grundlage=grundlage.value,
                            spitze=spitze.value)
                for verhalten, mantel in itertools.product(Verhalten, Mantel):
                    t.schicht(f"{verhalten.value}, {mantel.value}", verhalten=verhalten.value,
                              mantel=mantel.value)
                eintrag = t.als_dict()
                erwartet = maske("pfahl", eintrag)
                for i, schicht in enumerate(eintrag["schichten"], start=1):
                    erwartet += [(f"Schicht {i}: {schicht['name']}", f"{feld}_{i}")
                                 for _, feld in maske("pfahlschicht", schicht)]
                self.assertEqual(erwartet, herleitung(p.aufbauen().pfaehle[t.kennung]))


if __name__ == "__main__":
    unittest.main()
