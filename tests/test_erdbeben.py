"""
Das Ersatzkraftverfahren nach SIA 261:2020, 16.5.2 (opencivil.erdbeben.ersatzkraft).

Ein Haus von Hand nachgerechnet -- vier Geschosse auf zwei Wänden: die
Auslenkung des Dachs, T_1 (40), S_d (33), F_d (41), die Kräfte je Geschoss
(42), Querkraft und Moment unter jedem Geschoss, das Kippmoment, die Anteile
der Wände und dasselbe mit q = 1.0
(16.5.1.9). Dann, wann das Verfahren gilt (16.5.2.1), T_1 von Hand, was einem
Gebäude fehlt, die Prüfungen der Eingabe und was die Oberfläche sieht.
"""

import json
import math
import unittest

from opencivil.bericht.zusammenfassung import angaben, nachweistabelle, zusammenfassen
from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.erdbeben.ersatzkraft import (
    NICHT_GERECHNET, NICHT_ZULAESSIG, REGELMAESSIGKEIT, Wandlage, duktile_waende, momente,
    querkraefte,
)
from opencivil.projekt import ErdbebenEintrag, Projekt, ProjektFehler, QuerschnittsanalyseEintrag
from opencivil.web import dienst
from opencivil.web.api import katalog
from tests.unfertig import meldung

#: Die Wand des Hauses in m: lang in y ihrer Analyse, dünn in z.
LAENGE, DICKE = 5.0, 0.25
RECHTECK = ((0, 0), (5000, 0), (5000, 250), (0, 250))


def analyse(p, name, ecken=RECHTECK, beton=None):
    """Eine Querschnittsanalyse aus einem Polygon -- aus dem ersten Beton, wo keiner steht."""
    a = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name=name)
    a.polygon([list(e) for e in ecken],
              material=beton or next(m.kennung for m in p.materialien if m.art == "beton"))
    p.querschnittsanalysen.append(a)
    return a


def haus(**felder):
    """
    Das Haus von Hand: Zone Z2, Baugrund C, BWK I, q = 1.5 und C25/30. Drei
    Geschosse mit G_k = 3000 kN und Q_k = 1000 kN bei ψ₂ = 0.3, das Dach mit
    2500 kN, je 3 m hoch -- auf zwei gleichen Wänden in x, η_EI = 0.5.
    """
    p = Projekt(name="Probe")
    p.beton("C25/30")
    a = analyse(p, "Wand 5000 × 250")
    h = p.gebaeude("Haus", **{"zone": "Z2", **felder})
    for i in range(1, 4):
        h.geschoss(f"{i}. OG", h=3.0, G_k=3000.0, Q_k=1000.0)
    h.geschoss("Dach", h=3.0, G_k=2500.0)
    h.wand("W1", a.kennung)
    h.wand("W2", a.kennung)
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


class TestVonHand(unittest.TestCase):
    """Das Haus, Schritt für Schritt aus der Geometrie -- nicht aus Zwischenwerten der Rechnung."""

    @classmethod
    def setUpClass(cls):
        p, h = haus()
        cls.e, cls.befund, cls.urteile = rechnen(p, h)
        flaeche = cls.e.aufbau.querschnittsanalysen[h.waende[0].analyse].flaechen[0]
        cls.E_cm = cls.e.wert(flaeche.stoff.id_von("E_cm")).groesse.si
        cls.x, cls.y = cls.befund.richtungen
        cls.z = [3.0, 6.0, 9.0, 12.0]
        cls.W = [3300e3, 3300e3, 3300e3, 2500e3]

    def auslenkung(self, I):
        """Der Kopf des Kragarms unter den Gewichten, waagrecht auf ihrer Höhe -- in m."""
        EI = 2 * 0.5 * self.E_cm * I
        return sum(W * z * z * (3 * 12.0 - z) for W, z in zip(self.W, self.z)) / (6 * EI)

    def test_gewichte_und_hoehen(self):
        """W = G_k + ψ₂·Q_k, auf der Höhe der Decke über der Einspannung."""
        self.assertEqual(self.befund.z, tuple(self.z))
        for W, soll in zip(self.befund.W, self.W):
            self.assertAlmostEqual(W, soll, places=6)

    def test_schwingzeit_aus_der_auslenkung(self):
        """(40): T_1 = 2·√u, u in m -- in x biegt die Kraft die Wände um z, mit I_z."""
        u = self.auslenkung(DICKE * LAENGE ** 3 / 12)
        self.assertAlmostEqual(self.x.u, u, delta=1e-9 * u)
        self.assertAlmostEqual(self.x.T1, 2 * math.sqrt(u), places=9)
        self.assertAlmostEqual(self.x.T1, 0.4035, places=4)

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

    def test_zwei_gleiche_waende_je_die_haelfte(self):
        for w in self.x.waende:
            with self.subTest(wand=w.name):
                self.assertAlmostEqual(w.EI, 0.5 * self.E_cm * DICKE * LAENGE ** 3 / 12,
                                       delta=1.0)
                self.assertAlmostEqual(w.anteil, 0.5, places=12)
                self.assertAlmostEqual(w.V, self.x.F_d / 2, delta=1e-6)
                self.assertAlmostEqual(w.M, self.x.M_0 / 2, delta=1e-3)

    def test_in_y_nur_die_schwache_achse(self):
        """
        In y biegt die Kraft die Wände um y: T_1 ist √(I_z/I_y) = 20-mal so
        lang, über T_D (34) -- und S_d bleibt am unteren Wert 0.1·γ_f·a_gd/g.
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


class TestWannDasVerfahrenGilt(unittest.TestCase):
    """16.5.2.1: Grund- und Aufriss regelmässig, T_1 ≤ 4·T_C in beiden Richtungen."""

    def mit_wand_in_y(self, **felder):
        p, h = haus(**felder)
        h.waende[1].lage = Wandlage.NEUNZIG
        return p, h

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

    def test_ohne_wand_die_kraefte_ohne_verteilung(self):
        """
        Zone Z3b, Baugrund E, BWK III: in x unter T_B (31), in y zwischen
        T_C und T_D (33) und über 4·T_C. Ohne Wand trägt keine einen Anteil.
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
        self.assertEqual((x.waende, x.EI), ((), 0.0))
        self.assertTrue(urteile["Richtung x"].erfuellt)
        self.assertFalse(urteile["Richtung y"].erfuellt)

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
    """Es wird gebaut, aber ohne Nachweis -- grau, mit allem, was fehlt, und jeder Wand dazu."""

    def gebaeude(self, *analysen):
        p = Projekt(name="Probe")
        p.beton("C25/30")
        h = p.gebaeude("Haus")
        h.geschoss("EG", h=3.0, G_k=1000.0)
        for i, kennung in enumerate(analysen, start=1):
            h.wand(f"W{i}", kennung)
        return p, h

    def test_ohne_geschoss(self):
        p = Projekt(name="Probe")
        p.gebaeude("Leer")
        aufbau = p.aufbauen()
        self.assertEqual(aufbau.feld("erdbeben"), {})
        self.assertIn(("erdbeben.h1", "Erdbeben 'Leer': noch kein Geschoss – unter «Geschosse» "
                                      "eines anlegen → kein Nachweis."), aufbau.warnungen)

    def test_ohne_wand_braucht_es_T1_von_hand(self):
        p, h = self.gebaeude()
        self.assertEqual(warum_nicht(p, h), "noch keine Wand – unter «Wände» eine anlegen, "
                                            "oder T₁ von Hand angeben")

    def test_gleicher_grund_einmal_mit_jeder_wand(self):
        p, h = self.gebaeude("", "")
        self.assertEqual(warum_nicht(p, h), "noch keine Querschnittsanalyse gewählt («W1», «W2»)")

    def test_eine_wand_haelt_das_gebaeude_an(self):
        """Ohne sie stimmten Schwingzeit und Verteilung nicht -- und sähen doch richtig aus."""
        p, h = self.gebaeude()
        h.wand("W1", analyse(p, "Wand").kennung)
        h.wand("W2", "")
        self.assertEqual(warum_nicht(p, h), "noch keine Querschnittsanalyse gewählt («W2»)")

    def test_eine_geloeschte_analyse(self):
        p, h = self.gebaeude("a9")
        self.assertEqual(warum_nicht(p, h), "die gewählte Querschnittsanalyse gibt es nicht "
                                            "mehr – eine andere wählen («W1»)")

    def test_eine_analyse_die_nicht_rechnet(self):
        p, h = self.gebaeude()
        leer = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name="Leer")
        p.querschnittsanalysen.append(leer)
        h.wand("W1", leer.kennung)
        self.assertEqual(warum_nicht(p, h), "die Querschnittsanalyse «Leer» rechnet nicht "
                                            "(noch nichts gezeichnet) («W1»)")

    def test_zwei_betone_geben_kein_E_cm(self):
        p, h = self.gebaeude()
        zweiter = p.beton("C30/37")
        a = analyse(p, "Gemischt")
        a.polygon([[0, 250], [5000, 250], [5000, 500], [0, 500]], material=zweiter.kennung)
        h.wand("W1", a.kennung)
        self.assertEqual(warum_nicht(p, h), "die Querschnittsanalyse «Gemischt» hat mehr als "
                                            "einen Beton («C25/30», «C30/37») – für E_cm "
                                            "braucht es genau einen («W1»)")

    def test_keine_hauptachsen_sagt_es_einmal(self):
        """Ein Winkel: |I_yz| weit über 5 % -- derselbe Hinweis wie im Raum, je Analyse einmal."""
        p, h = self.gebaeude()
        winkel = analyse(p, "Winkel", ((0, 0), (4000, 0), (4000, 250), (250, 250),
                                       (250, 2000), (0, 2000)))
        h.wand("W1", winkel.kennung)
        h.wand("W2", winkel.kennung, lage=Wandlage.NEUNZIG)
        _, befund, _ = rechnen(p, h)
        self.assertEqual(len(befund.hinweise), 1)
        self.assertTrue(befund.hinweise[0].startswith(
            "Querschnittsanalyse «Winkel»: y und z sind keine Hauptachsen"))


class TestDuktileWaende(unittest.TestCase):
    """
    Über q = 2.0 ist das Tragwerk duktil bemessen (SIA 262:2025, Tabellen 14
    und 15): dann gelten für schlanke Wände eigene Bemessungswerte (4.3.9.4),
    die diese Rechnung nicht kennt. Sie sagt es grau, statt Kräfte je Wand zu
    zeigen, die nach Bemessung aussehen.
    """

    def test_nur_wo_q_ueber_zwei(self):
        for felder, richtungen in (({}, ()), ({"q_x": 2.0}, ()), ({"q_x": 3.0}, ("x",)),
                                   ({"q_x": 3.0, "q_y": 4.0}, ("x", "y"))):
            with self.subTest(**felder):
                p, h = haus(**felder)
                self.assertEqual(rechnen(p, h)[1].hinweise,
                                 (duktile_waende(richtungen),) if richtungen else ())

    def test_ohne_wand_kein_satz_ueber_waende(self):
        p = Projekt(name="Probe")
        h = p.gebaeude("Ohne Wand", schwingzeit="hand", q_x=3.0)
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

    def test_neu_mit_einem_geschoss_und_einer_wand(self):
        """Wie die Oberfläche es anlegt: noch ohne Last und ohne Querschnitt."""
        neu = ErdbebenEintrag.neu(kennung="h1", name="G")
        self.assertEqual([(g.name, g.h, g.G_k) for g in neu.geschosse], [("Geschoss 1", 3.0, 0.0)])
        self.assertEqual([(w.name, w.analyse) for w in neu.waende], [("Wand 1", "")])

    def test_unmoegliche_zahlen_vor_dem_rechnen(self):
        """Am Ort, mit dem Namen der Maske -- «Wand 'W1'», nicht das Feld der Datei."""
        for felder, geschoss, wand, satz in (
                ({"q_x": 0.5}, {}, {}, "Erdbeben 'Haus': Verhaltensbeiwert q_x muss mindestens "
                                       "1 sein"),
                ({}, {"h": 0.0}, {}, "Geschoss 'EG': Höhe h muss grösser als null sein"),
                ({}, {"G_k": -1.0}, {}, "Geschoss 'EG': Ständige Last G_k kann nicht negativ sein"),
                ({}, {"psi_2": 1.5}, {}, "ψ₂ muss mindestens null und höchstens 1 sein"),
                ({}, {}, {"eta_EI": 0.0}, "Wand 'W1': η_EI muss grösser als null und "
                                          "höchstens 1 sein"),
                ({}, {}, {"n": 0}, "Wand 'W1': Anzahl n muss mindestens 1 sein")):
            with self.subTest(satz=satz):
                p = Projekt(name="Probe")
                p.beton("C25/30")
                h = p.gebaeude("Haus", **felder)
                h.geschoss("EG", **{"h": 3.0, "G_k": 1000.0, **geschoss})
                h.wand("W1", analyse(p, "Wand").kennung, **wand)
                self.assertIn(satz, meldung(p))

    def test_eine_zone_die_es_nicht_gibt(self):
        with self.assertRaises(ProjektFehler) as fehler:
            Projekt(name="Probe").gebaeude("Haus", zone="Z4")
        self.assertIn("'Z4' gibt es als 'zone' nicht", str(fehler.exception))

    def test_datei_hin_und_zurueck(self):
        p, h = haus(schwingzeit="hand", T1_x=0.8, grundriss_regelmaessig=False)
        h.waende[1].lage = Wandlage.NEUNZIG
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.als_dict(), p.als_dict())
        self.assertIs(wieder.erdbeben[0].waende[1].lage, Wandlage.NEUNZIG)

    def test_die_analysen_der_waende_sind_bezuege(self):
        p, h = haus()
        self.assertEqual(h.bezuege(), [h.waende[0].analyse])


class TestZwischenspeicher(unittest.TestCase):
    """
    Ändert sich nur die Analyse einer Wand, rechnet das Gebäude neu. Bis
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
        self.assertEqual([lage["beschriftung"] for lage in e["lagen"]], ["0°", "90°"])
        self.assertEqual([s["wert"] for s in e["schwingzeiten"]], ["waende", "hand"])
        self.assertEqual([r["feld"] for r in e["regelmaessigkeit"]],
                         ["grundriss_regelmaessig", "aufriss_regelmaessig"])
        self.assertEqual(k["neu"]["erdbeben"]["geschosse"][0]["name"], "Geschoss 1")
        self.assertEqual(k["felder"]["geschoss"]["G_k"]["einheit"], "kN")
        self.assertEqual([f["feld"] for f in k["vorgaben"]["geschoss"][0]["felder"][""]],
                         ["h", "G_k", "Q_k", "psi_2"])

    def test_ansicht_des_beispiels(self):
        self.assertEqual(self.antwort.status, 200)
        d = self.antwort.daten["zeichendaten"][self.haus.kennung]
        self.assertEqual(len(d["geschosse"]), 4)
        self.assertEqual([r["richtung"] for r in d["richtungen"]], ["x", "y"])
        x = d["richtungen"][0]
        self.assertAlmostEqual(sum(x["kraefte"]), x["F_d"], places=6)
        self.assertAlmostEqual(x["querkraefte"][0], x["F_d"], places=6)
        self.assertAlmostEqual(x["momente"][0], x["M_0"], places=6)
        self.assertEqual(len(x["momente"]), 4)
        self.assertEqual([w["name"] for w in x["waende"]], ["Wände in x", "Wände in y"])
        self.assertEqual(d["waende"], [None, None])
        self.assertTrue(d["zulaessig"])
        self.assertEqual(d["meldungen"], [{"text": NICHT_GERECHNET, "fehler": False}])
        zeilen = ["".join(z.get("text") or z["mathe"] for z in zeile) for zeile in d["legende"]]
        self.assertTrue(zeilen[0].startswith("Richtung x: T_{1,x} = 0.356"))
        self.assertIn("– erfüllt", zeilen[0])
        self.assertIn("mit q = 1.0 für Abheben und Kippen (16.5.1.9)", zeilen[1])

    def test_die_waende_im_grundriss(self):
        """
        Um ihren Schwerpunkt, in mm: die Wand in x liegt wie gezeichnet, die
        in y um 90° gedreht -- dieselbe Analyse, lang in y des Gebäudes.
        """
        d = self.antwort.daten["zeichendaten"][self.haus.kennung]
        in_x, in_y = d["grundrisse"]

        def ausdehnung(wand):
            punkte = [p for poly in wand["polygone"] for p in poly["punkte"]]
            return tuple(round(max(p[k] for p in punkte) - min(p[k] for p in punkte))
                         for k in (0, 1))

        self.assertEqual((in_x["nummer"], in_x["lage"], in_y["lage"]), (1, "0°", "90°"))
        self.assertEqual(ausdehnung(in_y), tuple(reversed(ausdehnung(in_x))))
        self.assertGreater(*ausdehnung(in_x))
        self.assertEqual(in_x["polygone"][0]["material"], "beton")
        self.assertEqual(Wandlage.NEUNZIG.im_grundriss(1.0, 0.0), (0.0, 1.0))
        zeilen = ["".join(z.get("text") or z["mathe"] for z in zeile)
                  for zeile in d["verlaufslegende"]]
        self.assertIn("1 «Wände in x» (2×, 0°), 2 «Wände in y» (2×, 90°).", zeilen[0])
        self.assertTrue(zeilen[1].endswith("M am Fuss ist M_0."))

    def test_eine_wand_ohne_analyse_sagt_es_an_ihr(self):
        p = Projekt(name="Probe")
        h = p.gebaeude("Haus")
        h.geschoss("EG", h=3.0, G_k=1000.0)
        h.wand("W1", "")
        d = self.ansicht(p, h)
        self.assertEqual(d["waende"], [{"analyse": "", "fehler": False,
                                        "grund": "noch keine Querschnittsanalyse gewählt"}])
        self.assertEqual(d["meldungen"], [{"text": "«W1»: noch keine Querschnittsanalyse gewählt.",
                                           "fehler": False}])
        self.assertEqual(d["richtungen"], [])

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


if __name__ == "__main__":
    unittest.main()
