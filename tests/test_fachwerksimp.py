"""
Das Fachwerkmodell, Schritt 11d: das Verfahren SIMP -- die steifste Form,
Schritt um Schritt über den Dienst, und das Fachwerk, das das Werkzeug aus
ihr liest. Gegen Handrechnungen geprüft: das Element, die Konsole.
"""

import math
import unittest

from opencivil.core.protokoll import GleichungBlock, TabellenBlock
from opencivil.fachwerkmodell import form, simp
from opencivil.fachwerkmodell.form import Formeinstellung, Formzustand, ganz_formen, schritte
from opencivil.fachwerkmodell.simp import KE, NetzFehler, netz
from opencivil.fachwerkmodell.werk import ANGEHALTEN, VERALTET
from opencivil.fachwerkmodell.verfahren import Verfahren
from opencivil.projekt import beispiele
from opencivil.projekt.aufbau.fachwerkmodell import einstellung_von, modell_von
from opencivil.projekt.lesen import ProjektFehler
from opencivil.web import dienst

from tests.test_fachwerkmodell import wandscheibe
from tests.test_fachwerksuche import befund_von, konsole, uebersicht


def mit_simp(p, netzweite: float = 0.1, volumen: float = 30.0):
    """Das erste Fachwerkmodell von ``p`` nach dem Verfahren SIMP."""
    f = p.fachwerkmodelle[0]
    f.verfahren, f.netzweite, f.volumen = Verfahren.SIMP, netzweite, volumen
    return p


def geformt(p, kennung: str = "f1") -> tuple:
    """Anfrage um Anfrage über den Dienst, wie die Seite -- die Antwort der letzten und wie viele es waren."""
    zustand, anfragen = None, 0
    while True:
        antwort = dienst.bearbeite("fachwerk_suchen",
                                   {"projekt": p.als_dict(), "kennung": kennung, "zustand": zustand})
        assert antwort.status == 200, antwort.daten
        anfragen += 1
        if antwort.daten["fertig"]:
            return antwort.daten, anfragen
        zustand = antwort.daten["zustand"]


class TestElement(unittest.TestCase):
    """Das Element mit vier Knoten: symmetrisch, und eine Bewegung als Ganzes kostet nichts."""

    def test_symmetrisch(self):
        for r in range(8):
            for c in range(8):
                self.assertAlmostEqual(KE[r][c], KE[c][r], places=14)

    def test_starr_ohne_kraft(self):
        """Verschieben in x, in y und Drehen um die Mitte: K · u = 0."""
        ecken = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        for u in ([1, 0] * 4, [0, 1] * 4, [v for x, y in ecken for v in (-y, x)]):
            with self.subTest(u=u):
                for zeile in KE:
                    self.assertAlmostEqual(sum(k * v for k, v in zip(zeile, u)), 0.0, places=12)

    def test_handrechnung(self):
        """
        Die Diagonale bei E = 1, ν = 0.2: (3 − ν) / (6 (1 − ν²)) = 2.8 / 5.76
        = 0.48611 -- wie im 88-Zeilen-Code der Quelle.
        """
        self.assertAlmostEqual(KE[0][0], 2.8 / 5.76, places=12)


class TestNetz(unittest.TestCase):
    def test_konsole(self):
        modell, _ = modell_von(konsole().fachwerkmodelle[0])
        n = netz(modell, 0.1)
        self.assertEqual((n.spalten, n.zeilen, len(n.elemente)), (10, 20, 200))
        # 11 × 21 Ecken, je zwei Unbekannte, ohne die vier an den beiden Lagern.
        self.assertEqual(n.unbekannte, 2 * 11 * 21 - 4)
        self.assertAlmostEqual(max(map(abs, n.last)), 1.0)

    def test_tuere_ohne_elemente(self):
        """In der Türe der Wand liegt kein Element: dort steht «-» im Bild der Form."""
        modell, _ = modell_von(wandscheibe().fachwerkmodelle[0])
        n = netz(modell, 0.5)
        self.assertEqual((n.spalten, n.zeilen), (12, 6))
        self.assertEqual(len(n.elemente), 72 - 2 * 4)
        bild = form.formtext(n, [0.3] * len(n.elemente))
        self.assertEqual(len(bild), 72)
        self.assertEqual([bild[j * 12 + i] for j in range(6) for i in (7, 8)].count("-"), 8)

    def test_zu_fein(self):
        modell, _ = modell_von(wandscheibe().fachwerkmodelle[0])
        with self.assertRaises(NetzFehler) as fehler:
            netz(modell, 0.02)
        self.assertRegex(str(fehler.exception), r"^Mit der Netzweite 0\.02 m lägen weit über 2500 "
                                                r"Elemente in der Scheibe – mehr als 2500 rechnet das "
                                                r"Werkzeug nicht\. Bitte die Netzweite mindestens "
                                                r"0\.09 m wählen\.$")

    def test_zu_fein_ueber_den_dienst(self):
        p = mit_simp(wandscheibe(), netzweite=0.05)
        daten, _ = geformt(p)
        self.assertIsNone(daten["fachwerk"])
        self.assertEqual(len(daten["meldungen"]), 1)
        self.assertIn("rechnet das Werkzeug nicht", daten["meldungen"][0]["text"])


class TestKonsole(unittest.TestCase):
    """
    Die Konsole aus tests/test_fachwerksuche.py: die Form wird ein Dreieck
    zur Last, und das Fachwerk aus ihr ist das der Handrechnung -- zwei
    Stäbe von je √2 m, ±70.71 kN, V = 200 kNm.
    """

    def test_zwei_staebe(self):
        p = mit_simp(konsole())
        daten, _ = geformt(p)
        self.assertEqual(daten["verfahren"], "simp")
        kraefte = sorted(s["N"] for s in daten["fachwerk"]["staebe"])
        self.assertEqual(len(kraefte), 2)
        self.assertAlmostEqual(kraefte[0], -100 / math.sqrt(2), places=6)
        self.assertAlmostEqual(kraefte[1], 100 / math.sqrt(2), places=6)
        self.assertAlmostEqual(daten["fachwerk"]["V"], 200.0, places=6)
        self.assertEqual({k: v for k, v in daten["form"].items() if k != "werte"},
                         {"x0": 0.0, "y0": 0.0, "h": 0.1, "spalten": 10, "zeilen": 20})

    def test_suchen_wie_die_seite(self):
        """Der Baukasten sucht wie die Seite und legt dasselbe ab, mit der Form."""
        p = mit_simp(konsole())
        daten, _ = geformt(p)
        f = p.fachwerkmodelle[0]
        g = f.suchen()
        self.assertEqual((g.abdruck, g.runden, g.fertig, g.form),
                         (daten["abdruck"], daten["gefunden"]["runden"], True, daten["form"]["werte"]))
        loesung, befund = befund_von(p)
        self.assertEqual((befund.stand, befund.zum_fachwerk), ("gefunden", []))
        u = uebersicht(p)
        self.assertEqual((u["verfahren"], u["form"]), ("simp", daten["form"]))


class TestSchritte(unittest.TestCase):
    """Was herauskommt, hängt nicht daran, wie viele Schritte eine Anfrage rechnet."""

    def setUp(self):
        f = mit_simp(konsole()).fachwerkmodelle[0]
        self.modell, _ = modell_von(f)
        self.einstellung = einstellung_von(f)

    def test_einzeln_wie_ganz(self):
        zustand, anfragen = None, 0
        while True:
            r = schritte(self.modell, self.einstellung, zustand, sekunden=0.0)
            anfragen += 1
            if r.fertig:
                break
            zustand = r.zustand
        self.assertEqual(anfragen, r.zustand.schritt)
        ganz = ganz_formen(self.modell, self.einstellung)
        self.assertEqual((r.ergebnis.runden, r.ergebnis.form, r.ergebnis.fachwerk),
                         (ganz.runden, ganz.form, ganz.fachwerk))

    def test_fremder_zustand_von_vorn(self):
        """Ein Zustand zu einem anderen Modell, zu wenige Dichten, eine über eins: von vorn."""
        erste = schritte(self.modell, self.einstellung, None, sekunden=0.0)
        z = erste.zustand
        for fremd in (Formzustand("anders", z.schritt, z.dichte), Formzustand(z.abdruck, 5, z.dichte[1:]),
                      Formzustand(z.abdruck, 5, (2.0,) + z.dichte[1:])):
            with self.subTest(fremd=fremd.abdruck):
                r = schritte(self.modell, self.einstellung, fremd, sekunden=0.0)
                self.assertEqual(r.zustand.schritt, 1)

    def test_abschliessen(self):
        """Angehalten nach dem ersten Schritt: das Fachwerk aus der Form, wie sie ist, ohne weiteren Schritt."""
        erste = schritte(self.modell, self.einstellung, None, sekunden=0.0)
        r = schritte(self.modell, self.einstellung, erste.zustand, abschliessen=True)
        self.assertEqual((r.zustand.schritt, r.fertig, r.ergebnis.runden, r.ergebnis.fertig),
                         (1, False, 1, False))
        self.assertEqual(r.form, erste.form)
        self.assertIsNotNone(r.ergebnis.fachwerk)


class TestDienst(unittest.TestCase):
    def setUp(self):
        self.p = mit_simp(konsole())

    def frage(self, **rumpf):
        return dienst.bearbeite("fachwerk_suchen", {"projekt": self.p.als_dict(), "kennung": "f1", **rumpf})

    def test_abschliessen_angehalten(self):
        erste = self.frage(zustand=None).daten
        # Die Konsole ist in einer Anfrage fertig -- ein Zustand nach einem Schritt hält vorher an.
        modell, _ = modell_von(self.p.fachwerkmodelle[0])
        z = schritte(modell, einstellung_von(self.p.fachwerkmodelle[0]), None, sekunden=0.0).zustand
        daten = self.frage(zustand={"verfahren": "simp", "abdruck": z.abdruck, "schritt": z.schritt,
                                    "dichte": list(z.dichte)}, abschliessen=True).daten
        self.assertEqual((daten["fertig"], daten["stand"]["schritt"], daten["gefunden"]["fertig"]),
                         (False, 1, False))
        self.assertEqual(erste["abdruck"], daten["abdruck"])
        roh = self.p.als_dict()
        roh["fachwerkmodelle"][0]["fachwerk"] = daten["gefunden"]
        u = dienst.bearbeite("fachwerk_zeichnung", {"projekt": roh, "kennung": "f1"}).daten["uebersicht"]
        self.assertEqual(u["stand"], "gefunden")
        self.assertIn(ANGEHALTEN[Verfahren.SIMP].format(n=1), [m["text"] for m in u["zum_fachwerk"]])

    def test_zustand_des_anderen_verfahrens(self):
        """Wer mitten in der Suche das Verfahren wechselt, sucht im neuen von vorn."""
        gs = dienst.bearbeite("fachwerk_suchen", {"projekt": konsole().als_dict(), "kennung": "f1",
                                                  "zustand": None}).daten
        daten = self.frage(zustand=gs["zustand"]).daten
        self.assertEqual((daten["verfahren"], daten["zustand"]["verfahren"]), ("simp", "simp"))

    def test_unlesbarer_zustand(self):
        for zustand in ({"verfahren": "simp", "abdruck": "x", "schritt": 1, "dichte": ["a"]},
                        {"verfahren": "simp", "abdruck": "x", "schritt": 1}, {"abdruck": "x"}, [1, 2]):
            with self.subTest(zustand=zustand):
                antwort = self.frage(zustand=zustand)
                self.assertEqual(antwort.status, 400)
                self.assertIn("Der Zustand der Suche ist nicht lesbar.", str(antwort.daten))


class TestVerfahren(unittest.TestCase):
    def test_wechsel_macht_veraltet(self):
        """Ein Fachwerk der Ground Structure gilt nicht mehr, wenn das Modell SIMP wählt -- und umgekehrt."""
        p = konsole()
        f = p.fachwerkmodelle[0]
        f.suchen()
        mit_simp(p)
        loesung, befund = befund_von(p)
        self.assertEqual((befund.stand, [m.text for m in befund.zum_fachwerk]), ("veraltet", [VERALTET]))
        f.suchen()
        f.verfahren = Verfahren.GROUND_STRUCTURE
        loesung, befund = befund_von(p)
        self.assertEqual(befund.stand, "veraltet")

    def test_einstellung(self):
        e = einstellung_von(mit_simp(konsole(), netzweite=0.2, volumen=40.0).fachwerkmodelle[0])
        self.assertEqual(e, Formeinstellung(weite=0.2, volumen=0.4, w_Z=1.0, N_min=0.01))
        self.assertIs(e.verfahren, Verfahren.SIMP)
        self.assertFalse(e.zug_achsparallel)

    def test_katalog(self):
        katalog = dienst.bearbeite("katalog").daten["fachwerkmodell"]
        self.assertEqual([(v["wert"], v["beschriftung"]) for v in katalog["verfahren"]],
                         [("ground_structure", "Ground Structure"), ("simp", "SIMP")])

    def test_volumen_begrenzt(self):
        """Der Anteil Material liegt zwischen 5 und 80 % -- ausserhalb hält die Rechnung an."""
        for volumen, gut in ((5.0, True), (80.0, True), (4.9, False), (90.0, False)):
            with self.subTest(volumen=volumen):
                p = mit_simp(konsole(), volumen=volumen)
                if gut:
                    p.inhalt_pruefen()
                else:
                    with self.assertRaises(ProjektFehler):
                        p.inhalt_pruefen()


class TestWand(unittest.TestCase):
    """Die Wand mit Türe im Netz von 0.2 m: ein Fachwerk im Gleichgewicht um die Türe herum."""

    @classmethod
    def setUpClass(cls):
        cls.p = mit_simp(wandscheibe(), netzweite=0.2)
        cls.gefunden = cls.p.fachwerkmodelle[0].suchen()
        cls.loesung, cls.befund = befund_von(cls.p)

    def test_im_gleichgewicht(self):
        self.assertTrue(self.gefunden.fertig)
        self.assertEqual(self.befund.stand, "gefunden")
        self.assertTrue(self.befund.nachrechnung.im_gleichgewicht)
        self.assertEqual(self.befund.zum_fachwerk, [])

    def test_kein_stab_durch_die_tuere(self):
        for k in self.befund.nachrechnung.fachwerk.staebe:
            a, b = (self.befund.nachrechnung.fachwerk.knoten[i] for i in k[:2])
            for t in (0.25, 0.5, 0.75):
                m = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                self.assertFalse(3.5 < m[0] < 4.5 and m[1] < 2.2, (a, b))

    def test_herleitung(self):
        bloecke = self.loesung.protokoll.alle_bloecke()
        namen = [b.name for b in bloecke if isinstance(b, GleichungBlock)]
        self.assertEqual([n for n in namen if n], ["Steifste Form", "Leichtestes Fachwerk"])
        texte = " ".join(getattr(b, "text", "") for b in bloecke)
        self.assertIn(f"Gesucht nach dem Verfahren SIMP ({simp.QUELLE}): die Scheibe in 406 "
                      f"quadratische Elemente der Seite h = 0.2 m geteilt", texte)
        self.assertIn(f"nach {self.gefunden.runden} Schritten änderte sich keine Dichte mehr um 0.01",
                      texte)
        tabellen = [b.titel for b in bloecke if isinstance(b, TabellenBlock)]
        self.assertIn(f"Stäbe – {len(self.gefunden.staebe)}, nach der Grösse ihrer Kraft", tabellen)


class TestPruefprojekt(unittest.TestCase):
    def test_wand_nach_simp(self):
        p = beispiele.jeder_nachweis()
        f = next(x for x in p.fachwerkmodelle if x.verfahren is Verfahren.SIMP)
        loesung, befund = befund_von(p, f.kennung)
        self.assertEqual((befund.stand, befund.zum_fachwerk), ("gefunden", []))
        self.assertTrue(befund.nachrechnung.im_gleichgewicht)


if __name__ == "__main__":
    unittest.main()
