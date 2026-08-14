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
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen, _schnitte_bei_N,
)
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

    def test_zulage_liegt_auf_derselben_huelle(self):
        """
        Grundbewehrung und Zulage einer Lage berühren dieselbe Hüllebene und
        sind je um ihren eigenen Halbmesser eingerückt.
        """
        qs = platte([
            lage(1, Richtung.X, phi=20.0, zulage=12.0),
            lage(2, Richtung.Y), lage(3, Richtung.X), lage(4, Richtung.Y),
        ])
        werk = Rechenwerk()
        qs.ins_rechenwerk(werk)
        loesung = werk.loese(qs.id_von("lage.1g.z"), qs.id_von("lage.1z.z"))
        self.assertAlmostEqual(
            loesung.groesse(qs.id_von("lage.1g.z")).in_einheit(MM), 300 - (30 + 10))
        self.assertAlmostEqual(
            loesung.groesse(qs.id_von("lage.1z.z")).in_einheit(MM), 300 - (30 + 6))

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
            return max(_schnitte_bei_N(nachweis.linie, 0.0))

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
        momente = _schnitte_bei_N(self.nachweis.linie, 0.0)
        m_rd = max(momente) / 1e3
        self.assertAlmostEqual(m_rd, 179.0, delta=8.0)

    def test_nur_untere_bewehrung_gibt_bei_n_null_kaum_negatives_moment(self):
        momente = _schnitte_bei_N(self.nachweis.linie, 0.0)
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
        m_bei_null = max(_schnitte_bei_N(self.nachweis.linie, 0.0))
        self.assertGreater(bester.M, m_bei_null)

    def test_protokoll_zeigt_den_ablauf(self):
        from opencivil.core.protokoll import GleichungBlock, TabellenBlock

        bloecke = list(self.loesung.protokoll.alle_bloecke())
        titel = [b.titel for b in bloecke if isinstance(b, TabellenBlock)]
        self.assertIn("Stützstellen des Dehnungsfächers", titel)
        self.assertIn("Berücksichtigte Bewehrungslagen", titel)
        self.assertIn("Eckwerte der Resistenzlinie", titel)
        gleichungen = [b.latex for b in bloecke if isinstance(b, GleichungBlock)]
        self.assertTrue(any(r"\sigma_c" in g for g in gleichungen))
        self.assertTrue(any(r"\int_A" in g for g in gleichungen))


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
    def _pruefe(self, kombinationen):
        platte = einfache_platte()
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
        kombinationen = [
            Schnittgroessen("Feld", M_Ed=Groesse(100, KNM)),
            Schnittgroessen("Feld_mit_Druck", M_Ed=Groesse(100, KNM), N_Ed=Groesse(-200, KN)),
            Schnittgroessen("Feld_mit_Zug", M_Ed=Groesse(100, KNM), N_Ed=Groesse(200, KN)),
        ]
        nachweis, loesung = self._pruefe(kombinationen)
        self.assertEqual(len(loesung.urteile), 3)
        eta = {
            k.name: loesung.groesse(nachweis.d_ausnutzung[k.name].id).in_einheit(EINHEITSLOS)
            for k in kombinationen
        }
        # Druck erhöht den Momentenwiderstand, Zug verringert ihn -- beim
        # Erfüllungsgrad also genau umgekehrt zur früheren Ausnutzung.
        self.assertGreater(eta["Feld_mit_Druck"], eta["Feld"])
        self.assertLess(eta["Feld_mit_Zug"], eta["Feld"])

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

    def test_ohne_kombination_verboten(self):
        platte = einfache_platte()
        with self.assertRaises(ValueError):
            BiegungNormalkraft(platte, [], Richtung.X)


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


if __name__ == "__main__":
    unittest.main()
