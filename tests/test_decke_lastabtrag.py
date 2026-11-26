"""
Wie die Decke ihre Last von selbst aufteilt -- wo Folie 31 nichts sagt.

* Mitte eines Felds: je zur Hälfte bei gleichen Spannweiten, ganz in die
  kürzere ab dem Verhältnis 1.5, dazwischen geradlinig (Benutzer,
  2026-11-25). Fast quadratische Felder springen nicht mehr: 5 × 5.04 m und
  5 × 5.06 m teilen fast gleich.
* Wo Last ausfällt: wo keine Richtung trägt, zeigt das Bild «trägt nicht»
  statt «je zur Hälfte», und eine graue Meldung an der Platte sagt je
  Richtung, warum; gibt die feste Aufteilung oder eine Zone Last in eine
  Richtung, die nicht trägt, sagt sie wer und wie viel.
"""

import math
import unittest

from opencivil.decke import geometrie as geo
from opencivil.decke.aufteilung import GANZ_AB, in_der_mitte
from opencivil.decke.feld import an_stelle
from opencivil.decke.modell import Aufteilung, Decke, Flaechenlast, Lastfall, Platte, Zone
from opencivil.decke.rechnung import rechnen
from tests.test_decke_rechnung import E, WICHTE, Rechnung, q, rechteck, waende


class TestMitteEinesFelds(Rechnung):
    """Rechteckplatten a × b auf vier Wänden; Richtung 1 ist x."""

    def in_der_platte(self, a, b):
        """Der Anteil in x und die Schnittkräfte neben der Mitte -- nicht auf einer Grenze der Streifen."""
        ecken = rechteck(0, 0, a, b)
        e = self.gerechnet(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)],
                                 linienlager=waende(ecken, 0, 1, 2, 3),
                                 lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])]))
        p = (a / 2.0 + 0.1, b / 2.0 + 0.1)
        anteil = next(wert for zelle, wert in e.aufteilungen.zellen if geo.innen(p, zelle))
        return anteil, an_stelle(e, e.faelle[0], p)

    def test_die_regel(self):
        self.assertEqual(in_der_mitte(5.0, 5.0), 0.5)
        self.assertAlmostEqual(in_der_mitte(4.0, 5.0), 0.75)
        self.assertAlmostEqual(in_der_mitte(5.0, 4.0), 0.25)
        self.assertEqual(in_der_mitte(4.0, 4.0 * GANZ_AB), 1.0)
        self.assertEqual(in_der_mitte(8.0, 4.0), 0.0, "Folie 31: ganz in die kürzere")
        self.assertEqual(in_der_mitte(4.0, math.inf), 1.0, "nur eine Richtung hat ein Feld")
        self.assertEqual(in_der_mitte(math.inf, math.inf), 0.5)

    def test_ein_feld_4_mal_5(self):
        anteil, _ = self.in_der_platte(4.0, 5.0)
        self.assertAlmostEqual(anteil, 0.75)

    def test_kein_sprung_bei_fast_gleichen_spannweiten(self):
        anteil_1, k_1 = self.in_der_platte(5.0, 5.04)
        anteil_2, k_2 = self.in_der_platte(5.0, 5.06)
        self.assertAlmostEqual(anteil_1, 0.508)
        self.assertAlmostEqual(anteil_2, 0.512)
        self.assertLess(abs(k_2.mx - k_1.mx), 0.02 * k_1.mx)
        self.assertLess(abs(k_2.my - k_1.my), 0.02 * k_1.my)


class TestWoLastAusfaellt(Rechnung):
    """Platten mit zu wenig Lagern: die Last fällt aus, und die Decke sagt grau, wo und warum."""

    def gerechnet_ohne_probe(self, ecken, lager, **felder):
        e = rechnen(Decke(platten=[Platte("P", ecken, 0.2, E, WICHTE)], linienlager=lager,
                          lastfaelle=[Lastfall("q", [Flaechenlast("q", q, platte="P")])], **felder))
        self.assertFalse([m.text for m in e.meldungen if m.fehler])
        return e, e.faelle[0]

    def ausfall(self, e):
        """Die Meldungen der Aufteilung: Platte, Text -- jede grau."""
        meldungen = [m for m in e.meldungen if m.elemente == ("P",)]
        self.assertFalse(any(m.fehler or m.unfertig for m in meldungen))
        return [m.text for m in meldungen]

    def test_ueber_eck_traegt_keine_richtung(self):
        """
        Eine Platte nur auf zwei Wänden über Eck trüge nur über Drillmomente:
        die Streifen jeder Richtung liegen auf einer Wand und kippen. Vorher
        stand im Bild «je zur Hälfte» und eine rote Meldung ohne Grund.
        """
        ecken = rechteck(0, 0, 6, 5)
        e, f = self.gerechnet_ohne_probe(ecken, waende(ecken, 0, 3))
        self.assertEqual({w for _, w in e.aufteilungen.zellen}, {None})
        self.assertEqual(self.ausfall(e), [
            "Platte P: auf 30.00 m² trägt keine Richtung – in x liegt sie nur auf «W3», und nichts "
            "hält ihre Drehung; in y liegt sie nur auf «W0», und nichts hält ihre Drehung. Dort fällt "
            "die Last aus; es fehlt ein Lager oder ein Unterzug."])
        self.assertAlmostEqual(f.nicht_getragen, f.summe)
        self.assertFalse(any(m.fehler for m in f.meldungen), "auch der Ausfall je Fall ist grau")

    def test_gleiche_gruende_einmal(self):
        """Eine Platte ganz ohne Lager: in beiden Richtungen derselbe Grund, einmal gesagt."""
        e, _ = self.gerechnet_ohne_probe(rechteck(0, 0, 4, 2), [])
        self.assertEqual(self.ausfall(e), [
            "Platte P: auf 8.00 m² trägt keine Richtung – in x und y liegt sie auf nichts. Dort fällt "
            "die Last aus; es fehlt ein Lager oder ein Unterzug."])

    def test_die_feste_aufteilung_gibt_last_wohin_nichts_traegt(self):
        """Zwischen zwei Wänden in x trägt nur x; fest 30 % in x verliert die übrigen 70 %."""
        ecken = rechteck(0, 0, 4, 2)
        e, f = self.gerechnet_ohne_probe(ecken, waende(ecken, 1, 3), aufteilung=Aufteilung.FEST, anteil=0.3)
        self.assertEqual(self.ausfall(e), [
            "Platte P: auf 8.00 m² gibt die feste Aufteilung 70 % der Last in y, aber in y liegt sie "
            "auf nichts – dieser Teil fällt aus."])
        self.assertAlmostEqual(f.nicht_getragen, 0.7 * f.summe)

    def test_eine_zone_gibt_last_wohin_nichts_traegt(self):
        """Automatisch trägt x alles; die Zone über der linken Hälfte gibt dort alles in y."""
        ecken = rechteck(0, 0, 4, 2)
        e, f = self.gerechnet_ohne_probe(ecken, waende(ecken, 1, 3), zonen=[Zone("Z1", rechteck(0, 0, 2, 2), 0.0)])
        self.assertEqual(self.ausfall(e), [
            "Platte P: auf 4.00 m² gibt die Zone Z1 100 % der Last in y, aber in y liegt sie auf "
            "nichts – dieser Teil fällt aus."])
        self.assertAlmostEqual(f.nicht_getragen, 0.5 * f.summe)
        self.assertEqual({w for _, w in e.aufteilungen.zellen}, {1.0}, "das Bild zeigt die Zone für sich")

    def test_wo_eine_richtung_traegt_kein_ausfall(self):
        ecken = rechteck(0, 0, 4, 2)
        e, f = self.gerechnet_ohne_probe(ecken, waende(ecken, 1, 3))
        self.assertEqual(self.ausfall(e), [])
        self.assertAlmostEqual(f.nicht_getragen, 0.0)


if __name__ == "__main__":
    unittest.main()
