"""
Die Breite gilt nur in x -- in y wird immer je Laufmeter gerechnet.

Eine Platte hat eine Angabe ``b``, und die beschreibt einen Streifen in
x-Richtung. Die Bewehrung in y liegt quer dazu und ist mit ihrer Teilung auf
den Laufmeter bezogen; sie hat von ``b`` nichts mitbekommen. Wer beide
Richtungen mit derselben Breite rechnet, bekommt bei b = 2000 mm in y den
doppelten Widerstand aus derselben Bewehrung.

Geprüft wird darum nicht eine Zahl, sondern ein Verhalten: was passiert, wenn
man ``b`` verdoppelt? In x muss sich alles mitbewegen, in y nichts. Und ein
halb so breiter Streifen mit halben M und N ist dieselbe Platte -- jeder Grad
bleibt, wie er war.
"""

import unittest

from opencivil.projekt import Projekt
from opencivil.querschnitt.platte import BREITE_Y_MM, Richtung


def geloest(b_mm: float):
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.b = b_mm
    # Die Beispielplatte trägt in beiden Richtungen: 2. und 3. Lage in x,
    # 1. und 4. in y. Genau das braucht dieser Test -- nachgewiesen wird zwar
    # nur x, aber die y-Bewehrung steht im Querschnitt und muss ihre eigene
    # Breite behalten.
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.alle_nachweisziele())


def wert(loesung, kennung: str) -> float:
    return loesung.werte[kennung].groesse.si


class TestBreiteJeRichtung(unittest.TestCase):
    def setUp(self):
        self.einfach, self.l1 = geloest(1000.0)
        self.doppelt, self.l2 = geloest(2000.0)

    # -- Die Angabe selbst --------------------------------------------------

    def test_die_breite_in_y_haengt_nicht_an_der_eingabe(self):
        qs = self.doppelt.querschnitte["q1"]
        self.assertAlmostEqual(wert(self.l2, qs.id_von("b")), 2.0)
        self.assertAlmostEqual(wert(self.l2, qs.id_breite(Richtung.Y)),
                               BREITE_Y_MM / 1000.0)

    # -- Bewehrungsquerschnitte ---------------------------------------------

    def _flaeche(self, loesung, marke: str) -> float:
        return wert(loesung, f"querschnitt.q1.lage.{marke}.a_s")

    def test_die_y_lage_bleibt_wie_sie_war(self):
        self.assertAlmostEqual(self._flaeche(self.l2, "1g"),
                               self._flaeche(self.l1, "1g"), places=9)

    def test_das_bewehrungsmass_bleibt_dasselbe(self):
        """
        Dieselbe Platte, nur ein breiterer Streifen: je Kubikmeter Beton liegt
        gleich viel Stahl. Wäre die y-Lage mit b gerechnet, stiege die Zahl.
        """
        qs = self.einfach.querschnitte["q1"]
        self.assertAlmostEqual(wert(self.l1, qs.d_bewehrungsmass.id),
                               wert(self.l2, qs.d_bewehrungsmass.id),
                               places=6)


class TestHalbeBreiteHalbeSchnittgroessen(unittest.TestCase):
    def test_jeder_grad_bleibt(self):
        """
        M und N gelten je b, V je Meter. Kommt irgendwo eine Breite aus der
        falschen Richtung -- A_s je Laufmeter gegen b, ein Widerstand je
        Meter gegen M je b --, weicht mindestens ein Grad ab.
        """
        def grade(b_mm: float, anteil: float):
            projekt = Projekt.beispiel()
            q = projekt.querschnitte[0]
            q.b = b_mm
            q.sproede = q.duktilitaet = q.zwaengung = q.zwaengung_biegung = True
            q.rissanforderung = "erhoeht"
            q.haeufig.aus_tragsicherheit = q.quasistaendig.aus_tragsicherheit = True
            for k in q.kombinationen:
                k.M_Ed *= anteil
                k.N_Ed *= anteil
            aufbau = projekt.aufbauen()
            loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele(),
                                        ohne_herleitung=True)
            return [(u.art, u.fall, u.erfuellungsgrad.si) for u in loesung.urteile]

        voll, halb = grade(1000.0, 1.0), grade(500.0, 0.5)
        self.assertEqual([u[:2] for u in voll], [u[:2] for u in halb])
        self.assertGreater(len(voll), 10)
        for (art, fall, grad), (_, _, grad_halb) in zip(voll, halb):
            with self.subTest(nachweis=art, fall=fall):
                self.assertAlmostEqual(grad_halb, grad, places=6)


if __name__ == "__main__":
    unittest.main()
