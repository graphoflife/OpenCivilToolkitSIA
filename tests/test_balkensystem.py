"""
Die Beschreibung eines Balkensystems: lesen, ablegen, zeichnen ohne
Oberfläche -- und was Teilen und Umkehren mit den Lasten einer Linie tun.
"""

import dataclasses
import json
import math
import unittest

from opencivil.projekt import (
    BAUTEILE, BalkensystemEintrag, Projekt, ProjektFehler, QuerschnittsanalyseEintrag,
    StablastEintrag,
)
from opencivil.projekt.balkensystem import MATERIAL_DES_QUERSCHNITTS
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.linie import moment_kruemmung
from opencivil.spannungsanalyse.modul import aequivalenter_modul
from opencivil.spannungsanalyse.platte import loeserpaar
from opencivil.spannungsanalyse.schnitt import schnittpaar
from opencivil.web import dienst


def einfeldtraeger(kennung: str = "r1", name: str = "T", beton: str = "b1") -> BalkensystemEintrag:
    """
    Ein Einfeldträger von 6 m, Rechteck 300 × 600 mm, links gelenkig, rechts
    verschieblich, ein Lastfall mit 10 kN/m -- bis 2026-10-19 das neue System
    der Oberfläche. Gebaut ohne die Lastfälle, die ein neues System mitbringt.
    Sein Material ist ``beton`` des Projekts; leer: keines.
    """
    s = BalkensystemEintrag(kennung=kennung, name=name)
    q = s.querschnitt("Rechteck 300×600", "rechteck", b=300.0, h=600.0)
    linie = s.linie((0.0, 0.0), (6.0, 0.0), querschnitt=q,
                    material=s.beton(beton) if beton else None)
    s.lager_an((0.0, 0.0), "gelenkig")
    s.lager_an((6.0, 0.0), "verschieblich")
    s.stablast(s.lastfall("Lastfall 1"), linie, wert=10.0)
    return s


def rahmen() -> Projekt:
    """Zwei Stützen und ein Riegel, ein Lastfall und eine Kombination."""
    p = Projekt(name="Rahmen")
    p.beton("C30/37")
    s = p.balkensystem("Rahmen")
    beton = s.beton("b1")
    q = s.querschnitt("Riegel", "rechteck", b=300.0, h=600.0)
    links = s.linie((0, 0), (0, 4), querschnitt=q, material=beton)
    riegel = s.linie((0, 4), (6, 4), querschnitt=q, material=beton)
    rechts = s.linie((6, 4), (6, 0), querschnitt=q, material=beton, gelenk_anfang=True)
    s.lager_an((0, 0), "eingespannt")
    s.lager_an((6, 0), "gelenkig")
    g = s.lastfall("Eigengewicht")
    w = s.lastfall("Wind")
    s.stablast(g, riegel, wert=25.0)
    s.stablast(w, links, wert=3.0, richtung="quer")
    s.knotenlast(w, (0, 4), 10.0, richtung="waagrecht")
    s.kombination("Tragsicherheit", (g, 1.35), (w, 1.5))
    assert (links.kennung, riegel.kennung, rechts.kennung) == ("L1", "L2", "L3")
    return p


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        p = rahmen()
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)

    def test_knoten_werden_geteilt(self):
        s = rahmen().balkensysteme[0]
        self.assertEqual([k.kennung for k in s.knoten], ["K1", "K2", "K3", "K4"])
        self.assertEqual(s.linien[1].von, s.linien[0].bis)
        self.assertEqual(s.lager[0].knoten, "K1")
        self.assertEqual((s.lager[0].x, s.lager[0].z, s.lager[0].phi), ("fest", "fest", "fest"))
        self.assertEqual(s.knotenlasten[0].knoten, "K2")

    def test_kennungen_und_suche(self):
        p = rahmen()
        self.assertEqual(p.balkensysteme[0].kennung, "r1")
        self.assertIs(p.bauteil("r1"), p.balkensysteme[0])
        self.assertEqual(p.freie_kennung("r"), "r2")
        with self.assertRaises(ProjektFehler):
            p.bauteil("r7")

    def test_neu_ohne_tragwerk_mit_lastfaellen(self):
        """
        Ein neues System hat kein Tragwerk (Benutzer, 2026-10-19), aber
        Eigengewicht, Auflast und Nutzlast und die Kombinationen GZT und GZG
        (Benutzer, 2026-10-23).
        """
        s = BalkensystemEintrag.neu("r1", "Träger")
        self.assertEqual((s.knoten, s.linien, s.lager, s.knotenlasten, s.querschnitte),
                         ([], [], [], [], []))
        self.assertEqual([(lf.name, lf.eigengewicht) for lf in s.lastfaelle],
                         [("Eigengewicht", True), ("Auflast", False), ("Nutzlast", False)])
        self.assertEqual([(k.name, list(k.faktoren.values())) for k in s.kombinationen],
                         [("GZT", [1.35, 1.35, 1.5]), ("GZG", [1.0, 1.0, 1.0])])
        # Die Diagramme der Statik-Analyse: M, V, N der GZT, die Verschiebung der GZG.
        self.assertEqual([(d.fall, d.groesse) for d in s.diagramme],
                         [("LK1", "M"), ("LK1", "V"), ("LK1", "N"), ("LK2", "verschiebung")])

    def test_diagramme_der_statik_analyse(self):
        """Ein Diagramm ist ein Fall und eine Grösse -- es geht mit dem System hin und zurück."""
        s = einfeldtraeger()
        d = s.diagramm(s.lastfaelle[0], "V")
        self.assertEqual((d.fall, d.groesse), ("LF1", "V"))
        self.assertEqual(BalkensystemEintrag.aus_dict(s.als_dict()), s)
        with self.assertRaisesRegex(ProjektFehler, "groesse"):
            s.diagramm("LF1", "Q")

    def test_der_einfeldtraeger_der_tests(self):
        s = einfeldtraeger("r1", "Träger", "b1")
        self.assertEqual(len(s.linien), 1)
        self.assertTrue(s.linien[0].stab)
        self.assertEqual(s.laenge(s.linien[0]), 6.0)
        self.assertEqual([(l.x, l.z, l.phi) for l in s.lager],
                         [("fest", "fest", "frei"), ("frei", "fest", "frei")])
        self.assertEqual(s.linien[0].lasten[0].lastfall, s.lastfaelle[0].kennung)

    def test_eine_datei_nur_mit_systemen_ist_ein_projekt(self):
        self.assertIn("balkensysteme", [art.liste for art in BAUTEILE])
        roh = {"balkensysteme": [einfeldtraeger("r1", "T", "").als_dict()]}
        self.assertEqual(len(dienst.pruefen({"projekt": roh})["projekt"]["balkensysteme"]), 1)


class TestGleicheFallnamen(unittest.TestCase):
    """
    Gleiche Fallnamen sind ein Fehler des Systems, nicht des Projekts: das
    System zeigt die Meldung und rechnet nicht, alles andere rechnet weiter,
    und die Datei laesst sich oeffnen. Bis 2026-10-15 hielten sie das ganze
    Projekt auf, auch jede Platte.
    """

    def gerechnet(self, aendern) -> dict:
        p = Projekt.beispiel()
        aendern(p.balkensysteme[0])
        p.pruefen()                                     # oeffnen geht
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200)
        return antwort.daten

    def meldungen(self, daten) -> list:
        system = daten["balkensysteme"]["r1"]
        self.assertFalse(system["gueltig"])
        self.assertEqual(system["faelle"], [])
        return [m["text"] for m in system["meldungen"] if m["fehler"]]

    def test_lastfall_und_kombination(self):
        daten = self.gerechnet(lambda s: setattr(s.kombinationen[0], "name", "Wind"))
        self.assertTrue(any("«Wind» heisst ein Lastfall und eine Kombination" in t
                            for t in self.meldungen(daten)))
        # Die Platte und die Analyse rechnen weiter.
        self.assertTrue({u["raum"].split(".")[0] for u in daten["urteile"]}
                        >= {"querschnitt", "querschnittsanalyse"})

    def test_zwei_lastfaelle(self):
        daten = self.gerechnet(
            lambda s: setattr(s.lastfaelle[1], "name", s.lastfaelle[0].name))
        self.assertTrue(any("Mehrere Lastfälle heissen «Eigengewicht»" in t
                            for t in self.meldungen(daten)))

    def test_zwei_kombinationen(self):
        def zweite(s):
            s.kombinationen.append(dataclasses.replace(s.kombinationen[0], kennung="LK9"))
        daten = self.gerechnet(zweite)
        self.assertTrue(any("Mehrere Kombinationen heissen «GZT»" in t
                            for t in self.meldungen(daten)))


class TestLagerkraefteAmBildschirm(unittest.TestCase):
    """
    Bildschirm und Herleitung zeigen dieselben Lagerkräfte -- auch die Summe
    der Bettung. Bis 2026-10-15 zeigte der Bildschirm nur die Lager an
    Knoten, und beim gebetteten Balken gingen die Kräfte dort nicht auf.
    """

    def test_gebettet_halten_die_zeilen_der_last_das_gleichgewicht(self):
        p = Projekt(name="Bettung")
        p.beton("C30/37")
        s = p.balkensystem("Streifen")
        q = s.querschnitt("Balken", "rechteck", b=1000.0, h=400.0)
        balken = s.linie((0, 0), (6, 0), querschnitt=q, material=s.beton("b1"),
                         quer="feder", k_quer=20000.0)
        s.lager_an((0, 0), "gelenkig")
        g = s.lastfall("G")
        s.stablast(g, balken, wert=10.0)

        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        uebersicht = antwort.daten["balkensysteme"][s.kennung]
        zeilen = uebersicht["faelle"][0]["lagerkraefte"]
        self.assertEqual([z["wo"] for z in zeilen], ["A1 (K1)", "L1: Bettung, Summe"])
        self.assertEqual([z["summe"] for z in zeilen], [False, True])
        # 10 kN/m auf 6 m: was die Zeilen aufnehmen, ist die ganze Last.
        self.assertAlmostEqual(sum(z["R_z"] for z in zeilen), 60.0, places=6)
        self.assertIn("Bettung steht die Summe", uebersicht["summen_text"])

        # Dieselben Zeilen stehen in der Herleitung.
        herleitung = " ".join(getattr(b, "text", "") + " ".join(map(str, getattr(b, "zeilen", [])))
                              for b in p.rechnen().loesung.protokoll.alle_bloecke())
        self.assertIn("L1: Bettung, Summe", herleitung)


class TestPruefen(unittest.TestCase):

    def test_unbekannte_wahl(self):
        for roh in ({"art": "flaechenlast"}, {"richtung": "schraeg"}):
            with self.subTest(roh=roh):
                with self.assertRaises(ProjektFehler):
                    StablastEintrag.aus_dict(roh)
        with self.assertRaises(ProjektFehler):
            BalkensystemEintrag.aus_dict({"kennung": "r", "lager": [{"x": "halb"}]})

    def test_fassade_meldet_tippfehler(self):
        p = rahmen()
        with self.assertRaisesRegex(ProjektFehler, "beschreibung"):
            p.balkensystem("Zwei", beschreibng="…")
        with self.assertRaisesRegex(ProjektFehler, "ellipse"):
            p.balkensysteme[0].querschnitt("E", "ellipse")
        with self.assertRaisesRegex(ProjektFehler, "Lagerart"):
            p.balkensysteme[0].lager_an((6, 4), "halb")


class TestTeilen(unittest.TestCase):
    def setUp(self):
        self.s = einfeldtraeger("r1", "Träger", "b1")
        self.linie = self.s.linien[0]
        self.lf = self.s.lastfaelle[0]
        self.linie.lasten = []

    def last(self, **felder):
        return self.s.stablast(self.lf, self.linie, **felder)

    def test_gleichlast_wird_zwei(self):
        erste = self.last(wert=10.0)
        zweite = self.s.teilen("L1", 2.0)
        self.assertEqual(self.s.netz().lage(zweite.von), (2.0, 0.0))
        self.assertEqual(self.s.laenge(self.linie), 2.0)
        self.assertEqual(self.s.laenge(zweite), 4.0)
        for linie in (self.linie, zweite):
            (last,) = linie.lasten
            self.assertEqual((last.wert_a, last.wert_b), (10.0, None))
        # Die Last auf der zweiten Hälfte ist eine neue: mit eigener Kennung.
        self.assertEqual(self.linie.lasten[0].kennung, erste.kennung)
        self.assertNotEqual(zweite.lasten[0].kennung, erste.kennung)

    def test_trapez_mit_dem_wert_am_schnitt(self):
        """Von 0 auf 12 kN/m über 6 m, geteilt bei 2 m: 0 → 4 und 4 → 12."""
        self.last(wert=0.0, wert_b=12.0)
        zweite = self.s.teilen("L1", 2.0)
        a, b = self.linie.lasten[0], zweite.lasten[0]
        self.assertEqual(a.wert_a, 0.0)
        self.assertAlmostEqual(a.wert_b, 4.0)
        self.assertEqual(b.wert_b, 12.0)
        self.assertAlmostEqual(b.wert_a, 4.0)

    def test_einzellasten_bleiben_wo_sie_stehen(self):
        """Bei 3 m und 1.5 m auf 6 m, geteilt bei 2 m: 25 % der zweiten Hälfte, 75 % der ersten."""
        einzel = self.last(art="einzellast", wert=20.0, stelle=50.0)
        moment = self.last(art="moment", wert=7.0, stelle=25.0)
        zweite = self.s.teilen("L1", 2.0)
        self.assertEqual([(l.kennung, l.art) for l in self.linie.lasten],
                         [(moment.kennung, "moment")])
        self.assertAlmostEqual(self.linie.lasten[0].stelle, 75.0)
        self.assertEqual([(l.kennung, l.art) for l in zweite.lasten],
                         [(einzel.kennung, "einzellast")])
        self.assertAlmostEqual(zweite.lasten[0].stelle, 25.0)

    def test_gelenk_am_ende_wandert_mit(self):
        self.linie.gelenk_anfang = self.linie.gelenk_ende = True
        zweite = self.s.teilen("L1", 3.0)
        self.assertEqual((self.linie.gelenk_anfang, self.linie.gelenk_ende), (True, False))
        self.assertEqual((zweite.gelenk_anfang, zweite.gelenk_ende), (False, True))

    def test_ein_knoten_am_schnitt_wird_genommen(self):
        k = self.s.netz().an(2.0, 0.0)
        zweite = self.s.teilen("L1", 2.0)
        self.assertEqual(zweite.von, k)
        self.assertEqual(len(self.s.knoten), 3)

    def test_nur_dazwischen(self):
        for stelle in (0.0, 6.0, 7.5):
            with self.subTest(stelle=stelle):
                with self.assertRaises(ProjektFehler):
                    self.s.teilen("L1", stelle)


class TestUmkehren(unittest.TestCase):
    def setUp(self):
        self.s = einfeldtraeger("r1", "Träger", "b1")
        self.linie = self.s.linien[0]
        self.linie.lasten = []
        lf = self.s.lastfaelle[0]
        self.s.stablast(lf, self.linie, wert=2.0, wert_b=8.0)
        self.s.stablast(lf, self.linie, wert=3.0, richtung="quer")
        self.s.stablast(lf, self.linie, art="einzellast", wert=5.0, stelle=25.0, richtung="laengs")
        self.s.stablast(lf, self.linie, art="moment", wert=7.0, stelle=40.0)
        self.linie.gelenk_anfang = True

    def test_lasten_bleiben_wo_sie_wirken(self):
        vorher = [l.als_dict() for l in self.linie.lasten]
        self.s.umkehren("L1")
        self.assertEqual((self.linie.von, self.linie.bis), ("K2", "K1"))
        self.assertEqual((self.linie.gelenk_anfang, self.linie.gelenk_ende), (False, True))
        senkrecht, quer, einzel, moment = self.linie.lasten
        self.assertEqual((senkrecht.wert_a, senkrecht.wert_b), (8.0, 2.0))
        self.assertEqual((quer.wert_a, quer.wert_b), (-3.0, None))
        self.assertEqual((einzel.stelle, einzel.wert_a), (75.0, -5.0))
        self.assertEqual((moment.stelle, moment.wert_a), (60.0, 7.0))
        self.s.umkehren("L1")
        self.assertEqual([l.als_dict() for l in self.linie.lasten], vorher)


if __name__ == "__main__":
    unittest.main()


# ===========================================================================
# Zum Rechnen
# ===========================================================================


def traeger(**masse) -> Projekt:
    """Ein Einfeldträger von 6 m mit 10 kN/m -- max M = 45 kNm."""
    p = Projekt(name="Träger")
    p.beton("C30/37")
    p.stahl("B500B")
    s = p.balkensystem("Träger")
    q = s.querschnitt("R", "rechteck", **(masse or {"b": 300.0, "h": 600.0}))
    linie = s.linie((0, 0), (6, 0), querschnitt=q, material=s.beton("b1"))
    s.lager_an((0, 0), "gelenkig")
    s.lager_an((6, 0), "verschieblich")
    s.stablast(s.lastfall("G"), linie, wert=10.0)
    return p


class TestModell(unittest.TestCase):
    def test_einheiten_und_richtungen(self):
        p = rahmen()
        modell = p.balkensysteme[0].modell()
        self.assertTrue(modell.gueltig, modell.meldungen)
        g, w = modell.system.lastfaelle
        self.assertEqual(g.lasten[0].wert_a, 25e3)
        knotenlast = next(l for l in w.lasten if not hasattr(l, "stab"))
        self.assertEqual((knotenlast.Fx, knotenlast.Fz), (10e3, 0.0))
        self.assertEqual(modell.system.kombinationen[0].faktoren,
                         {"Eigengewicht": 1.35, "Wind": 1.5})
        self.assertEqual(modell.paare, {"L1": ("Q1", "M1"), "L2": ("Q1", "M1"),
                                        "L3": ("Q1", "M1")})

    def test_senkrecht_zeigt_nach_unten(self):
        s = einfeldtraeger("r1", "T", "b1")
        s.knotenlast(s.lastfaelle[0], (6, 0), 5.0)
        s.knotenlast(s.lastfaelle[0], (6, 0), 2.0, art="moment")
        lasten = s.modell().system.lastfaelle[0].lasten
        self.assertEqual(lasten[-2].Fz, -5e3)
        self.assertEqual(lasten[-1].M, 2e3)

    def test_federn(self):
        s = einfeldtraeger("r1", "T", "b1")
        s.lager[1].x, s.lager[1].k_x = "feder", 5000.0
        s.linien[0].quer, s.linien[0].k_quer = "feder", 2000.0
        modell = s.modell()
        self.assertEqual(modell.system.lager[1].x, 5e6)
        self.assertEqual(modell.system.staebe[0].quer, 2e6)
        s.lager[1].k_x = 0.0
        self.assertFalse(s.modell().gueltig)

    def test_fehler_der_beschreibung(self):
        for aendern, wort, elemente in (
                (lambda s: setattr(s.linien[0], "querschnitt", "Q9"), "keinen Querschnitt", {"L1"}),
                (lambda s: setattr(s.linien[0], "material", ""), "kein Material", {"L1"}),
                (lambda s: setattr(s.linien[0], "material", "M9"), "im System nicht gibt",
                 {"L1"}),
                (lambda s: s.querschnitte[0].masse.__setitem__("h", 0.0), "Höhe",
                 {"Q1", "L1"})):
            with self.subTest(wort=wort):
                s = einfeldtraeger("r1", "T", "b1")
                aendern(s)
                modell = s.modell()
                fehler = [m for m in modell.meldungen if m.fehler]
                self.assertEqual(len(fehler), 1)
                self.assertIn(wort, fehler[0].text)
                self.assertEqual(set(fehler[0].elemente), elemente)
                self.assertEqual(modell.paare, {})

    def test_last_ohne_lastfall_bleibt_mit_hinweis_weg(self):
        s = einfeldtraeger("r1", "T", "b1")
        s.linien[0].lasten[0].lastfall = "LF9"
        modell = s.modell()
        self.assertTrue(modell.gueltig)
        self.assertIn("keinem Lastfall", modell.meldungen[0].text)
        self.assertEqual(modell.system.lastfaelle[0].lasten, [])


class TestRechnen(unittest.TestCase):
    def test_einfeldtraeger(self):
        e = traeger().rechnen()
        system = e.balkensystem("Träger")
        self.assertTrue(system.ergebnis.gueltig)
        x, M = system.verlaeufe("G")["L1"].extrem("M").groesst
        self.assertAlmostEqual(x, 3.0, places=9)
        self.assertAlmostEqual(M, 45e3, places=4)
        E = e.wert("beton.b1.E_cm").groesse.si
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M1.EI").groesse.si,
                               E * 0.3 * 0.6 ** 3 / 12, delta=1e-6 * E)
        self.assertEqual(len(system.ergebnis.unbekannte), 3)

    def test_eigenes_material(self):
        """Ein Rundstab aus Stahl: E von Hand, als Eingabe im System."""
        p = traeger()
        s = p.balkensysteme[0]
        s.querschnitte[0].vorlage, s.querschnitte[0].masse = "kreis", {"d": 100.0}
        s.linien[0].material = s.eigenes_material("Stahl", E=200000.0, rho=7850.0).kennung
        e = p.rechnen()
        self.assertEqual(e.wert("balkensystem.r1.M2.E").groesse.si, 200000e6)
        EA = 200000e6 * math.pi * 0.05 ** 2
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M2.EA").groesse.si, EA,
                               delta=1e-12 * EA)

    def test_aus_platte_und_analyse(self):
        p = traeger()
        decke = p.platte("Decke", h=250)
        unterzug = p.analyse("Unterzug")
        s = p.balkensysteme[0]
        aus_platte = s.querschnitt_aus("Streifen", "platte", decke)
        aus_analyse = s.querschnitt_aus("Unterzug", "analyse", unterzug)
        s.linie((6, 0), (9, 0), querschnitt=aus_platte, material="M1")
        s.linie((9, 0), (12, 0), querschnitt=aus_analyse, material="M1")
        s.lager_an((12, 0), "verschieblich")
        e = p.rechnen()
        self.assertTrue(e.balkensystem("r1").ergebnis.gueltig,
                        e.balkensystem("r1").ergebnis.meldungen)
        self.assertEqual(e.wert(f"balkensystem.r1.{aus_platte.kennung}.A").groesse.si,
                         1.0 * 0.25)
        self.assertEqual(e.wert(f"balkensystem.r1.{aus_analyse.kennung}.I").groesse.si,
                         e.wert("querschnittsanalyse.a1.I_y").groesse.si)
        self.assertEqual(e.aufbau.balkensysteme["r1"].bezuege, ["a1", "q1"])

    def test_ein_fremder_verweis_scheitert_hart(self):
        p = traeger()
        p.balkensysteme[0].querschnitt_aus("Weg", "platte", "q7")
        with self.assertRaisesRegex(ProjektFehler, "q7"):
            p.aufbauen()

    def test_beweglich_ist_eine_meldung(self):
        p = traeger()
        p.balkensysteme[0].lager[0].x = "frei"
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200)
        uebersicht = antwort.daten["balkensysteme"]["r1"]
        self.assertFalse(uebersicht["gueltig"])
        self.assertIn("beweglich", uebersicht["meldungen"][0]["text"])
        self.assertTrue(uebersicht["beweglich"])
        verlauf = dienst.bearbeite("balkensystem_verlauf",
                                   {"projekt": p.als_dict(), "kennung": "r1", "fall": "G"})
        self.assertEqual((verlauf.status, verlauf.daten["verlauf"]), (200, None))

    def test_unbestimmte_drehung(self):
        """Ein Fachwerkknoten: alle Stäbe gelenkig, die Drehung ist gestrichen."""
        p = traeger()
        s = p.balkensysteme[0]
        q = s.querschnitte[0]
        s.linie((0, 0), (3, 3), querschnitt=q, material="M1", gelenk_ende=True)
        s.linie((6, 0), (3, 3), querschnitt=q, material="M1", gelenk_ende=True)
        e = p.rechnen()
        self.assertEqual(e.balkensystem("r1").ergebnis.unbestimmt(), ["K3"])
        antwort = dienst.bearbeite("balkensystem_verlauf",
                                   {"projekt": p.als_dict(), "kennung": "r1", "fall": "G"})
        knoten = antwort.daten["verlauf"]["knoten"]["K3"]
        self.assertTrue(knoten["unbestimmt"])
        self.assertIsNone(knoten["phi"])

    def test_herleitung(self):
        text = str(traeger().rechnen().bericht())
        for wort in ("Balkensystem: Träger", "nach Vorgabe, nicht nachgeschlagen",
                     "Gleichgewichtsprobe", "Extremwerte", "Lagerkräfte"):
            self.assertIn(wort, text)


class TestTeilenUndUmkehrenRechnenGleich(unittest.TestCase):
    """Teilen und Umkehren ändern die Beschreibung, nicht das Tragwerk."""

    def lagerkraefte(self, p):
        fall = p.rechnen().balkensystem("Rahmen").ergebnis.faelle[-1]
        return {k: tuple(round(v / 1e3, 6) for v in werte)
                for k, werte in fall.lagerkraefte.items()}

    def test_teilen(self):
        p = rahmen()
        s = p.balkensysteme[0]
        s.linien[1].lasten += [
            StablastEintrag(kennung="P8", lastfall="LF2", art="linienlast", wert_a=2.0, wert_b=8.0),
            StablastEintrag(kennung="P9", lastfall="LF2", art="einzellast", wert_a=5.0, stelle=70.0)]
        vorher = self.lagerkraefte(p)
        s.teilen("L2", 2.5)
        self.assertEqual(self.lagerkraefte(p), vorher)

    def test_umkehren(self):
        p = rahmen()
        vorher = self.lagerkraefte(p)
        for linie in ("L1", "L2", "L3"):
            p.balkensysteme[0].umkehren(linie)
        self.assertEqual(self.lagerkraefte(p), vorher)


class TestZwischenspeicher(unittest.TestCase):
    def beschreibung(self):
        p = traeger()
        unterzug = p.analyse("Unterzug")
        decke = p.platte("Decke", h=250)
        decke.einwirkung("Feld", M_Ed=20.0)
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Unterzug", "analyse", unterzug)
        s.linien[0].querschnitt = q.kennung
        return p.als_dict()

    def rechnen(self, d, frisch):
        if frisch:
            dienst.SPEICHER.leeren()
        return dienst.bearbeite("rechnen", {"projekt": d})

    def test_eine_geaenderte_analyse_rechnet_das_system_neu(self):
        d = self.beschreibung()
        self.rechnen(d, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        d["querschnittsanalysen"][0]["knoten"][2]["z"] = 700.0
        mit = self.rechnen(d, frisch=False)
        self.assertEqual((dienst.SPEICHER.treffer, dienst.SPEICHER.fehlgriffe), (1, 2))
        ohne = self.rechnen(d, frisch=True)
        self.assertEqual(json.dumps(mit.daten, sort_keys=True, default=str),
                         json.dumps(ohne.daten, sort_keys=True, default=str))

    def test_eine_fremde_platte_nicht(self):
        d = self.beschreibung()
        self.rechnen(d, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        d["querschnitte"][0]["h"] = 260.0
        self.rechnen(d, frisch=False)
        self.assertEqual((dienst.SPEICHER.treffer, dienst.SPEICHER.fehlgriffe), (2, 1))

    def test_die_bilder_kommen_aus_dem_speicher(self):
        d = self.beschreibung()
        self.rechnen(d, frisch=True)
        dienst.SPEICHER.treffer = 0
        antwort = dienst.bearbeite("balkensystem_verlauf",
                                   {"projekt": d, "kennung": "r1", "fall": "G"})
        self.assertEqual(antwort.status, 200)
        self.assertEqual(dienst.SPEICHER.treffer, 1)
        self.assertIn("L1", antwort.daten["verlauf"]["staebe"])


class TestBearbeiten(unittest.TestCase):
    def test_teilen_mit_punkt_und_umkehren(self):
        d = traeger().als_dict()
        antwort = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "r1", "aktion": "teilen", "linie": "L1",
            "punkt": [2.0, 0.4]})
        self.assertEqual((antwort.status, antwort.daten["neu"]), (200, ["L2"]))
        knoten = {k["kennung"]: (k["x"], k["z"]) for k in antwort.daten["balkensystem"]["knoten"]}
        self.assertEqual(knoten["K3"], (2.0, 0.0))
        d["balkensysteme"][0] = antwort.daten["balkensystem"]
        antwort = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "r1", "aktion": "umkehren", "linien": ["L1", "L2"]})
        linien = antwort.daten["balkensystem"]["linien"]
        self.assertEqual([(l["von"], l["bis"]) for l in linien], [("K3", "K1"), ("K2", "K3")])

    def test_teilen_in_der_mitte_und_uebersicht_ohne_fall(self):
        d = traeger().als_dict()
        antwort = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "r1", "aktion": "teilen", "linie": "L1", "anteil": 0.5})
        knoten = {k["kennung"]: (k["x"], k["z"]) for k in antwort.daten["balkensystem"]["knoten"]}
        self.assertEqual(knoten["K3"], (3.0, 0.0))
        antwort = dienst.bearbeite("balkensystem_verlauf", {"projekt": d, "kennung": "r1"})
        self.assertEqual(antwort.status, 200)
        self.assertIsNone(antwort.daten["verlauf"])
        self.assertTrue(antwort.daten["uebersicht"]["gueltig"])

    def test_falsche_anfragen(self):
        d = traeger().als_dict()
        for rumpf in ({"kennung": "q1", "aktion": "umkehren"},
                      {"kennung": "r1", "aktion": "drehen"},
                      {"kennung": "r1", "aktion": "teilen", "linie": "L1", "stelle": "mitte"},
                      {"kennung": "r1", "aktion": "teilen", "linie": "L1", "stelle": 9.0}):
            with self.subTest(rumpf=rumpf):
                antwort = dienst.bearbeite("balkensystem_bearbeiten", {"projekt": d, **rumpf})
                self.assertEqual(antwort.status, 400)


class TestEigengewicht(unittest.TestCase):
    """
    Das Eigengewicht kommt von selbst: g_k = ρ · g · A je Stab, mit g = 10
    m/s² und beim Beton der Dichte des Stahlbetons (Benutzer, 2026-10-23).
    """

    def system(self, eigen=None, **masse):
        """Der Träger aus dem Beton des Projekts -- oder mit ``eigen`` aus einem eigenen Material."""
        p = Projekt(name="Träger")
        p.beton("C30/37")
        s = BalkensystemEintrag.neu("r1", "Träger")
        q = s.querschnitt("R", "rechteck", **(masse or {"b": 300.0, "h": 600.0}))
        material = s.eigenes_material("Stahl", **eigen) if eigen else s.beton("b1")
        s.linie((0, 0), (6, 0), querschnitt=q, material=material)
        s.lager_an((0, 0), "gelenkig")
        s.lager_an((6, 0), "verschieblich")
        p.balkensysteme.append(s)
        return p

    def lagerkraefte(self, p, fall):
        f = p.rechnen().balkensystem("r1").ergebnis.fall(fall)
        return [round(rz / 1e3, 6) for _, rz, _ in f.lagerkraefte.values()]

    def test_stahlbeton_25_kn_pro_m3(self):
        # 2500 kg/m³ · 10 m/s² · 0.18 m² = 4.5 kN/m, auf 6 m je Lager 13.5 kN.
        p = self.system()
        self.assertAlmostEqual(p.rechnen().loesung.werte["balkensystem.r1.Q1.M1.g_k"].groesse.si,
                               4.5e3)
        self.assertEqual(self.lagerkraefte(p, "Eigengewicht"), [13.5, 13.5])

    def test_kombinationen(self):
        p = self.system()
        self.assertEqual(self.lagerkraefte(p, "GZT"), [18.225, 18.225])
        self.assertEqual(self.lagerkraefte(p, "GZG"), [13.5, 13.5])

    def test_eigenes_material_mit_seiner_dichte(self):
        # Ein Stahlstab 100 × 100 mm: 7850 · 10 · 0.01 = 785 N/m.
        p = self.system(eigen={"E": 200000.0, "rho": 7850.0}, b=100.0, h=100.0)
        self.assertAlmostEqual(p.rechnen().loesung.werte["balkensystem.r1.Q1.M1.g_k"].groesse.si,
                               785.0)

    def test_eine_linie_ohne_querschnitt_wiegt_nichts(self):
        p = self.system()
        p.balkensysteme[0].linie((6, 0), (6, -1), quer="fest")
        self.assertEqual(self.lagerkraefte(p, "Eigengewicht")[:2], [13.5, 13.5])

    def test_nur_ein_lastfall_bekommt_es(self):
        p = self.system()
        p.balkensysteme[0].lastfaelle[1].eigengewicht = True
        meldungen = [m for m in p.balkensysteme[0].modell().meldungen if m.fehler]
        self.assertTrue(any("Eigengewicht" in m.text for m in meldungen))



class TestMaterialien(unittest.TestCase):
    """
    Die Materialien eines Systems (Benutzer, 2026-10-24): ein Beton des
    Projekts -- E_cm und die Dichte des Stahlbetons von ihm -- oder ein
    eigenes mit E und Dichte von Hand.
    """

    def meldungen(self, p):
        return [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.fehler]

    def test_eigenes_material_rechnet_mit_seinem_e(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.linien[0].material = s.eigenes_material("Weich", E=10000.0, rho=2500.0).kennung
        e = p.rechnen()
        EI = 10000e6 * 0.3 * 0.6 ** 3 / 12
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.M2.EI").groesse.si, EI, delta=1e-9 * EI)
        # Die Durchbiegung in der Mitte, nach unten positiv: 5 q L⁴ / (384 EI).
        w = e.balkensystem("r1").verlaeufe("G")["L1"].extrem("w").groesst[1]
        self.assertAlmostEqual(w, 5 * 10e3 * 6 ** 4 / (384 * EI), delta=1e-6)

    def test_ein_querschnitt_aus_zwei_materialien(self):
        """Derselbe Querschnitt aus Beton und aus Stahl: verschieden steif, verschieden schwer."""
        p = traeger()
        s = p.balkensysteme[0]
        s.lastfaelle[0].eigengewicht = True
        stahl = s.eigenes_material("Stahl", E=200000.0, rho=7850.0)
        q = s.querschnitt("Gleich", "rechteck", b=100.0, h=100.0)
        s.linie((6, 0), (8, 0), querschnitt=q, material="M1")
        s.linie((8, 0), (10, 0), querschnitt=q, material=stahl)
        s.lager_an((10, 0), "verschieblich")
        e = p.rechnen()
        E_cm = e.wert("beton.b1.E_cm").groesse.si
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M1.EA").groesse.si, E_cm * 0.01,
                               delta=1e-9 * E_cm)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M2.EA").groesse.si, 200000e6 * 0.01,
                               delta=1e-6)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M1.g_k").groesse.si, 250.0)
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q2.M2.g_k").groesse.si, 785.0)

    def test_baukasten_und_herleitung(self):
        s = BalkensystemEintrag(kennung="r1", name="T")
        beton = s.beton("b1")
        self.assertIs(s.beton("b1"), beton)                    # einmal je Beton
        holz = s.eigenes_material("Holz", E=11000.0, rho=500.0)
        self.assertEqual([(m.kennung, m.art) for m in s.stabmaterialien],
                         [("M1", "beton"), ("M2", "eigen")])
        self.assertEqual((holz.name, holz.E, holz.rho), ("Holz", 11000.0, 500.0))
        self.assertEqual(s.materialien(), ["b1"])
        p = traeger()
        s = p.balkensysteme[0]
        s.linien[0].material = s.eigenes_material("Holz", E=11000.0, rho=500.0).kennung
        text = str(p.rechnen().bericht())
        self.assertIn("E-Modul, «Holz» (von Hand)", text)
        self.assertIn("Biegesteifigkeit, «R» aus Holz", text)

    def test_der_beton_ist_ein_verweis(self):
        """Den Beton eines Materials löscht man nicht; zeigt es ins Leere, scheitert es hart."""
        p = traeger()
        self.assertEqual(p.verweise("b1"), [p.balkensysteme[0]])
        p.balkensysteme[0].stabmaterialien[0].beton = "b7"
        with self.assertRaisesRegex(ProjektFehler, "b7"):
            p.aufbauen()

    def test_betonstahl_ist_kein_material_der_staebe(self):
        p = traeger()                                   # mit B500B als s1
        p.balkensysteme[0].stabmaterialien[0].beton = "s1"
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("L1 nimmt das Material M1", meldungen[0])
        self.assertIn("ist kein Beton", meldungen[0])

    def test_ohne_beton(self):
        p = traeger()
        p.balkensysteme[0].stabmaterialien[0].beton = ""
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("kein Beton gewählt", meldungen[0])

    def test_null_ist_kein_e_modul(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.linien[0].material = s.eigenes_material("Weich", E=10000.0, rho=0.0).kennung
        s.stabmaterialien[-1].E = 0.0
        with self.assertRaisesRegex(ProjektFehler, "E-Modul"):
            Projekt.aus_dict(p.als_dict()).rechnen()


class TestMaterialDesQuerschnitts(unittest.TestCase):
    """
    «gemäss Querschnitt»: eine Linie nimmt das Material, das ihre Platte oder
    Querschnittsanalyse mitbringt (Benutzer, 2026-10-23).
    """

    def projekt(self, art):
        """Der Träger und daneben ein Stab aus einer Platte oder Analyse in C25/30."""
        p = traeger()
        p.beton("C25/30")
        bezug = (p.platte("Decke", h=250, beton="b2") if art == "platte"
                 else p.analyse("Unterzug", beton="b2"))
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Aus dem Bauteil", art, bezug)
        s.linie((6, 0), (9, 0), querschnitt=q, material=MATERIAL_DES_QUERSCHNITTS)
        s.lager_an((9, 0), "verschieblich")
        return p, q

    def meldungen(self, p):
        return [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.fehler]

    def test_platte_und_analyse_bringen_ihren_beton(self):
        for art in ("platte", "analyse"):
            with self.subTest(art=art):
                p, q = self.projekt(art)
                e = p.rechnen()
                self.assertTrue(e.balkensystem("r1").ergebnis.gueltig,
                                e.balkensystem("r1").ergebnis.meldungen)
                quer, material = e.aufbau.balkensysteme["r1"].paare["L2"]
                self.assertEqual((quer, material.stoff.name), (q.kennung, "C25/30"))
                A = e.wert(f"balkensystem.r1.{q.kennung}.A").groesse.si
                self.assertAlmostEqual(
                    e.wert(f"balkensystem.r1.{q.kennung}.{MATERIAL_DES_QUERSCHNITTS}.EA").groesse.si,
                    e.wert("beton.b2.E_cm").groesse.si * A, delta=1e-3)

    def test_eine_vorlage_bringt_keines(self):
        p = traeger()
        p.balkensysteme[0].linien[0].material = MATERIAL_DES_QUERSCHNITTS
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("L1 nimmt das Material gemäss Querschnitt", meldungen[0])
        self.assertIn("nach Vorlage", meldungen[0])

    def test_zwei_betone_in_der_analyse(self):
        p, q = self.projekt("analyse")
        p.querschnittsanalysen[0].polygon([(300, 0), (600, 0), (600, 200), (300, 200)],
                                          material="b1")
        meldungen = self.meldungen(p)
        self.assertEqual(len(meldungen), 1)
        self.assertIn("C25/30 und C30/37", meldungen[0])

    def test_eine_leere_analyse(self):
        p, q = self.projekt("analyse")
        p.querschnittsanalysen[0] = QuerschnittsanalyseEintrag.neu(kennung="a1", name="Leer")
        meldungen = self.meldungen(p)
        self.assertTrue(any("gemäss Querschnitt" in m and "noch leer" in m for m in meldungen),
                        meldungen)


class TestUmrisse(unittest.TestCase):
    """Je Querschnitt sein Umriss für das Bildchen in seiner Zeile (Benutzer, 2026-10-24)."""

    def test_vorlage_platte_analyse_und_kennwerte(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.querschnitt_aus("Streifen", "platte", p.platte("Decke", h=250))
        s.querschnitt_aus("Unterzug", "analyse", p.analyse("Unterzug"))
        s.querschnitt_mit_kennwerten("Von Hand", A=1000.0, I=10.0)
        s.querschnitt("Unmöglich", "rechteck", h=0.0)
        umrisse = dienst.bearbeite("rechnen", {"projekt": p.als_dict()}).daten["stabumrisse"]["r1"]
        # Das Rechteck 300 × 600 mit seinen Massen, der Streifen 1000 × 250 der Platte.
        self.assertEqual(umrisse["Q1"], [[[0.0, 0.0], [300.0, 0.0], [300.0, 600.0], [0.0, 600.0]]])
        self.assertEqual(umrisse["Q2"], [[[0.0, 0.0], [1000.0, 0.0], [1000.0, 250.0], [0.0, 250.0]]])
        self.assertEqual([len(polygon) for polygon in umrisse["Q3"]], [4])
        # Kennwerte von Hand haben keine Form, ein unmöglicher Querschnitt auch nicht.
        self.assertEqual((umrisse["Q4"], umrisse["Q5"]), ([], []))


class TestEeq(unittest.TestCase):
    """
    E_eq aus einer Querschnittsanalyse bei N und M -- an derselben Stelle wie
    ihre Linie M–E_eq, für EA und EI jedes Stabs mit dem Querschnitt
    (Benutzer, 2026-10-23).
    """

    def projekt(self, **eq):
        """
        Der Träger, sein Stab mit dem Querschnitt der Analyse «Unterzug» und
        ihrem Material -- E_eq gilt für einen Stab gemäss Querschnitt.
        """
        p = traeger()
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Unterzug", "analyse", p.analyse("Unterzug"), E_eq=eq)
        s.linien[0].querschnitt = q.kennung
        s.linien[0].material = MATERIAL_DES_QUERSCHNITTS
        return p, q

    def linie(self, e, q, N=0.0):
        """Die Linie M–E_eq der Analyse selbst, gerechnet wie in ihrer Spannung-Dehnung-Analyse."""
        werte = e.loesung.werte
        paar = schnittpaar(e.aufbau.querschnittsanalysen["a1"], Zugseite.UNTEN,
                           lambda kid: werte[kid].groesse.si, q.eq.wahl)
        return aequivalenter_modul(moment_kruemmung(paar, N=N), I_c=paar.I_c, A_c=paar.A_c,
                                   E_cm=paar.E_cm)

    def test_ungerissen_wie_der_anfang_der_linie(self):
        p, q = self.projekt(M=0.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        self.assertAlmostEqual(E, self.linie(e, q).ungerissen, delta=1e-6 * E)

    def test_gerissen_auf_der_linie(self):
        """Bei 80 kNm gerissen: zwischen den beiden Punkten der Linie daneben, und weicher als ungerissen."""
        p, q = self.projekt(M=80.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        punkte = [pt for pt in self.linie(e, q).punkte if pt.gerissen and pt.modul is not None]
        vor = max((pt for pt in punkte if pt.kraft <= 80e3), key=lambda pt: pt.kraft)
        nach = min((pt for pt in punkte if pt.kraft >= 80e3), key=lambda pt: pt.kraft)
        self.assertLessEqual(min(vor.modul, nach.modul), E)
        self.assertLessEqual(E, max(vor.modul, nach.modul))
        self.assertLess(E, self.linie(e, q).ungerissen)
        # Dasselbe E für EA und EI.
        A = e.wert(f"balkensystem.r1.{q.kennung}.A").groesse.si
        self.assertAlmostEqual(
            e.wert(f"balkensystem.r1.{q.kennung}.{MATERIAL_DES_QUERSCHNITTS}.EA").groesse.si,
            E * A, delta=1e-6 * E * A)

    def test_ein_material_des_systems_nimmt_sein_e(self):
        """Mit dem Beton des Systems statt dem des Querschnitts gilt E_cm -- E_eq zählt nicht."""
        p, q = self.projekt(M=80.0)
        p.balkensysteme[0].linien[0].material = "M1"
        e = p.rechnen()
        A, E_cm = (e.wert(i).groesse.si for i in (f"balkensystem.r1.{q.kennung}.A", "beton.b1.E_cm"))
        self.assertAlmostEqual(e.wert(f"balkensystem.r1.{q.kennung}.M1.EA").groesse.si,
                               E_cm * A, delta=1e-9 * E_cm * A)

    def test_zu_grosses_moment_ist_eine_meldung(self):
        """Kein E_eq über dem Biegewiderstand: das System rechnet nicht und sagt warum."""
        p, q = self.projekt(M=1000.0)
        ergebnis = p.rechnen().balkensystem("r1").ergebnis
        self.assertFalse(ergebnis.gueltig)
        meldungen = [m.text for m in ergebnis.meldungen if m.fehler]
        self.assertEqual(len(meldungen), 1)
        self.assertIn("kein E_eq", meldungen[0])
        self.assertIn("Biegewiderstand", meldungen[0])

    def test_nur_aus_platte_oder_analyse(self):
        p = traeger()
        p.balkensysteme[0].querschnitte[0].e_modul = "e_eq"
        meldungen = [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.fehler]
        self.assertTrue(any("nur bei einem Querschnitt aus einer Platte oder Querschnittsanalyse"
                            in m for m in meldungen), meldungen)

    def test_herleitung(self):
        p, q = self.projekt(M=80.0)
        text = str(p.rechnen().bericht())
        for wort in ("Äquivalenter E-Modul, «Unterzug»", "der Querschnitt gilt gerissen",
                     "E-Modul, «Unterzug» (E_eq)", "Biegesteifigkeit, «Unterzug» mit E_eq"):
            self.assertIn(wort, text)


class TestEeqPlatte(unittest.TestCase):
    """
    E_eq aus einer Platte: immer in x-Richtung, Zug unten (Benutzer,
    2026-10-24) -- an derselben Stelle wie die Linie M–E_eq der Platte.
    """

    def projekt(self, **eq):
        """Der Träger mit dem Streifen der Platte «Decke» (h = 250 mm, M_Riss = 29 kNm)."""
        p = traeger()
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Streifen", "platte", p.platte("Decke", h=250), E_eq=eq)
        s.linien[0].querschnitt = q.kennung
        s.linien[0].material = MATERIAL_DES_QUERSCHNITTS
        return p, q

    def linie(self, e, q):
        """Die Linie M–E_eq der Platte in x, gerechnet wie in ihrer Spannung-Dehnung-Analyse."""
        werte = e.loesung.werte
        paar = loeserpaar(e.aufbau.querschnitte["q1"], Richtung.X,
                          lambda kid: werte[kid].groesse.si, q.eq.wahl)
        return aequivalenter_modul(moment_kruemmung(paar, N=0.0), I_c=paar.I_c, A_c=paar.A_c,
                                   E_cm=paar.E_cm)

    def test_ungerissen_wie_der_anfang_der_linie(self):
        p, q = self.projekt(M=20.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        self.assertAlmostEqual(E, self.linie(e, q).ungerissen, delta=1e-6 * E)

    def test_gerissen_auf_der_linie(self):
        p, q = self.projekt(M=40.0)
        e = p.rechnen()
        E = e.wert(f"balkensystem.r1.{q.kennung}.E").groesse.si
        punkte = [pt for pt in self.linie(e, q).punkte if pt.gerissen and pt.modul is not None]
        vor = max((pt for pt in punkte if pt.kraft <= 40e3), key=lambda pt: pt.kraft)
        nach = min((pt for pt in punkte if pt.kraft >= 40e3), key=lambda pt: pt.kraft)
        self.assertLessEqual(min(vor.modul, nach.modul), E)
        self.assertLessEqual(E, max(vor.modul, nach.modul))
        A = e.wert(f"balkensystem.r1.{q.kennung}.A").groesse.si
        self.assertAlmostEqual(
            e.wert(f"balkensystem.r1.{q.kennung}.{MATERIAL_DES_QUERSCHNITTS}.EA").groesse.si,
            E * A, delta=1e-6 * E * A)

    def test_ein_negatives_moment_hat_keines(self):
        p, q = self.projekt(M=-10.0)
        meldungen = [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen if m.fehler]
        self.assertEqual(len(meldungen), 1)
        self.assertIn("negatives Moment hat keines", meldungen[0])

    def test_herleitung(self):
        p, q = self.projekt(M=40.0)
        text = str(p.rechnen().bericht())
        self.assertIn("Platte «Decke», x-Richtung, Zug unten", text)
        self.assertIn("der Querschnitt gilt gerissen", text)

