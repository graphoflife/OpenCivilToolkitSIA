"""
Die Decke nach der Streifenmethode -- gegen die Vorlesung und das Kolloquium 4.

* Kolloquium 4 (Musterlösung Stahlbeton II, FS 2023): Platte 9 × 5.5 m,
  oben auf einer Wand, unten auf drei Stützen, mit versteckten Unterzügen von
  1 m; 30 % der Last in x, 70 % in y. Die Schnitte A-A und C-C rechnet die
  App wie die Musterlösung. Den Unterzug B-B rechnet die Musterlösung mit
  einem Faktor aus A-A, als läge die Last aus C-C über seine ganze Länge;
  die App legt sie dorthin, wo C-C aufliegt. Daher weichen B-B, D-D, E-E und
  die Stützenkräfte um wenige Prozent ab -- hier gegen die Handrechnung mit
  der genauen Last geprüft, und die Musterlösung daneben mit ihrer Toleranz.
* Folie 31: die einfach gelagerte Rechteckplatte mit randnaher Abtragung --
  die automatische Aufteilung trifft ihre Momente genau.
* Dieselbe Platte gedreht: schiefe Streifen tragen ``m_η``, und ``m_x``,
  ``m_y``, ``m_xy`` sind dessen Transformation.
"""

import math
import unittest

from opencivil.decke.feld import POSITIV_JE_LAST, an_stelle, lastverteilelemente, widerstaende
from opencivil.decke.modell import (
    Aufteilung, Decke, Flaechenlast, Kombination, Lastfall, Linienlager, Linienlast, Platte, Punktlast,
    Stuetze, Unterzug, Zone,
)
from opencivil.decke.rechnung import rechnen
from opencivil.decke.traeger import extreme, wert

E, WICHTE = 30e9, 25e3
q = 10e3


def rechteck(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def waende(ecken, *nummern):
    return [Linienlager(f"W{i}", ecken[i], ecken[(i + 1) % len(ecken)]) for i in nummern]


class Rechnung(unittest.TestCase):
    def gerechnet(self, decke):
        e = rechnen(decke)
        self.assertFalse([m.text for m in e.meldungen if m.fehler])
        for f in e.faelle:
            self.assertLess(abs(f.fehlbetrag), 1e-6 * max(f.summe, 1.0), f"Probe in {f.name}")
        self.zerlegung = e.zerlegung
        return e

    def je_meter(self, fall, streifen, groesse, s, links=False):
        r = fall.traeger[streifen]
        return wert(r.stuecke, groesse, s, links) / self.zerlegung[r.traeger.streifen].breite

    def kraefte(self, fall, streifen):
        """Je Lager des Trägers ``(Name, Kraft je Meter Streifen)``."""
        r = fall.traeger[streifen]
        b = self.zerlegung[r.traeger.streifen].breite
        return [(k.auflager.name, k.F / b) for k in r.lagerkraefte]


class TestKolloquium4(Rechnung):
    qd = 18.6e3

    @classmethod
    def setUpClass(cls):
        cls.decke = Decke(
            platten=[Platte("P", rechteck(0, 0, 9, 5.5), 0.24, E, WICHTE)],
            linienlager=[Linienlager("Wand", (0, 0), (9, 0))],
            stuetzen=[Stuetze(n, (x, 5.0), 0.3, 0.3) for n, x in (("S1", 0.5), ("S2", 4.5), ("S3", 8.5))],
            unterzuege=[Unterzug("SB1", (0.5, 0), (0.5, 5.5), 1.0, 2), Unterzug("SB2", (4.5, 0), (4.5, 5.5), 1.0, 2),
                        Unterzug("SB1r", (8.5, 0), (8.5, 5.5), 1.0, 2), Unterzug("SB3", (0, 5.0), (9, 5.0), 1.0, 1)],
            lastfaelle=[Lastfall("qd", [Flaechenlast("q_d", cls.qd, platte="P")])],
            aufteilung=Aufteilung.FEST, anteil=0.3)

    def setUp(self):
        self.e = self.gerechnet(self.decke)
        self.f = self.e.faelle[0]
        # Schnitt A-A, Handrechnung mit der Dreimomentengleichung:
        p = 0.3 * self.qd
        self.MA = -p * 0.5 ** 2 / 2.0
        self.MB = -p * 4.0 ** 2 / 8.0 - self.MA / 2.0
        self.RA = p * 0.5 + p * 2.0 + (self.MB - self.MA) / 4.0
        self.RB = 2.0 * (p * 2.0 - (self.MB - self.MA) / 4.0)

    def test_a_a_lagerkraefte(self):
        """q_A,r und q_A,m -- in der Musterlösung 11.5 und 27.4 kN/m² (mit 0.3·q_d = 5.6 gerundet)."""
        self.assertEqual([n for n, _ in self.kraefte(self.f, "x1")], ["SB1", "SB2", "SB1r"])
        for (_, F), soll in zip(self.kraefte(self.f, "x1"), (self.RA, self.RB, self.RA)):
            self.assertAlmostEqual(F, soll, places=3)
        self.assertAlmostEqual(self.RA / 1e3, 11.5, delta=0.1)
        self.assertAlmostEqual(self.RB / 1e3, 27.4, delta=0.1)
        self.assertEqual(self.kraefte(self.f, "x1"), self.kraefte(self.f, "x18"), "alle Streifen im Feld gleich")

    def test_a_a_momente_mit_pressung(self):
        """
        Über dem Mittelunterzug −7.3 kNm/m statt −10.9 mit Punktlager, im
        Feld 6.1, an den Rändern der Unterzüge 3.0 und −4.6 -- die
        Musterlösung rundet 0.3·q_d auf 5.6 und q_A,r auf 11.5.
        """
        p = 0.3 * self.qd
        soll = self.RA * 4.0 - p * 4.5 ** 2 / 2.0 + self.RB * 0.5 ** 2 / 2.0
        self.assertAlmostEqual(self.je_meter(self.f, "x1", "M", 4.5), soll, places=3)
        self.assertAlmostEqual(soll / 1e3, -7.3, delta=0.1)
        (_, _), (_, feld) = extreme(self.f.traeger["x1"].stuecke, "M")
        feld_soll = (self.RA - p * 0.5) ** 2 / (2.0 * p) + self.MA
        self.assertAlmostEqual(feld / 0.25, feld_soll, places=3)
        self.assertAlmostEqual(feld_soll / 1e3, 6.1, delta=0.15)
        for s, musterloesung in ((1.0, 3.0), (4.0, -4.6)):
            soll = self.RA * (s - 0.5) - p * s ** 2 / 2.0
            self.assertAlmostEqual(self.je_meter(self.f, "x1", "M", s), soll, places=3)
            self.assertAlmostEqual(soll / 1e3, musterloesung, delta=0.1)

    def test_c_c(self):
        """
        Wie in der Musterlösung: q_C = 39.3 kN/m², M = 39.9 kNm/m, am Rand
        des Unterzugs 13.2; die Querkraft 32.2 an der Wand, −26.3 am Unterzug.
        """
        p = 0.7 * self.qd
        qC = p * 5.5 ** 2 / 2.0 / 5.0
        (wand, A), (sb3, C) = self.kraefte(self.f, "y5")
        self.assertEqual((wand, sb3), ("Wand", "SB3"))
        self.assertAlmostEqual(C, qC, places=3)
        self.assertAlmostEqual(qC / 1e3, 39.3, delta=0.1)
        (_, _), (_, M) = extreme(self.f.traeger["y5"].stuecke, "M")
        self.assertAlmostEqual(M / 0.25, A ** 2 / (2.0 * p), places=3)
        self.assertAlmostEqual(M / 0.25 / 1e3, 39.9, delta=0.05)
        self.assertAlmostEqual(self.je_meter(self.f, "y5", "M", 4.5) / 1e3, 13.2, delta=0.05)
        self.assertAlmostEqual(self.je_meter(self.f, "y5", "V", 0.0) / 1e3, 32.2, delta=0.05)
        self.assertAlmostEqual(self.je_meter(self.f, "y5", "V", 4.5), A - p * 4.5, places=3)
        self.assertAlmostEqual((A - p * 4.5) / 1e3, -26.3, delta=0.1)

    def test_im_unterzug_tragen_die_feldstreifen_seiner_richtung_nichts(self):
        self.assertNotIn("x20", self.f.traeger)
        self.assertNotIn("y2", self.f.traeger)

    def test_b_b_mit_der_last_dort_wo_c_c_aufliegt(self):
        """
        Dreimomentengleichung mit 0.3·q_d überall und q_C nur über den
        Feldern 1..4 und 5..8 m. Die Musterlösung, mit dem Faktor 8.0:
        52.9 und 180.4 kN/m², −58.5 kNm/m über der Mitte.
        """
        p, w = 0.3 * self.qd, 0.7 * self.qd * 5.5 ** 2 / 2.0 / 5.0
        MA = -p * 0.5 ** 2 / 2.0
        drei_A = p * 4.0 ** 3 / 4.0 + 3.0 * (w / 2.0) * (
            (4.0 * 3.5 ** 2 / 2.0 - 3.5 ** 3 / 3.0) - (4.0 * 0.5 ** 2 / 2.0 - 0.5 ** 3 / 3.0))
        MB = (-2.0 * drei_A - 2.0 * MA * 4.0) / 16.0
        W = p * 4.0 + w * 3.0
        RA = p * 0.5 + W / 2.0 + (MB - MA) / 4.0
        RB = 2.0 * (W / 2.0 - (MB - MA) / 4.0)
        kraefte = self.kraefte(self.f, "SB3")
        self.assertEqual([n for n, _ in kraefte], ["SB1", "SB2", "SB1r"], "auf den Unterzügen, nicht den Stützen")
        self.assertAlmostEqual(kraefte[0][1], RA, places=2)
        self.assertAlmostEqual(kraefte[1][1], RB, places=2)
        self.assertAlmostEqual(RA / 1e3, 52.9, delta=0.6)
        self.assertAlmostEqual(RB / 1e3, 180.4, delta=1.5)
        M = self.je_meter(self.f, "SB3", "M", 4.5)
        self.assertAlmostEqual(M, RA * 4.0 - p * 4.5 ** 2 / 2.0 - w * 3.0 * 2.0 + RB * 0.5 ** 2 / 2.0, places=2)
        self.assertAlmostEqual(M / 1e3, -58.5, delta=2.0)

    def test_stuetzen_und_wand(self):
        """
        D-D und E-E: die Stütze trägt, was über die Wand hinaus bleibt. In der
        Musterlösung 115.5 und 275.1 kN.
        """
        p = 0.7 * self.qd
        x1 = self.kraefte(self.f, "x1")
        b3 = self.kraefte(self.f, "SB3")
        for stuetze, aus_a, aus_b, musterloesung in (("S1", x1[0][1], b3[0][1], 115.5),
                                                     ("S2", x1[1][1], b3[1][1], 275.1)):
            soll = (p * 5.5 ** 2 / 2.0 + aus_a * 4.5 ** 2 / 2.0 + aus_b * 5.0) / 5.0
            self.assertAlmostEqual(self.f.stuetzenkraft(stuetze), soll, places=2)
            self.assertAlmostEqual(soll / 1e3, musterloesung, delta=1.5)
        self.assertAlmostEqual(self.f.stuetzenkraft("S3"), self.f.stuetzenkraft("S1"), places=3)
        self.assertAlmostEqual(self.f.summe, self.qd * 9.0 * 5.5, places=3)
        self.assertAlmostEqual(self.f.wandkraft("Wand") + sum(self.f.stuetzenkraft(s) for s in ("S1", "S2", "S3")),
                               self.f.summe, places=3)

    def test_wand_je_meter(self):
        """Unter den Feldstreifen von C-C trägt die Wand 32.2 kN/m."""
        stueck = next(w for w in self.f.linienlager["Wand"] if w.traeger == "y5")
        self.assertAlmostEqual(stueck.laenge, 0.25)
        self.assertAlmostEqual(stueck.je_meter[0] / 1e3, 32.2, delta=0.05)

    def test_lastverteilelement_ueber_der_mittelstuetze(self):
        """Musterlösung: m'_u = Q/8 = 34.4 kN, m_u = 0.034 Q = 9.4 kN über dem 1 × 1 m Stützenbereich."""
        element = next(l for l in lastverteilelemente(self.e, self.f) if l.name == "S2")
        self.assertAlmostEqual(element.lx, 1.0)
        self.assertAlmostEqual(element.ly, 1.0)
        (oben, unten), _ = element.zusatz()
        self.assertAlmostEqual(oben, -element.Q / 8.0)
        self.assertAlmostEqual(unten, POSITIV_JE_LAST * element.Q)
        self.assertAlmostEqual(-oben / 1e3, 34.4, delta=0.3)
        self.assertAlmostEqual(unten / 1e3, 9.4, delta=0.1)


class TestFolie31(Rechnung):
    """Einfach gelagerte Rechteckplatte a × b, b < a: randnahe Lasten zum nächsten Rand."""

    a, b = 8.0, 4.0

    def setUp(self):
        ecken = rechteck(0, 0, self.a, self.b)
        self.e = self.gerechnet(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)], linienlager=waende(ecken, 0, 1, 2, 3),
                                      lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])]))
        self.f = self.e.faelle[0]

    def test_momente_der_folie(self):
        b = self.b
        mitte = an_stelle(self.e, self.f, (4.0, 2.0))
        self.assertAlmostEqual(mitte.mx, q * b * b / 32.0, places=6)
        self.assertAlmostEqual(mitte.my, q * b * b / 8.0, places=6)
        self.assertAlmostEqual(mitte.mxy, 0.0)
        self.assertAlmostEqual(an_stelle(self.e, self.f, (4.0, 0.5)).mx, q * b * b / 64.0, places=6)
        self.assertAlmostEqual(an_stelle(self.e, self.f, (0.5, 2.0)).my, q * b * b / 64.0, places=6)

    def test_die_ecken_je_zur_haelfte(self):
        zelle = next(z for z in self.e.aufteilungen.zellen if all(0.0 <= x <= 0.25 and 0.0 <= y <= 0.25
                                                                   for x, y in z[0]))
        self.assertEqual(zelle[1], 0.5)


class TestSchief(Rechnung):
    """Die Platte der Folie 31, um 30° gedreht, mit Streifen parallel zu ihren Rändern."""

    def test_m_eta_wie_im_rechteck_und_m_xy_daraus(self):
        phi = math.radians(30.0)
        c, s = math.cos(phi), math.sin(phi)

        def gedreht(p):
            return (c * p[0] - s * p[1] + 3.0, s * p[0] + c * p[1] - 1.0)

        ecken = tuple(gedreht(p) for p in rechteck(0, 0, 8, 4))
        e = self.gerechnet(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE, (phi, phi + math.pi / 2.0))],
                                 linienlager=waende(ecken, 0, 1, 2, 3),
                                 lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])]))
        k = an_stelle(e, e.faelle[0], gedreht((4.0, 2.0)))
        m_eta = k.mx * c * c + k.my * s * s + 2.0 * k.mxy * s * c
        m_xi = k.mx * s * s + k.my * c * c - 2.0 * k.mxy * s * c
        m_eta_xi = (k.my - k.mx) * s * c + k.mxy * (c * c - s * s)
        self.assertAlmostEqual(m_eta, q * 16.0 / 32.0, places=6)
        self.assertAlmostEqual(m_xi, q * 16.0 / 8.0, places=6)
        self.assertAlmostEqual(m_eta_xi, 0.0, places=6)
        self.assertAlmostEqual(k.mxy, (m_eta - m_xi) * s * c, places=6)
        w = widerstaende(k)
        self.assertAlmostEqual(w.mxu, k.mx + abs(k.mxy))
        self.assertAlmostEqual(w.myu_oben, 0.0)


class TestEinachsig(Rechnung):
    """Platte 4 × 2 m zwischen zwei Wänden bei x = 0 und x = 4."""

    def decke(self, *lasten, **felder):
        ecken = rechteck(0, 0, 4, 2)
        felder.setdefault("platten", [Platte("P", ecken, 0.2, E, WICHTE)])
        felder.setdefault("linienlager", waende(ecken, 1, 3))
        return Decke(lastfaelle=[Lastfall("L", list(lasten))], **felder)

    def test_automatisch_traegt_nur_die_richtung_mit_lagern(self):
        e = self.gerechnet(self.decke(Flaechenlast("q", q, platte="P")))
        self.assertAlmostEqual(an_stelle(e, e.faelle[0], (2.0, 1.0)).mx, q * 16.0 / 8.0, places=6)
        self.assertAlmostEqual(an_stelle(e, e.faelle[0], (2.0, 1.0)).my, 0.0)

    def test_linienlast_am_freien_rand_bleibt_ganz_auf_der_platte(self):
        e = self.gerechnet(self.decke(Linienlast("Fassade", (0, 0), (4, 0), q)))
        f = e.faelle[0]
        self.assertAlmostEqual(f.daneben, 0.0)
        self.assertAlmostEqual(f.summe, 4.0 * q, places=6)
        self.assertAlmostEqual(wert(f.traeger["x1"].stuecke, "M", 2.0), q * 16.0 / 8.0, places=3)
        self.assertNotIn("x2", f.traeger)

    def test_linienlast_auf_einer_streifengrenze_je_zur_haelfte(self):
        e = self.gerechnet(self.decke(Linienlast("Wand oben", (0, 1.0), (4, 1.0), q)))
        f = e.faelle[0]
        for streifen in ("x4", "x5"):
            self.assertAlmostEqual(wert(f.traeger[streifen].stuecke, "M", 2.0), q * 16.0 / 16.0, places=3)

    def test_einzellast_und_ihr_lastverteilelement(self):
        Q = 40e3
        e = self.gerechnet(self.decke(Punktlast("Q", (2.0, 1.0), Q, 1.0, 1.0)))
        f = e.faelle[0]
        # Je Streifen 0.25 m der Fläche: W = Q/4 über 1 m in der Mitte des Felds.
        W = Q / 4.0
        self.assertAlmostEqual(wert(f.traeger["x3"].stuecke, "M", 2.0), W * 4.0 / 4.0 - W * 1.0 / 8.0, places=3)
        element, = lastverteilelemente(e, f)
        (oben, unten), _ = element.zusatz()
        self.assertAlmostEqual(unten, Q / 8.0)
        self.assertAlmostEqual(oben, -POSITIV_JE_LAST * Q)

    def test_last_neben_der_platte(self):
        e = rechnen(self.decke(Flaechenlast("halb daneben", q, ecken=rechteck(3, 0, 5, 2))))
        f = e.faelle[0]
        self.assertAlmostEqual(f.daneben, 2.0 * 2.0 * q / 2.0)
        self.assertTrue(any("neben den Platten" in m.text for m in f.meldungen))
        self.assertAlmostEqual(f.fehlbetrag, 0.0, places=6)

    def test_kombination_ist_die_summe(self):
        ecken = rechteck(0, 0, 4, 2)
        d = Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)], linienlager=waende(ecken, 1, 3),
                  lastfaelle=[Lastfall("G", [], eigengewicht=True), Lastfall("Q", [Flaechenlast("q", q, platte="P")])],
                  kombinationen=[Kombination("ULS", {"G": 1.35, "Q": 1.5})])
        e = self.gerechnet(d)
        g, nutz, uls = (e.fall(n) for n in ("G", "Q", "ULS"))
        self.assertAlmostEqual(g.summe, WICHTE * 0.2 * 8.0)
        for wand in ("W1", "W3"):
            self.assertAlmostEqual(uls.wandkraft(wand), 1.35 * g.wandkraft(wand) + 1.5 * nutz.wandkraft(wand), places=6)

    def test_zone_geht_vor(self):
        """Fest je halb -- aber die Zone links gibt alles in x."""
        ecken = rechteck(0, 0, 4, 4)
        e = self.gerechnet(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)], linienlager=waende(ecken, 0, 1, 2, 3),
                                 zonen=[Zone("links", rechteck(0, 0, 2, 4), 1.0)],
                                 lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])],
                                 aufteilung=Aufteilung.FEST, anteil=0.5))
        f = e.faelle[0]
        # Ein x-Streifen trägt q auf 0..2 und q/2 auf 2..4: links 1.75·q je Meter.
        (_, links), (_, rechts) = self.kraefte(f, "x1")
        self.assertAlmostEqual(links, q * 2.0 * 3.0 / 4.0 + q / 2.0 * 2.0 * 1.0 / 4.0, places=6)
        self.assertAlmostEqual(links + rechts, 1.5 * q * 2.0, places=6)
        # In y trägt die Zone nichts, rechts davon die Hälfte.
        self.assertTrue(all(abs(F) < 1e-6 for _, F in self.kraefte(f, "y1")))
        self.assertAlmostEqual(an_stelle(e, f, (1.0, 2.0)).my, 0.0, places=6)
        self.assertAlmostEqual(an_stelle(e, f, (3.0, 2.0)).my, q / 2.0 * 16.0 / 8.0, places=6)

    def test_verschieden_dicke_platten_laufen_durch(self):
        """Felder 4 m (h = 0.2) und 6 m (h = 0.3): die Dreimomentengleichung mit l/EI."""
        p1 = Platte("dünn", rechteck(0, 0, 4, 1), 0.2, E, WICHTE)
        p2 = Platte("dick", rechteck(4, 0, 10, 1), 0.3, E, WICHTE)
        lager = [Linienlager(f"W{x}", (x, 0), (x, 1)) for x in (0, 4, 10)]
        e = self.gerechnet(Decke(platten=[p1, p2], linienlager=lager,
                                 lastfaelle=[Lastfall("q", [Flaechenlast("q1", q, platte="dünn"),
                                                            Flaechenlast("q2", q, platte="dick")])],
                                 aufteilung=Aufteilung.FEST, anteil=1.0))
        f = e.faelle[0]
        k = (0.3 / 0.2) ** 3
        MB = -q / 4.0 * (4.0 ** 3 + 6.0 ** 3 / k) / (2.0 * (4.0 + 6.0 / k))
        self.assertAlmostEqual(an_stelle(e, f, (4.0, 0.5)).mx, MB, places=3)
        self.assertEqual(len(e.zerlegung["x1"].traeger), 1, "über die Plattengrenze ein Träger")

    def test_eingespannt(self):
        """Kragplatte 2 m, an der Wand eingespannt: −qL²/2 an der Wand, die Wand trägt qL je Meter."""
        ecken = rechteck(0, 0, 2, 1)
        e = self.gerechnet(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)],
                                 linienlager=[Linienlager("W", (0, 0), (0, 1), eingespannt=True)],
                                 lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])]))
        f = e.faelle[0]
        self.assertAlmostEqual(an_stelle(e, f, (0.0, 0.5)).mx, -q * 4.0 / 2.0, places=6)
        r, m = f.linienlager["W"][0].je_meter
        self.assertAlmostEqual(r, 2.0 * q)
        self.assertAlmostEqual(m, q * 4.0 / 2.0)

    def test_ohne_lager_traegt_nichts(self):
        ecken = rechteck(0, 0, 4, 2)
        e = rechnen(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)], linienlager=waende(ecken, 3),
                          lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])],
                          aufteilung=Aufteilung.FEST, anteil=1.0))
        f = e.faelle[0]
        self.assertAlmostEqual(f.nicht_getragen, f.summe)
        self.assertTrue(any("trägt nicht" in m.text and m.fehler for m in f.meldungen))


class TestPruefen(unittest.TestCase):
    def test_ueberlappende_platten(self):
        e = rechnen(Decke(platten=[Platte("A", rechteck(0, 0, 4, 4), 0.2, E, WICHTE),
                                   Platte("B", rechteck(3, 0, 6, 4), 0.2, E, WICHTE)]))
        self.assertTrue(any("überlappen" in m.text for m in e.meldungen))
        self.assertEqual(e.faelle, [])

    def test_parallele_unterzuege_uebereinander(self):
        e = rechnen(Decke(platten=[Platte("A", rechteck(0, 0, 4, 4), 0.2, E, WICHTE)],
                          unterzuege=[Unterzug("U1", (0, 2), (4, 2), 1.0), Unterzug("U2", (1, 2.5), (3, 2.5), 0.5)]))
        self.assertTrue(any("parallel" in m.text for m in e.meldungen))


if __name__ == "__main__":
    unittest.main()
