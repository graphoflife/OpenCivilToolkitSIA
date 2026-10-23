"""
Die Setzung eines Flachfundaments auf geschichtetem Baugrund (opencivil.geotechnik.setzung).

Der Einflussfaktor gegen die Tabellen 8.4 und 8.5 des Kapitels 8, das der
Benutzer geliefert hat, das Beispiel der Tabelle 8.4 als Ganzes, Wieder- und
Erstbelastung (Kap. 8.5), starr und schlaff (Kap. 8.10), die Teilschichten,
die Pruefungen der Eingabe und was die Oberflaeche davon zu sehen bekommt.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import angaben, nachweistabelle, zusammenfassen
from opencivil.geotechnik.setzung import K, einflussfaktor, einflussfaktor_ecke
from opencivil.projekt import Projekt, ProjektFehler, SetzungEintrag
from opencivil.web import dienst
from opencivil.web.api import katalog


def rechnen(schichten=(("Ton", 4.0, 10.0, 30.0),), **felder):
    """Eine Setzung mit diesen Schichten -- je Name, d in m, M_E und M'_E in MN/m²."""
    p = Projekt(name="Probe")
    s = p.setzung("F", **{"B": 2.0, "L": 3.0, "q_E": 100.0, **felder})
    for name, d, M_E, M_E_strich in schichten:
        s.schicht(name, d=d, M_E=M_E, M_E_strich=M_E_strich)
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    nachweis = aufbau.setzung["w1"]
    urteil = next(u for u in loesung.urteile if u.raum == nachweis.id)
    return aufbau, loesung, loesung.befunde[nachweis.id], urteil


def grenztiefe(L_durch_B: float, J: float) -> float:
    """z/B, in der J unter dem Punkt K auf ``J`` gefallen ist -- halbiert, B = 1."""
    unten, oben = 1e-3, 100.0
    for _ in range(100):
        mitte = (unten + oben) / 2.0
        if einflussfaktor(L_durch_B, 1.0, K * L_durch_B, K, mitte) > J:
            unten = mitte
        else:
            oben = mitte
    return unten


class TestEinflussfaktorWieDasKapitel(unittest.TestCase):

    def test_j_k_wie_tabelle_8_4(self):
        """Bauwerk 15 × 8 m, Punkt K: J_K in ‰ auf die gedruckte Stelle."""
        for z, soll in ((5, 428), (6, 378), (7, 336), (8, 302), (9, 272)):
            with self.subTest(z=z):
                self.assertEqual(round(1000 * einflussfaktor(15.0, 8.0, K * 15.0, K * 8.0, z)),
                                 soll)

    def test_grenztiefen_wie_tabelle_8_5(self):
        """
        z/B, in der J = Δσ'_z/Δσ' unter K auf den Grenzwert fällt. Die Tabelle
        nennt eine Stelle; bei L/B = 5 und 10 liegt sie bis 0.23 neben der
        Formel -- abgelesen, nicht gerechnet --, darum die Toleranz.
        """
        tabelle = {0.20: (1.2, 1.6, 2.1, 2.4, 3.0), 0.15: (1.5, 2.0, 2.7, 3.2, 4.2),
                   0.10: (1.9, 2.7, 3.6, 4.4, 6.2), 0.05: (3.0, 4.1, 5.9, 7.2, None)}
        for J, zeile in tabelle.items():
            for L_durch_B, soll in zip((1.0, 2.0, 5.0, 10.0, 1000.0), zeile):
                with self.subTest(J=J, L_durch_B=L_durch_B):
                    ist = grenztiefe(L_durch_B, J)
                    if soll is None:
                        self.assertGreater(ist, 10.0)
                    else:
                        self.assertAlmostEqual(ist, soll, delta=max(0.1, 0.035 * soll))

    def test_in_der_sohle_die_ganze_pressung(self):
        self.assertEqual(einflussfaktor_ecke(2.0, 3.0, 0.0), 0.25)
        for x, y in ((K * 3.0, K * 2.0), (1.5, 1.0)):
            self.assertAlmostEqual(einflussfaktor(3.0, 2.0, x, y, 0.0), 1.0)
            self.assertAlmostEqual(einflussfaktor(3.0, 2.0, x, y, 1e-9), 1.0, places=6)

    def test_ecke_ist_symmetrisch_und_nimmt_ab(self):
        for z in (0.1, 1.0, 5.0):
            self.assertAlmostEqual(einflussfaktor_ecke(2.0, 5.0, z),
                                   einflussfaktor_ecke(5.0, 2.0, z))
        tiefen = [0.1 * i for i in range(1, 100)]
        werte = [einflussfaktor_ecke(2.0, 5.0, z) for z in tiefen]
        self.assertEqual(werte, sorted(werte, reverse=True))

    def test_unter_der_mitte_mehr_als_unter_k(self):
        for z in (0.5, 1.0, 2.0, 5.0, 10.0):
            self.assertGreater(einflussfaktor(3.0, 2.0, 1.5, 1.0, z),
                               einflussfaktor(3.0, 2.0, K * 3.0, K * 2.0, z))


class TestBeispielDerTabelle84(unittest.TestCase):
    """
    Das Bauwerk 15 × 8 m auf Kiessand über Ton, Δσ' = 60 kN/m², M_E = 4000
    kN/m² im Ton, Teilschichten von 1 m. Der Kiessand setzt sich im Kapitel
    gar nicht; hier trägt er mit M_E = 10⁶ MN/m² nichts Messbares bei.
    """

    @classmethod
    def setUpClass(cls):
        cls.befund = rechnen((("Kiessand", 5.0, 1e6, 1e6), ("Ton", 4.0, 4.0, 24.0)),
                             B=8.0, L=15.0, q_E=60.0, dz=1.0)[2]

    def test_j_mittel_je_teilschicht(self):
        ton = [t for t in self.befund.teilschichten if t.schicht == 1]
        self.assertEqual([round(1000 * t.J) for t in ton], [403, 357, 319, 287])

    def test_setzung_je_teilschicht(self):
        """Die Tabelle rundet Δσ'_z vorher auf eine Stelle -- 24.2 statt 24.17 kN/m²."""
        ton = [t for t in self.befund.teilschichten if t.schicht == 1]
        for t, soll in zip(ton, (0.0061, 0.0054, 0.0048, 0.0043)):
            self.assertAlmostEqual(t.ds_E, soll, delta=0.00007)

    def test_rund_zwei_zentimeter(self):
        """«Im Beispiel ergibt sich eine rechnerische Setzung von 2,1 cm aus der Tonschicht.»"""
        self.assertAlmostEqual(self.befund.schichten[1].s, 0.021, delta=0.0006)
        self.assertLess(self.befund.schichten[0].s, 1e-6)
        self.assertEqual(self.befund.s_W, 0.0)

    def test_am_fuss_wie_die_letzte_zeile(self):
        self.assertEqual(round(1000 * self.befund.J_fuss), 272)


class TestWiederUndErstbelastung(unittest.TestCase):
    """Kap. 8.5: die Wiederbelastung mit M'_E, die Erstbelastung mit M_E."""

    def test_jede_pressung_mit_ihrem_modul(self):
        nur_e = rechnen(q_W=0.0, q_E=100.0)[2]
        nur_w = rechnen(q_W=100.0, q_E=0.0)[2]
        beide = rechnen(q_W=100.0, q_E=100.0)[2]
        # M'_E = 3 M_E: dieselbe Pressung setzt in Wiederbelastung ein Drittel.
        self.assertAlmostEqual(nur_w.s_W, nur_e.s_E / 3.0, places=12)
        self.assertEqual(nur_e.s_W, 0.0)
        self.assertEqual(nur_w.s_E, 0.0)
        self.assertAlmostEqual(beide.s, nur_w.s + nur_e.s, places=12)

    def test_gleiche_moduln_nur_die_summe_zaehlt(self):
        a = rechnen((("Ton", 4.0, 10.0, 10.0),), q_W=40.0, q_E=60.0)[2]
        b = rechnen((("Ton", 4.0, 10.0, 10.0),), q_W=0.0, q_E=100.0)[2]
        self.assertAlmostEqual(a.s, b.s, places=12)

    def test_von_hand_eine_teilschicht(self):
        """Eine Schicht, so dünn wie Δz: Δs = J̄ q Δz / M mit J an Ober- und Unterkante."""
        befund = rechnen((("Ton", 0.5, 10.0, 30.0),), q_W=20.0, q_E=80.0)[2]
        x, y = K * 3.0, K * 2.0
        J = (einflussfaktor(3.0, 2.0, x, y, 0.0) + einflussfaktor(3.0, 2.0, x, y, 0.5)) / 2.0
        self.assertAlmostEqual(befund.s_W, J * 20e3 * 0.5 / 30e6, places=15)
        self.assertAlmostEqual(befund.s_E, J * 80e3 * 0.5 / 10e6, places=15)


class TestTeilschichten(unittest.TestCase):

    def test_gleich_dick_und_hoechstens_dz(self):
        befund = rechnen((("Kies", 1.25, 50.0, 150.0), ("Ton", 2.0, 8.0, 24.0)), dz=0.5)[2]
        dicken = [t.z_u - t.z_o for t in befund.teilschichten]
        self.assertEqual([t.schicht for t in befund.teilschichten], [0, 0, 0, 1, 1, 1, 1])
        for dicke, soll in zip(dicken, [1.25 / 3] * 3 + [0.5] * 4):
            self.assertAlmostEqual(dicke, soll, places=12)
        # Die Schichtgrenze ist eine Grenze von Teilschichten.
        self.assertAlmostEqual(befund.teilschichten[2].z_u, 1.25, places=12)
        self.assertAlmostEqual(befund.teilschichten[3].z_o, 1.25, places=12)

    def test_feiner_geteilt_kaum_anders(self):
        """Die Mittelung je Teilschicht nähert das Integral: mit Δz/10 bleibt es auf 2 %."""
        grob = rechnen(dz=0.5)[2].s
        fein = rechnen(dz=0.05)[2].s
        self.assertAlmostEqual(grob, fein, delta=0.02 * fein)


class TestStarrUndSchlaff(unittest.TestCase):

    def test_schlaff_unter_der_mitte_mehr(self):
        starr = rechnen(steifigkeit="starr")
        schlaff = rechnen(steifigkeit="schlaff")
        self.assertEqual(starr[2].punkt, (K * 3.0, K * 2.0))
        self.assertEqual(schlaff[2].punkt, (1.5, 1.0))
        self.assertGreater(schlaff[2].s, starr[2].s)
        self.assertEqual(starr[3].fall, "starr, Punkt K")
        self.assertEqual(schlaff[3].fall, "schlaff, Mitte")


class TestNachweis(unittest.TestCase):

    def test_erfuellungsgrad_ist_zulaessig_durch_vorhanden(self):
        _, _, befund, urteil = rechnen(s_zul=50.0)
        self.assertTrue(urteil.erfuellt)
        self.assertAlmostEqual(urteil.erfuellungsgrad.si, 0.05 / befund.s, places=12)
        self.assertAlmostEqual(urteil.einwirkung.groesse.si, befund.s, places=12)
        self.assertEqual(urteil.widerstand.groesse.si, 0.05)
        self.assertEqual(urteil.langname, "Setzung")

    def test_zu_viel_setzung(self):
        _, _, befund, urteil = rechnen(s_zul=5.0)
        self.assertGreater(befund.s, 0.005)
        self.assertFalse(urteil.erfuellt)
        self.assertLess(urteil.erfuellungsgrad.si, 1.0)

    def test_ohne_pressung_keine_setzung(self):
        _, _, befund, urteil = rechnen(q_E=0.0)
        self.assertEqual(befund.s, 0.0)
        self.assertTrue(urteil.erfuellt)
        self.assertTrue(math.isinf(urteil.erfuellungsgrad.si))

    def test_ohne_schicht_kein_nachweis(self):
        p = Projekt(name="Probe")
        p.setzung("Leer", q_E=100.0)
        aufbau = p.aufbauen()
        self.assertEqual(aufbau.setzung, {})
        self.assertIn("Setzung 'Leer': keine Schicht → kein Nachweis.", aufbau.warnungen)


class TestEingaben(unittest.TestCase):

    def test_neu_mit_einer_schicht_ohne_pressung(self):
        neu = SetzungEintrag.neu(kennung="w1", name="F")
        self.assertEqual(len(neu.schichten), 1)
        self.assertEqual((neu.q_W, neu.q_E), (0.0, 0.0))

    def test_unmoegliche_zahlen_vor_dem_rechnen(self):
        for felder, schicht, satz in (
                ({"B": 0.0}, {}, "Breite B muss grösser als null sein"),
                ({"q_W": -10.0}, {}, "q_W kann nicht negativ sein"),
                ({"s_zul": 0.0}, {}, "s_zul muss grösser als null sein"),
                ({"dz": 0.0}, {}, "Δz_max muss grösser als null sein"),
                ({}, {"d": 0.0}, "Dicke d muss grösser als null sein"),
                ({}, {"M_E": 0.0}, "M_E muss grösser als null sein"),
                ({}, {"M_E_strich": -1.0}, "M'_E muss grösser als null sein")):
            with self.subTest(felder=felder, schicht=schicht):
                p = Projekt(name="Probe")
                s = p.setzung("F", **felder)
                s.schicht("Ton", **{"d": 2.0, "M_E": 10.0, "M_E_strich": 30.0, **schicht})
                with self.assertRaises(ProjektFehler) as fehler:
                    p.aufbauen()
                self.assertIn(satz, str(fehler.exception))

    def test_eine_steifigkeit_die_es_nicht_gibt(self):
        with self.assertRaises(ProjektFehler) as fehler:
            Projekt(name="Probe").setzung("F", steifigkeit="halbstarr")
        self.assertIn("'halbstarr' gibt es als 'steifigkeit' nicht", str(fehler.exception))

    def test_datei_hin_und_zurueck(self):
        p = Projekt(name="Probe")
        s = p.setzung("F", B=2.0, L=3.0, q_W=20.0, q_E=80.0, steifigkeit="schlaff")
        s.schicht("Ton", d=4.0, M_E=10.0, M_E_strich=30.0)
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.als_dict(), p.als_dict())
        self.assertEqual(wieder.setzungen[0].schichten[0].M_E_strich, 30.0)


class TestWasDieOberflaecheSieht(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.antwort = dienst.bearbeite("rechnen", {"projekt": Projekt.beispiel().als_dict()})

    def test_katalog(self):
        k = katalog()
        self.assertEqual(k["neue_setzung"]["schichten"][0]["name"], "Schicht 1")
        self.assertEqual(k["felder"]["schicht"]["M_E"]["einheit"], "MN/m²")
        self.assertEqual(k["felder"]["setzung"]["q_W"]["einheit"], "kN/m²")
        self.assertEqual([s["wert"] for s in k["setzung"]["steifigkeiten"]], ["starr", "schlaff"])

    def test_situation(self):
        self.assertEqual(self.antwort.status, 200)
        s = self.antwort.daten["setzungen"]["w1"]
        self.assertEqual(s["punkt"], "Punkt K")
        self.assertEqual(s["lage"], [K * 2.5, K * 2.0])
        self.assertEqual([x["name"] for x in s["schichten"]],
                         ["Kies, sandig", "Silt, tonig", "Moräne"])
        self.assertAlmostEqual(s["s"], sum(x["s"] for x in s["schichten"]), places=9)
        self.assertEqual(s["linie"][0], [0.0, 1.0])
        self.assertAlmostEqual(s["linie"][-1][0], 9.0)
        self.assertTrue(s["erfuellt"])

    def test_zusammenfassung_mit_den_schichten(self):
        p = Projekt.beispiel()
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        teil = next(b for b in zusammenfassen(aufbau, loesung).bauteile if b.kennung == "w1")
        kopf, schichten = angaben(aufbau, "w1", loesung)
        self.assertEqual(kopf.titel, "Angaben zum Fundament")
        self.assertIn("starr, Punkt K", kopf.latex)
        self.assertEqual([z[0] for z in schichten.zeilen],
                         ["Kies, sandig", "Silt, tonig", "Moräne"])
        tabelle = nachweistabelle(teil)
        self.assertEqual([z[:2] for z in tabelle.zeilen], [["Setzung", "starr, Punkt K"]])


if __name__ == "__main__":
    unittest.main()
