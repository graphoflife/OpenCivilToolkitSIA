"""
Die Bänder, die eine Decke bei automatischer Aufteilung selbst legt
(:mod:`opencivil.decke.baender`): an offenen Rändern und über Stützen --
und wo sie keines legt.
"""

import math
import unittest

from opencivil.core.protokoll import TabellenBlock, TextBlock
from opencivil.decke.baender import STUFE_RAND, STUFE_STUETZE
from opencivil.decke.herleitung import BAENDER
from opencivil.decke.modell import (
    Aufteilung, Decke, Flaechenlast, Lastfall, Linienlager, Platte, Stuetze, Traeger,
)
from opencivil.decke.rechnung import rechnen
from opencivil.projekt import Projekt
from opencivil.web import dienst

Q = 10e3


def platte(name, ecken, **k):
    return Platte(name, tuple(ecken), 0.25, 30e9, 25e3, von_selbst=True, **k)


def rand(ecken):
    """Wände rundum."""
    return [Linienlager(f"L{i + 1}", a, b) for i, (a, b) in enumerate(zip(ecken, ecken[1:] + ecken[:1]))]


def last(*platten):
    return [Lastfall("q", [Flaechenlast(f"q{p}", Q, platte=p) for p in platten])]


def frei_oben(**k):
    """6 × 5 m auf Wänden unten, rechts und links -- oben frei."""
    return Decke(platten=[platte("P1", [(0, 0), (6, 0), (6, 5), (0, 5)])],
                 linienlager=[Linienlager("L1", (0, 0), (6, 0)), Linienlager("L2", (6, 0), (6, 5)),
                              Linienlager("L3", (0, 5), (0, 0))], lastfaelle=last("P1"), **k)


def baender(e):
    """Die Bänder der gerechneten Decke, je ``(name, a, b, breite, stufe)``, auf den mm gerundet."""
    return [(u.name, tuple(round(c, 3) for c in u.a), tuple(round(c, 3) for c in u.b), u.breite, u.stufe)
            for u in e.decke.traeger if u.von_selbst]


class Fall(unittest.TestCase):
    def getragen(self, decke):
        """Die gerechnete Decke -- ihr Fall ganz getragen."""
        e = rechnen(decke)
        (f,) = e.faelle
        self.assertAlmostEqual(f.nicht_getragen, 0.0, delta=1e-6 * f.summe)
        self.assertAlmostEqual(f.lagerkraft, f.summe, delta=1e-6 * f.summe)
        return e, f


class TestAmRand(Fall):
    def test_freier_rand(self):
        """
        Oben frei: ohne Band spannte alles 6 m in x, und die untere Wand
        trüge nichts. Das Band liegt innen am Rand, von Wand zu Wand, und die
        Streifen in y liegen auf ihm.
        """
        e, f = self.getragen(frei_oben())
        self.assertEqual(baender(e), [("B1", (0.0, 4.5), (6.0, 4.5), 1.0, STUFE_RAND)])
        self.assertGreater(f.wandkraft("L1"), 0.2 * f.summe)

    def test_so_breit_wie_das_feld_der_decke(self):
        e, _ = self.getragen(frei_oben(bandbreite=0.5))
        self.assertEqual(baender(e), [("B1", (0.0, 4.75), (6.0, 4.75), 0.5, STUFE_RAND)])

    def test_ein_eigener_traeger_ersetzt_es(self):
        e, _ = self.getragen(frei_oben(traeger=[Traeger("T1", (0, 4.75), (6, 4.75), 0.5)]))
        self.assertEqual(baender(e), [])

    def test_fest_legt_keines(self):
        e = rechnen(frei_oben(aufteilung=Aufteilung.FEST))
        self.assertEqual(baender(e), [])

    def test_ein_loch(self):
        """Ein Loch 2 × 2 m: an jedem seiner Ränder ein Band, von Wand zu Wand."""
        e, _ = self.getragen(Decke(
            platten=[platte("P1", [(0, 0), (10, 0), (10, 3), (0, 3)]), platte("P2", [(0, 5), (10, 5), (10, 8), (0, 8)]),
                     platte("P3", [(0, 3), (4, 3), (4, 5), (0, 5)]), platte("P4", [(6, 3), (10, 3), (10, 5), (6, 5)])],
            linienlager=rand([(0, 0), (10, 0), (10, 8), (0, 8)]), lastfaelle=last("P1", "P2", "P3", "P4")))
        self.assertEqual({(a, b) for _, a, b, _, _ in baender(e)},
                         {((0.0, 2.5), (10.0, 2.5)), ((0.0, 5.5), (10.0, 5.5)),
                          ((3.5, 0.0), (3.5, 8.0)), ((6.5, 0.0), (6.5, 8.0))})

    def test_eine_l_form(self):
        """Die zwei Ränder der inneren Ecke sind frei: je ein Band, bis zu den Wänden."""
        e, _ = self.getragen(Decke(
            platten=[platte("P1", [(0, 0), (10, 0), (10, 4), (4, 4), (4, 10), (0, 10)])],
            linienlager=[Linienlager("L1", (0, 0), (10, 0)), Linienlager("L2", (10, 0), (10, 4)),
                         Linienlager("L3", (4, 10), (0, 10)), Linienlager("L4", (0, 10), (0, 0))],
            lastfaelle=last("P1")))
        self.assertEqual({(a, b) for _, a, b, _, _ in baender(e)},
                         {((0.0, 3.5), (10.0, 3.5)), ((3.5, 0.0), (3.5, 10.0))})

    def test_platten_mit_anderen_richtungen(self):
        """An der Fuge enden die Streifen beider Platten: je Platte ein Band, innen an ihr."""
        e, _ = self.getragen(Decke(
            platten=[platte("P1", [(0, 0), (6, 0), (6, 5), (0, 5)]),
                     Platte("P2", ((6, 0), (12, 0), (12, 5), (6, 5)), 0.25, 30e9, 25e3,
                            (math.radians(30), math.radians(120)))],
            linienlager=rand([(0, 0), (12, 0), (12, 5), (0, 5)]), lastfaelle=last("P1", "P2")))
        self.assertEqual({(a, b) for _, a, b, _, _ in baender(e)},
                         {((5.5, 0.0), (5.5, 5.0)), ((6.5, 0.0), (6.5, 5.0))})

    def test_kein_kragarm(self):
        """Auf einer eingespannten Wand trägt die Platte selbst, als Kragplatte -- ohne Band."""
        e, _ = self.getragen(Decke(platten=[platte("P1", [(0, 0), (6, 0), (6, 2), (0, 2)])],
                                   linienlager=[Linienlager("L1", (0, 0), (6, 0), eingespannt=True)],
                                   lastfaelle=last("P1")))
        self.assertEqual(baender(e), [])

    def test_nicht_an_einer_platte_die_einachsig_traegt(self):
        """
        Zwischen zwei Wänden trägt die Platte nur in x: oben und unten hat
        kein Streifen in y ein Lager. Zwei Bänder dort nähmen ihr die Last ab.
        """
        e, _ = self.getragen(Decke(platten=[platte("P1", [(0, 0), (4, 0), (4, 2), (0, 2)])],
                                   linienlager=[Linienlager("L1", (4, 0), (4, 2)), Linienlager("L2", (0, 2), (0, 0))],
                                   lastfaelle=last("P1")))
        self.assertEqual(baender(e), [])

    def test_ueber_eck_traegt_auch_mit_baendern_nicht(self):
        """Nur zwei Wände über Eck: kein Band fände zwei Lager -- die Last fällt aus, wie ohne Bänder."""
        e = rechnen(Decke(platten=[platte("P1", [(0, 0), (6, 0), (6, 5), (0, 5)])],
                          linienlager=[Linienlager("L1", (0, 0), (6, 0)), Linienlager("L3", (0, 5), (0, 0))],
                          lastfaelle=last("P1")))
        (f,) = e.faelle
        self.assertEqual(baender(e), [])
        self.assertAlmostEqual(f.nicht_getragen, f.summe, delta=1e-6 * f.summe)


class TestUeberStuetzen(Fall):
    def test_flachdecke(self):
        """
        8 × 8 m auf vier Eckstützen: ohne Bänder fielen 86 % der Last aus.
        Die Bänder liegen innen an den Rändern, ganz in der Platte, und jede
        Stütze trägt ein Viertel.
        """
        ecken = [(0, 0), (8, 0), (8, 8), (0, 8)]
        e, f = self.getragen(Decke(platten=[platte("P1", ecken)],
                                   stuetzen=[Stuetze(f"S{i + 1}", o, 0.3, 0.3) for i, o in enumerate(ecken)],
                                   lastfaelle=last("P1")))
        self.assertEqual({(a, b) for _, a, b, _, _ in baender(e)},
                         {((0.0, 0.5), (8.0, 0.5)), ((0.5, 0.0), (0.5, 8.0)),
                          ((7.5, 0.0), (7.5, 8.0)), ((0.0, 7.5), (8.0, 7.5))})
        self.assertEqual({stufe for *_, stufe in baender(e)}, {STUFE_STUETZE})
        for s in ("S1", "S2", "S3", "S4"):
            self.assertAlmostEqual(f.stuetzenkraft(s), f.summe / 4.0, delta=1.0, msg=s)

    def test_von_wand_zu_wand(self):
        """Eine Stütze in der Mitte, Wände rundum: ein Band je Richtung, quer über die ganze Platte."""
        e, _ = self.getragen(Decke(platten=[platte("P1", [(0, 0), (12, 0), (12, 12), (0, 12)])],
                                   linienlager=rand([(0, 0), (12, 0), (12, 12), (0, 12)]),
                                   stuetzen=[Stuetze("S1", (6, 6), 0.3, 0.3)], lastfaelle=last("P1")))
        self.assertEqual({(a, b) for _, a, b, _, _ in baender(e)},
                         {((0.0, 6.0), (12.0, 6.0)), ((6.0, 0.0), (6.0, 12.0))})

    def test_nicht_ueber_einer_wand_laengs(self):
        """
        Unten eine Wand bis x = 4, dann zwei Stützen am Rand: das Band über
        ihnen beginnt, wo die Wand endet -- über ihr trägt sie selbst --, und
        liegt innen am Rand.
        """
        e, _ = self.getragen(Decke(
            platten=[platte("P1", [(0, 0), (16, 0), (16, 6), (0, 6)])],
            linienlager=[Linienlager("L1", (0, 0), (4, 0)), Linienlager("L2", (16, 0), (16, 6)),
                         Linienlager("L3", (16, 6), (0, 6)), Linienlager("L4", (0, 6), (0, 0))],
            stuetzen=[Stuetze("S1", (8, 0), 0.3, 0.3), Stuetze("S2", (12, 0), 0.3, 0.3)], lastfaelle=last("P1")))
        self.assertEqual({(a, b) for _, a, b, _, _ in baender(e)},
                         {((4.0, 0.5), (16.0, 0.5)), ((8.0, 0.0), (8.0, 6.0)), ((12.0, 0.0), (12.0, 6.0))})

    def test_unter_einem_eigenen_traeger(self):
        """
        Ein Band liegt auf einem Träger des Benutzers, nie trägt es einen:
        B1 reicht von T1 bis zur Wand rechts und liegt auf T1, T1 nicht auf B1.
        """
        ecken = [(0, 0), (8, 0), (8, 3), (0, 3)]
        e, _ = self.getragen(Decke(
            platten=[platte("P1", [(0, 0), (4, 0), (4, 3), (0, 3)]), platte("P2", [(4, 0), (8, 0), (8, 3), (4, 3)])],
            linienlager=rand(ecken), traeger=[Traeger("T1", (4, 0), (4, 3), 0.5)],
            stuetzen=[Stuetze("S1", (6, 1.5), 0.3, 0.3)], lastfaelle=last("P1", "P2")))
        self.assertEqual(baender(e)[0][:3], ("B1", (3.75, 1.5), (8.0, 1.5)))
        lager = {u.name: {a.name for t in u.durchlauftraeger for a in t.auflager} for u in e.zerlegung.traeger}
        self.assertIn("T1", lager["B1"])
        self.assertFalse(lager["T1"] & {"B1", "B2"})

    def test_namen_neben_denen_der_decke(self):
        """Heisst schon ein Teil der Decke B1, heisst das erste Band B2."""
        d = frei_oben()
        d.platten[0] = Platte("B1", d.platten[0].ecken, 0.25, 30e9, 25e3, von_selbst=True)
        d.lastfaelle[0] = Lastfall("q", [Flaechenlast("q", Q, platte="B1")])
        e, _ = self.getragen(d)
        self.assertEqual([b[0] for b in baender(e)], ["B2"])


def projekt_frei_oben():
    p = Projekt(name="Bänder")
    d = p.decke("Frei oben")
    d.platte([(0, 0), (6, 0), (6, 5), (0, 5)], beton=p.beton("C30/37"), h=250)
    d.lager((0, 0), (6, 0))
    d.lager((6, 0), (6, 5))
    d.lager((0, 5), (0, 0))
    d.plattenlast(d.lastfall("q"), "P1", 10.0)
    return p, d


class TestImProjekt(unittest.TestCase):
    def test_das_feld_der_decke(self):
        """Vorgabe 1 m; eine andere Breite geht an die Rechnung."""
        p, d = projekt_frei_oben()
        self.assertEqual(d.bandbreite, 1.0)
        d.bandbreite = 0.5
        aufbau = p.aufbauen()
        self.assertEqual(aufbau.decken[d.kennung].decke.bandbreite, 0.5)

    def test_herleitung_und_bild(self):
        """
        Die Herleitung zeigt die Bänder in einer eigenen Tabelle, mit der
        Regel; das Bild bekommt sie getrennt von den Trägern.
        """
        p, d = projekt_frei_oben()
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.materialziele(), *aufbau.ziele_von(d.kennung))
        bloecke = loesung.protokoll.alle_bloecke()
        (tabelle,) = [b for b in bloecke if isinstance(b, TabellenBlock) and b.titel == "Bänder, von der Rechnung gelegt"]
        self.assertEqual([[z if isinstance(z, str) else z.latex for z in zeile] for zeile in tabelle.zeilen],
                         [["B1", "(0.00, 4.50)", "(6.00, 4.50)", "1.00", "am Rand"]])
        texte = [b.text for b in bloecke if isinstance(b, TextBlock)]
        self.assertIn(BAENDER, texte)
        self.assertTrue(any("dann die Bänder, die tiefere Stufe zuerst: B1 (Band am Rand)." in t
                            for t in texte), texte)
        self.assertFalse([b for b in bloecke if isinstance(b, TabellenBlock) and b.titel == "Träger"])

        bild = dienst.bearbeite("rechnen", {"projekt": p.als_dict()}).daten["zeichendaten"][d.kennung]
        self.assertEqual(bild["traeger"], [])
        (band,) = bild["baender"]
        self.assertEqual({k: band[k] for k in ("name", "achse", "art", "breite")},
                         {"name": "B1", "achse": [[0.0, 4.5], [6.0, 4.5]], "art": "am Rand", "breite": 1.0})


if __name__ == "__main__":
    unittest.main()
