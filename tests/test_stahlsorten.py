"""
Gemischte Stahlsorten: jede Lage rechnet mit dem Stahl ihrer Seite.

Der Editor laesst je Seite einen eigenen Stahl waehlen. Bis 2026-10-12
nahmen Stahlspannung, Knicken, Querkraft und Spannung-Dehnung-Analyse den
Stahl der ersten Lage fuer alle Lagen -- unten B700B und oben B500B rechnete
die obere Lage mit f_yd = 609 statt 435 N/mm². Nur die Tragsicherheit
rechnete je Sorte.
"""

import unittest

from opencivil.nachweis.querschnittsloeser import Stahllage, lagen_je_seite
from opencivil.projekt import KnickEintrag, Projekt
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.werkstoffgesetz import Stahlgesetz
from opencivil.spannungsanalyse import loeserpaar
from opencivil.nachweis.rechenwahl import Rechenart, Rechenwahl

#: Bemessungswerte der Fliessgrenze, in Pa.
F_YD_B500B = 500e6 / 1.15
F_YD_B700B = 700e6 / 1.15


def gemischt() -> Projekt:
    """
    Das Beispiel, unten B700B und oben B500B -- so, wie der Editor den Stahl
    je Seite setzt: an der x-Lage, die y-Lage derselben Seite bekommt ihn mit.
    """
    p = Projekt.beispiel()
    b700 = p.stahl("B700B")
    q = p.querschnitte[0]
    for lage in q.lagen[:2]:
        lage.stahl = b700.kennung
    q.rissanforderung = "hoch"
    q.haeufig.aus_tragsicherheit = True
    for kombination in q.kombinationen:
        kombination.V_Ed = 50.0
    q.knickfaelle = [KnickEintrag("Stütze", N_Ed=-800.0, M_Ed_1=20.0,
                                  laenge=4.0, knicklaenge=4.0)]
    return p


def unten(z: float, h: float) -> bool:
    return z > h / 2.0


class TestGemischteSorten(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.projekt = gemischt()
        cls.aufbau = cls.projekt.aufbauen()
        cls.loesung = cls.aufbau.werk.loese(*cls.aufbau.alle_nachweisziele())

    def staehle(self, nachweis) -> set:
        """Die Stahlsorten, deren Kennwerte ein Nachweis liest."""
        return {".".join(b.wert_id.split(".")[:2]) for b in nachweis.bezuege
                if b.wert_id.startswith("betonstahl.")}

    def test_jeder_nachweis_liest_beide_sorten(self):
        beide = {"betonstahl.s1", "betonstahl.s2"}
        for nachweis in (self.aufbau.knicken["q1"], self.aufbau.spannung["q1.x"],
                         self.aufbau.spannung_riss["q1.x"], self.aufbau.querkraft["q1.x"]):
            with self.subTest(nachweis=nachweis.id):
                self.assertEqual(self.staehle(nachweis), beide)

    def test_die_grenze_gegen_fliessen_gilt_je_lage(self):
        """Feld: gezogen ist unten (B700B). Stütze: oben (B500B)."""
        urteile = {u.fall: u for u in self.loesung.urteile
                   if u.raum == self.aufbau.spannung["q1.x"].id}
        self.assertAlmostEqual(urteile["Feld (70 %)"].widerstand.groesse.si,
                               F_YD_B700B - 80e6, delta=1e4)
        self.assertAlmostEqual(urteile["Stütze (70 %)"].widerstand.groesse.si,
                               F_YD_B500B - 80e6, delta=1e4)

    def test_die_querkraft_nimmt_den_stahl_der_zugseite(self):
        """ε_v = f_yd·(|m_Ed| − m_Dd) / (E_s·(m_Rd − m_Dd)), mit f_yd der Zugseite."""
        E_s = self.loesung.groesse("betonstahl.s1.E_s").si
        erwartet = {"Feld": F_YD_B700B, "Stütze": F_YD_B500B}
        geprueft = set()
        for erg in self.loesung.befund(self.aufbau.querkraft["q1.x"]).ergebnisse:
            if erg.fall.name not in erwartet:
                continue
            with self.subTest(fall=erg.fall.name):
                f_yd = (erg.eps_v * E_s * (erg.m_Rd - erg.m_Dd)
                        / (abs(erg.fall.M_Ed.si) - erg.m_Dd))
                self.assertAlmostEqual(f_yd, erwartet[erg.fall.name], delta=1e4)
                geprueft.add(erg.fall.name)
        self.assertEqual(geprueft, set(erwartet))

    def test_das_knicken_rechnet_jede_lage_mit_ihrem_stahl(self):
        loeser = self.loesung.befund(self.aufbau.knicken["q1"]).loeser
        for lage, stab in zip(loeser.lagen, loeser.querschnitt.staebe):
            with self.subTest(z=lage.z):
                erwartet = F_YD_B700B if unten(lage.z, loeser.h) else F_YD_B500B
                self.assertAlmostEqual(stab.gesetz(0.01), erwartet, delta=1e4)

    def test_die_analyse_rechnet_jede_lage_mit_ihrem_stahl(self):
        q = self.aufbau.querschnitte["q1"]
        paar = loeserpaar(q, Richtung.X, lambda wid: self.loesung.groesse(wid).si,
                          wahl=Rechenwahl(art=Rechenart.PARABEL))
        for zustand in (paar.gerissen, paar.ungerissen):
            for lage, stab in zip(zustand.lagen, zustand.querschnitt.staebe):
                with self.subTest(z=lage.z):
                    erwartet = F_YD_B700B if unten(lage.z, zustand.h) else F_YD_B500B
                    self.assertAlmostEqual(stab.gesetz(0.01), erwartet, delta=1e4)
                    self.assertAlmostEqual(lage.stahl.eps_yd, erwartet / 200e9, delta=1e-6)


class TestHandrechnungImLoeser(unittest.TestCase):
    """Je Seite eine Lage im Schwerpunkt -- mit dem Stahl dieser Seite."""

    B500B = Stahlgesetz(E_s=200e9, f_yd=F_YD_B500B, f_yd_druck=F_YD_B500B, eps_ud=0.045)
    B700B = Stahlgesetz(E_s=200e9, f_yd=F_YD_B700B, f_yd_druck=F_YD_B700B, eps_ud=0.045)

    def test_jede_seite_behaelt_ihren_stahl(self):
        lagen = lagen_je_seite([
            Stahllage(a_s=1e-3, z=0.25, stahl=self.B700B, von_unten=True),
            Stahllage(a_s=5e-4, z=0.24, stahl=self.B700B, von_unten=True),
            Stahllage(a_s=5e-4, z=0.05, stahl=self.B500B, von_unten=False)], 0.3)
        self.assertEqual([l.stahl for l in lagen], [self.B700B, self.B500B])

    def test_zwei_staehle_auf_einer_seite_sind_ein_fehler(self):
        """Die Platte kann das nicht -- je Seite und Richtung liegt eine Lage."""
        with self.assertRaises(ValueError):
            lagen_je_seite([Stahllage(a_s=1e-3, z=0.25, stahl=self.B700B, von_unten=True),
                            Stahllage(a_s=5e-4, z=0.24, stahl=self.B500B, von_unten=True)],
                           0.3)


if __name__ == "__main__":
    unittest.main()
