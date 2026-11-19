"""
Fallnamen: eindeutig je Liste, auch als Kennung -- am Namensfeld abgewiesen
und vor dem Rechnen gemeldet, mit denselben Worten (Benutzer, 2026-11-19).

Die Nachweise legen ihre Ergebnisse unter dem Fallnamen ab, in Wert-IDs:
«Wand A» und «Wand-A» würden beide «Wand_A». Bis 2026-10-17 prüften das nur
drei von neun Listen; bei den übrigen meldete das Rechenwerk «bereits mit
abweichender Definition bekannt», und bei zwei gleichen Kombinationen sprach
die Meldung von häufigen Lastfällen «(70 %)», die niemand eingegeben hatte.
Gleiche Namen hielten ausserdem schon das Öffnen auf -- ein abgelegtes
Projekt liess sich dann nicht mehr laden.
"""

import re
import unittest
from pathlib import Path

from opencivil.projekt import Projekt
from opencivil.web import dienst
from tests.unfertig import meldung

WURZEL = Path(__file__).resolve().parents[1]


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
    "Kombinationen des Pfahls": lambda p, n: p.pfaehle[0].kombination(n, N_Ed=100.0),
}


#: Je Liste, wo das Namensfeld sie findet: das Bauteil und der Pfad darin.
ORTE = {
    "Tragsicherheit der Platte": ("q1", "kombinationen"),
    "Knicken der Platte": ("q1", "knickfaelle"),
    "Spannung-Dehnung der Platte": ("q1", "spannungsfaelle"),
    "Verformung der Platte": ("q1", "verformung.faelle"),
    "häufige Lastfälle der Platte": ("q1", "haeufig.faelle"),
    "Lastfälle der Analyse": ("a1", "lastfaelle"),
    "Knicken der Analyse": ("a1", "knickfaelle"),
    "Spannung-Dehnung der Analyse": ("a1", "spannungsfaelle"),
    "Kombinationen des Grundbruchs": ("g1", "kombinationen"),
    "Kombinationen des Pfahls": ("t1", "kombinationen"),
}


def umbenennen(p: Projekt, liste: str, name: str) -> dict:
    """Was das Namensfeld hört, wenn es den letzten Fall der Liste so nennen will."""
    kennung, pfad = ORTE[liste]
    faelle = p.bauteil(kennung)
    for teil in pfad.split("."):
        faelle = getattr(faelle, teil)
    antwort = dienst.bearbeite("fallname", {
        "projekt": p.als_dict(), "kennung": kennung, "pfad": pfad,
        "index": len(faelle) - 1, "name": name})
    assert antwort.status == 200, antwort.daten
    return antwort.daten


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
                    text = meldung(mit_zwei(liste, erster, zweiter))
                    self.assertNotIn("abweichender Definition", text)
                    self.assertIn(f"«{zweiter}» ist als", text)
                    if erster != zweiter:
                        self.assertIn(f"als «{erster}» – die beiden unterscheiden sich nur "
                                      f"in Satz- oder Leerzeichen", text)

    def test_oeffnen_geht_und_rechnen_meldet(self):
        roh = mit_zwei("Tragsicherheit der Platte", "Wand A", "Wand A").als_dict()
        self.assertEqual(dienst.bearbeite("pruefen", {"projekt": roh}).status, 200)
        gerechnet = dienst.bearbeite("rechnen", {"projekt": roh})
        self.assertEqual(gerechnet.status, 200)
        self.assertIn("«Wand A» ist als Tragsicherheitseinwirkung schon vergeben",
                      gerechnet.daten["unfertige"]["querschnitte"]["q1"]["grund"])

    def test_die_tragsicherheit_zuerst(self):
        """Ihre Namen, nicht die daraus abgeleiteten häufigen Lastfälle «(70 %)»."""
        text = meldung(mit_zwei("Tragsicherheit der Platte", "Feld A", "Feld-A"))
        self.assertIn("«Feld-A» ist als Tragsicherheitseinwirkung schon vergeben, als «Feld A»",
                      text)
        self.assertNotIn("%", text)

    def test_das_namensfeld_weist_mit_denselben_worten_ab(self):
        """Was vor dem Rechnen anhielte, nimmt schon das Feld nicht an."""
        for liste in LISTEN:
            with self.subTest(liste=liste):
                p = Projekt.beispiel()
                for name in ("Wand A", "Wand B"):
                    LISTEN[liste](p, name)
                grund = umbenennen(p, liste, "Wand A")["grund"]
                self.assertTrue(grund.startswith("«Wand A» ist als "), grund)
                self.assertIn(grund, meldung(mit_zwei(liste, "Wand A", "Wand A")))
                self.assertEqual(umbenennen(p, liste, "Wand C"), {"grund": ""})
                self.assertEqual(umbenennen(p, liste, "Wand B"), {"grund": ""})

    def test_das_feld_sagt_in_welchem_fenster_der_andere_steht(self):
        """Die sechs Fenster der Spannung-Dehnung-Analysen teilen sich eine Liste."""
        p = Projekt.beispiel()
        platte(p).spannungsfall("Bild", art="moment_kruemmung")
        platte(p).spannungsfall("Neu", M_Ed=10.0)
        self.assertEqual(umbenennen(p, "Spannung-Dehnung der Platte", "Bild"), {
            "grund": "«Bild» ist als Spannung-Dehnung-Analyse schon vergeben, "
                     "im Fenster «Momenten-Krümmungs-Linie»"})

    def test_ein_abgeleiteter_name_ist_schon_vergeben(self):
        p = Projekt.beispiel()
        LISTEN["häufige Lastfälle der Platte"](p, "Eigen")
        abgeleitet = f"{platte(p).kombinationen[0].name} (70 %)"
        self.assertEqual(umbenennen(p, "häufige Lastfälle der Platte", abgeleitet), {
            "grund": f"«{abgeleitet}» ist als häufiger Lastfall schon vergeben, "
                     f"aus der Tragsicherheit abgeleitet"})

    def test_jede_liste_der_oberflaeche_kennt_der_kern(self):
        """
        Die Listen, die eine Fallzeile ihrem Namensfeld nennt (``liste`` in
        web/js), hat auch ein Bauteil -- sonst fragte das Feld ins Leere und
        nähme jeden Namen.
        """
        quelltext = "".join(p.read_text(encoding="utf-8")
                            for p in sorted((WURZEL / "web" / "js").glob("*.js")))
        pfade = set(re.findall(r"pfad: '([^']+)'", quelltext))
        kern = {l.pfad for b in Projekt.beispiel().bauteile() for l in b.fallnamen()}
        self.assertTrue(pfade)
        self.assertLessEqual(pfade, kern)

    def test_gleiche_namen_in_verschiedenen_listen_gehen(self):
        p = Projekt.beispiel()
        LISTEN["Tragsicherheit der Platte"](p, "Wand A")
        LISTEN["Knicken der Platte"](p, "Wand A")
        p.aufbauen()


if __name__ == "__main__":
    unittest.main()
