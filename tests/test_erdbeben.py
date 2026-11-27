"""
Das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2 (opencivil.erdbeben.ersatzkraft).

Ein Haus von Hand nachgerechnet -- vier Geschosse auf einem Kern aus zwei
getrennten Wänden: die Auslenkung des Dachs, T_1 (40), S_d (33), F_d (41),
die Kräfte je Geschoss (42), Querkraft und Moment unter jedem Geschoss, das
Kippmoment, die Anteile der Teile am Fuss und dasselbe mit q = 1.0
(16.5.1.9). Dann die Teile eines Kerns, der Kragarm mit eigener
Steifigkeit je Geschoss, wann das Verfahren gilt (16.5.2.1), T_1 von Hand,
was einem Gebäude fehlt, die Prüfungen der Eingabe und was die Oberfläche
sieht.
"""

import json
import math
import unittest

from opencivil.bericht.zusammenfassung import angaben, nachweistabelle, zusammenfassen
from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.erdbeben.ersatzkraft import (
    NICHT_GERECHNET, NICHT_ZULAESSIG, REGELMAESSIGKEIT, duktile_waende,
)
from opencivil.erdbeben.kern import teile
from opencivil.erdbeben.kragarm import beitraege, momente, querkraefte
from opencivil.projekt import ErdbebenEintrag, Projekt, ProjektFehler, QuerschnittsanalyseEintrag
from opencivil.querschnitt import geometrie as geo
from opencivil.web import dienst
from opencivil.web.api import katalog
from tests.unfertig import meldung

#: Eine Wand des Hauses in m: lang in y ihrer Analyse, dünn in z.
LAENGE, DICKE = 5.0, 0.25


def rechteck(y1, z1, y2, z2):
    """Die Ecken eines Rechtecks in mm, linksherum."""
    return ((y1, z1), (y2, z1), (y2, z2), (y1, z2))


RECHTECK = rechteck(0, 0, 5000, 250)
#: Zwei gleiche Wände in x, 5 m auseinander -- ein Kern aus zwei getrennten Teilen.
ZWEI_WAENDE = (RECHTECK, rechteck(0, 5000, 5000, 5250))
#: Eine Wand in x und eine in y, getrennt: in beiden Richtungen eine starke.
IN_X_UND_Y = (RECHTECK, rechteck(6000, 1000, 6250, 6000))


def analyse(p, name, *polygone, beton=None):
    """Eine Querschnittsanalyse aus Polygonen -- aus dem ersten Beton, wo keiner steht."""
    a = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name=name)
    for ecken in polygone or (RECHTECK,):
        a.polygon([list(e) for e in ecken],
                  material=beton or next(m.kennung for m in p.materialien if m.art == "beton"))
    p.querschnittsanalysen.append(a)
    return a


def haus(polygone=ZWEI_WAENDE, **felder):
    """
    Das Haus von Hand: Zone Z2, Baugrund C, BWK I, q = 1.5 und C25/30. Drei
    Geschosse mit G_k = 3000 kN und Q_k = 1000 kN bei ψ₂ = 0.3, das Dach mit
    2500 kN, je 3 m hoch -- jedes auf demselben Kern, η_EI = 0.5: zwei
    gleiche, getrennte Wände in x.
    """
    p = Projekt(name="Probe")
    p.beton("C25/30")
    a = analyse(p, "Kern", *polygone)
    h = p.gebaeude("Haus", **{"zone": "Z2", **felder})
    for i in range(1, 4):
        h.geschoss(f"{i}. OG", h=3.0, G_k=3000.0, Q_k=1000.0, kern=a.kennung)
    h.geschoss("Dach", h=3.0, G_k=2500.0, kern=a.kennung)
    return p, h


def rechnen(p, h):
    """Das Ergebnis, der Befund und die Urteile des Gebäudes, nach ihrem Fall."""
    e = p.rechnen()
    nachweis = e.aufbau.feld("erdbeben")[h.kennung]
    urteile = {u.fall: u for u in e.loesung.urteile if u.raum == nachweis.id}
    return e, e.loesung.befunde[nachweis.id], urteile


def warum_nicht(p, h):
    """Warum das Gebäude ohne Nachweis bleibt -- es wird trotzdem gebaut."""
    aufbau = p.aufbauen()
    if h.kennung in aufbau.feld("erdbeben"):
        raise AssertionError(f"'{h.name}' rechnet doch")
    return aufbau.teile[h.kennung].ohne_nachweis


def E_cm(e, h, i=0):
    """E_cm des Betons im Kern des Geschosses ``i``, N/m²."""
    flaeche = e.aufbau.querschnittsanalysen[h.geschosse[i].kern].flaechen[0]
    return e.wert(flaeche.stoff.id_von("E_cm")).groesse.si


def kragarm(z, W, EI, schritte=60):
    """
    Die Auslenkung des Dachs, unabhängig von :mod:`opencivil.erdbeben.kragarm`
    nachgerechnet: M(s)·a(s)/EI(s) nach Simpson über jedes Geschoss -- M aus
    den Gewichten, a aus einer Kraft 1 am Dach. Beide laufen im Geschoss
    gerade, Simpson ist darum genau.
    """
    H, u, unten = z[-1], 0.0, 0.0
    for zi, EIi in zip(z, EI):
        dz = (zi - unten) / schritte
        for k in range(schritte + 1):
            s = unten + k * dz
            M = sum(Wj * (zj - s) for Wj, zj in zip(W, z) if zj > s)
            g = 1 if k in (0, schritte) else (4 if k % 2 else 2)
            u += g * dz / 3 * M * (H - s) / EIi
        unten = zi
    return u


class TestVonHand(unittest.TestCase):
    """Das Haus, Schritt für Schritt aus der Geometrie -- nicht aus Zwischenwerten der Rechnung."""

    @classmethod
    def setUpClass(cls):
        p, h = haus()
        cls.e, cls.befund, cls.urteile = rechnen(p, h)
        cls.E_cm = E_cm(cls.e, h)
        cls.x, cls.y = cls.befund.richtungen
        cls.z = [3.0, 6.0, 9.0, 12.0]
        cls.W = [3300e3, 3300e3, 3300e3, 2500e3]

    def auslenkung(self, I):
        """Der Kopf des Kragarms unter den Gewichten, waagrecht auf ihrer Höhe -- in m."""
        EI = 0.5 * self.E_cm * 2 * I
        return sum(W * z * z * (3 * 12.0 - z) for W, z in zip(self.W, self.z)) / (6 * EI)

    def test_gewichte_und_hoehen(self):
        """W = G_k + ψ₂·Q_k, auf der Höhe der Decke über der Einspannung."""
        self.assertEqual(self.befund.z, tuple(self.z))
        for W, soll in zip(self.befund.W, self.W):
            self.assertAlmostEqual(W, soll, places=6)

    def test_schwingzeit_aus_der_auslenkung(self):
        """
        (40): T_1 = 2·√u, u in m -- in x biegt die Kraft die Wände um z, je
        um ihren eigenen Schwerpunkt: EI = η_EI·E_cm·2·I_z einer Wand.
        """
        u = self.auslenkung(DICKE * LAENGE ** 3 / 12)
        self.assertAlmostEqual(self.x.u, u, delta=1e-9 * u)
        self.assertAlmostEqual(self.x.T1, 2 * math.sqrt(u), places=9)
        self.assertAlmostEqual(self.x.T1, 0.4035, places=4)
        for EI in self.x.EI:
            self.assertAlmostEqual(EI, 0.5 * self.E_cm * 2 * DICKE * LAENGE ** 3 / 12, delta=1.0)

    def test_spektrum_ersatzkraft_und_kraefte(self):
        """T_C < T_1 ≤ T_D, also (33); dann (41), (42) und das Kippmoment am Fuss."""
        S_d = 2.5 * 1.0 * 1.0 / 10.0 * 1.45 * 0.40 / (self.x.T1 * 1.5)
        self.assertAlmostEqual(self.x.S_d, S_d, places=12)
        F_d = S_d * sum(self.W)
        self.assertAlmostEqual(self.x.F_d, F_d, delta=1e-6)
        self.assertAlmostEqual(F_d / 1e3, 2970.5, delta=0.1)
        zW = [z * W for z, W in zip(self.z, self.W)]
        for F, soll in zip(self.x.kraefte, [k / sum(zW) * F_d for k in zW]):
            self.assertAlmostEqual(F, soll, delta=1e-6)
        self.assertAlmostEqual(self.x.M_0, sum(F * z for F, z in zip(self.x.kraefte, self.z)),
                               delta=1e-3)

    def test_querkraft_und_moment_unter_jedem_geschoss(self):
        """
        Zwei Kräfte, 10 kN auf 3 m und 20 kN auf 6 m: unten V = 30 kN und
        M = 10·3 + 20·6 = 150 kNm, im oberen Geschoss V = 20 kN und
        M = 20·(6 − 3) = 60 kNm. Am Fuss des Hauses ist M das Kippmoment.
        """
        self.assertEqual(querkraefte([10.0, 20.0]), (30.0, 20.0))
        self.assertEqual(momente([10.0, 20.0], [3.0, 6.0]), (150.0, 60.0))
        M = momente(self.x.kraefte, self.z)
        self.assertAlmostEqual(M[0], self.x.M_0, delta=1e-6)
        self.assertAlmostEqual(M[-1], self.x.kraefte[-1] * 3.0, delta=1e-6)
        self.assertEqual(list(M), sorted(M, reverse=True))

    def test_abheben_und_kippen_mit_q_eins(self):
        """16.5.1.9: q = 1.0 -- im Ast (33) ist S_d umgekehrt proportional zu q."""
        self.assertAlmostEqual(self.x.S_d_1, 1.5 * self.x.S_d, places=12)
        self.assertAlmostEqual(self.x.F_d_1, 1.5 * self.x.F_d, delta=1e-6)
        self.assertAlmostEqual(self.x.M_0_1, 1.5 * self.x.M_0, delta=1e-3)

    def test_zwei_gleiche_teile_je_die_haelfte(self):
        self.assertEqual([t.nummer for t in self.x.teile], [1, 2])
        for t in self.x.teile:
            with self.subTest(teil=t.nummer):
                self.assertAlmostEqual(t.I, DICKE * LAENGE ** 3 / 12, places=9)
                self.assertAlmostEqual(t.anteil, 0.5, places=12)
                self.assertAlmostEqual(t.V, self.x.F_d / 2, delta=1e-6)
                self.assertAlmostEqual(t.M, self.x.M_0 / 2, delta=1e-3)

    def test_in_y_nur_die_schwache_achse(self):
        """
        In y biegt die Kraft die Wände um y -- je um ihren eigenen
        Schwerpunkt, ohne Steiner-Anteil zwischen ihnen, auch 5 m
        auseinander: T_1 ist √(I_z/I_y) = 20-mal so lang, über T_D (34),
        und S_d bleibt am unteren Wert 0.1·γ_f·a_gd/g.
        """
        u = self.auslenkung(LAENGE * DICKE ** 3 / 12)
        self.assertAlmostEqual(self.y.T1, 2 * math.sqrt(u), places=9)
        self.assertAlmostEqual(self.y.T1, 20 * self.x.T1, places=9)
        self.assertAlmostEqual(self.y.S_d, 0.1 * 1.0 * 1.0 / 10.0, places=12)

    def test_erfuellungsgrad_ist_vier_T_C_durch_T_1(self):
        """(39) je Richtung; wer verfehlt, sagt warum -- das Verfahren gilt dann gar nicht."""
        x, y = self.urteile["Richtung x"], self.urteile["Richtung y"]
        self.assertTrue(x.erfuellt)
        self.assertAlmostEqual(x.erfuellungsgrad.si, 1.6 / self.x.T1, places=9)
        self.assertEqual(x.hinweis, "")
        self.assertFalse(y.erfuellt)
        self.assertAlmostEqual(y.erfuellungsgrad.si, 1.6 / self.y.T1, places=9)
        self.assertEqual(y.hinweis, f"{NICHT_ZULAESSIG}: in y ist T₁ > 4·T_C (39)")
        self.assertEqual(self.befund.gruende, ("in y ist T₁ > 4·T_C (39)",))
        self.assertFalse(self.befund.zulaessig)
        self.assertNotIn(REGELMAESSIGKEIT, self.urteile)


class TestTeileDesKerns(unittest.TestCase):
    """
    Was ein Stück Kante teilt, biegt sich gemeinsam -- mit Steiner-Anteil,
    um den gemeinsamen Schwerpunkt. Getrennte Teile zählen je um ihren
    eigenen (Benutzer, 2026-11-27).
    """

    def kern(self, *polygone, eltern=None, gewichte=None):
        n = len(polygone)
        gewichte = gewichte or [1.0] * n
        return teile([list(p) for p in polygone], [f"Polygon {i}" for i in range(1, n + 1)],
                     eltern or [None] * n, lambda i: gewichte[i])

    def test_eine_gemeinsame_kante_ist_ein_teil(self):
        """Zwei Wände übereinander, 5000 × 250 je: ein Teil, so steif wie eine 500 mm dicke."""
        k, = self.kern(rechteck(0, 0, 5000, 250), rechteck(0, 250, 5000, 500))
        self.assertEqual(k.polygone, ("Polygon 1", "Polygon 2"))
        self.assertAlmostEqual(k.werte.I_y, 5000 * 500 ** 3 / 12, delta=1.0)

    def test_ein_stueck_kante_genuegt(self):
        self.assertEqual(len(self.kern(rechteck(0, 0, 1000, 250),
                                       rechteck(500, 250, 1500, 500))), 1)
        self.assertTrue(geo.beruehren(rechteck(0, 0, 1000, 250), rechteck(500, 250, 1500, 500)))

    def test_getrennt_ohne_steiner_anteil(self):
        a, b = self.kern(rechteck(0, 0, 5000, 250), rechteck(0, 5000, 5000, 5250))
        self.assertEqual((a.nummer, b.nummer), (1, 2))
        for t in (a, b):
            self.assertAlmostEqual(t.werte.I_y, 5000 * 250 ** 3 / 12, delta=1.0)

    def test_eine_ecke_allein_verbindet_nicht(self):
        self.assertEqual(len(self.kern(rechteck(0, 0, 1000, 250),
                                       rechteck(1000, 250, 2000, 500))), 2)
        self.assertFalse(geo.beruehren(rechteck(0, 0, 1000, 250), rechteck(1000, 250, 2000, 500)))

    def test_eine_aussparung_gehoert_zu_ihrem_polygon(self):
        """Ein Rohr 1000 × 1000 mit einem Loch 500 × 500: ein Teil, die Fläche ohne das Loch."""
        k, = self.kern(rechteck(0, 0, 1000, 1000), rechteck(250, 250, 750, 750),
                       eltern=[None, 0], gewichte=[1.0, -1.0])
        self.assertEqual(k.polygone, ("Polygon 1",))
        self.assertAlmostEqual(k.werte.A, 1000 ** 2 - 500 ** 2, delta=1e-6)
        self.assertAlmostEqual(k.werte.I_y, (1000 ** 4 - 500 ** 4) / 12, delta=1.0)

    def test_ein_u_und_eine_wand(self):
        """Drei Wände, die sich berühren, und eine für sich -- nummeriert, wie gezeichnet."""
        u, wand = self.kern(rechteck(0, 0, 2000, 250), rechteck(0, 250, 250, 2000),
                            rechteck(4000, 0, 4250, 2000), rechteck(250, 1750, 2000, 2000))
        self.assertEqual(u.polygone, ("Polygon 1", "Polygon 2", "Polygon 4"))
        self.assertEqual(wand.polygone, ("Polygon 3",))


class TestKragarm(unittest.TestCase):
    """Der Kern als Kragarm, Geschoss für Geschoss mit eigener Steifigkeit (Arbeitssatz)."""

    def test_zwei_geschosse_mit_eigener_steifigkeit(self):
        """
        Eine Kraft 1 am Dach auf 6 m, unten EI = 2, oben EI = 1: u =
        ∫₀³ (6 − z)²/2 dz + ∫₃⁶ (6 − z)² dz = 31.5 + 9 = 40.5.
        """
        u = sum(b.du for b in beitraege((3.0, 6.0), (0.0, 1.0), (2.0, 1.0)))
        self.assertAlmostEqual(u, 40.5, places=12)

    def test_ein_EI_gibt_die_geschlossene_formel(self):
        """Mit einem EI über die ganze Höhe: u = Σ W z² (3H − z) / (6 EI), wie bis 2026-11-27."""
        z, W, EI = (3.0, 6.0, 9.0, 12.0), (3.3e6, 3.3e6, 3.3e6, 2.5e6), 5e10
        soll = sum(Wi * zi ** 2 * (3 * 12.0 - zi) for Wi, zi in zip(W, z)) / (6 * EI)
        self.assertAlmostEqual(sum(b.du for b in beitraege(z, W, (EI,) * 4)), soll,
                               delta=1e-12 * soll)

    def test_oben_duenner(self):
        """
        Die oberen zwei Geschosse auf Wänden von 200 statt 250 mm: jedes
        biegt sich mit seinem Kern. u stimmt mit dem Integral über die
        Höhe und liegt zwischen dem Haus ganz auf dicken und ganz auf dünnen
        Wänden; am Fuss tragen die Teile des unteren Kerns.
        """
        dick, _ = rechnen(*haus())[1].richtungen
        p, h = haus()
        duenn = analyse(p, "Kern, oben", rechteck(0, 0, 5000, 200), rechteck(0, 5000, 5000, 5200))
        for g in h.geschosse[2:]:
            g.kern = duenn.kennung
        e, befund, _ = rechnen(p, h)
        x, _ = befund.richtungen
        I = [2 * t * LAENGE ** 3 / 12 for t in (DICKE, DICKE, 0.2, 0.2)]
        EI = [0.5 * E_cm(e, h) * Ii for Ii in I]
        for ist, soll in zip(x.EI, EI):
            self.assertAlmostEqual(ist, soll, delta=1e-9 * soll)
        u = kragarm(befund.z, befund.W, EI)
        self.assertAlmostEqual(x.u, u, delta=1e-9 * u)
        p_duenn, h_duenn = haus(polygone=(rechteck(0, 0, 5000, 200), rechteck(0, 5000, 5000, 5200)))
        ganz_duenn, _ = rechnen(p_duenn, h_duenn)[1].richtungen
        self.assertLess(dick.u, x.u)
        self.assertLess(x.u, ganz_duenn.u)
        self.assertAlmostEqual(x.teile[0].I, DICKE * LAENGE ** 3 / 12, places=9)

    def test_ein_teil_verteilt_nichts(self):
        """Ein Kern aus einem Teil trägt alles selbst: keine Tabelle der Teile."""
        x, _ = rechnen(*haus(polygone=(RECHTECK,)))[1].richtungen
        self.assertEqual(x.teile, ())


class TestWannDasVerfahrenGilt(unittest.TestCase):
    """16.5.2.1: Grund- und Aufriss regelmässig, T_1 ≤ 4·T_C in beiden Richtungen."""

    def mit_wand_in_y(self, **felder):
        return haus(polygone=IN_X_UND_Y, **felder)

    def test_regelmaessig_und_in_beiden_richtungen_kurz(self):
        """Dann steht je Richtung ein Urteil -- und keines zur Regelmässigkeit."""
        _, befund, urteile = rechnen(*self.mit_wand_in_y())
        self.assertTrue(befund.zulaessig)
        self.assertEqual(set(urteile), {"Richtung x", "Richtung y"})
        self.assertTrue(all(u.erfuellt for u in urteile.values()))

    def test_ein_unregelmaessiger_grundriss_ist_rot(self):
        """Die Zahlen bleiben; das Urteil der Regelmässigkeit verfehlt, mit seinem Grund."""
        _, befund, urteile = rechnen(*self.mit_wand_in_y(grundriss_regelmaessig=False))
        regel = urteile[REGELMAESSIGKEIT]
        self.assertFalse(regel.erfuellt)
        self.assertEqual(regel.erfuellungsgrad.si, 0.0)
        self.assertEqual(regel.hinweis,
                         f"{NICHT_ZULAESSIG}: der Grundriss ist nicht regelmässig (16.5.1.3)")
        self.assertEqual(len(befund.richtungen), 2)
        self.assertTrue(urteile["Richtung x"].erfuellt)

    def test_ein_unregelmaessiger_aufriss(self):
        _, befund, _ = rechnen(*self.mit_wand_in_y(aufriss_regelmaessig=False))
        self.assertEqual(befund.gruende, ("der Aufriss ist nicht regelmässig (16.5.1.4)",))

    def test_wird_es_nach_oben_schwerer_sagt_es_die_rechnung(self):
        """Auch wenn beide Schalter auf «ja» stehen: das Gewicht zeigt es selbst."""
        p, h = self.mit_wand_in_y()
        h.geschosse[3].G_k = 4000.0
        _, befund, urteile = rechnen(p, h)
        self.assertEqual(befund.gruende,
                         ("das Gewicht nimmt nach oben zu, in «Dach» (16.5.1.4)",))
        self.assertFalse(urteile[REGELMAESSIGKEIT].erfuellt)

    def test_wer_verfehlt_nennt_jeden_grund(self):
        """(39) verfehlt in y, und der Grundriss ist unregelmässig: beide Urteile nennen beides."""
        _, _, urteile = rechnen(*haus(grundriss_regelmaessig=False))
        satz = (f"{NICHT_ZULAESSIG}: der Grundriss ist nicht regelmässig (16.5.1.3); "
                "in y ist T₁ > 4·T_C (39)")
        self.assertEqual(urteile["Richtung y"].hinweis, satz)
        self.assertEqual(urteile[REGELMAESSIGKEIT].hinweis, satz)
        self.assertEqual(urteile["Richtung x"].hinweis, "")


class TestSchwingzeitVonHand(unittest.TestCase):

    def test_ohne_kern_die_kraefte_ohne_verteilung(self):
        """
        Zone Z3b, Baugrund E, BWK III: in x unter T_B (31), in y zwischen
        T_C und T_D (33) und über 4·T_C. Ohne Kern trägt kein Teil einen Anteil.
        """
        p = Projekt(name="Probe")
        h = p.gebaeude("Lager", zone="Z3b", baugrund="E", bauwerksklasse="III",
                       schwingzeit="hand", T1_x=0.05, T1_y=1.2)
        h.geschoss("Halle", h=5.0, G_k=1200.0, Q_k=2000.0, psi_2=0.8)
        _, befund, urteile = rechnen(p, h)
        x, y = befund.richtungen
        faktor = 1.5 * 1.6 / 10.0
        self.assertIsNone(x.u)
        self.assertAlmostEqual(
            x.S_d, faktor * 1.70 * (0.67 + (2.5 / 1.5 - 0.67) * 0.05 / 0.09), places=12)
        self.assertAlmostEqual(y.S_d, 2.5 * faktor * 1.70 * 0.25 / (1.2 * 1.5), places=12)
        self.assertAlmostEqual(x.F_d, x.S_d * 2800e3, delta=1e-6)
        self.assertEqual((x.teile, x.EI), ((), ()))
        self.assertTrue(urteile["Richtung x"].erfuellt)
        self.assertFalse(urteile["Richtung y"].erfuellt)

    def test_mit_kern_verteilt_es_auch_von_hand(self):
        """T_1 von Hand, der Kern verteilt trotzdem auf seine Teile."""
        p, h = haus(schwingzeit="hand", T1_x=0.5, T1_y=0.5)
        x, _ = rechnen(p, h)[1].richtungen
        self.assertEqual((x.T1, x.u), (0.5, None))
        self.assertEqual([t.anteil for t in x.teile], [0.5, 0.5])

    def test_ohne_gewicht_keine_einwirkung(self):
        """Wie bei allen Nachweisen -- nicht «erfüllt, ∞» ohne ein Wort."""
        p = Projekt(name="Probe")
        h = p.gebaeude("Leer", schwingzeit="hand")
        h.geschoss("EG", h=3.0, G_k=0.0)
        _, befund, urteile = rechnen(p, h)
        self.assertEqual(befund.richtungen, ())
        for r in ("x", "y"):
            with self.subTest(richtung=r):
                u = urteile[f"Richtung {r}"]
                self.assertTrue(u.erfuellt)
                self.assertTrue(math.isinf(u.erfuellungsgrad.si))
                self.assertEqual(u.hinweis, OHNE_EINWIRKUNG)


class TestWasEinemGebaeudeFehlt(unittest.TestCase):
    """Es wird gebaut, aber ohne Nachweis -- grau, mit allem, was fehlt, und jedem Geschoss dazu."""

    def gebaeude(self, *kerne):
        """Ein Geschoss je Kern, «G1», «G2», … -- ohne Kern eines ohne."""
        p = Projekt(name="Probe")
        p.beton("C25/30")
        h = p.gebaeude("Haus")
        for i, kennung in enumerate(kerne or ("",), start=1):
            h.geschoss(f"G{i}", h=3.0, G_k=1000.0, kern=kennung)
        return p, h

    def test_ohne_geschoss(self):
        p = Projekt(name="Probe")
        p.gebaeude("Leer")
        aufbau = p.aufbauen()
        self.assertEqual(aufbau.feld("erdbeben"), {})
        self.assertIn(("erdbeben.h1", "Erdbeben 'Leer': noch kein Geschoss – unter «Geschosse» "
                                      "eines anlegen → kein Nachweis."), aufbau.warnungen)

    def test_ohne_kern_braucht_es_T1_von_hand(self):
        p, h = self.gebaeude()
        self.assertEqual(warum_nicht(p, h), "noch kein Kern – unter «Kern» je Geschoss eine "
                                            "Querschnittsanalyse wählen, oder T₁ von Hand angeben")

    def test_hat_eines_einen_braucht_jedes_einen(self):
        """Ohne ihn stimmten Schwingzeit und Verteilung nicht -- und sähen doch richtig aus."""
        p, h = self.gebaeude()
        h.geschosse[0].kern = analyse(p, "Wand").kennung
        h.geschoss("G2", h=3.0, G_k=1000.0)
        h.geschoss("G3", h=3.0, G_k=1000.0)
        self.assertEqual(warum_nicht(p, h), "noch keine Querschnittsanalyse gewählt («G2», «G3»)")

    def test_eine_geloeschte_analyse(self):
        p, h = self.gebaeude("a9")
        self.assertEqual(warum_nicht(p, h), "die gewählte Querschnittsanalyse gibt es nicht "
                                            "mehr – eine andere wählen («G1»)")

    def test_eine_analyse_die_nicht_rechnet(self):
        p, h = self.gebaeude()
        leer = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name="Leer")
        p.querschnittsanalysen.append(leer)
        h.geschosse[0].kern = leer.kennung
        self.assertEqual(warum_nicht(p, h), "die Querschnittsanalyse «Leer» rechnet nicht "
                                            "(noch nichts gezeichnet) («G1»)")

    def test_zwei_betone_geben_kein_E_cm(self):
        p, h = self.gebaeude()
        zweiter = p.beton("C30/37")
        a = analyse(p, "Gemischt")
        a.polygon([[0, 250], [5000, 250], [5000, 500], [0, 500]], material=zweiter.kennung)
        h.geschosse[0].kern = a.kennung
        self.assertEqual(warum_nicht(p, h), "die Querschnittsanalyse «Gemischt» hat mehr als "
                                            "einen Beton («C25/30», «C30/37») – für E_cm "
                                            "braucht es genau einen («G1»)")

    def test_keine_hauptachsen_sagt_es_einmal(self):
        """Ein Winkel: |I_yz| weit über 5 % -- derselbe Hinweis wie im Raum, je Analyse einmal."""
        p, h = self.gebaeude()
        winkel = analyse(p, "Winkel", ((0, 0), (4000, 0), (4000, 250), (250, 250),
                                       (250, 2000), (0, 2000)))
        h.geschosse[0].kern = winkel.kennung
        h.geschoss("G2", h=3.0, G_k=1000.0, kern=winkel.kennung)
        _, befund, _ = rechnen(p, h)
        self.assertEqual(len(befund.hinweise), 1)
        self.assertTrue(befund.hinweise[0].startswith(
            "Querschnittsanalyse «Winkel»: y und z sind keine Hauptachsen"))


class TestDuktileWaende(unittest.TestCase):
    """
    Über q = 2.0 ist das Tragwerk duktil bemessen (SIA 262:2025, Tabellen 14
    und 15): dann gelten für schlanke Wände eigene Bemessungswerte (4.3.9.4),
    die diese Rechnung nicht kennt. Sie sagt es grau, statt Kräfte am Kern zu
    zeigen, die nach Bemessung aussehen.
    """

    def test_nur_wo_q_ueber_zwei(self):
        for felder, richtungen in (({}, ()), ({"q_x": 2.0}, ()), ({"q_x": 3.0}, ("x",)),
                                   ({"q_x": 3.0, "q_y": 4.0}, ("x", "y"))):
            with self.subTest(**felder):
                p, h = haus(**felder)
                self.assertEqual(rechnen(p, h)[1].hinweise,
                                 (duktile_waende(richtungen),) if richtungen else ())

    def test_ohne_kern_kein_satz_ueber_waende(self):
        p = Projekt(name="Probe")
        h = p.gebaeude("Ohne Kern", schwingzeit="hand", q_x=3.0)
        h.geschoss("EG", h=3.0, G_k=1000.0)
        self.assertEqual(rechnen(p, h)[1].hinweise, ())

    def test_grau_in_der_ansicht_und_in_der_herleitung(self):
        p, h = haus(q_y=3.0)
        daten = dienst.bearbeite("rechnen", {"projekt": p.als_dict()}).daten
        self.assertIn({"text": duktile_waende(["y"]), "fehler": False},
                      daten["zeichendaten"][h.kennung]["meldungen"])
        self.assertIn(duktile_waende(["y"]),
                      [b.get("text") for b in daten["protokoll"] if b["art"] == "hinweis"])


class TestEingaben(unittest.TestCase):

    def test_neu_mit_einem_geschoss_ohne_kern(self):
        """Wie die Oberfläche es anlegt: noch ohne Last und ohne Kern, η_EI = 0.5."""
        neu = ErdbebenEintrag.neu(kennung="h1", name="G")
        self.assertEqual([(g.name, g.h, g.G_k, g.kern, g.eta_EI) for g in neu.geschosse],
                         [("Geschoss 1", 3.0, 0.0, "", 0.5)])
        self.assertNotIn("waende", neu.als_dict())

    def test_unmoegliche_zahlen_vor_dem_rechnen(self):
        """Am Ort, mit dem Namen der Maske -- «Geschoss 'EG'», nicht das Feld der Datei."""
        for felder, geschoss, satz in (
                ({"q_x": 0.5}, {}, "Erdbeben 'Haus': Verhaltensbeiwert q_x muss mindestens "
                                   "1 sein"),
                ({}, {"h": 0.0}, "Geschoss 'EG': Höhe h muss grösser als null sein"),
                ({}, {"G_k": -1.0}, "Geschoss 'EG': Ständige Last G_k kann nicht negativ sein"),
                ({}, {"psi_2": 1.5}, "ψ₂ muss mindestens null und höchstens 1 sein"),
                ({}, {"eta_EI": 0.0}, "Geschoss 'EG': η_EI muss grösser als null und "
                                      "höchstens 1 sein")):
            with self.subTest(satz=satz):
                p = Projekt(name="Probe")
                p.beton("C25/30")
                h = p.gebaeude("Haus", **felder)
                h.geschoss("EG", **{"h": 3.0, "G_k": 1000.0, "kern": analyse(p, "Wand").kennung,
                                    **geschoss})
                self.assertIn(satz, meldung(p))

    def test_eine_zone_die_es_nicht_gibt(self):
        with self.assertRaises(ProjektFehler) as fehler:
            Projekt(name="Probe").gebaeude("Haus", zone="Z4")
        self.assertIn("'Z4' gibt es als 'zone' nicht", str(fehler.exception))

    def test_datei_hin_und_zurueck(self):
        p, h = haus(schwingzeit="hand", T1_x=0.8, grundriss_regelmaessig=False)
        h.geschosse[3].eta_EI = 0.4
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.als_dict(), p.als_dict())
        self.assertEqual([g.eta_EI for g in wieder.erdbeben[0].geschosse], [0.5, 0.5, 0.5, 0.4])

    def test_die_kerne_sind_bezuege(self):
        """Jede Analyse einmal, auch wo viele Geschosse sie nehmen."""
        p, h = haus()
        oben = analyse(p, "Oben")
        h.geschosse[3].kern = oben.kennung
        self.assertEqual(h.bezuege(), sorted({h.geschosse[0].kern, oben.kennung}))


class TestZwischenspeicher(unittest.TestCase):
    """
    Ändert sich nur die Analyse eines Kerns, rechnet das Gebäude neu. Bis
    2026-11-27 blieb sein altes Ergebnis im Zwischenspeicher stehen: die
    Analyse war kein Bezug des Gebäudes.
    """

    def rechnen(self, d, frisch):
        if frisch:
            dienst.SPEICHER.leeren()
        return dienst.bearbeite("rechnen", {"projekt": d})

    def F_d(self, antwort, h):
        richtungen = antwort.daten["zeichendaten"][h.kennung]["richtungen"]
        return next(r["F_d"] for r in richtungen if r["richtung"] == "x")

    def test_eine_kuerzere_wand_rechnet_das_gebaeude_neu(self):
        p, h = haus()
        d = p.als_dict()
        vorher = self.rechnen(d, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        for knoten in d["querschnittsanalysen"][0]["knoten"][1:3]:
            knoten["y"] = 2500.0
        mit = self.rechnen(d, frisch=False)
        self.assertEqual((dienst.SPEICHER.treffer, dienst.SPEICHER.fehlgriffe), (0, 2))
        ohne = self.rechnen(d, frisch=True)
        self.assertEqual(json.dumps(mit.daten, sort_keys=True, default=str),
                         json.dumps(ohne.daten, sort_keys=True, default=str))
        self.assertNotAlmostEqual(self.F_d(mit, h), self.F_d(vorher, h), delta=1.0)


class TestWasDieOberflaecheSieht(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.projekt = Projekt.beispiel()
        cls.haus = cls.projekt.erdbeben[0]
        cls.antwort = dienst.bearbeite("rechnen", {"projekt": cls.projekt.als_dict()})
        cls.d = cls.antwort.daten["zeichendaten"][cls.haus.kennung]

    def ansicht(self, p, h):
        return dienst.bearbeite("rechnen", {"projekt": p.als_dict()}).daten["zeichendaten"][
            h.kennung]

    def test_katalog(self):
        k = katalog()
        e = k["erdbeben"]
        self.assertEqual([z["wert"] for z in e["zonen"]], ["Z1a", "Z1b", "Z2", "Z3a", "Z3b"])
        self.assertEqual(e["zonen"][0]["titel"], "Zone Z1a: a_gd = 0.6 m/s²")
        self.assertEqual([b["wert"] for b in e["baugrund"]], ["A", "B", "C", "D", "E"])
        self.assertTrue(e["bauwerksklassen"][2]["titel"].endswith("– γ_f = 1.5"))
        self.assertNotIn("lagen", e)
        self.assertEqual([s["wert"] for s in e["schwingzeiten"]], ["kern", "hand"])
        self.assertEqual([r["feld"] for r in e["regelmaessigkeit"]],
                         ["grundriss_regelmaessig", "aufriss_regelmaessig"])
        neu, = k["neu"]["erdbeben"]["geschosse"]
        self.assertEqual((neu["name"], neu["kern"], neu["eta_EI"]), ("Geschoss 1", "", 0.5))
        self.assertNotIn("waende", k["neu"]["erdbeben"])
        self.assertEqual(k["felder"]["geschoss"]["G_k"]["einheit"], "kN")
        self.assertEqual([(g["titel"], [f["feld"] for f in g["felder"][""]])
                          for g in k["vorgaben"]["geschoss"]],
                         [("Geschoss", ["h", "G_k", "Q_k", "psi_2"]), ("Kern", ["eta_EI"])])

    def test_ansicht_des_beispiels(self):
        """Das Wohnhaus auf seinem Kern aus vier Wänden: je Richtung tragen zwei fast alles."""
        self.assertEqual(self.antwort.status, 200)
        d = self.d
        self.assertEqual([r["richtung"] for r in d["richtungen"]], ["x", "y"])
        x = d["richtungen"][0]
        self.assertAlmostEqual(sum(x["kraefte"]), x["F_d"], places=6)
        self.assertAlmostEqual(x["querkraefte"][0], x["F_d"], places=6)
        self.assertAlmostEqual(x["momente"][0], x["M_0"], places=6)
        self.assertEqual(len(x["momente"]), 4)
        stark = 0.25 * 5.0 ** 3 / 12
        schwach = 5.0 * 0.25 ** 3 / 12
        self.assertEqual([t["nummer"] for t in x["teile"]], [1, 2, 3, 4])
        for t, I in zip(x["teile"], (stark, stark, schwach, schwach)):
            self.assertAlmostEqual(t["anteil"], I / (2 * stark + 2 * schwach), places=9)
        self.assertAlmostEqual(sum(t["V"] for t in x["teile"]), x["F_d"], places=6)
        self.assertEqual(d["kerne"], [None] * 4)
        self.assertTrue(d["zulaessig"])
        self.assertEqual(d["meldungen"], [{"text": NICHT_GERECHNET, "fehler": False}])
        zeilen = ["".join(z.get("text") or z["mathe"] for z in zeile) for zeile in d["legende"]]
        self.assertTrue(zeilen[0].startswith("Richtung x: T_{1,x} = 0.356"))
        self.assertIn("– erfüllt", zeilen[0])
        self.assertIn("mit q = 1.0 für Abheben und Kippen (16.5.1.9)", zeilen[1])

    def test_massen_auf_den_decken(self):
        """m = W/g in t: 2500 + 0.3 · 800 = 2740 kN gibt 274 t, das Dach 200 t."""
        massen = [(g["z"], round(g["W"], 6), round(g["m"], 6)) for g in self.d["geschosse"]]
        self.assertEqual(massen,
                         [(3.0, 2740.0, 274.0), (6.0, 2740.0, 274.0), (9.0, 2740.0, 274.0),
                          (12.0, 2000.0, 200.0)])

    def test_der_kern_im_grundriss(self):
        """
        Um den Schwerpunkt seiner Analyse, in mm, wie gezeichnet: 12 × 10 m,
        die vier Wände mit ihrer Nummer an ihrem Schwerpunkt.
        """
        kern, = self.d["grundrisse"].values()
        self.assertEqual(list(self.d["grundrisse"]), [self.haus.geschosse[0].kern])
        punkte = [p for poly in kern["polygone"] for p in poly["punkte"]]
        self.assertEqual([round(min(p[k] for p in punkte)) for k in (0, 1)], [-6000, -5000])
        self.assertEqual([round(max(p[k] for p in punkte)) for k in (0, 1)], [6000, 5000])
        self.assertEqual(kern["polygone"][0]["material"], "beton")
        self.assertEqual([(t["nummer"], [round(v) for v in t["mitte"]]) for t in kern["teile"]],
                         [(1, [0, -4875]), (2, [0, 4875]), (3, [-5875, 0]), (4, [5875, 0])])
        zeilen = ["".join(z.get("text") or z["mathe"] for z in zeile)
                  for zeile in self.d["verlaufslegende"]]
        self.assertIn("«Kern aus vier Wänden» in jedem", zeilen[0])
        self.assertTrue(zeilen[1].endswith("M am Fuss ist M_0."))

    def test_ein_teil_ohne_nummern(self):
        p, h = haus(polygone=(RECHTECK,))
        kern, = self.ansicht(p, h)["grundrisse"].values()
        self.assertEqual(kern["teile"], [])

    def test_ein_geschoss_ohne_kern_sagt_es_an_ihm(self):
        p, h = haus()
        h.geschosse[3].kern = ""
        d = self.ansicht(p, h)
        self.assertEqual(d["kerne"], [None, None, None, {
            "analyse": "", "fehler": False, "grund": "noch keine Querschnittsanalyse gewählt"}])
        self.assertEqual(d["meldungen"], [{"text": "«Dach»: noch keine Querschnittsanalyse "
                                                   "gewählt.", "fehler": False}])
        self.assertEqual(d["richtungen"], [])
        self.assertEqual(list(d["grundrisse"]), [h.geschosse[0].kern])

    def test_die_massen_auch_ohne_rechnung(self):
        """Wer Geschosse eingibt, sieht ihre Massen, auch bevor ein Kern gewählt ist."""
        p = Projekt(name="Probe")
        h = p.gebaeude("Haus")
        h.geschoss("EG", h=3.0, G_k=2500.0, Q_k=800.0)
        h.geschoss("Dach", h=2.5, G_k=2000.0)
        d = self.ansicht(p, h)
        self.assertEqual(d["richtungen"], [])
        self.assertEqual([(g["z"], round(g["W"], 6), round(g["m"], 6)) for g in d["geschosse"]],
                         [(3.0, 2740.0, 274.0), (5.5, 2000.0, 200.0)])

    def test_ohne_geschoss_sagt_es_die_ansicht(self):
        p = Projekt(name="Probe")
        h = p.gebaeude("Haus")
        self.assertEqual(self.ansicht(p, h)["meldungen"], [{
            "text": "Noch kein Geschoss – unter «Geschosse» eines anlegen → kein Nachweis.",
            "fehler": False}])

    def test_ohne_gewicht_sagt_es_die_ansicht(self):
        """Grau und zuerst: ohne Gewicht keine Kraft, die das Bild zeigen könnte."""
        p = Projekt(name="Probe")
        h = p.gebaeude("Leer", schwingzeit="hand")
        h.geschoss("EG", h=3.0, G_k=0.0)
        d = self.ansicht(p, h)
        self.assertEqual(d["richtungen"], [])
        self.assertEqual(d["meldungen"][0], {"text": OHNE_EINWIRKUNG, "fehler": False})
        self.assertNotIn(True, [m["fehler"] for m in d["meldungen"]])

    def test_nicht_zulaessig_steht_rot_da(self):
        p, h = haus(grundriss_regelmaessig=False)
        d = self.ansicht(p, h)
        self.assertFalse(d["zulaessig"])
        self.assertEqual(d["meldungen"][0], {
            "text": "Nicht zulässig – Antwortspektrenverfahren (16.5.3.1): der Grundriss ist "
                    "nicht regelmässig (16.5.1.3); in y ist T₁ > 4·T_C (39).",
            "fehler": True})

    def test_zusammenfassung(self):
        aufbau = self.projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        teil = next(b for b in zusammenfassen(aufbau, loesung).bauteile
                    if b.kennung == self.haus.kennung)
        kopf, kraefte = angaben(aufbau, self.haus.kennung, loesung)
        self.assertEqual(kopf.titel, "Angaben zum Gebäude")
        self.assertIn(r"\text{Zone Z1b, Baugrund C, BWK I}", kopf.latex)
        self.assertEqual([z[0] for z in kraefte.zeilen], ["x", "y"])
        self.assertEqual([z[:2] for z in nachweistabelle(teil).zeilen],
                         [["Ersatzkraftverfahren", "Richtung x"],
                          ["Ersatzkraftverfahren", "Richtung y"]])


class TestVonFrueher(unittest.TestCase):
    """
    Eine Datei von früher, deren Gebäude Wände trug statt Kerne: sie öffnet
    sich, die Wände werden ein Kern, und das Haus rechnet wie zuvor.
    """

    def datei(self, *waende, schwingzeit="waende"):
        """
        Das Haus von Hand als Datei von früher: seine Analyse ist eine Wand
        5000 × 250 mm mit einem Stab und einer Stablinie, die Geschosse ohne
        Kern und ohne η_EI, dazu die Wände ``waende``, je ein dict -- die
        Kennung der Analyse steht dort als ``"wand"``.
        """
        p, h = haus(polygone=(RECHTECK,))
        a = p.querschnittsanalysen[0]
        stahl = p.stahl("B500B").kennung
        a.stab(100.0, 125.0, durchmesser=20.0, stahl=stahl)
        a.stablinie([50.0, 50.0], [4950.0, 50.0], art="teilung", durchmesser=12.0,
                    teilung=150.0, stahl=stahl)
        roh = p.als_dict()
        gebaeude = roh["erdbeben"][0]
        for g in gebaeude["geschosse"]:
            del g["kern"], g["eta_EI"]
        gebaeude["schwingzeit"] = schwingzeit
        gebaeude["waende"] = [{"name": f"Wand {i}", **w,
                               "analyse": a.kennung if w["analyse"] == "wand" else w["analyse"]}
                              for i, w in enumerate(waende, 1)]
        return roh

    @staticmethod
    def ecken(analyse, element):
        """Die Ecken eines Elements der Analyse in mm, wie gezeichnet."""
        orte = {k.kennung: (k.y, k.z) for k in analyse.knoten}
        return [orte[k] for k in element]

    def test_zwei_waende_werden_ein_kern_und_rechnen_wie_zuvor(self):
        """
        Zwei Wände in x, n = 2: im Kern zwei Teile, 1 m auseinander -- jede
        um ihren eigenen Schwerpunkt, wie das Haus von Hand.
        """
        p = Projekt.aus_dict(self.datei({"analyse": "wand", "lage": "0", "n": 2,
                                         "eta_EI": 0.5}))
        h = p.erdbeben[0]
        kern = p.querschnittsanalysen[-1]
        self.assertEqual((kern.name, len(p.querschnittsanalysen)), ("Kern Haus", 2))
        self.assertEqual(h.schwingzeit.value, "kern")
        self.assertEqual({(g.kern, g.eta_EI) for g in h.geschosse}, {(kern.kennung, 0.5)})
        self.assertEqual([self.ecken(kern, f.knoten)[0] for f in kern.flaechen],
                         [(0.0, 0.0), (6000.0, 0.0)])
        self.assertEqual((len(kern.staebe), len(kern.stablinien)), (2, 2))
        _, befund, _ = rechnen(p, h)
        x, _ = befund.richtungen
        self.assertAlmostEqual(x.T1, 0.4035, places=4)
        self.assertAlmostEqual(x.F_d / 1e3, 2970.5, delta=0.1)
        self.assertEqual([round(t.anteil, 9) for t in x.teile], [0.5, 0.5])

    def test_eine_gedrehte_wand_liegt_in_y(self):
        """In 90° gedreht: die Wand steht in y, ihr Stab und ihre Linie mit ihr."""
        p = Projekt.aus_dict(self.datei({"analyse": "wand", "lage": "90", "n": 1,
                                         "eta_EI": 0.4}))
        kern = p.querschnittsanalysen[-1]
        flaeche, = kern.flaechen
        self.assertEqual(self.ecken(kern, flaeche.knoten),
                         [(250.0, 0.0), (250.0, 5000.0), (0.0, 5000.0), (0.0, 0.0)])
        self.assertEqual(self.ecken(kern, [kern.staebe[0].knoten]), [(125.0, 100.0)])
        linie, = kern.stablinien
        self.assertEqual(self.ecken(kern, [linie.von, linie.bis]),
                         [(200.0, 50.0), (200.0, 4950.0)])
        self.assertEqual((linie.durchmesser, linie.teilung), (12.0, 150.0))
        self.assertEqual({g.eta_EI for g in p.erdbeben[0].geschosse}, {0.4})

    def test_waende_ohne_analyse_fallen_weg(self):
        """Sie trugen nichts bei: das Gebäude hat danach keinen Kern und sagt es."""
        p = Projekt.aus_dict(self.datei({"analyse": "", "lage": "0", "n": 1, "eta_EI": 0.5}))
        h = p.erdbeben[0]
        self.assertEqual(len(p.querschnittsanalysen), 1)
        self.assertEqual({g.kern for g in h.geschosse}, {""})
        self.assertIn("noch kein Kern", warum_nicht(p, h))

    def test_von_hand_bleibt_von_hand(self):
        p = Projekt.aus_dict(self.datei({"analyse": "wand", "lage": "0", "n": 1,
                                         "eta_EI": 0.5}, schwingzeit="hand"))
        self.assertEqual(p.erdbeben[0].schwingzeit.value, "hand")

    def test_was_nicht_ohne_rueckfrage_geht_meldet_sich(self):
        """Verschiedene η_EI oder eine Analyse, die es nicht gibt: die Datei meldet sich."""
        for waende in ([{"analyse": "wand", "lage": "0", "n": 1, "eta_EI": 0.5},
                        {"analyse": "wand", "lage": "90", "n": 1, "eta_EI": 0.4}],
                       [{"analyse": "a99", "lage": "0", "n": 1, "eta_EI": 0.5}]):
            with self.subTest(waende=waende), self.assertRaisesRegex(
                    ProjektFehler, "Erdbeben 'Haus': ein Feld 'waende' gibt es nicht"):
                Projekt.aus_dict(self.datei(*waende))

    def test_eine_neue_datei_bleibt_wie_sie_ist(self):
        p, _ = haus()
        self.assertEqual(Projekt.aus_dict(p.als_dict()).als_dict(), p.als_dict())


if __name__ == "__main__":
    unittest.main()
