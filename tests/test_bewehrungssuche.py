"""
Die Bewehrung suchen lassen.

Geprüft wird nicht, welcher Durchmesser herauskommt -- das hinge an den
Normsorten des Beispiels und wäre bei der ersten Änderung dort falsch.
Geprüft wird, was die Suche *zusagt*: dass das Ergebnis alle eingeschalteten
Nachweise erfüllt, dass es das kleinste ist, das sie erfüllt, und dass sie
ehrlich Nein sagt, wo es keines gibt.
"""

import unittest

from opencivil import bewehrungssuche as suche
from opencivil.projekt import KnickEintrag, Projekt
from opencivil.web import dienst


def platte(**abweichungen) -> Projekt:
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    return projekt


def schlechtester(projekt) -> float:
    return suche.bewerte(projekt).grad


class TestSuche(unittest.TestCase):
    def test_das_ergebnis_erfuellt_alle_nachweise(self):
        """Die eine Zusage, die das Werkzeug macht."""
        projekt = platte()
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        self.assertGreaterEqual(schlechtester(projekt), 1.0)

    def test_ein_durchmesser_kleiner_reicht_nicht(self):
        """
        Die zweite Zusage: es ist das *kleinste* Ergebnis. Nimmt man irgendwo
        einen Durchmesser zurück, geht mindestens ein Nachweis nicht mehr auf.
        """
        projekt = platte()
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ergebnis.gefunden)

        for marke, d in ergebnis.beste.durchmesser.items():
            kleiner = [x for x in suche.DURCHMESSER if x < d]
            if not kleiner:
                continue
            probe = platte()
            suche.uebernehmen(probe, "q1", ergebnis.beste)
            lage, art = int(marke[:-1]), ("grund" if marke[-1] == "g" else "zulage")
            getattr(probe.querschnitt("q1").lagen[lage - 1], art).durchmesser = kleiner[-1]
            with self.subTest(posten=marke):
                self.assertLess(schlechtester(probe), 1.0)

    def test_ohne_kraefte_bleibt_weniger_stahl(self):
        """
        Ohne Einwirkungen fallen M-N und Querkraft weg; übrig bleiben die
        Nachweise, die eine Platte unabhängig von der Belastung erfüllen muss.
        Weniger Anforderungen heisst nie mehr Stahl.
        """
        projekt = platte()
        ohne = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_OHNE)
        mit = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertTrue(ohne.gefunden and mit.gefunden)
        self.assertLessEqual(ohne.beste.stahlflaeche, mit.beste.stahlflaeche)

    def test_das_projekt_bleibt_unberuehrt(self):
        """Gesucht wird auf einer Kopie -- sonst wäre ein Versuch eine Änderung."""
        projekt = platte()
        vorher = projekt.als_dict()
        suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertEqual(projekt.als_dict(), vorher)

    def test_grund_und_zulage_teilen_die_teilung(self):
        projekt = platte()
        ergebnis = suche.suche(
            projekt, "q1", modus=suche.Suchmodus.GRUND_OHNE_ZULAGE_MIT)
        self.assertTrue(ergebnis.gefunden, ergebnis.begruendung)
        suche.uebernehmen(projekt, "q1", ergebnis.beste)
        for lage in projekt.querschnitt("q1").lagen:
            if lage.grund.durchmesser and lage.zulage.durchmesser:
                self.assertEqual(lage.grund.abstand, lage.zulage.abstand)

    def test_nur_die_angegebenen_teilungen_kommen_heraus(self):
        ergebnis = suche.suche(platte(), "q1", teilungen=[125.0],
                               modus=suche.Suchmodus.GRUND_OHNE)
        self.assertTrue(ergebnis.gefunden)
        self.assertEqual(ergebnis.beste.teilung, 125.0)

    def test_eine_unloesbare_platte_sagt_warum(self):
        """
        Eine zu dünne Platte bekommt kein Ergebnis -- und das Werkzeug erfindet
        auch keins. Der Grund steht dabei, sonst steht dort nur ein Nein.
        """
        projekt = platte(h=80.0)
        for k in projekt.querschnitt("q1").kombinationen:
            k.M_Ed = 400.0
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_MIT)
        self.assertFalse(ergebnis.gefunden)
        self.assertTrue(ergebnis.begruendung)
        self.assertTrue(any(l.begruendung for l in ergebnis.loesungen))

    def test_eine_leere_lage_wird_nicht_erfunden(self):
        """
        Welche Lage es gibt, ist eine Anordnung und keine Suche. Steht dort
        null, bleibt dort null.
        """
        projekt = platte()
        for nummer in (2, 3):
            projekt.querschnitt("q1").lagen[nummer - 1].grund.durchmesser = 0
        for k in projekt.querschnitt("q1").kombinationen:
            k.richtung = "x"
        ergebnis = suche.suche(projekt, "q1", modus=suche.Suchmodus.GRUND_OHNE)
        self.assertNotIn("2g", ergebnis.beste.durchmesser)
        self.assertNotIn("3g", ergebnis.beste.durchmesser)


class TestNurEingeschaltetes(unittest.TestCase):
    """Gesucht wird gegen das, was eingeschaltet ist -- nicht gegen mehr."""

    def test_ein_ausgeschalteter_nachweis_zaehlt_nicht(self):
        streng = platte()
        for k in streng.querschnitt("q1").kombinationen:
            k.M_Ed = 260.0
        mit = suche.suche(streng, "q1", modus=suche.Suchmodus.GRUND_MIT)

        locker = platte()
        for k in locker.querschnitt("q1").kombinationen:
            k.M_Ed, k.aktiv = 260.0, False
        ohne = suche.suche(locker, "q1", modus=suche.Suchmodus.GRUND_MIT)

        self.assertTrue(mit.gefunden and ohne.gefunden)
        self.assertLess(ohne.beste.stahlflaeche, mit.beste.stahlflaeche)


class TestBuegel(unittest.TestCase):
    def test_ohne_bedarf_keine_buegel(self):
        loesung = suche.buegel_suchen(platte(), "q1")
        self.assertTrue(loesung.gefunden)
        self.assertEqual(loesung.durchmesser, 0.0)

    def test_bei_grosser_querkraft_kommen_welche(self):
        projekt = platte()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 600.0
        loesung = suche.buegel_suchen(projekt, "q1")
        self.assertTrue(loesung.gefunden, loesung.begruendung)
        self.assertGreater(loesung.durchmesser, 0.0)
        suche.buegel_uebernehmen(projekt, "q1", loesung)
        self.assertGreaterEqual(schlechtester(projekt), 1.0)

    def test_das_raster_ist_quadratisch(self):
        projekt = platte()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 600.0
        loesung = suche.buegel_suchen(projekt, "q1")
        suche.buegel_uebernehmen(projekt, "q1", loesung)
        buegel = projekt.querschnitt("q1").querkraftbewehrung
        self.assertEqual(buegel.abstand_x, buegel.abstand_y)


class TestUeberDenDienst(unittest.TestCase):
    def test_die_antwort_traegt_das_fertige_projekt(self):
        antwort = dienst.bearbeite("bewehrung_suchen", {
            "projekt": platte().als_dict(), "kennung": "q1",
            "modus": "grund_mit"})
        self.assertEqual(antwort.status, 200)
        self.assertTrue(antwort.daten["gefunden"])
        # Das Projekt kommt fertig zurück: die Oberfläche soll die gefundenen
        # Durchmesser nicht selbst einsetzen müssen.
        fertig = Projekt.aus_dict(antwort.daten["projekt"])
        self.assertGreaterEqual(schlechtester(fertig), 1.0)

    def test_eine_unbekannte_platte_ist_ein_404(self):
        antwort = dienst.bearbeite("bewehrung_suchen", {
            "projekt": platte().als_dict(), "kennung": "gibt-es-nicht"})
        self.assertEqual(antwort.status, 404)

    def test_ein_unbekannter_modus_nennt_die_moeglichen(self):
        antwort = dienst.bearbeite("bewehrung_suchen", {
            "projekt": platte().als_dict(), "kennung": "q1", "modus": "raten"})
        self.assertEqual(antwort.status, 400)
        self.assertIn("grund_ohne", antwort.daten["fehler"])


class TestSchnellerKnicknachweis(unittest.TestCase):
    """
    Die Abkürzung darf das Urteil nicht ändern.

    Ohne die Suche nach N_Rd steht eine andere Zahl da -- das Verhältnis der
    Momente statt der Kräfte. Erfüllt oder nicht muss gleich herauskommen,
    sonst suchte das Werkzeug gegen andere Nachweise als der Bericht.
    """

    def faelle(self):
        return [
            ("gedrungen", KnickEintrag("K", N_Ed=-600.0, M_Ed_1=20.0,
                                       laenge=3.0, knicklaenge=3.0)),
            ("mittel", KnickEintrag("K", N_Ed=-1800.0, M_Ed_1=40.0,
                                    laenge=5.0, knicklaenge=5.0)),
            ("schlank", KnickEintrag("K", N_Ed=-1500.0, M_Ed_1=30.0,
                                     laenge=12.0, knicklaenge=12.0)),
        ]

    def test_erfuellt_kommt_gleich_heraus(self):
        for name, fall in self.faelle():
            projekt = platte(knickfaelle=[fall])
            with self.subTest(fall=name):
                genau = projekt.aufbauen()
                genau.werk.loese(*genau.alle_nachweisziele())
                kurz = projekt.aufbauen(schnell=True)
                kurz.werk.loese(*kurz.alle_nachweisziele())
                self.assertEqual(
                    genau.knicken["q1"].ergebnisse[0].erfuellt,
                    kurz.knicken["q1"].ergebnisse[0].erfuellt)

    def test_die_abkuerzung_ist_schneller(self):
        import time
        projekt = platte(knickfaelle=[self.faelle()[1][1]])
        t0 = time.perf_counter()
        a = projekt.aufbauen(schnell=True)
        a.werk.loese(*a.alle_nachweisziele())
        kurz = time.perf_counter() - t0
        t0 = time.perf_counter()
        b = projekt.aufbauen()
        b.werk.loese(*b.alle_nachweisziele())
        genau = time.perf_counter() - t0
        self.assertLess(kurz, genau)


if __name__ == "__main__":
    unittest.main()
