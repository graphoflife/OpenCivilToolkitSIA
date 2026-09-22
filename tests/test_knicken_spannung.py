"""Tests für Spannungsbegrenzung und Knicknachweis."""

import unittest

from opencivil.nachweis import knicken as knick_modul
from opencivil.projekt import KnickEintrag, Projekt
from opencivil.web import dienst


def urteile(projekt: Projekt):
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, {u.name: u for u in loesung.urteile}


class TestSpannungsbegrenzung(unittest.TestCase):
    def projekt(self, anforderung="hoch", **abweichungen) -> Projekt:
        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        q.rissanforderung = anforderung
        for name, wert in abweichungen.items():
            setattr(q, name, wert)
        return projekt

    def test_bei_normaler_anforderung_entfaellt_er(self):
        """In Tabelle 17 steht dort ein Strich."""
        aufbau, gefunden = urteile(self.projekt("normal"))
        self.assertEqual(aufbau.spannung, {})
        self.assertFalse([n for n in gefunden if n.startswith("Stahlspannung")])

    def test_bei_erhoehter_anforderung_laeuft_er(self):
        """
        Er läuft -- still, solange die 70 % nicht eingeschaltet sind. Die
        Abschätzung ist bequem, aber nicht selbstverständlich; sie ungefragt
        in die Tabelle zu stellen hiesse, sie zur Norm zu erklären.
        """
        aufbau, gefunden = urteile(self.projekt("erhoeht"))
        self.assertEqual(sorted(aufbau.spannung), ["q1.x", "q1.y"])
        self.assertTrue([n for n in gefunden if n.startswith("Stahlspannung")])
        self.assertTrue(all(n.still for n in aufbau.spannung.values()))

    def test_mit_den_siebzig_prozent_wird_er_laut(self):
        aufbau, _ = urteile(
            self.projekt("erhoeht", haeufige_aus_tragsicherheit=True))
        laut = [u.fall for u in aufbau.spannung["q1.x"].urteile if not u.still]
        self.assertIn("Feld (70 %)", laut)

    def test_die_grenze_ist_f_yd_minus_80(self):
        _, gefunden = urteile(self.projekt("hoch"))
        urteil = next(u for n, u in gefunden.items() if n.startswith("Stahlspannung"))
        # B500B: f_yd = 434.8, minus 80 -> 354.8 N/mm²
        self.assertAlmostEqual(urteil.widerstand.groesse.si / 1e6, 354.8, delta=0.5)

    def test_die_ebene_erzeugt_die_einwirkung(self):
        """Das ist die Aussage der Mitschrift -- also wird sie geprüft."""
        aufbau, _ = urteile(self.projekt("hoch"))
        for erg in aufbau.spannung["q1.x"].ergebnisse:
            with self.subTest(fall=erg.fall.name):
                self.assertTrue(erg.konvergiert)
                self.assertAlmostEqual(erg.N_int, erg.fall.N_Ed.si,
                                       delta=max(1.0, abs(erg.fall.N_Ed.si) * 1e-5))
                self.assertAlmostEqual(erg.M_int, erg.fall.M_Ed.si,
                                       delta=max(1.0, abs(erg.fall.M_Ed.si) * 1e-5))

    def test_die_siebzig_prozent_kommen_aus_dem_kern(self):
        aufbau, _ = urteile(self.projekt("hoch"))
        faelle = {e.fall.name: e.fall for e in aufbau.spannung["q1.x"].ergebnisse}
        self.assertIn("Feld (70 %)", faelle)
        self.assertAlmostEqual(faelle["Feld (70 %)"].M_Ed.si / 1e3, 70.0, delta=0.01)

    def test_eigene_lastfaelle_statt_der_ableitung(self):
        """
        Ohne die 70 % zählen nur die eigenen Fälle. Gerechnet wird die
        Abschätzung trotzdem -- still, damit ein Hinweis stehen kann, wenn sie
        nicht aufgeht.
        """
        from opencivil.projekt import HaeufigEintrag

        projekt = self.projekt("hoch")
        q = projekt.querschnitte[0]
        q.haeufige_aus_tragsicherheit = False
        q.haeufige = [HaeufigEintrag("Gebrauch", M_Ed=60.0, N_Ed=0.0, richtung="x")]
        aufbau, _ = urteile(projekt)
        spannung = aufbau.spannung["q1.x"]
        self.assertEqual([u.fall for u in spannung.urteile if not u.still],
                         ["Gebrauch"])
        self.assertIn("Feld (70 %)", [e.fall.name for e in spannung.ergebnisse])

    def test_mehr_moment_gibt_mehr_spannung(self):
        wenig = self.projekt("hoch")
        viel = self.projekt("hoch")
        for k in viel.querschnitte[0].kombinationen:
            k.M_Ed *= 1.5
        a, _ = urteile(wenig)
        b, _ = urteile(viel)
        self.assertLess(a.spannung["q1.x"].ergebnisse[0].sigma_s,
                        b.spannung["q1.x"].ergebnisse[0].sigma_s)


class TestSchiefstellung(unittest.TestCase):
    def test_die_riegel_greifen(self):
        """α_i = min[max(0.01/√l; 1/300); 1/200]."""
        self.assertAlmostEqual(knick_modul.schiefstellung(0.5), 1 / 200)   # kurz
        self.assertAlmostEqual(knick_modul.schiefstellung(4.0), 0.005)     # dazwischen
        self.assertAlmostEqual(knick_modul.schiefstellung(20.0), 1 / 300)  # lang


class TestKnicken(unittest.TestCase):
    def projekt(self, *faelle) -> Projekt:
        projekt = Projekt.beispiel()
        projekt.querschnitte[0].knickfaelle = list(faelle)
        return projekt

    def test_gedrungen_und_maessig_belastet_ist_stabil(self):
        aufbau, gefunden = urteile(self.projekt(
            KnickEintrag("Stütze", N_Ed=-800.0, M_Ed_1=20.0,
                         laenge=4.0, knicklaenge=4.0)))
        erg = aufbau.knicken["q1"].ergebnisse[0]
        self.assertTrue(erg.stabil)
        self.assertTrue(gefunden["Knicken – Stütze"].erfuellt)
        # Die Probe: die gefundene Ebene erzeugt die Schnittgrössen.
        self.assertAlmostEqual(erg.N_int / 1e3, -800.0, delta=1.0)
        self.assertAlmostEqual(erg.M_int / 1e3, erg.M_ges / 1e3, delta=0.5)

    def test_schlank_und_stark_belastet_knickt(self):
        """
        Nicht erfüllt, und zwar nicht wegen einer Spannung: es gibt gar keine
        Gleichgewichtslage mehr.
        """
        aufbau, gefunden = urteile(self.projekt(
            KnickEintrag("schlank", N_Ed=-1500.0, M_Ed_1=30.0,
                         laenge=12.0, knicklaenge=12.0)))
        erg = aufbau.knicken["q1"].ergebnisse[0]
        self.assertFalse(erg.stabil)
        self.assertFalse(gefunden["Knicken – schlank"].erfuellt)
        self.assertIn("keine Gleichgewichtslage", gefunden["Knicken – schlank"].hinweis)

    def test_der_erfuellungsgrad_ist_ein_verhaeltnis_von_normalkraeften(self):
        """
        N_Rd/|N_Ed| -- und beide stehen als Betrag in der Tabelle.

        Über Momente zu vergleichen ginge nur, solange es ein Gleichgewicht
        gibt; beim Knicken fehlt gerade das.
        """
        aufbau, gefunden = urteile(self.projekt(
            KnickEintrag("Stütze", N_Ed=-800.0, M_Ed_1=20.0,
                         laenge=4.0, knicklaenge=4.0)))
        urteil = gefunden["Knicken – Stütze"]
        erg = aufbau.knicken["q1"].ergebnisse[0]
        self.assertEqual(urteil.einwirkung.groesse.si, 800e3)
        self.assertAlmostEqual(urteil.widerstand.groesse.si, erg.N_Rd, delta=1.0)
        self.assertAlmostEqual(urteil.erfuellungsgrad.si, erg.N_Rd / 800e3,
                               places=6)

    def test_auch_ein_knickender_stab_bekommt_einen_grad(self):
        """
        Vorher stand dort nichts: ohne Gleichgewicht gab es kein Moment und
        damit keine Zahl. Ein Nachweis ohne Zahl sagt aber nicht, wie weit er
        danebenliegt.
        """
        _, gefunden = urteile(self.projekt(
            KnickEintrag("schlank", N_Ed=-1500.0, M_Ed_1=30.0,
                         laenge=12.0, knicklaenge=12.0)))
        urteil = gefunden["Knicken – schlank"]
        self.assertFalse(urteil.erfuellt)
        self.assertLess(urteil.erfuellungsgrad.si, 1.0)
        self.assertGreater(urteil.erfuellungsgrad.si, 0.0)
        # N_Rd ist die Kraft, bei der er gerade noch steht.
        self.assertLess(urteil.widerstand.groesse.si, 1500e3)

    def test_die_grenzkraft_traegt_und_ein_bisschen_mehr_nicht(self):
        """Die Probe auf die Halbierung: bei N_Rd steht er, knapp darüber nicht."""
        aufbau, _ = urteile(self.projekt(
            KnickEintrag("Stütze", N_Ed=-800.0, M_Ed_1=20.0,
                         laenge=6.0, knicklaenge=6.0)))
        nachweis = aufbau.knicken["q1"]
        erg = nachweis.ergebnisse[0]
        loeser = nachweis.loeser
        l_cr = 6.0
        self.assertTrue(nachweis._gleichgewicht(loeser, erg.N_Rd * 0.999,
                                                erg, l_cr).traegt)
        self.assertFalse(nachweis._gleichgewicht(loeser, erg.N_Rd * 1.02,
                                                 erg, l_cr).traegt)

    def test_die_iteration_steht_schritt_fuer_schritt_da(self):
        """
        Das Verfahren ist die Iteration -- also wird sie gezeigt, nicht nur
        ihr Ergebnis. Jeder Durchlauf trägt das Moment, mit dem er gerechnet
        hat, und die Krümmung, die dabei herauskam.
        """
        aufbau, _ = urteile(self.projekt(
            KnickEintrag("Stütze", N_Ed=-800.0, M_Ed_1=20.0,
                         laenge=4.0, knicklaenge=4.0)))
        erg = aufbau.knicken["q1"].ergebnisse[0]
        self.assertGreaterEqual(len(erg.schritte), 2)
        self.assertEqual(erg.schritte[0].nummer, 1)
        # Begonnen wird ohne Verformung.
        self.assertEqual(erg.schritte[0].e_2d_vorher, 0.0)
        # Und der letzte Durchlauf ist der, der in der Herleitung steht.
        self.assertAlmostEqual(erg.schritte[-1].M_ziel, erg.M_ges, delta=1.0)
        self.assertAlmostEqual(erg.schritte[-1].e_2d, erg.e_2d, places=9)

    def test_eine_laengere_knicklaenge_ist_unguenstiger(self):
        kurz, _ = urteile(self.projekt(
            KnickEintrag("k", N_Ed=-800.0, M_Ed_1=20.0, laenge=3.0, knicklaenge=3.0)))
        lang, _ = urteile(self.projekt(
            KnickEintrag("k", N_Ed=-800.0, M_Ed_1=20.0, laenge=7.0, knicklaenge=7.0)))
        self.assertLess(kurz.knicken["q1"].ergebnisse[0].e_2d,
                        lang.knicken["q1"].ergebnisse[0].e_2d)

    def test_zug_braucht_keinen_knicknachweis(self):
        _, gefunden = urteile(self.projekt(
            KnickEintrag("Zug", N_Ed=200.0, M_Ed_1=20.0, laenge=4.0, knicklaenge=4.0)))
        urteil = gefunden["Knicken – Zug"]
        self.assertTrue(urteil.erfuellt)
        self.assertIn("setzt eine Druckkraft voraus", urteil.hinweis)

    def test_ohne_knickfall_laeuft_er_nicht(self):
        aufbau, gefunden = urteile(Projekt.beispiel())
        self.assertEqual(aufbau.knicken, {})
        self.assertFalse([n for n in gefunden if n.startswith("Knicken")])

    def test_die_knickfaelle_ueberleben_die_datei(self):
        import json
        projekt = self.projekt(
            KnickEintrag("Stütze", N_Ed=-900.0, M_Ed_1=25.0,
                         laenge=5.0, knicklaenge=3.5))
        kopie = Projekt.aus_dict(json.loads(json.dumps(projekt.als_dict())))
        fall = kopie.querschnitt("q1").knickfaelle[0]
        self.assertEqual((fall.name, fall.N_Ed, fall.M_Ed_1), ("Stütze", -900.0, 25.0))
        self.assertEqual((fall.laenge, fall.knicklaenge), (5.0, 3.5))
