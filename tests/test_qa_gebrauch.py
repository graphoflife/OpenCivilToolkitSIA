"""
Die Gebrauchsnachweise des gezeichneten Querschnitts.

Geprueft wird gegen das, was sich von Hand rechnen laesst: am Rechteck mit
Staeben nur unten ist die Ebene unter Gebrauchslast der gerissene
Querschnitt der Platte (``x``, ``z = d - x/3``), die Risskraft des ganzen
Querschnitts ``b·h·k_t·f_ctm``, und das Moment an der Grenze ``sigma_s,adm
· A_s · z``. Dazu, was nur der gezeichnete Querschnitt kennt: die Grenze je
Stab, der fiktive Durchmesser einer verschmierten Linie und die Nulllinie,
die bei schiefer Biegung dreht.
"""

import math
import unittest

from opencivil.nachweis.gebrauchsebene import gebrauchsebene
from opencivil.nachweis.mindestbewehrung import zulaessige_stahlspannung
from opencivil.nachweis.rechenwahl import Rechenart
from opencivil.nachweis.spannungsbegrenzung import VORGABE
from opencivil.nachweis.zustand2 import gerissen
from opencivil.projekt import Projekt, ProjektFehler
from opencivil.projekt.querschnittsanalyse import (
    QAGebrauchsfallEintrag, QAGebrauchsliste, QuerschnittsanalyseEintrag,
)
from opencivil.nachweis.stabgrenzen import fiktiver_durchmesser
from opencivil.querschnitt.interaktion import Querschnitt
from opencivil.querschnitt.schnittanalyse import querschnitt_nach_wahl

#: Die Kennwerte von C30/37 und B500B, wie das Rechenwerk sie liefert.
E_S, F_YK, F_YD, F_CTM, E_CM = 200e9, 500e6, 500e6 / 1.15, 2.9e6, 33.62e9


def rechteck(*, unten=((50, 16, 3),), oben=(), b=300, h=500, **felder):
    """Ein Rechteck b × h, je Lage (Abstand vom Rand, ⌀, Anzahl) -- C30/37, B500B."""
    p = Projekt(name="Gebrauch")
    p.beton("C30/37")
    p.stahl("B500B")
    a = QuerschnittsanalyseEintrag(kennung=p.freie_kennung("a"), name="Balken", **felder)
    a.polygon([[0, 0], [b, 0], [b, h], [0, h]], material="b1")
    for z, d, n in unten:
        a.stablinie([50, z], [b - 50, z], art="anzahl", anzahl=n, durchmesser=d, stahl="s1")
    for z, d, n in oben:
        a.stablinie([50, h - z], [b - 50, h - z], art="anzahl", anzahl=n, durchmesser=d,
                    stahl="s1")
    a.lastfall("Feld", M_y_Ed=100.0)
    p.querschnittsanalysen.append(a)
    return p, a


def rechnen(projekt):
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


def urteile(loesung, nachweis):
    return [u for u in loesung.urteile if u.ziel.startswith(nachweis.id)]


def urteil_zu(loesung, nachweis, fall):
    return next(u for u in urteile(loesung, nachweis) if u.fall == fall)


def querschnitt(projekt, wahl=VORGABE):
    """Der gezeichnete Querschnitt mit den Gesetzen einer Wahl -- und seine Stäbe."""
    aufbau, loesung = rechnen(projekt)
    analyse = aufbau.querschnittsanalysen["a1"]
    q, herkunft, _ = querschnitt_nach_wahl(
        analyse, lambda kid: loesung.werte[kid].groesse.si, wahl)
    return q


class TestFiktiverDurchmesser(unittest.TestCase):
    def test_flaeche_je_laenge_bei_150_mm(self):
        """1000 mm² auf 1 m sind Stäbe mit 150 mm² bei 150 mm Teilung: ⌀ 13.8."""
        p, a = rechteck(unten=())
        a.stablinie([50, 50], [250, 50], art="flaeche", flaeche=200.0, stahl="s1")
        aufbau, _ = rechnen(p)
        linie = aufbau.querschnittsanalysen["a1"].gruppen[0]
        self.assertAlmostEqual(fiktiver_durchmesser(linie) * 1e3,
                               math.sqrt(4.0 / math.pi * 150.0), places=9)


class TestDieEbene(unittest.TestCase):
    def test_einachsig_ist_der_gerissene_querschnitt(self):
        """Stäbe nur unten, reine Biegung: σ_s = M / (A_s · (d − x/3)), wie bei der Platte."""
        p, _ = rechteck()
        q = querschnitt(p)
        M = 60e3
        ebene = gebrauchsebene(q, N=0.0, M_y=M, M_z=0.0, einachsig=True)
        a_s = 3 * math.pi * 0.016 ** 2 / 4
        riss = gerissen(n=E_S / E_CM, a_s=a_s, b=0.3, d=0.45)
        self.assertTrue(ebene.konvergiert)
        for sigma in ebene.sigma_s:
            self.assertAlmostEqual(sigma / (M / (a_s * riss.z)), 1.0, delta=5e-4)

    def test_schief_symmetrisch_steht_die_nulllinie_quer_zum_moment(self):
        """Quadrat, gleich bewehrt, M_y = M_z: die Zugrichtung ist die Diagonale."""
        p, a = rechteck(unten=((50, 16, 3),), oben=((50, 16, 3),), b=500, h=500)
        a.stab(50, 250, durchmesser=16, stahl="s1")
        a.stab(450, 250, durchmesser=16, stahl="s1")
        q = querschnitt(p)
        ebene = gebrauchsebene(q, N=-100e3, M_y=50e3, M_z=50e3, einachsig=False)
        self.assertTrue(ebene.konvergiert)
        self.assertAlmostEqual(math.remainder(ebene.psi + 0.75 * math.pi, 2 * math.pi), 0.0,
                               delta=1e-6)
        self.assertAlmostEqual(ebene.N, -100e3, delta=1.0)
        self.assertAlmostEqual(ebene.M_y, 50e3, delta=1.0)
        self.assertAlmostEqual(ebene.M_z, 50e3, delta=1.0)

    def test_schief_unsymmetrisch_erzeugt_die_ebene_die_einwirkung(self):
        """Ein L: die Nulllinie dreht von der Lage, die bei Symmetrie gälte, weg."""
        p = Projekt(name="L")
        p.beton("C30/37")
        p.stahl("B500B")
        a = QuerschnittsanalyseEintrag(kennung="a1", name="L")
        a.polygon([[0, 0], [600, 0], [600, 200], [200, 200], [200, 600], [0, 600]],
                  material="b1")
        a.stablinie([50, 50], [550, 50], art="anzahl", anzahl=5, durchmesser=16, stahl="s1")
        a.stablinie([50, 100], [50, 550], art="anzahl", anzahl=4, durchmesser=16, stahl="s1")
        p.querschnittsanalysen.append(a)
        q = querschnitt(p)
        ebene = gebrauchsebene(q, N=-50e3, M_y=80e3, M_z=-30e3, einachsig=False)
        self.assertTrue(ebene.konvergiert)
        self.assertAlmostEqual(ebene.N, -50e3, delta=1.0)
        self.assertAlmostEqual(ebene.M_y, 80e3, delta=1.0)
        self.assertAlmostEqual(ebene.M_z, -30e3, delta=1.0)
        self.assertGreater(abs(math.remainder(ebene.psi - Querschnitt.neigung_fuer(80e3, -30e3),
                                              2 * math.pi)), 0.01)


class TestStahlspannung(unittest.TestCase):
    def test_der_dicke_stab_gibt_die_grenze(self):
        """Zwei Linien in derselben Tiefe: dieselbe Dehnung, der dicke Stab hat die kleinere Grenze."""
        p, a = rechteck(unten=((50, 12, 3), (51, 26, 2)), rissanforderung="erhoeht")
        a.quasistaendig.lastfall("Dauer", M_y_Ed=60.0)
        aufbau, loesung = rechnen(p)
        urteil = urteil_zu(loesung, aufbau.qa_spannung_riss["a1"], "Dauer")
        grenze = zulaessige_stahlspannung(anforderung="erhoeht", f_yk=F_YK, E_s=E_S,
                                          f_ctm=F_CTM, durchmesser=0.026)
        self.assertIn("Linie 2", urteil.begruendung)
        self.assertAlmostEqual(urteil.widerstand.groesse.si, grenze, delta=1.0)

    def test_gegen_fliessen_nur_bei_erhoehter_anforderung(self):
        p, a = rechteck()
        a.haeufig.lastfall("Häufig", M_y_Ed=60.0)
        aufbau, _ = rechnen(p)
        self.assertEqual(aufbau.qa_spannung, {})
        a.rissanforderung = "erhoeht"
        aufbau, loesung = rechnen(p)
        urteil = urteil_zu(loesung, aufbau.qa_spannung["a1"], "Häufig")
        self.assertAlmostEqual(urteil.widerstand.groesse.si, F_YD - 80e6, delta=1.0)

    def test_abgeleitet_aus_der_tragsicherheit(self):
        """«Feld (60 %)»: 60 % des Lastfalls der Tragsicherheit, still, bis man ihn führt."""
        p, a = rechteck()
        aufbau, loesung = rechnen(p)
        [urteil] = urteile(loesung, aufbau.qa_spannung_riss["a1"])
        self.assertEqual(urteil.fall, "Feld (60 %)")
        self.assertTrue(urteil.still)
        a.quasistaendig.aus_tragsicherheit = True
        aufbau, loesung = rechnen(p)
        [urteil] = urteile(loesung, aufbau.qa_spannung_riss["a1"])
        self.assertFalse(urteil.still)
        # Bei normaler Anforderung ist die Grenze f_yk.
        self.assertAlmostEqual(urteil.widerstand.groesse.si, F_YK, delta=1.0)

    def test_ohne_zug_ist_nichts_zu_begrenzen(self):
        p, a = rechteck()
        a.quasistaendig.lastfall("Druck", N_Ed=-500.0)
        aufbau, loesung = rechnen(p)
        urteil = next(u for u in urteile(loesung, aufbau.qa_spannung_riss["a1"])
                      if u.fall == "Druck")
        self.assertTrue(urteil.erfuellt)
        self.assertTrue(math.isinf(urteil.erfuellungsgrad.si))


class TestRissnormalkraft(unittest.TestCase):
    def test_der_ganze_querschnitt(self):
        """N_Riss = b·h·k_t·f_ctm mit t = min(b; h); dagegen alle Stäbe bei f_yk."""
        p, _ = rechteck(oben=((50, 12, 2),), zwaengung=True)
        aufbau, loesung = rechnen(p)
        [urteil] = urteile(loesung, aufbau.qa_rissnormalkraft["a1"])
        k_t = 1.0 / (1.0 + 0.5 * 0.3)
        self.assertAlmostEqual(urteil.einwirkung.groesse.si, 0.3 * 0.5 * k_t * F_CTM,
                               delta=10.0)
        a_s = math.pi / 4 * (3 * 0.016 ** 2 + 2 * 0.012 ** 2)
        self.assertAlmostEqual(urteil.widerstand.groesse.si, a_s * F_YK, delta=10.0)

    def test_begrenzt_auf_500_mm(self):
        p, _ = rechteck(b=800, h=600, zwaengung=True, zwaengung_begrenzt=True)
        aufbau, loesung = rechnen(p)
        [urteil] = urteile(loesung, aufbau.qa_rissnormalkraft["a1"])
        self.assertAlmostEqual(urteil.einwirkung.groesse.si,
                               0.8 * 0.6 / (1.0 + 0.5 * 0.5) * F_CTM, delta=10.0)


class TestZwaengungBiegung(unittest.TestCase):
    def test_das_moment_an_der_grenze(self):
        """Stäbe nur unten: M_s,adm = σ_s,adm · A_s · (d − x/3), gegen dasselbe M_Riss."""
        p, _ = rechteck(zwaengung_biegung=True, einachsig=True)
        aufbau, loesung = rechnen(p)
        unten, *rest = urteile(loesung, aufbau.qa_zwaengung_biegung["a1"])
        a_s = 3 * math.pi * 0.016 ** 2 / 4
        riss = gerissen(n=E_S / E_CM, a_s=a_s, b=0.3, d=0.45)
        self.assertEqual(unten.fall, "Zug unten")
        self.assertAlmostEqual(unten.widerstand.groesse.si / (F_YK * a_s * riss.z), 1.0,
                               delta=5e-4)
        sproede = next(u for u in urteile(loesung, aufbau.qa_sproede["a1"])
                       if u.fall == "Zug unten")
        self.assertEqual(unten.einwirkung.groesse.si, sproede.einwirkung.groesse.si)
        # Oben liegt kein Stab: dort gibt es keinen Nachweis.
        self.assertEqual(rest, [])

    def test_das_kriechen_senkt_das_moment(self):
        """Mehr φ, weicherer Beton, kleinerer Hebelarm -- weniger Moment an der Grenze."""
        momente = []
        for phi in (0.0, 2.0):
            p, _ = rechteck(zwaengung_biegung=True, einachsig=True,
                            zwaengung_biegung_kriechzahl=phi)
            aufbau, loesung = rechnen(p)
            momente.append(urteile(loesung, aufbau.qa_zwaengung_biegung["a1"])[0]
                           .widerstand.groesse.si)
        self.assertLess(momente[1], momente[0])


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        p, a = rechteck(rissanforderung="hoch", zwaengung=True, zwaengung_biegung_kriechzahl=1.5)
        a.haeufig.lastfall("H", N_Ed=-10.0, M_y_Ed=20.0, M_z_Ed=5.0)
        a.quasistaendig.wahl.rechenart = "parabel"
        zurueck = QuerschnittsanalyseEintrag.aus_dict(a.als_dict())
        self.assertEqual(zurueck, a)
        self.assertEqual(zurueck.haeufig.faelle,
                         [QAGebrauchsfallEintrag("H", N_Ed=-10.0, M_y_Ed=20.0, M_z_Ed=5.0)])

    def test_keine_handrechnung(self):
        """Der gezeichnete Querschnitt rechnet über die Fasern -- die Handrechnung gibt es nicht."""
        p, a = rechteck()
        self.assertNotIn(Rechenart.HANDRECHNUNG, QAGebrauchsliste.ARTEN)
        roh = a.als_dict()
        roh["quasistaendig"]["wahl"]["rechenart"] = "quatsch"
        with self.assertRaises(ProjektFehler):
            QuerschnittsanalyseEintrag.aus_dict(roh)

    def test_gleiche_namen_werden_gemeldet(self):
        p, a = rechteck()
        a.haeufig.lastfall("H", M_y_Ed=1.0)
        a.haeufig.lastfall("H", M_y_Ed=2.0)
        with self.assertRaises(ProjektFehler) as fehler:
            a.pruefen()
        self.assertIn("Querschnitt 'Balken'", str(fehler.exception))


if __name__ == "__main__":
    unittest.main()
