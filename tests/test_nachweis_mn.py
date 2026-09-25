"""
Tests fuer Plattenquerschnitt und den M-N-Nachweis.

Die Eckwerte der Resistenzlinie lassen sich von Hand nachrechnen und werden
darum genau geprueft; fuer den Biegewiderstand wird gegen die Handrechnung mit
Spannungsblock verglichen, die naturgemaess leicht abweicht.
"""

import math
import unittest

from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, MM, MM2, N_PRO_MM2, Groesse,
)
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.material.beton import beton
from opencivil.material.betonstahl import betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.nachweis.linie import MOMENT, schnitte
from opencivil.querschnitt.platte import (
    Bewehrungslage, Bewehrungsposten, Plattenquerschnitt, Postenart, Richtung,
)
from opencivil.querschnitt.werkstoffgesetz import Betongesetz, Dehnungsebene, Stahlgesetz


def posten(phi: float, s: float = 150.0) -> Bewehrungsposten:
    return Bewehrungsposten(durchmesser=Groesse(phi, MM), abstand=Groesse(s, MM))


def leer() -> Bewehrungsposten:
    return Bewehrungsposten()


def lage(nummer: int, richtung: Richtung, phi: float = 0.0, zulage: float = 0.0,
         s: float = 150.0) -> Bewehrungslage:
    return Bewehrungslage(
        nummer=nummer, richtung=richtung, stahl=betonstahl("B500B"),
        grund=posten(phi, s) if phi else leer(),
        zulage=posten(zulage, s) if zulage else leer(),
    )


def platte(lagen, **abweichungen) -> Plattenquerschnitt:
    """h = 300 mm, b = 1 m, C30/37."""
    vorgaben = dict(
        name="Decke", h=Groesse(300, MM), b=Groesse(1000, MM), beton=beton("C30/37"),
        lagen=lagen, ueberdeckung_unten=Groesse(30, MM), ueberdeckung_oben=Groesse(30, MM),
    )
    vorgaben.update(abweichungen)
    return Plattenquerschnitt(**vorgaben)


def einfache_platte() -> Plattenquerschnitt:
    """Nur die 1. Lage bewehrt: ⌀18@150 in x-Richtung."""
    return platte([
        lage(1, Richtung.X, phi=18.0),
        lage(2, Richtung.Y),
        lage(3, Richtung.Y),
        lage(4, Richtung.X),
    ])


def symmetrische_platte() -> Plattenquerschnitt:
    """1. und 4. Lage gleich, beide x -- ergibt eine punktsymmetrische Linie."""
    return platte([
        lage(1, Richtung.X, phi=16.0),
        lage(2, Richtung.Y),
        lage(3, Richtung.Y),
        lage(4, Richtung.X, phi=16.0),
    ])


# ---------------------------------------------------------------------------


class TestWerkstoffgesetz(unittest.TestCase):
    def setUp(self):
        self.beton = Betongesetz(f_cd=20e6, eps_c1d=0.002, eps_c2d=0.0035, k_sigma=4.2)
        self.stahl = Stahlgesetz(E_s=200e9, f_yd=434.8e6, f_yd_druck=434.8e6, eps_ud=0.045)

    def test_beton_nimmt_keinen_zug(self):
        self.assertEqual(self.beton.spannung(0.001), 0.0)

    def test_beton_erreicht_f_cd_im_plateau(self):
        self.assertAlmostEqual(self.beton.spannung(-0.003), -20e6)
        self.assertAlmostEqual(self.beton.spannung(-0.0035), -20e6)

    def test_beton_parabelast_steigt_monoton(self):
        werte = [self.beton.spannung(-e / 10000) for e in range(0, 21)]
        for a, b in zip(werte, werte[1:]):
            self.assertLessEqual(b, a + 1e-6)

    def test_beton_bei_null(self):
        self.assertAlmostEqual(self.beton.spannung(0.0), 0.0)

    def test_stahl_elastisch(self):
        self.assertAlmostEqual(self.stahl.spannung(0.001), 200e9 * 0.001)

    def test_stahl_fliesst(self):
        self.assertAlmostEqual(self.stahl.spannung(0.01), 434.8e6)
        self.assertAlmostEqual(self.stahl.spannung(-0.01), -434.8e6)


class TestDehnungsebene(unittest.TestCase):
    def test_durch_zwei_punkte(self):
        ebene = Dehnungsebene.durch_zwei_punkte(0.0045, 0.26, -0.0035, 0.0, h=0.3)
        self.assertAlmostEqual(ebene.bei(0.0), -0.0035)
        self.assertAlmostEqual(ebene.bei(0.26), 0.0045)

    def test_nulllinie(self):
        ebene = Dehnungsebene(eps_oben=-0.0035, eps_unten=0.0035, h=0.3)
        self.assertAlmostEqual(ebene.nulllinie, 0.15)

    def test_gleichmaessige_dehnung_hat_keine_nulllinie(self):
        ebene = Dehnungsebene(eps_oben=0.002, eps_unten=0.002, h=0.3)
        self.assertEqual(ebene.nulllinie, float("inf"))


class TestQuerschnitt(unittest.TestCase):
    def setUp(self):
        self.platte = einfache_platte()
        self.werk = Rechenwerk()
        self.platte.ins_rechenwerk(self.werk)

    def test_bewehrungsflaeche(self):
        wid = self.platte.id_von("lage.1g.a_s")
        a_s = self.werk.loese(wid).groesse(wid)
        erwartet = math.pi * 18**2 / 4 * (1000 / 150)
        self.assertAlmostEqual(a_s.in_einheit(MM2), erwartet, places=3)

    def test_statische_hoehe(self):
        wid = self.platte.id_von("lage.1g.z")
        z = self.werk.loese(wid).groesse(wid)
        # z ab Oberkante: h - (c + phi/2) = 300 - (30 + 9)
        self.assertAlmostEqual(z.in_einheit(MM), 261.0)

    def test_obere_lage_zaehlt_von_oben(self):
        platte = symmetrische_platte()
        werk = Rechenwerk()
        platte.ins_rechenwerk(werk)
        loesung = werk.loese(platte.id_von("lage.4g.z"), platte.id_von("lage.1g.z"))
        self.assertAlmostEqual(loesung.groesse(platte.id_von("lage.4g.z")).in_einheit(MM), 38.0)
        self.assertAlmostEqual(loesung.groesse(platte.id_von("lage.1g.z")).in_einheit(MM), 262.0)

    def test_lagenstapelung(self):
        """Die 2. Lage liegt um den grössten Durchmesser der 1. weiter innen."""
        qs = platte([
            lage(1, Richtung.X, phi=20.0),
            lage(2, Richtung.Y, phi=16.0),
            lage(3, Richtung.X),
            lage(4, Richtung.Y),
        ])
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        loesung = werk.loese(qs.id_von("lage.1g.z"), qs.id_von("lage.2g.z"))
        # 1. Lage: 30 + 20/2 = 40 -> z = 260
        self.assertAlmostEqual(loesung.groesse(qs.id_von("lage.1g.z")).in_einheit(MM), 260.0)
        # 2. Lage: 30 + 20 + 16/2 = 58 -> z = 242
        self.assertAlmostEqual(loesung.groesse(qs.id_von("lage.2g.z")).in_einheit(MM), 242.0)

    def _lage_mit_zulage(self, unguenstig: bool):
        """1. Lage: Grund ⌀20 und Zulage ⌀12, Überdeckung 30 mm."""
        lagen = [
            lage(1, Richtung.X, phi=20.0, zulage=12.0),
            lage(2, Richtung.Y), lage(3, Richtung.X), lage(4, Richtung.Y),
        ]
        lagen[0].unguenstig = unguenstig
        qs = platte(lagen)
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        loesung = werk.loese(qs.id_von("lage.1g.z"), qs.id_von("lage.1z.z"))
        return (loesung.groesse(qs.id_von("lage.1g.z")).in_einheit(MM),
                loesung.groesse(qs.id_von("lage.1z.z")).in_einheit(MM))

    def test_guenstige_lage_laesst_die_aeusseren_kanten_fluchten(self):
        """
        Beide berühren dieselbe Hüllebene, je um ihren eigenen Halbmesser
        eingerückt. Die Zulage liegt damit weiter aussen und hat mehr Hebelarm.
        """
        grund, zulage = self._lage_mit_zulage(unguenstig=False)
        self.assertAlmostEqual(grund, 300 - (30 + 10))
        self.assertAlmostEqual(zulage, 300 - (30 + 6))

    def test_unguenstige_lage_laesst_die_inneren_kanten_fluchten(self):
        """
        Der dünnere Stab rückt zur Plattenmitte, bis seine innere Kante mit
        der des dickeren fluchtet. Das ist die Vorgabe: auf der Baustelle
        lässt sich nicht steuern, welche Kante fluchtet.
        """
        grund, zulage = self._lage_mit_zulage(unguenstig=True)
        self.assertAlmostEqual(grund, 300 - (30 + 10))
        # Zulage: Rand = 30 + 20 - 6 = 44  ->  d = 256
        self.assertAlmostEqual(zulage, 300 - (30 + 20 - 6))
        # Innere Kanten auf gleicher Höhe -- das ist die Aussage.
        self.assertAlmostEqual(grund - 20 / 2, zulage - 12 / 2)

    def test_unguenstig_ist_die_vorgabe(self):
        self.assertTrue(lage(1, Richtung.X, phi=20.0, zulage=12.0).unguenstig)

    def test_zulage_zaehlt_zur_flaeche(self):
        qs = platte([
            lage(1, Richtung.X, phi=18.0, zulage=12.0),
            lage(2, Richtung.Y), lage(3, Richtung.X), lage(4, Richtung.Y),
        ])
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        loesung = werk.loese(qs.id_von("lage.1g.a_s"), qs.id_von("lage.1z.a_s"))
        self.assertAlmostEqual(
            loesung.groesse(qs.id_von("lage.1z.a_s")).in_einheit(MM2),
            math.pi * 12**2 / 4 * (1000 / 150), places=3)

    def test_stabzahl_statt_abstand(self):
        qs = platte([
            Bewehrungslage(1, Richtung.X, betonstahl("B500B"),
                           grund=Bewehrungsposten(Groesse(18, MM), anzahl=7)),
            lage(2, Richtung.Y), lage(3, Richtung.X), lage(4, Richtung.Y),
        ])
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        wid = qs.id_von("lage.1g.a_s")
        self.assertAlmostEqual(
            werk.loese(wid).groesse(wid).in_einheit(MM2), math.pi * 18**2 / 4 * 7, places=3)

    def test_ohne_bewehrung_verboten(self):
        with self.assertRaises(ValueError):
            platte([lage(n, Richtung.X if n in (1, 4) else Richtung.Y) for n in range(1, 5)])

    def test_gekoppelte_richtungen_erzwungen(self):
        """Die 1. und die 2. Lage müssen entgegengesetzte Richtungen haben."""
        with self.assertRaises(ValueError) as ctx:
            platte([
                lage(1, Richtung.X, phi=16.0),
                lage(2, Richtung.X, phi=16.0),   # falsch: gleiche Richtung
                lage(3, Richtung.Y), lage(4, Richtung.X),
            ])
        self.assertIn("entgegengesetzte", str(ctx.exception))

    def test_falsche_lagenzahl_verboten(self):
        with self.assertRaises(ValueError):
            platte([lage(1, Richtung.X, phi=16.0), lage(2, Richtung.Y)])

    def test_richtungen_trennen_die_bewehrung(self):
        qs = platte([
            lage(1, Richtung.X, phi=18.0),
            lage(2, Richtung.Y, phi=12.0),
            lage(3, Richtung.Y), lage(4, Richtung.X),
        ])
        self.assertEqual(len(qs.posten_in_richtung(Richtung.X)), 1)
        self.assertEqual(len(qs.posten_in_richtung(Richtung.Y)), 1)
        self.assertEqual(qs.richtungen_mit_bewehrung, [Richtung.X, Richtung.Y])

    def test_querbewehrung_traegt_nicht_zum_moment_bei(self):
        """
        Eine Lage in y-Richtung darf den Widerstand um x nicht erhöhen -- sonst
        wäre die Bemessung auf der unsicheren Seite.
        """
        def m_rd(qs) -> float:
            werk = Rechenwerk()
            qs.ins_rechenwerk(werk)
            nachweis = BiegungNormalkraft(
                qs, [Schnittgroessen("F", M_Ed=Groesse(1, KNM))], Richtung.X)
            werk.registriere(nachweis)
            werk.loese(nachweis.d_eckwerte["M_Rd_max"].id)
            return max(schnitte(nachweis.linie, MOMENT, 0.0))

        ohne = m_rd(platte([
            lage(1, Richtung.X, phi=18.0), lage(2, Richtung.Y),
            lage(3, Richtung.Y), lage(4, Richtung.X)]))
        mit_quer = m_rd(platte([
            lage(1, Richtung.X, phi=18.0), lage(2, Richtung.Y, phi=20.0),
            lage(3, Richtung.Y), lage(4, Richtung.X)]))
        self.assertAlmostEqual(ohne, mit_quer, places=6)

    def test_lagenaufbau_wird_protokolliert(self):
        from opencivil.core.protokoll import TabellenBlock

        loesung = self.werk.loese(self.platte.id_von("lage.1g.z"))
        tabellen = [
            b for b in loesung.protokoll.alle_bloecke() if isinstance(b, TabellenBlock)
        ]
        self.assertTrue(any("Randabstände" in t.titel for t in tabellen))


# ---------------------------------------------------------------------------


class TestResistenzlinie(unittest.TestCase):
    def setUp(self):
        self.platte = einfache_platte()
        self.werk = Rechenwerk()
        self.platte.ins_rechenwerk(self.werk)
        self.nachweis = BiegungNormalkraft(
            self.platte,
            [Schnittgroessen("Feld", M_Ed=Groesse(100, KNM))],
            Richtung.X,
        )
        self.werk.registriere(self.nachweis)
        self.loesung = self.werk.loese(
            self.nachweis.d_eckwerte["M_Rd_max"].id,
            self.nachweis.d_ausnutzung["Feld"].id,
        )

    def eck(self, name: str) -> Groesse:
        return self.loesung.groesse(self.nachweis.d_eckwerte[name].id)

    def test_linie_ist_geschlossen(self):
        self.assertGreater(len(self.nachweis.linie), 100)

    def test_linie_schneidet_sich_nicht_selbst(self):
        """
        Eine Resistenzlinie ist der Rand eines zusammenhängenden Bereichs. Kreuzt
        sie sich, stimmt weder der Punkt-in-Linie-Test noch die Schnittsuche --
        und beides trägt jedes Urteil dieses Nachweises.
        """
        punkte = [(p.M, p.N) for p in self.nachweis.linie]
        anzahl = len(punkte)

        def richtung(p, q, r):
            return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])

        def kreuzt(a, b, c, d):
            return ((richtung(a, b, c) > 0) != (richtung(a, b, d) > 0)
                    and (richtung(c, d, a) > 0) != (richtung(c, d, b) > 0))

        for i in range(anzahl):
            for j in range(i + 2, anzahl):
                if i == 0 and j == anzahl - 1:
                    continue  # gemeinsamer Ringschluss
                with self.subTest(i=i, j=j):
                    self.assertFalse(
                        kreuzt(punkte[i], punkte[(i + 1) % anzahl],
                               punkte[j], punkte[(j + 1) % anzahl]),
                        f"Segment {i} ({self.nachweis.linie[i].abschnitt}) kreuzt "
                        f"{j} ({self.nachweis.linie[j].abschnitt})")

    def test_keine_faser_ueberschreitet_die_bruchdehnung(self):
        for p in self.nachweis.linie:
            self.assertGreaterEqual(min(p.eps_oben, p.eps_unten), -0.0035 - 1e-12)

    def test_keine_doppelten_punkte(self):
        linie = self.nachweis.linie
        for i in range(len(linie)):
            a, b = linie[i], linie[(i + 1) % len(linie)]
            with self.subTest(i=i):
                self.assertGreater(abs(a.N - b.N) + abs(a.M - b.M), 0.0)

    def test_groesste_zugkraft_ist_summe_der_fliesskraefte(self):
        a_s = math.pi * 18**2 / 4 * (1000 / 150) * 1e-6  # m^2
        f_yd = 500 / 1.15 * 1e6
        self.assertAlmostEqual(
            self.eck("N_Rd_zug").in_einheit(KN), a_s * f_yd / 1e3, delta=1.0
        )

    def test_gleichmaessiger_druck(self):
        """
        Bei reinem Druck ist eps_c1d massgebend, nicht eps_c2d -- und bei
        eps_c1d = 2.0 ‰ fliesst der Stahl noch nicht (eps_yd = 2.17 ‰).
        Anzusetzen ist also E_s * eps_c1d = 400 N/mm^2, nicht f_yd = 435.
        """
        a_s = math.pi * 18**2 / 4 * (1000 / 150) * 1e-6
        sigma_s = 200e9 * 0.002
        erwartet = -(20e6 * (1.0 * 0.3 - a_s) + a_s * sigma_s) / 1e3

        gleichmaessig = [
            p for p in self.nachweis.linie if abs(p.eps_oben - p.eps_unten) < 1e-9
        ]
        druckpunkt = min(gleichmaessig, key=lambda p: p.N)
        self.assertAlmostEqual(druckpunkt.eps_oben * 1000, -2.0, places=6)
        self.assertAlmostEqual(druckpunkt.N / 1e3, erwartet, delta=0.5)

    def test_groesste_druckkraft_liegt_leicht_neben_dem_reinen_druck(self):
        """
        Der Grösstwert der Druckkraft tritt nicht bei gleichmässiger Stauchung
        auf: eine leicht geneigte Ebene staucht die untere Bewehrung über
        eps_yd hinaus, sodass sie mit f_yd statt mit E_s*eps mitträgt.
        """
        extrem = min(self.nachweis.linie, key=lambda p: p.N)
        gleichmaessig = min(
            (p for p in self.nachweis.linie if abs(p.eps_oben - p.eps_unten) < 1e-9),
            key=lambda p: p.N)
        self.assertLess(extrem.N, gleichmaessig.N)
        self.assertGreater(extrem.N, gleichmaessig.N * 1.02)
        self.assertNotAlmostEqual(extrem.eps_oben, extrem.eps_unten, places=6)

    def test_biegewiderstand_bei_n_null_deckt_sich_mit_handrechnung(self):
        """
        Handrechnung mit Spannungsblock:

            a_s   = pi*18^2/4 * 1000/150      = 1696 mm^2
            F_s   = 1696 * 500/1.15           =  737 kN
            x_eff = 737e3 / (20 * 1000)       = 36.9 mm
            M_Rd  = 737 * (261 - 36.9/2)      ≈ 179 kNm
        """
        momente = schnitte(self.nachweis.linie, MOMENT, 0.0)
        m_rd = max(momente) / 1e3
        self.assertAlmostEqual(m_rd, 179.0, delta=8.0)

    def test_nur_untere_bewehrung_gibt_bei_n_null_kaum_negatives_moment(self):
        momente = schnitte(self.nachweis.linie, MOMENT, 0.0)
        self.assertLess(abs(min(momente)) / 1e3, 20.0)

    def test_groesstes_moment_liegt_beim_balancepunkt(self):
        """
        Der Höchstwert von M liegt nicht bei N = 0, sondern unter Druck:
        eine Normaldruckkraft vergrössert den Momentenwiderstand, bis die
        Druckzone zu gross wird. Das ist die charakteristische Bauchform des
        Interaktionsdiagramms.
        """
        bester = max(self.nachweis.linie, key=lambda punkt: punkt.M)
        self.assertLess(bester.N, 0.0)
        m_bei_null = max(schnitte(self.nachweis.linie, MOMENT, 0.0))
        self.assertGreater(bester.M, m_bei_null)

    def test_protokoll_zeigt_die_handrechnung(self):
        """
        Hergeleitet wird die Handrechnung, nicht die genaue Linie.

        Die genaue Linie entsteht aus hunderten Faserintegrationen; sie in die
        Mitschrift zu schreiben hiesse, Zeilen zu liefern, die niemand
        nachrechnen kann. Sie steht nur noch zum Vergleich im Diagramm.
        """
        from opencivil.core.protokoll import GleichungBlock, TabellenBlock

        bloecke = list(self.loesung.protokoll.alle_bloecke())
        titel = [b.titel for b in bloecke if isinstance(b, TabellenBlock)]
        self.assertIn("Zusammengefasste Bewehrung", titel)
        self.assertIn("Eckpunkte der Resistenzlinie aus Handrechnung", titel)

        # Die Herleitung der genauen Linie ist stillgelegt.
        self.assertNotIn("Stützstellen des Dehnungsfächers", titel)
        gleichungen = [b.latex for b in bloecke if isinstance(b, GleichungBlock)]
        self.assertFalse(any(r"\int_A" in g for g in gleichungen),
                         "die Faserintegration gehört nicht mehr in die Mitschrift")

    def test_protokoll_zeigt_die_formeln_der_eckpunkte(self):
        """Jeder Eckpunkt muss mit seiner Formel dastehen, nicht nur als Zahl."""
        from opencivil.core.protokoll import GleichungBlock

        titel = [b.titel for b in self.loesung.protokoll.alle_bloecke()
                 if isinstance(b, GleichungBlock)]
        for erwartet in (
            "Gleichmässiger Druck, ohne Bewehrung",
            "Beide Lagen fliessen auf Zug",
            "Druckzonenhöhe aus dem Kräftegleichgewicht",
            "Momentenwiderstand bei reiner Biegung",
        ):
            with self.subTest(titel=erwartet):
                self.assertIn(erwartet, titel)

    def test_protokoll_zeigt_die_interpolation(self):
        """
        Der Widerstand darf nicht vom Himmel fallen.

        Bei einer Normalkraft zwischen zwei Eckpunkten muss dastehen, zwischen
        welchen interpoliert wurde und mit welchem Anteil.
        """
        from opencivil.core.protokoll import GleichungBlock, TabellenBlock

        werk = Rechenwerk()
        platte = einfache_platte()
        platte.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(
            platte,
            [Schnittgroessen("Druck", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-200, KN))],
            Richtung.X,
        )
        werk.registriere(nachweis)
        loesung = werk.loese(nachweis.d_ausnutzung["Druck"].id)

        bloecke = list(loesung.protokoll.alle_bloecke())
        self.assertIn("Stützpunkte der Interpolation",
                      [b.titel for b in bloecke if isinstance(b, TabellenBlock)])
        self.assertTrue(any(
            isinstance(b, GleichungBlock) and "Widerstand bei festgehaltenem" in b.titel
            for b in bloecke))

    def test_bei_n_null_wird_nicht_interpoliert(self):
        """
        Trifft die Einwirkung genau einen Eckpunkt, ist nichts zu interpolieren.

        Bei ``N_Ed = 0`` stand dort ein Bruch mit null im Zähler --
        ``(0.0 - 0.0)/(910.6 - 0.0)`` --, der nichts erklärt und nur aussieht,
        als wäre etwas gerechnet worden. Jetzt steht der Eckpunkt selbst da.
        """
        from opencivil.core.protokoll import GleichungBlock, TabellenBlock

        bloecke = list(self.loesung.protokoll.alle_bloecke())
        self.assertNotIn("Stützpunkte der Interpolation",
                         [b.titel for b in bloecke if isinstance(b, TabellenBlock)])
        gleichungen = [b for b in bloecke if isinstance(b, GleichungBlock)]
        self.assertFalse(
            any(r"\frac{0.0 - 0.0}" in b.latex for b in gleichungen),
            "der entartete Bruch gehört nicht in die Mitschrift")
        self.assertTrue(
            any("liegt genau dort" in (b.titel or "") for b in gleichungen),
            "der getroffene Eckpunkt muss benannt sein")

    def test_der_massstab_steht_nicht_in_der_mitschrift(self):
        """
        Ob waagrecht oder senkrecht gemessen wird, ist eine Festlegung und
        kein Rechenschritt -- sie gehört nicht in die Herleitung.
        """
        from opencivil.core.protokoll import TextBlock

        texte = " ".join(b.text for b in self.loesung.protokoll.alle_bloecke()
                         if isinstance(b, TextBlock))
        self.assertNotIn("Massgebender Massstab", texte)


class TestSymmetrisch(unittest.TestCase):
    def setUp(self):
        self.platte = symmetrische_platte()
        self.werk = Rechenwerk()
        self.platte.ins_rechenwerk(self.werk)
        self.nachweis = BiegungNormalkraft(
            self.platte, [Schnittgroessen("Feld", M_Ed=Groesse(50, KNM))], Richtung.X
        )
        self.werk.registriere(self.nachweis)
        self.loesung = self.werk.loese(self.nachweis.d_eckwerte["M_Rd_max"].id)

    def test_linie_ist_punktsymmetrisch(self):
        """Bei symmetrischer Bewehrung muss M_Rd^+ = -M_Rd^- gelten."""
        m_plus = self.loesung.groesse(self.nachweis.d_eckwerte["M_Rd_max"].id).in_einheit(KNM)
        m_minus = self.loesung.groesse(self.nachweis.d_eckwerte["M_Rd_min"].id).in_einheit(KNM)
        self.assertAlmostEqual(m_plus, -m_minus, delta=0.5)


class TestErfuellungsgrad(unittest.TestCase):
    def _pruefe(self, kombinationen, querschnitt=None):
        platte = querschnitt if querschnitt is not None else einfache_platte()
        werk = Rechenwerk()
        platte.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(platte, kombinationen, Richtung.X)
        werk.registriere(nachweis)
        loesung = werk.loese(*[d.id for d in nachweis.d_ausnutzung.values()])
        return nachweis, loesung

    def test_kleines_moment_ist_erfuellt(self):
        nachweis, loesung = self._pruefe([Schnittgroessen("Feld", M_Ed=Groesse(100, KNM))])
        self.assertTrue(loesung.alle_nachweise_erfuellt)
        grad = loesung.groesse(nachweis.d_ausnutzung["Feld"].id).in_einheit(EINHEITSLOS)
        self.assertGreater(grad, 1.0)   # Erfüllungsgrad, nicht Ausnutzung

    def test_zu_grosses_moment_ist_nicht_erfuellt(self):
        nachweis, loesung = self._pruefe([Schnittgroessen("Feld", M_Ed=Groesse(400, KNM))])
        self.assertFalse(loesung.alle_nachweise_erfuellt)
        grad = loesung.groesse(nachweis.d_ausnutzung["Feld"].id).in_einheit(EINHEITSLOS)
        self.assertLess(grad, 1.0)

    def test_mehrere_kombinationen_gleichzeitig(self):
        # Alle drei mit demselben Massstab, sonst vergleicht man Momenten- mit
        # Normalkraftwiderständen -- zwei verschiedene Grössen.
        waagrecht = Erfuellungsart.NORMALKRAFT_KONSTANT
        kombinationen = [
            Schnittgroessen("Feld", M_Ed=Groesse(100, KNM), art=waagrecht),
            Schnittgroessen("Feld_mit_Druck", M_Ed=Groesse(100, KNM),
                            N_Ed=Groesse(-200, KN), art=waagrecht),
            Schnittgroessen("Feld_mit_Zug", M_Ed=Groesse(100, KNM),
                            N_Ed=Groesse(200, KN), art=waagrecht),
        ]
        nachweis, loesung = self._pruefe(kombinationen)
        self.assertEqual(len(loesung.urteile), 3)
        eta = {
            k.name: loesung.groesse(nachweis.d_ausnutzung[k.name].id).in_einheit(EINHEITSLOS)
            for k in kombinationen
        }
        # Zug verringert den Momentenwiderstand, Druck erhöht ihn -- der Bauch
        # des Interaktionsdiagramms. Siehe test_handrechnung_hat_einen_bauch.
        self.assertLess(eta["Feld_mit_Zug"], eta["Feld"])
        self.assertGreater(eta["Feld_mit_Druck"], eta["Feld"])

    def test_es_gilt_der_kleinere_der_beiden_massstaebe(self):
        """
        Gerechnet werden beide Wege, massgebend ist der ungünstigere.

        Vorher entschied eine Schwelle am Anteil der Grenznormalkraft, ob
        waagrecht (Momentenwiderstand bei festgehaltener Normalkraft) oder
        senkrecht gemessen wird. Das war eine Faustregel -- und sie konnte den
        grösseren der beiden Erfüllungsgrade stehen lassen, also den
        günstigeren. Jetzt wird nicht mehr geraten.
        """
        from opencivil.nachweis.biegung_normalkraft import geo

        nachweis, _ = self._pruefe([Schnittgroessen("x", M_Ed=Groesse(100, KNM))])
        N_zug = max(p.N for p in nachweis.handlinie)
        N_druck = min(p.N for p in nachweis.handlinie)

        for anteil, N_grenze, was in [
            (0.20, N_zug, "wenig Zug"), (0.30, N_zug, "viel Zug"),
            (0.50, N_druck, "wenig Druck"), (0.70, N_druck, "viel Druck"),
        ]:
            with self.subTest(fall=was):
                kombination = Schnittgroessen(
                    "x", M_Ed=Groesse(100, KNM),
                    N_Ed=Groesse.aus_si(N_grenze * anteil, KN))
                beide = [nachweis._messen(kombination, achse, True)
                         for achse in (geo.MOMENT, geo.NORMALKRAFT)]
                grade = [g.erfuellungsgrad for g in beide if g is not None]
                gewaehlt = nachweis._auswerten(kombination, {})
                self.assertAlmostEqual(gewaehlt.erfuellungsgrad, min(grade))

    def test_ein_vorgegebener_massstab_bleibt_stehen(self):
        """
        Wer die Richtung selbst wählt, bekommt sie -- auch die ungünstigere.

        Der Vergleich gilt nur für `automatisch`; sonst liesse sich ein
        Zwischenwert gar nicht mehr gezielt nachrechnen.
        """
        nachweis, _ = self._pruefe([
            Schnittgroessen("N_fest", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-200, KN),
                            art=Erfuellungsart.NORMALKRAFT_KONSTANT),
            Schnittgroessen("M_fest", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-200, KN),
                            art=Erfuellungsart.MOMENT_KONSTANT),
        ])
        nach_name = {a.schnittgroessen.name: a for a in nachweis.auswertungen}
        self.assertIs(nach_name["N_fest"].massstab, Erfuellungsart.NORMALKRAFT_KONSTANT)
        self.assertIs(nach_name["M_fest"].massstab, Erfuellungsart.MOMENT_KONSTANT)

    def test_handrechnung_hat_einen_bauch(self):
        """
        Auch das Polygon zeigt den Bauch unter Druck.

        Eine Normaldruckkraft vergrössert den Momentenwiderstand, bis die
        Druckzone zu gross wird. Beim Polygon kommt das vom Eckpunkt bei
        x = h/2; der gilt, solange die Zugbewehrung dort noch fliesst.

        Beide Höchstwerte liegen nahe beieinander. Auf welcher Seite die
        Handrechnung landet, ist nicht festgelegt und soll es auch nicht sein:
        sie vernachlässigt den gedrückten Stahl (das drückt), setzt dafür aber
        einen Spannungsblock der Höhe 0.85x an, dessen Resultierende etwas über
        der Parabel-Rechteck-Beziehung liegt (das hebt). Welcher Einfluss
        überwiegt, hängt vom Querschnitt ab.
        """
        nachweis, _ = self._pruefe(
            [Schnittgroessen("Druck", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-200, KN))])

        genau = max(nachweis.linie, key=lambda punkt: punkt.M)
        hand = max(nachweis.handlinie, key=lambda punkt: punkt.M)
        self.assertLess(genau.N, 0.0, "die genaue Linie hat ihren Bauch unter Druck")
        self.assertLess(hand.N, 0.0, "das Polygon auch")
        self.assertAlmostEqual(hand.M / genau.M, 1.0, delta=0.10)

    def test_eckpunkt_faellt_weg_wenn_die_bewehrung_nicht_fliesst(self):
        """
        Ohne Fliessen bei x = h/2 wäre f_sd = f_yd zu günstig angesetzt.

        Erzwungen mit einer sehr grossen unteren Überdeckung: dann liegt die
        untere Bewehrung nahe der Nulllinie und dehnt sich kaum. Für das
        positive Moment muss der Eckpunkt wegfallen, statt mit einer Spannung
        zu rechnen, die der Stahl nicht erreicht.
        """
        querschnitt = platte(
            [lage(1, Richtung.X, phi=18.0), lage(2, Richtung.Y),
             lage(3, Richtung.Y), lage(4, Richtung.X, phi=12.0)],
            ueberdeckung_unten=Groesse(130, MM))
        nachweis, _ = self._pruefe(
            [Schnittgroessen("Feld", M_Ed=Groesse(40, KNM))], querschnitt=querschnitt)

        # Auf der Druckseite darf kein Bauch mehr entstehen: der Höchstwert des
        # positiven Moments liegt wieder bei N = 0.
        bester = max(nachweis.handlinie, key=lambda punkt: punkt.M)
        self.assertAlmostEqual(bester.N, 0.0, places=6)
        self.assertEqual(
            1, sum(1 for q in nachweis.handlinie if q.name.startswith("x = h/2")),
            "nur die negative Seite darf den Eckpunkt behalten")

    def test_alle_drei_massstaebe_liefern_ein_ergebnis(self):
        kombinationen = [
            Schnittgroessen("N_konst", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-100, KN),
                            art=Erfuellungsart.NORMALKRAFT_KONSTANT),
            Schnittgroessen("M_konst", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-100, KN),
                            art=Erfuellungsart.MOMENT_KONSTANT),
            Schnittgroessen("naechster", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-100, KN),
                            art=Erfuellungsart.NAECHSTER_PUNKT),
        ]
        nachweis, loesung = self._pruefe(kombinationen)
        for k in kombinationen:
            grad = loesung.groesse(nachweis.d_ausnutzung[k.name].id).in_einheit(EINHEITSLOS)
            with self.subTest(art=k.art):
                self.assertGreater(grad, 1.0)
        # Derselbe Punkt liegt drin -- unabhängig vom Massstab.
        self.assertTrue(loesung.alle_nachweise_erfuellt)

    def test_automatisch_ist_der_standard(self):
        """Der ungünstigere der beiden Massstäbe wird selbst gefunden."""
        self.assertIs(
            Schnittgroessen("x", M_Ed=Groesse(1, KNM)).art,
            Erfuellungsart.AUTOMATISCH,
        )

    def test_automatik_nimmt_den_kleineren_erfuellungsgrad(self):
        platte_ = einfache_platte()
        werk = Rechenwerk(); platte_.ins_rechenwerk(werk)
        auto = BiegungNormalkraft(
            platte_, [Schnittgroessen("K", M_Ed=Groesse(100, KNM),
                                      N_Ed=Groesse(-500, KN))], Richtung.X)
        werk.registriere(auto)
        werk.loese(auto.d_ausnutzung["K"].id)
        gewaehlt = auto.auswertungen[0]

        einzeln = []
        for art in (Erfuellungsart.NORMALKRAFT_KONSTANT, Erfuellungsart.MOMENT_KONSTANT):
            w2 = Rechenwerk(); platte_.ins_rechenwerk(w2)
            n2 = BiegungNormalkraft(
                platte_, [Schnittgroessen("K", M_Ed=Groesse(100, KNM),
                                          N_Ed=Groesse(-500, KN), art=art)], Richtung.X)
            w2.registriere(n2)
            w2.loese(n2.d_ausnutzung["K"].id)
            einzeln.append(n2.auswertungen[0].erfuellungsgrad)
        self.assertAlmostEqual(gewaehlt.erfuellungsgrad, min(einzeln), places=6)

    def test_begruendung_nennt_den_widerstand(self):
        nachweis, loesung = self._pruefe([Schnittgroessen("Feld", M_Ed=Groesse(100, KNM))])
        self.assertIn("Momentenwiderstand", loesung.urteile[0].begruendung)

    def test_normalkraft_ausserhalb_ist_nicht_erfuellt(self):
        nachweis, loesung = self._pruefe(
            [Schnittgroessen("Zugbruch", M_Ed=Groesse(0, KNM), N_Ed=Groesse(5000, KN))]
        )
        self.assertFalse(loesung.alle_nachweise_erfuellt)

    def test_ohne_kombination_bleiben_die_eckwerte(self):
        """
        Die Resistenzlinie gehört dem Querschnitt, nicht der Einwirkung.

        Ohne Kombinationen fällt kein Urteil -- die Eckwerte entstehen
        trotzdem. Der Nachweis gegen sprödes Versagen hält M_Rd(N=0) gegen das
        Rissmoment und braucht dafür keine Schnittgrösse.
        """
        platte = einfache_platte()
        werk = Rechenwerk()
        platte.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(platte, [], Richtung.X)
        werk.registriere(nachweis)
        loesung = werk.loese(nachweis.d_eckwerte["M_Rd_N0_pos"].id)
        self.assertTrue(loesung.vollstaendig)
        self.assertEqual(loesung.urteile, [])
        self.assertGreater(
            loesung.groesse(nachweis.d_eckwerte["M_Rd_N0_pos"].id).si, 0.0)


class TestRueckverfolgungNachweis(unittest.TestCase):
    def test_nachweis_zieht_die_ganze_kette(self):
        platte = einfache_platte()
        werk = Rechenwerk()
        platte.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(
            platte, [Schnittgroessen("Feld", M_Ed=Groesse(100, KNM))], Richtung.X
        )
        werk.registriere(nachweis)
        ziel = nachweis.d_ausnutzung["Feld"].id
        loesung = werk.loese(ziel)

        benoetigt = loesung.benoetigte_werte(ziel)
        for erwartet in (
            platte.beton.id_von("f_cd"),
            platte.beton.id_von("f_ck"),
            platte.beton.id_von("k_sigma"),
            platte.id_von("lage.1g.a_s"),
            platte.id_von("lage.1g.z"),
            platte.id_von("h"),
        ):
            self.assertIn(erwartet, benoetigt)

    def test_fehlender_kennwert_wird_benannt(self):
        """Ohne k_sigma lässt sich die Interaktionslinie nicht aufbauen."""
        platte = einfache_platte()
        werk = Rechenwerk()
        platte.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(
            platte, [Schnittgroessen("Feld", M_Ed=Groesse(100, KNM))], Richtung.X
        )
        werk.registriere(nachweis)
        # k_sigma braucht E_cd; dessen Kette wird gekappt.
        werk._nach_ausgabe.pop(platte.beton.id_von("k_sigma"))
        loesung = werk.loese(nachweis.d_ausnutzung["Feld"].id)
        self.assertFalse(loesung.vollstaendig)
        self.assertIn(
            platte.beton.id_von("k_sigma"), [f.id for f in loesung.fehlende]
        )


class TestHandrechnungSymbole(unittest.TestCase):
    """
    Die zusammengefassten Lagen tragen ihren Index und ihre Teile.

    Beides ging verloren, als die Posten als blanke Tupel an
    ``lagen_zusammenfassen`` gingen: die Mitschrift schrieb ``A_{s,}`` mit
    leerem Index, und die Herleitung des Schwerpunkts fiel still aus, weil sie
    ``len(teile) > 1`` verlangt.
    """

    def mitschrift(self, qs) -> str:
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(
            qs, [Schnittgroessen("Feld", M_Ed=Groesse(100, KNM))], Richtung.X)
        werk.registriere(nachweis)
        loesung = werk.loese(nachweis.d_ausnutzung["Feld"].id)
        self.assertTrue(loesung.vollstaendig)
        return "\n".join(
            str(getattr(b, "latex", "") or "") for b in loesung.protokoll.bloecke)

    def test_kein_symbol_mit_leerem_index(self):
        text = self.mitschrift(einfache_platte())
        self.assertNotIn("A_{s,}", text)
        self.assertNotIn("d_{}", text)

    def test_zusammengefasste_lage_traegt_den_index_ihrer_teile(self):
        """Grund 1,x,g und Zulage 1,x,z ergeben zusammen 1,x."""
        text = self.mitschrift(platte([
            lage(1, Richtung.X, phi=18.0, zulage=12.0),
            lage(2, Richtung.Y), lage(3, Richtung.Y), lage(4, Richtung.X, phi=12.0),
        ]))
        self.assertIn("A_{s,1,x}", text)
        self.assertIn("d_{4,x}", text)

    def test_der_schwerpunkt_wird_hergeleitet_wo_zwei_posten_zusammenkommen(self):
        """
        Besteht eine Seite aus Grundbewehrung und Zulage, muss dastehen, wie
        ihre gemeinsame Tiefe z entsteht -- sonst fällt der Wert aus dem
        Nichts. Die statische Höhe d folgt daraus in einer eigenen Zeile.
        """
        text = self.mitschrift(platte([
            lage(1, Richtung.X, phi=18.0, zulage=12.0),
            lage(2, Richtung.Y), lage(3, Richtung.Y), lage(4, Richtung.X, phi=12.0),
        ]))
        # Ein- oder mehrzeilig gesetzt -- «=» oder «&=».
        self.assertRegex(
            text, r"z_\{1,x\} &?= \\frac\{A_\{s,1,x,g\} \\cdot z_\{1,x,g\}")
        self.assertIn("A_{s,1,x} = A_{s,1,x,g} + A_{s,1,x,z}", text)
        self.assertIn("d_{1,x} = z_{1,x}", text)
        self.assertIn(r"d_{4,x} = h - z_{4,x}", text)

    def test_ohne_zulage_gibt_es_nichts_herzuleiten(self):
        """Eine Seite aus einem einzigen Posten braucht keine Schwerpunktformel."""
        text = self.mitschrift(einfache_platte())
        self.assertNotIn(r"\frac{A_{s,1,x,g} \cdot z_{1,x,g}", text)


if __name__ == "__main__":
    unittest.main()


class TestOhneZugbewehrung(unittest.TestCase):
    """
    Ein Widerstand darf nicht aus dem Nichts entstehen.

    Ohne Bewehrung auf der gezogenen Seite gab es trotzdem einen Eckpunkt
    x = h/2: der Betondruckblock stand allein da und schob dem Polygon ein
    Moment unter. Eine Platte nur mit unterer Bewehrung wies so ein negatives
    Moment von 220 kNm nach.
    """

    def nur_unten(self):
        return platte([
            lage(1, Richtung.X, phi=18.0),
            lage(2, Richtung.Y), lage(3, Richtung.Y), lage(4, Richtung.X),
        ])

    def linie(self, qs):
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(
            qs, [Schnittgroessen("Feld", M_Ed=Groesse(100, KNM))], Richtung.X)
        werk.registriere(nachweis)
        werk.loese(nachweis.d_ausnutzung["Feld"].id)
        return nachweis

    def test_kein_eckpunkt_ohne_zugbewehrung(self):
        nachweis = self.linie(self.nur_unten())
        namen = [q.name for q in nachweis.handlinie]
        self.assertIn("x = h/2 +", namen)       # unten ist bewehrt
        self.assertNotIn("x = h/2 -", namen)    # oben nicht

    def test_kein_negatives_moment_ohne_obere_bewehrung(self):
        nachweis = self.linie(self.nur_unten())
        self.assertAlmostEqual(min(q.M for q in nachweis.handlinie), 0.0, places=6)

    def test_mit_oberer_bewehrung_gibt_es_den_eckpunkt(self):
        beidseitig = platte([
            lage(1, Richtung.X, phi=18.0),
            lage(2, Richtung.Y), lage(3, Richtung.Y),
            lage(4, Richtung.X, phi=12.0),
        ])
        namen = [q.name for q in self.linie(beidseitig).handlinie]
        self.assertIn("x = h/2 -", namen)


class TestPolygonreihenfolge(unittest.TestCase):
    """
    Das Polygon darf sich nicht selbst kreuzen.

    Welcher der beiden Punkte einer Seite oben liegt, steht nicht fest: der
    Punkt x = h/2 liegt gewöhnlich im Druck, bei einer dünnen, stark bewehrten
    Platte aber im Zug. Fest verdrahtet kreuzte sich das Polygon dort -- und
    ein sich kreuzendes Polygon ist keine Resistenzlinie mehr.
    """

    def duenn_und_stark_bewehrt(self):
        """
        h = 150 mm, ⌀20@100 beidseitig, Überdeckung 15 mm.

        A_s·f_yd = 3142·435 = 1367 kN übersteigt die Blockdruckkraft
        0.85·1000·20·75 = 1275 kN -- N bei x = h/2 wird damit positiv.
        """
        return platte([
            lage(1, Richtung.X, phi=20.0, s=100.0),
            lage(2, Richtung.Y), lage(3, Richtung.Y),
            lage(4, Richtung.X, phi=20.0, s=100.0),
        ], h=Groesse(150, MM),
           ueberdeckung_unten=Groesse(15, MM), ueberdeckung_oben=Groesse(15, MM))

    def linie(self):
        qs = self.duenn_und_stark_bewehrt()
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        nachweis = BiegungNormalkraft(
            qs, [Schnittgroessen("Feld", M_Ed=Groesse(50, KNM))], Richtung.X)
        werk.registriere(nachweis)
        werk.loese(nachweis.d_ausnutzung["Feld"].id)
        return nachweis.handlinie

    def test_der_fall_tritt_ueberhaupt_ein(self):
        """Ohne eine Zugkraft bei x = h/2 prüfte der Test nichts."""
        punkt = next(q for q in self.linie() if q.name == "x = h/2 +")
        self.assertGreater(punkt.N, 0.0)

    def test_x_halbe_hoehe_steht_hinter_dem_punkt_bei_n_null(self):
        namen = [q.name for q in self.linie()]
        self.assertLess(namen.index("M_Rd(N_Ed=0) +"), namen.index("x = h/2 +"))
        # Auf dem Rückweg umgekehrt.
        self.assertLess(namen.index("x = h/2 -"), namen.index("M_Rd(N_Ed=0) -"))

    def test_die_normalkraft_steigt_und_faellt_je_einmal(self):
        """
        Ein einfaches Polygon dieser Form ist in N monoton: hinauf zur
        Zugspitze, wieder hinunter zum Druck. Mehr als ein Wechsel hiesse,
        dass sich die Linie kreuzt.
        """
        werte = [q.N for q in self.linie()]
        richtungen = [b > a for a, b in zip(werte, werte[1:] + werte[:1])]
        wechsel = sum(1 for a, b in zip(richtungen, richtungen[1:] + richtungen[:1])
                      if a != b)
        self.assertEqual(wechsel, 2)

    def test_das_polygon_kreuzt_sich_nicht(self):
        punkte = [(q.M, q.N) for q in self.linie()]
        anzahl = len(punkte)

        def richtung(p, q, r):
            return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])

        def kreuzt(a, b, c, d):
            return ((richtung(a, b, c) > 0) != (richtung(a, b, d) > 0)
                    and (richtung(c, d, a) > 0) != (richtung(c, d, b) > 0))

        for i in range(anzahl):
            for j in range(i + 2, anzahl):
                if i == 0 and j == anzahl - 1:
                    continue                      # gemeinsamer Ringschluss
                a, b = punkte[i], punkte[(i + 1) % anzahl]
                c, d = punkte[j], punkte[(j + 1) % anzahl]
                self.assertFalse(kreuzt(a, b, c, d),
                                 f"Kanten {i} und {j} kreuzen sich")


class TestSortenindex(unittest.TestCase):
    """
    Symbole tragen die Sorte, sobald mehrere in Frage kommen.

    Bei zwei Betonen stünde sonst zweimal `f_cd` mit verschiedenen Zahlen im
    selben Bericht, und niemand könnte sagen, welcher gemeint ist. Solange es
    nur einen gibt, wäre der Index Ballast.
    """

    def mitschrift(self, projekt) -> str:
        """Mit Querkraft, damit auch tau_cd und E_s vorkommen."""
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 120.0
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        return "\n".join(
            str(getattr(b, "latex", "") or "") for b in loesung.protokoll.bloecke)

    def test_ohne_index_wenn_es_nur_einen_gibt(self):
        from opencivil.projekt import Projekt

        text = self.mitschrift(Projekt.beispiel())
        self.assertIn("f_{cd}", text)
        self.assertNotIn(r"f_{cd,\text", text)

    def test_mit_index_bei_zwei_betonen(self):
        from opencivil.projekt import MaterialEintrag, Projekt

        projekt = Projekt.beispiel()
        projekt.materialien.append(MaterialEintrag("b2", "beton", "C40/50", "C40/50"))
        text = self.mitschrift(projekt)
        self.assertIn(r"f_{cd,\text{C30/37}}", text)
        self.assertIn(r"\tau_{cd,\text{C30/37}}", text)
        self.assertIn(r"\varepsilon_{c2d,\text{C30/37}}", text)

    def test_mit_index_bei_zwei_staehlen(self):
        from opencivil.projekt import MaterialEintrag, Projekt

        projekt = Projekt.beispiel()
        projekt.materialien.append(MaterialEintrag("s2", "betonstahl", "B500A", "B500A"))
        # Eine Lage in x -- nur dort wird gerechnet, und nur was gerechnet
        # wird, steht in der Mitschrift.
        projekt.querschnitt("q1").lagen[2].stahl = "s2"
        text = self.mitschrift(projekt)
        self.assertIn(r"f_{yd,\text{B500B}}", text)
        self.assertIn(r"f_{yd,\text{B500A}}", text)

    def test_die_lage_traegt_den_index_ihrer_massgebenden_sorte(self):
        """
        Zusammengefasst zählt die schwächere Sorte -- und der Index gehört
        derselben, sonst stünde ein fremder Name an der Zahl.
        """
        from opencivil.nachweis.handrechnung import Posten, lagen_zusammenfassen

        seiten = lagen_zusammenfassen([
            Posten(a_s=1e-3, z=0.26, f_yd=500e6, E_s=205e9, text="stark",
                   index="1,x,g", stahl_index="B500B", von_unten=True),
            Posten(a_s=1e-3, z=0.25, f_yd=435e6, E_s=205e9, text="schwach",
                   index="1,x,z", stahl_index="B500A", von_unten=True),
            Posten(a_s=1e-3, z=0.04, f_yd=435e6, E_s=205e9, text="oben",
                   index="4,x,g", stahl_index="B500A", von_unten=False),
        ])
        unten = seiten["unten"]
        self.assertAlmostEqual(unten.f_yd, 435e6)
        self.assertEqual(unten.stahl_index, "B500A")
        self.assertEqual(unten.symbol_f_yd, r"f_{yd,\text{B500A}}")
