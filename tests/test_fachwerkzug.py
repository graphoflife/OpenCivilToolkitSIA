"""
Das Fachwerkmodell, Schritt 11c: «Zug nur waagrecht und senkrecht» --
geneigte Stäbe tragen dann nur Druck. Gegen eine Handrechnung an der
Konsole, gegen die Optimierung über alle möglichen Stäbe und dort, wo so
kein Fachwerk aufgeht.
"""

import unittest

from opencivil.core.protokoll import HinweisArt, HinweisBlock, TabellenBlock, TextBlock
from opencivil.fachwerkmodell.grundstruktur import liegt_achsparallel
from opencivil.fachwerkmodell.optimierung import Gleichgewicht, optimieren
from opencivil.fachwerkmodell.suche import ZUG_ACHSPARALLEL, _grundstruktur, _optimum, abdruck
from opencivil.fachwerkmodell.werk import IM_FENSTER, VERALTET
from opencivil.projekt import Projekt, beispiele
from opencivil.projekt.aufbau.fachwerkmodell import einstellung_von, modell_von
from opencivil.web import dienst

from tests.test_fachwerksuche import befund_von, gesucht, konsole

#: Was die Last des Streifens sagt, wenn kein Fachwerk sie trägt.
OFFEN = ("Die Last F1 lässt sich mit Zug nur waagrecht und senkrecht nicht ganz zu den Lagern "
         "tragen: 10.0 kN bleiben offen.")


def mit_schalter(p: Projekt) -> Projekt:
    p.fachwerkmodelle[0].zug_achsparallel = True
    return p


def streifen(zug_achsparallel: bool) -> Projekt:
    """
    Ein Streifen unter 45°, 0.1 m breit und 2 m hoch, oben an zwei Lagern;
    unten hängt 10 kN. Hinauf trägt ihn nur Zug längs des Streifens -- und
    der ist geneigt.
    """
    p = Projekt(name="Streifen")
    f = p.fachwerkmodell("Streifen")
    f.zug_achsparallel = zug_achsparallel
    f.scheibe([(0, 0), (0.1, 0), (2.1, 2), (2, 2)])
    f.lager_setzen((2, 2))
    f.lager_setzen((2.1, 2))
    f.last((0, 0), F_v=10)
    return p


def geneigt_auf_zug(fw: dict) -> list:
    """Die geneigten Stäbe mit Zug eines Fachwerks, wie der Dienst es gibt."""
    k = fw["knoten"]
    return [s for s in fw["staebe"] if s["N"] > 0.0
            and not liegt_achsparallel((k[s["von"]]["x"], k[s["von"]]["y"]),
                                       (k[s["bis"]]["x"], k[s["bis"]]["y"]))]


class TestKonsole(unittest.TestCase):
    """
    Die Konsole aus tests/test_fachwerksuche.py: ohne den Schalter trägt
    ein geneigter Stab die Last als Zug zum oberen Lager, V = 200 kNm. Mit
    ihm geht der Zug senkrecht und waagrecht, von unten trägt eine Strebe.
    Im Raster von 1 m etwa ein Band von (1, 1) nach (1, 2) mit 100 kN, eine
    Strebe von (0, 0) nach (1, 2) mit 50 · √5 = 111.8 kN und ein Band nach
    (0, 2) mit 50 kN: V = 100 · 1 + 111.8 · √5 + 50 · 1 = 400 kNm. Leichter
    geht es nicht: die virtuellen Verschiebungen u = (2, −4) an der Last,
    (1, −1) bei (0, 1), (1, −3) bei (1, 2) und (0, −4) bei (1, 0) dehnen
    keinen waagrechten oder senkrechten Stab um mehr als 1 und stauchen
    keinen um mehr als 1 -- einen geneigten dürfen sie beliebig dehnen, er
    trägt keinen Zug --, also V ≥ 100 · 4 = 400 kNm.
    """

    def test_400_gegen_die_handrechnung(self):
        fw = gesucht(mit_schalter(konsole(1.0)))["fachwerk"]
        self.assertAlmostEqual(fw["V"], 400.0, places=3)
        self.assertEqual(geneigt_auf_zug(fw), [])

    def test_ohne_schalter_200(self):
        fw = gesucht(konsole(1.0))["fachwerk"]
        self.assertAlmostEqual(fw["V"], 200.0, places=3)
        self.assertEqual(len(geneigt_auf_zug(fw)), 1)

    def test_feiner_leichter_und_nie_geneigt_auf_zug(self):
        """Feiner kommen Wege dazu: im Raster von 0.5 m 375 kNm."""
        V = {}
        for weite in (1.0, 0.5, 0.25):
            with self.subTest(weite=weite):
                fw = gesucht(mit_schalter(konsole(weite)))["fachwerk"]
                self.assertEqual(geneigt_auf_zug(fw), [])
                V[weite] = fw["V"]
        self.assertAlmostEqual(V[0.5], 375.0, places=3)
        self.assertLessEqual(V[0.25], V[0.5] + 1e-6)

    def test_wie_die_optimierung_ueber_alle_staebe(self):
        """Runde um Runde kommt die Suche dorthin, wo die Optimierung über alle möglichen Stäbe ist."""
        f = mit_schalter(konsole(0.5)).fachwerkmodelle[0]
        modell, _ = modell_von(f)
        e = einstellung_von(f)
        gs = _grundstruktur(modell, e.weite)
        skala = max(map(abs, gs.last))
        alle = _optimum(gs, range(len(gs.staebe)), e, skala)
        fw = gesucht(mit_schalter(konsole(0.5)))["fachwerk"]
        self.assertAlmostEqual(fw["V"], alle.ziel * skala / 1e3, places=3)


class TestOptimierung(unittest.TestCase):
    def test_ohne_zug_traegt_nur_druck(self):
        """
        Ein Knoten an zwei Stäben zu Lagern, links waagrecht, oben senkrecht,
        unter einer Last schräg nach rechts unten: beide ziehen mit 1. Darf
        der linke nicht ziehen, bleibt die Last waagrecht als Rest stehen.
        """
        # Die Zeilen x und y des freien Knotens; Stab 1 geht nach links, Stab 2 nach oben.
        gl = Gleichgewicht(2, [((0, 1.0),), ((1, -1.0),)])
        mit = optimieren(gl, [1.0, -1.0], [1.0, 1.0], [1.0, 1.0], 1000.0)
        self.assertAlmostEqual(mit.q[0], 1.0, places=6)
        self.assertAlmostEqual(mit.q[1], 1.0, places=6)
        ohne = optimieren(gl, [1.0, -1.0], [None, 1.0], [1.0, 1.0], 1000.0)
        self.assertLessEqual(ohne.q[0], 0.0)
        self.assertAlmostEqual(ohne.q[1], 1.0, places=6)
        self.assertAlmostEqual(ohne.rest[0], 1.0, places=6)


class TestKeinFachwerk(unittest.TestCase):
    """Geht mit dem Schalter kein Fachwerk auf, sagt es die Last, rot -- an ihrem Ort."""

    def test_der_streifen_mit_schalter(self):
        daten = gesucht(streifen(True))
        self.assertEqual(daten["fachwerk"]["staebe"], [])
        self.assertEqual([(m["text"], m["elemente"], m["fehler"]) for m in daten["meldungen"]],
                         [(OFFEN, ["F1"], True)])

    def test_der_streifen_ohne_schalter(self):
        daten = gesucht(streifen(False))
        self.assertTrue(daten["fachwerk"]["staebe"])
        self.assertEqual(daten["meldungen"], [])

    def test_abgelegt_sagt_es_die_rechnung(self):
        p = streifen(True)
        p.fachwerkmodelle[0].suchen()
        loesung, befund = befund_von(p)
        self.assertEqual(befund.stand, "gefunden")
        self.assertEqual([(m.text, m.fehler) for m in befund.zum_fachwerk], [(OFFEN, True)])
        texte = [b.text for b in loesung.protokoll.alle_bloecke() if isinstance(b, TextBlock)]
        self.assertTrue(any(t.startswith("Kein Stab trägt") for t in texte))
        tabellen = [b.titel for b in loesung.protokoll.alle_bloecke() if isinstance(b, TabellenBlock)]
        self.assertFalse(any(t.startswith("Stäbe") for t in tabellen))


class TestAblage(unittest.TestCase):
    def test_umschalten_macht_es_veraltet(self):
        p = konsole(1.0)
        f = p.fachwerkmodelle[0]
        f.suchen()
        f.zug_achsparallel = True
        loesung, befund = befund_von(p)
        self.assertEqual((befund.stand, [m.text for m in befund.zum_fachwerk]), ("veraltet", [VERALTET]))

    def test_geneigt_auf_zug_steht_rot(self):
        """Die Suche gibt keinen -- nur eine Datei, die jemand von Hand änderte."""
        p = konsole(1.0)
        f = p.fachwerkmodelle[0]
        f.suchen()
        f.zug_achsparallel = True
        modell, _ = modell_von(f)
        f.fachwerk.abdruck = abdruck(modell, einstellung_von(f))
        loesung, befund = befund_von(p)
        self.assertEqual(befund.stand, "gefunden")
        zug = next(i for i, s in enumerate(f.fachwerk.staebe, start=1) if s.N > 0)
        self.assertIn((f"Stab {zug} ist geneigt und trägt Zug, obwohl {ZUG_ACHSPARALLEL} gilt – neu "
                       f"suchen {IM_FENSTER}.", True),
                      [(m.text, m.fehler) for m in befund.zum_fachwerk])


class TestHerleitung(unittest.TestCase):
    def test_pruefprojekt_sagt_es(self):
        p = beispiele.jeder_nachweis()
        f = next(x for x in p.fachwerkmodelle if x.zug_achsparallel)
        loesung, befund = befund_von(p, f.kennung)
        self.assertEqual((befund.stand, befund.zum_fachwerk), ("gefunden", []))
        bloecke = loesung.protokoll.alle_bloecke()
        texte = [b.text for b in bloecke if isinstance(b, TextBlock)]
        self.assertTrue(any(f"{ZUG_ACHSPARALLEL}: ein geneigter Stab trägt nur Druck." in t
                            for t in texte))
        fw = befund.nachrechnung.fachwerk
        self.assertFalse([s for s in fw.staebe if s[2] > 0
                          and not liegt_achsparallel(fw.knoten[s[0]], fw.knoten[s[1]])])
        warnungen = [b for b in bloecke if isinstance(b, HinweisBlock) and b.art is HinweisArt.WARNUNG]
        self.assertEqual(warnungen, [])

    def test_schalter_im_katalog(self):
        katalog = dienst.bearbeite("katalog").daten
        zug = katalog["fachwerkmodell"]["zug"]
        self.assertEqual(zug["beschriftung"], "Zug nur waagrecht und senkrecht")
        self.assertIn("Druck", zug["titel"])


class TestAchsparallel(unittest.TestCase):
    def test_bis_auf_rundung(self):
        self.assertTrue(liegt_achsparallel((0.0, 0.0), (3.0, 0.0)))
        self.assertTrue(liegt_achsparallel((0.1, 0.2), (0.1, 3.0)))
        self.assertTrue(liegt_achsparallel((0.0, 0.0), (0.1 + 0.2, 0.3 - 0.1 - 0.2)))
        self.assertFalse(liegt_achsparallel((0.0, 0.0), (3.0, 0.001)))
        self.assertFalse(liegt_achsparallel((0.0, 0.0), (1.0, 1.0)))


if __name__ == "__main__":
    unittest.main()
