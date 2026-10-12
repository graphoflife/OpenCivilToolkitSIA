"""
Das Stabwerk als Ganzes -- gegen Handrechnungen.

Einfeldträger, Kragarm, Zweifeldträger, Rahmen, Dreigelenkrahmen, Fachwerk,
Federn, Bettung, feste Linienlager, T-Stoss, Kombinationen -- und was
geschieht, wenn das System beweglich ist oder ein Knoten nur an Gelenken
hängt.

Vorzeichen des Systems: x nach rechts, z nach oben, Drehungen im
Gegenuhrzeigersinn; eine Lagerkraft nach oben ist positiv. Am Stabende: das
Moment auf den Stab im Gegenuhrzeigersinn, am Ende b ist es das Moment der
Baustatik, am Anfang a dessen Gegenteil.
"""

import math
import unittest

from opencivil.stabwerk.modell import (
    FEST, Kombination, Knoten, Knotenlast, Lager, Lastart, Lastfall, Lastrichtung,
    Stab, Stablast, System,
)
from opencivil.stabwerk.system import UNBESTIMMT, rechnen

EI, EA = 50e6, 5e9
q, P = 10e3, 20e3


def stab(name, a, b, **felder):
    return Stab(name, a, b, EA=felder.pop("EA", EA), EI=felder.pop("EI", EI), **felder)


def linienlast(stab_, wert=q, **felder):
    return Stablast(stab_, Lastart.LINIENLAST, wert, **felder)


def gelenkig(name, knoten):
    return Lager(name, knoten, x=FEST, z=FEST)


def rolle(name, knoten):
    return Lager(name, knoten, z=FEST)


def eingespannt(name, knoten):
    return Lager(name, knoten, x=FEST, z=FEST, phi=FEST)


def system(knoten, staebe, lager, *lastfaelle, kombinationen=()):
    return System(knoten=[Knoten(n, x, z) for n, x, z in knoten], staebe=staebe, lager=lager,
                  lastfaelle=list(lastfaelle), kombinationen=list(kombinationen))


class Rechnung(unittest.TestCase):
    def gerechnet(self, s):
        e = rechnen(s)
        self.assertTrue(e.gueltig, [m.text for m in e.meldungen])
        for f in e.faelle:
            groesse = max(abs(v) for v in f.lastsumme) or 1.0
            for rest in f.gleichgewicht:
                self.assertLess(abs(rest), 1e-9 * groesse, f"Gleichgewicht in {f.name}")
        return e


class TestEinfeldtraeger(Rechnung):
    def setUp(self):
        self.L = 6.0
        self.e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", self.L, 0)], [stab("L1", "K1", "K2")],
            [gelenkig("A1", "K1"), rolle("A2", "K2")],
            Lastfall("q", [linienlast("L1")])))

    def test_lagerkraefte(self):
        f = self.e.faelle[0]
        self.assertAlmostEqual(f.lagerkraefte["K1"][1], q * self.L / 2, places=6)
        self.assertAlmostEqual(f.lagerkraefte["K2"][1], q * self.L / 2, places=6)
        self.assertAlmostEqual(f.lagerkraefte["K1"][0], 0.0, places=6)

    def test_enddrehung(self):
        """qL³/24EI, links im Uhrzeigersinn -- also negativ."""
        phi = self.e.faelle[0].verschiebungen["K1"][2]
        self.assertAlmostEqual(phi, -q * self.L ** 3 / (24 * EI), places=12)

    def test_unbekannte(self):
        self.assertEqual(self.e.unbekannte, ["φ(K1)", "u_x(K2)", "φ(K2)"])


class TestKragarm(Rechnung):
    def test_einzellast_am_ende(self):
        L = 3.0
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", L, 0)], [stab("L1", "K1", "K2")], [eingespannt("A1", "K1")],
            Lastfall("P", [Knotenlast("K2", Fz=-P)])))
        f = e.faelle[0]
        ux, uz, phi = f.verschiebungen["K2"]
        self.assertAlmostEqual(uz, -P * L ** 3 / (3 * EI), places=12)
        self.assertAlmostEqual(phi, -P * L ** 2 / (2 * EI), places=12)
        rx, rz, m = f.lagerkraefte["K1"]
        self.assertAlmostEqual(rz, P, places=6)
        self.assertAlmostEqual(m, P * L, places=6)

    def test_drei_stuecke_wie_eines(self):
        L = 3.0
        ein = self.gerechnet(system(
            [("K1", 0, 0), ("K2", L, 0)], [stab("L1", "K1", "K2")], [eingespannt("A1", "K1")],
            Lastfall("q", [linienlast("L1")])))
        drei = self.gerechnet(system(
            [("K1", 0, 0), ("K3", 1, 0), ("K4", 2, 0), ("K2", L, 0)],
            [stab("L1", "K1", "K3"), stab("L2", "K3", "K4"), stab("L3", "K4", "K2")],
            [eingespannt("A1", "K1")],
            Lastfall("q", [linienlast(n) for n in ("L1", "L2", "L3")])))
        for i in range(3):
            self.assertAlmostEqual(ein.faelle[0].verschiebungen["K2"][i],
                                   drei.faelle[0].verschiebungen["K2"][i], places=12)


class TestZweifeldtraeger(Rechnung):
    def test_stuetzmoment_und_lagerkraefte(self):
        L = 5.0
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", L, 0), ("K3", 2 * L, 0)],
            [stab("L1", "K1", "K2"), stab("L2", "K2", "K3")],
            [gelenkig("A1", "K1"), rolle("A2", "K2"), rolle("A3", "K3")],
            Lastfall("q", [linienlast("L1"), linienlast("L2")])))
        f = e.faelle[0]
        self.assertAlmostEqual(f.lagerkraefte["K2"][1], 1.25 * q * L, places=5)
        self.assertAlmostEqual(f.lagerkraefte["K1"][1], 0.375 * q * L, places=5)
        # Das Moment am Ende b ist das der Baustatik: −qL²/8 über der Stütze.
        self.assertAlmostEqual(f.teile[0].s[5], -q * L * L / 8, places=5)


class TestRahmen(Rechnung):
    def test_waagrechte_last_teilt_sich_auf_zwei_gelenkige_fuesse(self):
        """
        Gleiche Stiele, Fussgelenke: je H/2 und senkrecht ±H·h/L -- genau so
        nur mit einem Riegel, der sich nicht staucht. Mit EA wie die Stiele
        bekäme der rechte Fuss 0.04 % weniger.
        """
        h, L, H = 4.0, 6.0, 30e3
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 0, h), ("K3", L, h), ("K4", L, 0)],
            [stab("L1", "K1", "K2"), stab("L2", "K2", "K3", EA=1e13), stab("L3", "K4", "K3")],
            [gelenkig("A1", "K1"), gelenkig("A2", "K4")],
            Lastfall("Wind", [Knotenlast("K2", Fx=H)])))
        r1, r4 = e.faelle[0].lagerkraefte["K1"], e.faelle[0].lagerkraefte["K4"]
        self.assertAlmostEqual(r1[0], -H / 2, delta=1e-6 * H)
        self.assertAlmostEqual(r4[0], -H / 2, delta=1e-6 * H)
        self.assertAlmostEqual(r1[1], -H * h / L, delta=1e-6 * H)
        self.assertAlmostEqual(r4[1], H * h / L, delta=1e-6 * H)


class TestDreigelenkrahmen(Rechnung):
    def setUp(self):
        self.h, self.L = 4.0, 8.0
        self.e = self.gerechnet(system(
            [("A", 0, 0), ("B", 0, self.h), ("C", self.L / 2, self.h), ("D", self.L, self.h),
             ("E", self.L, 0)],
            [stab("L1", "A", "B"), stab("L2", "B", "C", gelenk_b=True),
             stab("L3", "C", "D", gelenk_a=True), stab("L4", "E", "D")],
            [gelenkig("A1", "A"), gelenkig("A2", "E")],
            Lastfall("q", [linienlast("L2"), linienlast("L3")])))

    def test_horizontalschub(self):
        """H = qL²/(8h), senkrecht je qL/2."""
        f = self.e.faelle[0]
        H = q * self.L ** 2 / (8 * self.h)
        self.assertAlmostEqual(f.lagerkraefte["A"][0], H, delta=1e-6 * H)
        self.assertAlmostEqual(f.lagerkraefte["E"][0], -H, delta=1e-6 * H)
        self.assertAlmostEqual(f.lagerkraefte["A"][1], q * self.L / 2, delta=1e-6 * q * self.L)

    def test_der_gelenkknoten_hat_keine_drehung(self):
        """Am Scheitel hängen beide Riegel an Gelenken: die Drehung ist gestrichen."""
        self.assertEqual(self.e.unbestimmt(), ["C"])
        self.assertNotIn("φ(C)", self.e.unbekannte)
        self.assertIn("φ(L2, Ende)", self.e.unbekannte)
        self.assertEqual(self.e.faelle[0].verschiebungen["C"][2], 0.0)
        self.assertIn("nicht bestimmbar", UNBESTIMMT)

    def test_ein_moment_dort_ist_ein_fehler(self):
        s = system([("A", 0, 0), ("C", 2, 0), ("E", 4, 0)],
                   [stab("L1", "A", "C", gelenk_b=True), stab("L2", "C", "E", gelenk_a=True)],
                   [eingespannt("A1", "A"), eingespannt("A2", "E")],
                   Lastfall("M", [Knotenlast("C", M=5e3)]))
        e = rechnen(s)
        self.assertFalse(e.gueltig)
        self.assertIn("gelenkig", e.meldungen[0].text)
        self.assertEqual(e.meldungen[0].elemente, ("C",))


class TestFachwerk(Rechnung):
    def test_dreieck(self):
        """Zwei Stäbe unter 45° zur Spitze, Last P nach unten: je Stab −P/√2 (Druck)."""
        s = system([("A", 0, 0), ("S", 2, 2), ("B", 4, 0)],
                   [stab("L1", "A", "S", gelenk_a=True, gelenk_b=True),
                    stab("L2", "S", "B", gelenk_a=True, gelenk_b=True)],
                   [gelenkig("A1", "A"), gelenkig("A2", "B")],
                   Lastfall("P", [Knotenlast("S", Fz=-P)]))
        e = self.gerechnet(s)
        self.assertEqual(sorted(e.unbestimmt()), ["A", "B", "S"])
        for t in e.faelle[0].teile:
            # N = −s_u am Anfang.
            self.assertAlmostEqual(-t.s[0], -P / math.sqrt(2), delta=1e-6 * P)


class TestBeweglich(unittest.TestCase):
    def test_zwei_rollen(self):
        s = system([("K1", 0, 0), ("K2", 6, 0)], [stab("L1", "K1", "K2")],
                   [rolle("A1", "K1"), rolle("A2", "K2")],
                   Lastfall("q", [linienlast("L1")]))
        e = rechnen(s)
        self.assertFalse(e.gueltig)
        meldung = e.meldungen[-1]
        self.assertIn("beweglich", meldung.text)
        self.assertIn("singulär", meldung.text)
        self.assertEqual(sorted(e.beweglich), ["K1", "K2"])

    def test_ohne_stab(self):
        e = rechnen(system([("K1", 0, 0), ("K2", 6, 0)],
                           [Stab("L1", "K1", "K2", traegt=False)], []))
        self.assertFalse(e.gueltig)
        self.assertIn("Kein Stab", e.meldungen[0].text)

    def test_laenge_null(self):
        e = rechnen(system([("K1", 0, 0), ("K2", 0, 0)], [stab("L1", "K1", "K2")], []))
        self.assertIn("Länge null", e.meldungen[0].text)

    def test_last_hinter_dem_ende(self):
        e = rechnen(system([("K1", 0, 0), ("K2", 6, 0)], [stab("L1", "K1", "K2")],
                           [gelenkig("A1", "K1"), rolle("A2", "K2")],
                           Lastfall("P", [Stablast("L1", Lastart.EINZELLAST, P, von=7.0)])))
        self.assertFalse(e.gueltig)
        self.assertIn("7 m", e.meldungen[0].text)


class TestFedern(Rechnung):
    def test_federlager(self):
        """Ein Kragarm ohne Biegung -- starr genug -- auf einer Feder: w = F/k."""
        k = 2e6
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 4, 0)], [stab("L1", "K1", "K2")],
            [gelenkig("A1", "K1"), Lager("A2", "K2", z=k)],
            Lastfall("P", [Knotenlast("K2", Fz=-P)])))
        self.assertAlmostEqual(e.faelle[0].verschiebungen["K2"][1], -P / k, places=12)
        self.assertAlmostEqual(e.faelle[0].lagerkraefte["K2"][1], P, places=6)

    def test_drehfeder_haelt_einen_gelenkknoten(self):
        s = system([("A", 0, 0), ("C", 2, 0), ("E", 4, 0)],
                   [stab("L1", "A", "C", gelenk_b=True), stab("L2", "C", "E", gelenk_a=True)],
                   [eingespannt("A1", "A"), eingespannt("A2", "E"), Lager("A3", "C", phi=1e5)],
                   Lastfall("M", [Knotenlast("C", M=5e3)]))
        e = self.gerechnet(s)
        self.assertAlmostEqual(e.faelle[0].verschiebungen["C"][2], 5e3 / 1e5, places=12)


class TestKombination(Rechnung):
    def test_ist_die_summe(self):
        lastfaelle = [Lastfall("g", [linienlast("L1")]),
                      Lastfall("w", [Knotenlast("K2", Fx=5e3)])]
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 0, 3)], [stab("L1", "K1", "K2")], [eingespannt("A1", "K1")],
            *lastfaelle, kombinationen=[Kombination("ULS", {"g": 1.35, "w": 1.5})]))
        g, w, uls = (e.fall(n) for n in ("g", "w", "ULS"))
        for a, b, c in zip(g.x, w.x, uls.x):
            self.assertAlmostEqual(1.35 * a + 1.5 * b, c, places=12)
        self.assertTrue(uls.kombination)


class TestUmgekehrt(Rechnung):
    def test_dieselben_verschiebungen(self):
        """Quer zeigt dann zur anderen Seite: die Last quer wechselt ihr Vorzeichen."""
        def gerechnet(a, b, wert):
            return self.gerechnet(system(
                [("K1", 0, 0), ("K2", 5, 0)], [stab("L1", a, b)],
                [gelenkig("A1", "K1"), rolle("A2", "K2")],
                Lastfall("q", [linienlast("L1", wert, richtung=Lastrichtung.QUER)])))
        hin, zurueck = gerechnet("K1", "K2", q), gerechnet("K2", "K1", -q)
        for i in range(3):
            self.assertAlmostEqual(hin.faelle[0].verschiebungen["K1"][i],
                                   zurueck.faelle[0].verschiebungen["K1"][i], places=12)


class TestProjiziert(Rechnung):
    def test_schnee_auf_dem_schraegen_stab(self):
        """Je Meter Projektion: die senkrechte Summe ist q mal die waagrechte Länge."""
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 4, 3)], [stab("L1", "K1", "K2")],
            [gelenkig("A1", "K1"), rolle("A2", "K2")],
            Lastfall("s", [linienlast("L1", projiziert=True)])))
        self.assertAlmostEqual(e.faelle[0].lastsumme[1], -q * 4.0, places=6)


class TestBettung(Rechnung):
    def test_gleichlast_senkt_gleichmaessig(self):
        """Ohne Lager, auf Bettung, unter Gleichlast: überall w = q/k."""
        k = 5e6
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 10, 0)], [stab("L1", "K1", "K2", quer=k)],
            [Lager("A1", "K1", x=FEST)], Lastfall("q", [linienlast("L1")])))
        f = e.faelle[0]
        for name, (ux, uz, phi) in f.verschiebungen.items():
            self.assertAlmostEqual(uz, -q / k, delta=1e-9)
        self.assertGreater(len(e.teilstaebe), 1)
        self.assertAlmostEqual(f.bettung["L1"][1], q * 10.0, delta=1e-6 * q)

    def test_einzellast_auf_langem_balken(self):
        """Hetényi, unendlich lang: w = P·β/(2k) unter der Last."""
        k, L = 20e6, 40.0
        beta = (k / (4 * EI)) ** 0.25
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", L / 2, 0), ("K3", L, 0)],
            [stab("L1", "K1", "K2", quer=k), stab("L2", "K2", "K3", quer=k)],
            [Lager("A1", "K1", x=FEST)], Lastfall("P", [Knotenlast("K2", Fz=-P)])))
        w = -e.faelle[0].verschiebungen["K2"][1]
        self.assertAlmostEqual(w / (P * beta / (2 * k)), 1.0, delta=1e-3)


class TestFestesLinienlager(Rechnung):
    def test_aufliegender_stab_traegt_nichts(self):
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 6, 0)], [stab("L1", "K1", "K2", quer=FEST)],
            [Lager("A1", "K1", x=FEST)], Lastfall("q", [linienlast("L1")])))
        f = e.faelle[0]
        self.assertEqual(f.verschiebungen["K2"], (0.0, 0.0, 0.0))
        self.assertAlmostEqual(f.linienlast["L1"][1], q * 6, places=6)
        for wert in f.teile[0].s:
            self.assertAlmostEqual(wert, 0.0, places=6)

    def test_geneigt(self):
        """Ein schräger Stab, quer fest: senkrecht zur Linie hält er, längs nicht -- dort ein Lager."""
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 3, 4)], [stab("L1", "K1", "K2", quer=FEST)],
            [Lager("A1", "K1", x=FEST)], Lastfall("q", [linienlast("L1")])))
        f = e.faelle[0]
        ux, uz, _ = f.verschiebungen["K2"]
        # Nur längs beweglich: (ux, uz) parallel zu (3, 4).
        self.assertAlmostEqual(ux * 4 - uz * 3, 0.0, places=15)

    def test_stuetze_auf_aufliegendem_balken(self):
        """Eine eingespannte Stütze auf einem aufliegenden Balken: der Balken klemmt sie ein."""
        e = self.gerechnet(system(
            [("K1", 0, 0), ("K2", 4, 0), ("K3", 4, 3)],
            [stab("L1", "K1", "K2", quer=FEST, laengs=FEST), stab("L2", "K2", "K3")],
            [], Lastfall("H", [Knotenlast("K3", Fx=10e3)])))
        rx, rz, m = e.faelle[0].lagerkraefte["K2"]
        self.assertAlmostEqual(rx, -10e3, places=6)
        self.assertAlmostEqual(m, 10e3 * 3, places=6)


class TestTStoss(Rechnung):
    def test_knoten_auf_dem_stab_verbindet(self):
        """Eine Stütze, die auf die Mitte eines Balkens trifft, wie ein geteilter Balken."""
        def gerechnet(staebe):
            return self.gerechnet(system(
                [("K1", 0, 0), ("K2", 6, 0), ("K3", 3, 0), ("K4", 3, -3)], staebe,
                [gelenkig("A1", "K1"), rolle("A2", "K2"), gelenkig("A3", "K4")],
                Lastfall("P", [Knotenlast("K3", Fz=-P)])))
        durch = gerechnet([stab("L1", "K1", "K2"), stab("L3", "K4", "K3")])
        geteilt = gerechnet([stab("L1", "K1", "K3"), stab("L2", "K3", "K2"),
                             stab("L3", "K4", "K3")])
        for i in range(3):
            self.assertAlmostEqual(durch.faelle[0].verschiebungen["K3"][i],
                                   geteilt.faelle[0].verschiebungen["K3"][i], places=12)

    def test_kreuzen_ohne_knoten_ist_ein_hinweis(self):
        e = rechnen(system(
            [("K1", 0, 0), ("K2", 4, 0), ("K3", 2, -2), ("K4", 2, 2)],
            [stab("L1", "K1", "K2"), stab("L2", "K3", "K4")],
            [eingespannt("A1", "K1"), eingespannt("A2", "K3")]))
        hinweise = [m for m in e.meldungen if not m.fehler]
        self.assertTrue(e.gueltig)
        self.assertIn("kreuzen sich", hinweise[0].text)


if __name__ == "__main__":
    unittest.main()
