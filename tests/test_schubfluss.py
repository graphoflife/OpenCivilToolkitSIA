"""
Der Schubfluss in den Schnitten einer Querschnittsanalyse (opencivil.nachweis.qa_schubfluss).

Was ein Schnitt abtrennt (opencivil.querschnitt.abtrennen), dann der
Schubfluss v = ΔF′/Δx gegen Handrechnungen: elastisch V·S′/I an einem
I-Profil und an einem Verbundträger über der Stütze, im Plattenbalken
3/8 des Flansches, in der Aufdopplung die ganze Druckkraft durch die Fuge,
solange die Druckzone im Aufbeton liegt. Dazu, was ohne Querkraft, ohne
Gleichgewichtslage und mit einem Schnitt geschieht, der nichts abtrennt, und
was Bericht und Zeichnung davon zeigen.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import schubfluss
from opencivil.nachweis.qa_schubfluss import KEINE_LAGE, teilquerschnitt
from opencivil.projekt import Projekt
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.querschnitt.abtrennen import (
    NICHT_GETRENNT, OHNE_LAENGE, OHNE_MATERIAL, Schnitt, abtrennen,
)
from opencivil.web.zeichengeometrie import geometrie
from tests.unfertig import meldung

#: Ein I-Profil in mm: Flansche 200 × 20, Steg 10 × 360, 400 hoch.
I_PROFIL = [[-100, 0], [100, 0], [100, 20], [5, 20], [5, 380], [100, 380], [100, 400],
            [-100, 400], [-100, 380], [-5, 380], [-5, 20], [-100, 20]]
#: Sein Flächenträgheitsmoment um y, in mm⁴.
I_Y = 2 * (200 * 20 ** 3 / 12 + 200 * 20 * 190 ** 2) + 10 * 360 ** 3 / 12

#: Ein Plattenbalken in mm: Flansch 1600 × 200 über einem Steg 400 × 600.
PLATTENBALKEN = [[-800, 800], [-800, 600], [-200, 600], [-200, 0], [200, 0], [200, 600],
                 [800, 600], [800, 800]]


def rechnen(p):
    """Aufbau und Lösung -- mit allem, was die Bauteile über ihre Nachweise hinaus rechnen."""
    aufbau = p.aufbauen()
    return aufbau, aufbau.werk.loese(*[z for t in aufbau.bauteile() for z in t.weitere_ziele])


def analyse(p, name, einachsig=True):
    a = QuerschnittsanalyseEintrag(kennung=p.freie_kennung("a"), name=name, einachsig=einachsig)
    p.querschnittsanalysen.append(a)
    return a


def ergebnisse(aufbau, loesung, kennung):
    """Je Schnitt und Fall: v in kN/m, τ in N/mm² und b_i in mm."""
    w = loesung.werte
    return {(z.schnitt, z.fall): (w[z.v.id].groesse.si / 1e3, w[z.tau.id].groesse.si / 1e6,
                                  w[z.b_i.id].groesse.si * 1e3)
            for z in aufbau.teile[kennung].schubfluss.zeilen}


class Abtrennen(unittest.TestCase):
    """Was eine Strecke vom Plattenbalken abtrennt -- reine Geometrie, in mm."""

    def setUp(self):
        self.polygone = [[tuple(p) for p in PLATTENBALKEN]]

    def trenne(self, von, bis, links=True, polygone=None, traegt=None, eltern=None):
        polygone = polygone or self.polygone
        return abtrennen(polygone, traegt or [True] * len(polygone),
                         eltern or [None] * len(polygone), von, bis, links=links)

    def test_flansch_neben_dem_steg(self):
        # Nach unten gezeichnet zeigt «rechts» nach links: der Flansch links des Stegs.
        a = self.trenne((-200, 800), (-200, 600), links=False)
        self.assertAlmostEqual(a.breite, 200.0)
        self.assertAlmostEqual(a.flaeche, 600 * 200)
        self.assertTrue(a.enthaelt((-500, 700)))
        self.assertFalse(a.enthaelt((0, 700)))
        # Auf dem Schnitt zählt ein Punkt zum Rest, gleich daneben zum Teil.
        self.assertFalse(a.enthaelt((-200, 700)))
        self.assertTrue(a.enthaelt((-201, 700)))

    def test_strecke_am_schnitt_geteilt(self):
        a = self.trenne((-200, 800), (-200, 600), links=False)
        teile = a.strecke_teilen((-700, 760), (700, 760))
        self.assertEqual(len(teile), 1)
        (p, q), = teile
        self.assertAlmostEqual(math.dist(p, q), 500.0)
        self.assertAlmostEqual(max(p[0], q[0]), -200.0)

    def test_steg_trennt_den_ganzen_flansch(self):
        a = self.trenne((-200, 600), (200, 600))
        self.assertAlmostEqual(a.breite, 400.0)
        self.assertAlmostEqual(a.flaeche, 1600 * 200)

    def test_was_nichts_abtrennt(self):
        # Zu kurz: der Flansch hängt unter der Strecke noch am Steg.
        self.assertEqual(self.trenne((-200, 800), (-200, 700), links=False), NICHT_GETRENNT)
        self.assertEqual(self.trenne((-200, 800), (-200, 800)), OHNE_LAENGE)
        # Längs des Rands trennt sie kein Material von Material.
        self.assertEqual(self.trenne((-800, 800), (800, 800)), OHNE_MATERIAL)

    def test_kasten_durch_eine_wand(self):
        # Durch eine Wand eines Kastens hängt der Teil jenseits über die andere noch am Rest.
        kasten = [[(0, 0), (1000, 0), (1000, 600), (0, 600)],
                  [(200, 150), (800, 150), (800, 450), (200, 450)]]
        self.assertEqual(self.trenne((0, 300), (200, 300), polygone=kasten,
                                     traegt=[True, False], eltern=[None, 0]), NICHT_GETRENNT)
        # Durch beide Wände trennt er die obere Hälfte ab, b_i nur im Material.
        a = self.trenne((-10, 300), (1010, 300), polygone=kasten, traegt=[True, False],
                        eltern=[None, 0])
        self.assertAlmostEqual(a.breite, 400.0)
        self.assertAlmostEqual(a.flaeche, 1000 * 300 - 600 * 150)

    def test_pfeil_in_worten(self):
        waagrecht = Schnitt("Schnitt 1", "L1", (0, 0), (100, 0), True)
        self.assertEqual((waagrecht.pfeil(True), waagrecht.pfeil(False)),
                         ("nach oben", "nach unten"))
        abwaerts = Schnitt("Schnitt 2", "L2", (0, 0), (0, -100), True)
        self.assertEqual((abwaerts.pfeil(True), abwaerts.pfeil(False)),
                         ("nach rechts", "nach links"))
        schraeg = Schnitt("Schnitt 3", "L3", (0, 0), (100, 100), True)
        self.assertEqual(schraeg.pfeil(True), "nach links oben")
        self.assertEqual(Schnitt("Schnitt 4", "L4", (0, 0), (0, 0), True).pfeil(True), "")


class ElastischesIProfil(unittest.TestCase):
    """Ein I-Profil aus S235, weit unter dem Fliessen: v = V·S′/I."""

    @classmethod
    def setUpClass(cls):
        p = Projekt(name="I-Profil")
        p.baustahl("S235")
        a = analyse(p, "I-Profil")
        a.polygon(I_PROFIL, material=p.materialien[0].kennung)
        a.schnitt([-5, 380], [5, 380], seite="links")    # der Steg unter dem oberen Flansch
        a.schnitt([50, 400], [50, 380], seite="links")   # der Flansch rechts von y = 50
        a.schnitt([-5, 200], [5, 200], seite="links")    # die Mitte des Stegs
        a.schubflussfall("Feld", V_z_Ed=100.0, M_y_Ed=50.0)
        a.schubflussfall("Negativ", V_z_Ed=-100.0, M_y_Ed=-50.0)
        aufbau, loesung = rechnen(p)
        cls.werte = ergebnisse(aufbau, loesung, a.kennung)

    def test_v_gleich_V_S_durch_I(self):
        statisch = {"Schnitt 1": 200 * 20 * 190, "Schnitt 2": 50 * 20 * 190,
                    "Schnitt 3": 200 * 20 * 190 + 10 * 180 * 90}
        for schnitt, S in statisch.items():
            for fall in ("Feld", "Negativ"):
                with self.subTest(schnitt=schnitt, fall=fall):
                    v, _, _ = self.werte[(schnitt, fall)]
                    hand = 100e3 * S / I_Y          # N/mm = kN/m
                    self.assertAlmostEqual(v / hand, 1.0, delta=1e-3)

    def test_tau_ueber_b_i(self):
        for (schnitt, fall), (v, tau, b_i) in self.werte.items():
            with self.subTest(schnitt=schnitt, fall=fall):
                self.assertAlmostEqual(b_i, 20.0 if schnitt == "Schnitt 2" else 10.0)
                self.assertAlmostEqual(tau, v / b_i, places=9)


class Plattenbalken(unittest.TestCase):
    """
    Flansch 1600 × 200, Steg 400, 4 ⌀26 unten, C30/37, gerissen: die
    Nulllinie liegt im Flansch, der Schnitt am Steg trennt 600 mm ab --
    3/8 der Druckkraft, 3/8 · V/z. Der Plan schätzte z = 0.70 m und damit
    214 kN/m; gerechnet sind es 211 kN/m, z = 0.71 m.
    """

    @classmethod
    def setUpClass(cls):
        p = Projekt(name="Plattenbalken")
        p.beton("C30/37")
        p.stahl("B500B")
        a = analyse(p, "Plattenbalken")
        a.polygon(PLATTENBALKEN, material="b1")
        a.stablinie([-150, 50], [150, 50], art="anzahl", anzahl=4, durchmesser=26, stahl="s1")
        a.schnitt([-200, 800], [-200, 600], seite="rechts")   # Flansch links des Stegs
        a.schnitt([-200, 600], [200, 600], seite="links")     # der ganze Flansch
        a.schnitt([-200, 800], [-200, 700], seite="rechts")   # zu kurz
        a.schubflussfall("Feld", V_z_Ed=400.0, M_y_Ed=500.0)
        a.schubflussfall("Ohne V", V_z_Ed=0.0, M_y_Ed=500.0)
        a.schubflussfall("Zu viel", V_z_Ed=400.0, M_y_Ed=50000.0)
        cls.aufbau, cls.loesung = rechnen(p)
        cls.kennung = a.kennung
        cls.werte = ergebnisse(cls.aufbau, cls.loesung, a.kennung)

    def test_drei_achtel_des_flanschs(self):
        flansch, _, b_flansch = self.werte[("Schnitt 1", "Feld")]
        ganz, _, b_ganz = self.werte[("Schnitt 2", "Feld")]
        self.assertAlmostEqual(flansch / ganz, 3 / 8, places=6)
        self.assertAlmostEqual(b_flansch, 200.0)
        self.assertAlmostEqual(b_ganz, 400.0)
        # Der Hebelarm, den v ergibt: z = 3/8 · V/v, bei d = 0.75 m.
        self.assertAlmostEqual(3 / 8 * 400 / flansch, 0.71, delta=0.005)

    def test_ohne_querkraft_kein_schubfluss(self):
        for schnitt in ("Schnitt 1", "Schnitt 2"):
            self.assertEqual(self.werte[(schnitt, "Ohne V")][:2], (0.0, 0.0))

    def test_ohne_gleichgewichtslage(self):
        v, tau, _ = self.werte[("Schnitt 1", "Zu viel")]
        self.assertTrue(math.isnan(v) and math.isnan(tau))
        befund = self.loesung.befunde[self.aufbau.teile[self.kennung].schubfluss.id]
        self.assertEqual(befund.gruende, {"Zu viel": KEINE_LAGE})

    def test_schnitt_der_nichts_abtrennt(self):
        sf = self.aufbau.teile[self.kennung].schubfluss
        self.assertEqual(sf.ohne, [f"Schnitt 3 trennt nichts ab: {NICHT_GETRENNT}."])
        self.assertNotIn("Schnitt 3", {z.schnitt for z in sf.zeilen})

    def test_tabelle_und_saetze(self):
        tabelle, saetze = schubfluss(self.aufbau, self.kennung, self.loesung)
        self.assertEqual(len(tabelle.zeilen), 6)
        zu_viel = [z for z in tabelle.zeilen if z[:2] == ["Schnitt 1", "Zu viel"]][0]
        self.assertEqual(zu_viel[3:], ["–", "–"])
        self.assertEqual(saetze, [f"Schnitt 3 trennt nichts ab: {NICHT_GETRENNT}.",
                                  f"Lastfall «Zu viel»: kein Schubfluss. {KEINE_LAGE}"])


class Aufdopplung(unittest.TestCase):
    """
    Ein Fertigteil 1000 × 200 mit Aufbeton 100 mm, unten ⌀16 @ 150: die
    Druckzone liegt im Aufbeton. Dann geht die ganze Druckkraft durch die
    Fuge, so viel wie durch einen Schnitt über dem Stahl; ein Schnitt in der
    Druckzone trägt weniger.
    """

    @classmethod
    def setUpClass(cls):
        p = Projekt(name="Aufdopplung")
        p.beton("C30/37")
        p.stahl("B500B")
        a = analyse(p, "Aufdopplung")
        a.polygon([[0, 0], [1000, 0], [1000, 200], [0, 200]], material="b1")
        a.polygon([[0, 200], [1000, 200], [1000, 300], [0, 300]], material="b1")
        a.stablinie([40, 40], [960, 40], art="teilung", teilung=150, durchmesser=16, stahl="s1")
        a.schnitt([0, 200], [1000, 200], seite="links")       # die Fuge
        a.schnitt([-10, 60], [1010, 60], seite="links")       # über dem Stahl
        a.schnitt([-10, 290], [1010, 290], seite="links")     # in der Druckzone
        a.schubflussfall("Feld", V_z_Ed=100.0, M_y_Ed=60.0)
        aufbau, loesung = rechnen(p)
        cls.werte = ergebnisse(aufbau, loesung, a.kennung)

    def test_die_ganze_druckkraft_geht_durch_die_fuge(self):
        fuge = self.werte[("Schnitt 1", "Feld")][0]
        ueber_dem_stahl = self.werte[("Schnitt 2", "Feld")][0]
        self.assertAlmostEqual(fuge / ueber_dem_stahl, 1.0, places=9)
        self.assertLess(self.werte[("Schnitt 3", "Feld")][0], 0.9 * fuge)


class Verbundtraeger(unittest.TestCase):
    """
    Ein I-Profil aus S355 unter einer Platte 2000 × 200 aus C30/37 mit
    1000 mm² Betonstahl: über der Stütze reisst die Platte, ihr Stahl allein
    zieht -- elastisch, v = V·S′/I mit E_s/E_a. Der Schnitt längs der
    Oberkante des Profils trennt die Platte ab: v tragen die Dübel.
    """

    @classmethod
    def setUpClass(cls):
        p = Projekt(name="Verbund")
        p.beton("C30/37")
        p.baustahl("S355")
        p.stahl("B500B")
        stahl = next(m.kennung for m in p.materialien if m.art == "baustahl")
        a = analyse(p, "Verbundträger")
        a.polygon(I_PROFIL, material=stahl)
        a.polygon([[-1000, 400], [1000, 400], [1000, 600], [-1000, 600]], material="b1")
        a.stablinie([-950, 560], [950, 560], art="flaeche", flaeche=1000.0, stahl="s1")
        a.schnitt([-100, 400], [100, 400], seite="links")
        a.schnitt([-300, 600], [-300, 400], seite="rechts")    # die Platte links von y = −300
        a.schubflussfall("Stütze", V_z_Ed=300.0, M_y_Ed=-400.0)
        cls.aufbau, cls.loesung = rechnen(p)
        cls.kennung = a.kennung
        cls.werte = ergebnisse(cls.aufbau, cls.loesung, a.kennung)

    def test_ueber_der_stuetze_elastisch(self):
        n = 200000 / 210000                                   # E_s / E_a
        A_s, A_a = 1000 * n, 11600
        z_S = (A_s * 560 + A_a * 200) / (A_s + A_a)
        I = (200 * 400 ** 3 - 190 * 360 ** 3) / 12 + A_a * (z_S - 200) ** 2 + A_s * (560 - z_S) ** 2
        v, tau, b_i = self.werte[("Schnitt 1", "Stütze")]
        self.assertAlmostEqual(v / (300e3 * A_s * (560 - z_S) / I), 1.0, delta=1e-3)
        self.assertAlmostEqual(b_i, 200.0)
        # Die Platte links von y = −300 hat 650 der 1900 mm verschmierten Stahls.
        self.assertAlmostEqual(self.werte[("Schnitt 2", "Stütze")][0] / v, 650 / 1900, places=6)

    def test_verschmierte_linie_am_schnitt_geteilt(self):
        sf = self.aufbau.teile[self.kennung].schubfluss
        an = sf.analyse
        wert = lambda kennung: self.loesung.werte[kennung].groesse.si   # noqa: E731
        q, herkunft, _ = an.querschnitt(wert, sf.faelle[0].wahl)
        (_, platte), (_, kragteil) = sf.getrennt
        teil, namen = teilquerschnitt(q, herkunft, kragteil)
        self.assertAlmostEqual(sum(b.flaeche for b in teil.bewehrung) * 1e6, 1000 * 650 / 1900,
                               places=6)
        self.assertEqual(len(namen), 1)
        self.assertAlmostEqual(sum(b.flaeche for b in teilquerschnitt(q, herkunft, platte)[0]
                                   .bewehrung) * 1e6, 1000.0, places=6)

    def test_zeichnung(self):
        p = Projekt(name="Platte")
        p.beton("C30/37")
        a = analyse(p, "Platte")
        a.polygon([[0, 0], [1000, 0], [1000, 200], [0, 200]], material="b1")
        a.schnitt([500, 0], [500, 200], seite="links")
        a.schnitt([500, 0], [500, 100], seite="links")
        g = geometrie(a, p)
        ganz, halb = g["schnitte"]
        self.assertEqual(ganz["pfeile"], {"links": "nach links", "rechts": "nach rechts"})
        self.assertAlmostEqual(ganz["breite"], 200.0)
        self.assertAlmostEqual(ganz["flaeche"], 500 * 200)
        self.assertEqual(halb["stuecke"], [])
        meldung = [m for m in g["meldungen"] if m["elemente"] == [halb["kennung"]]]
        self.assertEqual(meldung, [{"text": f"Schnitt 2 trennt nichts ab: {NICHT_GETRENNT}.",
                                    "elemente": [halb["kennung"]], "fehler": False}])
        self.assertTrue(g["gueltig"])


class Fallnamen(unittest.TestCase):
    def test_zwei_faelle_gleichen_namens(self):
        p = Projekt(name="Namen")
        p.beton("C30/37")
        a = analyse(p, "Rechteck")
        a.polygon([[0, 0], [300, 0], [300, 500], [0, 500]], material="b1")
        a.schubflussfall("Feld", V_z_Ed=100.0)
        a.schubflussfall("Feld", V_z_Ed=200.0)
        self.assertIn("«Feld» ist als Lastfall des Schubflusses schon vergeben", meldung(p))


if __name__ == "__main__":
    unittest.main()
