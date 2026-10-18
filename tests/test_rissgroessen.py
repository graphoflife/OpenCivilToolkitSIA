"""
Die Rissgrössen an einer Stelle (opencivil.nachweis.rissgroessen).

Die Regeln hat der Benutzer am 2026-10-17 entschieden: unter Biegung reisst
ein Drittel der Höhe in Biegerichtung, unter Zug die kleinere Abmessung,
wahlweise höchstens 500 mm; das Rissmoment ist das Moment unter reiner
Biegung, bei dem f_ct,eff zum ersten Mal irgendwo erreicht wird -- mit I_yz,
einachsig mit waagrechter Nulllinie.
"""

import dataclasses
import math
import unittest

from opencivil.nachweis.rissgroessen import (
    DICKENGRENZE, Bruttoquerschnitt, Ecke, beiwert_dicke, rissaktive_dicke, rissmoment,
    rissmoment_rechteck,
)


def rechteck(b: float, h: float, f_ctm: float = 2.9e6) -> Bruttoquerschnitt:
    """Ein Rechteck b × h um seinen Schwerpunkt, in m."""
    ecken = tuple(Ecke(y=y, z=z, punkt=((y + b / 2) * 1e3, (z + h / 2) * 1e3),
                       stoff=None, f_ctm=f_ctm)
                  for y, z in ((-b / 2, -h / 2), (b / 2, -h / 2), (b / 2, h / 2), (-b / 2, h / 2)))
    return Bruttoquerschnitt(I_y=b * h ** 3 / 12, I_z=h * b ** 3 / 12, I_yz=0.0, ecken=ecken)


class TestRissaktiveDicke(unittest.TestCase):
    def test_unter_biegung_ein_drittel_der_hoehe(self):
        self.assertAlmostEqual(rissaktive_dicke(h=0.6, b=0.3, zug=False), 0.2)

    def test_unter_zug_die_kleinere_abmessung(self):
        self.assertEqual(rissaktive_dicke(h=0.6, b=0.3, zug=True), 0.3)
        self.assertEqual(rissaktive_dicke(h=0.3, b=0.6, zug=True), 0.3)

    def test_wahlweise_hoechstens_500_mm(self):
        self.assertEqual(rissaktive_dicke(h=0.8, b=0.9, zug=True, begrenzt=True), DICKENGRENZE)
        self.assertEqual(rissaktive_dicke(h=0.8, b=0.9, zug=True), 0.8)

    def test_die_platte_reisst_unter_zug_ueber_ihre_dicke(self):
        """Ihre Breite ist ein Streifen, keine Abmessung -- auch ein schmaler zählt nicht."""
        self.assertEqual(rissaktive_dicke(h=0.6, zug=True), 0.6)


class TestRissmoment(unittest.TestCase):
    def test_der_bruttoquerschnitt_rechnet_wie_seine_analyse(self):
        """«einachsig» steht an der Analyse; der Bruttoquerschnitt trägt es weiter."""
        from opencivil.nachweis.rissgroessen import bruttoquerschnitt
        from opencivil.projekt import Projekt
        for einachsig in (False, True):
            with self.subTest(einachsig=einachsig):
                projekt = Projekt.jeder_nachweis()
                eintrag = projekt.querschnittsanalysen[0]
                eintrag.einachsig = einachsig
                aufbau = projekt.aufbauen()
                analyse = aufbau.querschnittsanalysen[eintrag.kennung]
                loesung = aufbau.werk.loese(*aufbau.ziele_von(eintrag.kennung))
                brutto = bruttoquerschnitt(analyse, lambda kid: loesung.werte[kid].groesse.si)
                self.assertIs(brutto.einachsig, einachsig)

    def test_am_rechteck_wie_bei_der_platte(self):
        q = rechteck(0.3, 0.5)
        for einachsig in (False, True):
            with self.subTest(einachsig=einachsig):
                riss = rissmoment(dataclasses.replace(q, einachsig=einachsig), 1.0, 0.0)
                self.assertAlmostEqual(
                    riss.M_Riss, rissmoment_rechteck(h=0.5, b=0.3, f_ctm=2.9e6).M_Riss,
                    delta=1e-6)
                self.assertAlmostEqual(riss.k_t, beiwert_dicke(0.5 / 3))

    def test_einachsig_bleibt_die_nulllinie_waagrecht(self):
        """Mit I_yz kippt sie, und eine Ecke weit aussen reisst früher: W = I/v ist mehr."""
        q = rechteck(0.3, 0.5)
        schief = Bruttoquerschnitt(I_y=q.I_y, I_z=q.I_z, I_yz=0.4 * math.sqrt(q.I_y * q.I_z),
                                   ecken=q.ecken)
        gekippt = rissmoment(schief, 1.0, 0.0)
        waagrecht = rissmoment(dataclasses.replace(schief, einachsig=True), 1.0, 0.0)
        self.assertAlmostEqual(waagrecht.W, q.I_y / 0.25, delta=1e-12)
        self.assertLess(gekippt.M_Riss, waagrecht.M_Riss)

    def test_bei_zwei_betonen_reisst_zuerst_der_schwaechere_an_seiner_grenze(self):
        """Nicht die gezogenste Ecke zählt, sondern die, die zuerst ihre Zugfestigkeit erreicht."""
        q = rechteck(0.3, 0.5)
        unten_rechts, unten_links = q.ecken[1], q.ecken[0]
        schwach = Ecke(y=0.0, z=-0.2, punkt=(150.0, 50.0), stoff="schwach", f_ctm=1.0e6)
        q = Bruttoquerschnitt(I_y=q.I_y, I_z=q.I_z, I_yz=0.0,
                              ecken=(unten_links, unten_rechts, schwach) + q.ecken[2:],
                              einachsig=True)
        riss = rissmoment(q, 1.0, 0.0)
        self.assertEqual(riss.ecke.stoff, "schwach")
        self.assertAlmostEqual(riss.W, q.I_y / 0.2, delta=1e-12)


if __name__ == "__main__":
    unittest.main()
