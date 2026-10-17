"""
Fallnamen: eindeutig je Liste, auch als Kennung -- gemeldet vor dem Rechnen.

Die Nachweise legen ihre Ergebnisse unter dem Fallnamen ab, in Wert-IDs:
«Wand A» und «Wand-A» würden beide «Wand_A». Bis 2026-10-17 prüften das nur
drei von neun Listen; bei den übrigen meldete das Rechenwerk «bereits mit
abweichender Definition bekannt», und bei zwei gleichen Kombinationen sprach
die Meldung von häufigen Lastfällen «(70 %)», die niemand eingegeben hatte.
Gleiche Namen hielten ausserdem schon das Öffnen auf -- ein abgelegtes
Projekt liess sich dann nicht mehr laden.
"""

import unittest

from opencivil.projekt import Projekt, ProjektFehler
from opencivil.web import dienst


def platte(p):
    return p.querschnitte[0]


def analyse(p):
    return p.querschnittsanalysen[0]


#: Je Liste: wie ein Fall mit diesem Namen hineinkommt.
LISTEN = {
    "Tragsicherheit der Platte": lambda p, n: platte(p).einwirkung(n, M_Ed=50.0),
    "Knicken der Platte": lambda p, n: platte(p).knickfall(n, N_Ed=-500.0),
    "Spannung-Dehnung der Platte": lambda p, n: platte(p).spannungsfall(n, M_Ed=10.0),
    "Verformung der Platte": lambda p, n: platte(p).verformungsfall(n, w=5.0, laenge=6.0),
    "häufige Lastfälle der Platte": lambda p, n: platte(p).haeufig.lastfall(n, M_Ed=10.0),
    "Lastfälle der Analyse": lambda p, n: analyse(p).lastfall(n, M_y_Ed=10.0),
    "Knicken der Analyse": lambda p, n: analyse(p).knickfall(n, N_Ed=-500.0),
    "Spannung-Dehnung der Analyse": lambda p, n: analyse(p).spannungsfall(n, M_Ed=10.0),
    "Kombinationen des Grundbruchs": lambda p, n: p.grundbrueche[0].kombination(n, N_Ed=100.0),
}


def mit_zwei(liste: str, erster: str, zweiter: str) -> Projekt:
    p = Projekt.beispiel()
    for name in (erster, zweiter):
        LISTEN[liste](p, name)
    return p


class TestNamen(unittest.TestCase):

    def test_jede_liste_meldet_gleiche_und_fast_gleiche_namen(self):
        for liste in LISTEN:
            for erster, zweiter in (("Wand A", "Wand A"), ("Wand A", "Wand-A")):
                with self.subTest(liste=liste, namen=(erster, zweiter)):
                    with self.assertRaises(ProjektFehler) as fehler:
                        mit_zwei(liste, erster, zweiter).aufbauen()
                    text = str(fehler.exception)
                    self.assertNotIn("abweichender Definition", text)
                    self.assertIn(f"'{zweiter}'", text)
                    if erster != zweiter:
                        self.assertIn(f"'{erster}' und '{zweiter}'", text)

    def test_oeffnen_geht_und_rechnen_meldet(self):
        roh = mit_zwei("Tragsicherheit der Platte", "Wand A", "Wand A").als_dict()
        self.assertEqual(dienst.bearbeite("pruefen", {"projekt": roh}).status, 200)
        gerechnet = dienst.bearbeite("rechnen", {"projekt": roh})
        self.assertEqual(gerechnet.status, 400)
        self.assertIn("'Wand A' ist zweimal", gerechnet.daten["fehler"])

    def test_die_tragsicherheit_zuerst(self):
        """Ihre Namen, nicht die daraus abgeleiteten häufigen Lastfälle «(70 %)»."""
        with self.assertRaises(ProjektFehler) as fehler:
            mit_zwei("Tragsicherheit der Platte", "Feld A", "Feld-A").aufbauen()
        self.assertIn("'Feld A' und 'Feld-A'", str(fehler.exception))
        self.assertNotIn("%", str(fehler.exception))

    def test_gleiche_namen_in_verschiedenen_listen_gehen(self):
        p = Projekt.beispiel()
        LISTEN["Tragsicherheit der Platte"](p, "Wand A")
        LISTEN["Knicken der Platte"](p, "Wand A")
        p.aufbauen()


if __name__ == "__main__":
    unittest.main()
