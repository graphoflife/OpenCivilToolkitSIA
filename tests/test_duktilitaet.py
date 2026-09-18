"""Tests für den Duktilitätsnachweis."""

import unittest

from opencivil.core.einheiten import EINHEITSLOS
from opencivil.nachweis import duktilitaet
from opencivil.projekt import Projekt
from opencivil.web import dienst


def projekt_mit(lagen=(True, False, False, True), **abweichungen) -> Projekt:
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.duktilitaet = list(lagen)
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    return projekt


def urteile(projekt: Projekt):
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, {u.name: u for u in loesung.urteile}


class TestDruckzonenhoehe(unittest.TestCase):
    """Die Formel für sich, ohne Rechenwerk."""

    def test_von_hand(self):
        """
        0.85 · x · b · f_cd = A_s · f_sd

            x = 2450e-6 · 434.78e6 / (0.85 · 1.0 · 20e6)
              = 1065.2e3 / 17.0e6
              = 62.7 mm
        """
        x = duktilitaet.druckzonenhoehe(
            a_s=2450e-6, f_sd=434.78e6, b=1.0, f_cd=20.0e6)
        self.assertAlmostEqual(x * 1e3, 62.7, delta=0.1)

    def test_die_grenze_steht_als_benannte_groesse_da(self):
        """Eine 0.35 mitten in einer Bedingung sagt niemandem, was sie ist."""
        self.assertAlmostEqual(duktilitaet.GRENZE, 0.35)


class TestNachweis(unittest.TestCase):
    def test_erste_lage_von_hand(self):
        """
        1. Lage, x: Grund ⌀18@150 (A = 1696 mm², z = 261 mm) und Zulage
        ⌀12@150 (A = 754 mm², z = 258 mm).

            A_s = 2450 mm²
            z   = (1696·261 + 754·258)/2450 = 260.1 mm
            d   = z                (untere Lage -> gedrückt ist oben)
            x   = 62.7 mm
            x/d = 0.241 ≤ 0.35     -> erfüllt
            α   = 0.35/0.241 = 1.45
        """
        aufbau, gefunden = urteile(projekt_mit())
        erg = aufbau.duktilitaet["q1"].ergebnisse[0]
        self.assertEqual(erg.lage.nummer, 1)
        self.assertAlmostEqual(erg.a_s * 1e6, 2450.0, delta=2.0)
        self.assertAlmostEqual(erg.d * 1e3, 260.1, delta=0.2)
        self.assertAlmostEqual(erg.x * 1e3, 62.7, delta=0.2)
        self.assertAlmostEqual(erg.verhaeltnis, 0.241, delta=0.002)
        self.assertTrue(erg.erfuellt)
        self.assertAlmostEqual(erg.erfuellungsgrad, 1.45, delta=0.02)

    def test_der_erfuellungsgrad_ist_die_grenze_durch_das_verhaeltnis(self):
        aufbau, _ = urteile(projekt_mit((True, True, True, True)))
        for erg in aufbau.duktilitaet["q1"].ergebnisse:
            if not erg.machbar:
                continue
            with self.subTest(lage=erg.lage.nummer):
                self.assertAlmostEqual(
                    erg.erfuellungsgrad, duktilitaet.GRENZE / erg.verhaeltnis)

    def test_bei_den_oberen_lagen_wird_von_unten_gemessen(self):
        """
        d gilt ab der **gedrückten** Randfaser. Bei einer oberen Lage ist das
        die Unterkante, also d = h - z. Wer hier z stehen liesse, bekäme eine
        Zahl, die keine statische Höhe ist -- derselbe Fehler, der beim
        Querkraftnachweis einmal d = 39 mm lieferte.
        """
        aufbau, _ = urteile(projekt_mit((True, False, False, True)))
        nach_lage = {e.lage.nummer: e for e in aufbau.duktilitaet["q1"].ergebnisse}
        h = 0.300

        unten = nach_lage[1]
        self.assertAlmostEqual(unten.d, unten.z)

        oben = nach_lage[4]
        self.assertAlmostEqual(oben.d, h - oben.z)
        self.assertLess(oben.z, h / 2)          # liegt wirklich oben
        self.assertGreater(oben.d, h / 2)

    def test_eine_lage_zaehlt_mit_ihrem_schwerpunkt(self):
        """
        Grundbewehrung und Zulage liegen auf leicht verschiedenen Höhen, sind
        aber eine Lage. Gerechnet wird mit dem gemeinsamen Schwerpunkt.
        """
        ohne = projekt_mit()
        ohne.querschnitte[0].lagen[0].zulage.durchmesser = 0.0
        mit = projekt_mit()

        a, _ = urteile(ohne)
        b, _ = urteile(mit)
        nur_grund = a.duktilitaet["q1"].ergebnisse[0]
        beide = b.duktilitaet["q1"].ergebnisse[0]

        self.assertGreater(beide.a_s, nur_grund.a_s)
        # Die Zulage liegt weiter innen, zieht den Schwerpunkt also nach oben.
        self.assertLess(beide.d, nur_grund.d)
        # Mehr Stahl bei kleinerem Hebel: die Druckzone wird tiefer.
        self.assertGreater(beide.verhaeltnis, nur_grund.verhaeltnis)

    def test_zu_viel_bewehrung_faellt_durch(self):
        projekt = projekt_mit()
        lage = projekt.querschnitte[0].lagen[0]
        lage.grund.durchmesser = 34.0
        lage.grund.abstand = 75.0
        aufbau, gefunden = urteile(projekt)
        erg = aufbau.duktilitaet["q1"].ergebnisse[0]
        self.assertGreater(erg.verhaeltnis, duktilitaet.GRENZE)
        self.assertFalse(erg.erfuellt)
        self.assertLess(gefunden["Duktilität – 1. Lage"].erfuellungsgrad.si, 1.0)

    def test_eingeschaltet_aber_unbewehrt(self):
        """
        Kein Fehler der Beschreibung, sondern ein Urteil mit Hinweis. Ohne
        Bewehrung gibt es keine Druckzone, deren Höhe sich begrenzen liesse.
        """
        projekt = projekt_mit((True, True, False, True))
        lage = projekt.querschnitte[0].lagen[1]
        lage.grund.durchmesser = 0.0
        lage.zulage.durchmesser = 0.0

        aufbau, gefunden = urteile(projekt)
        urteil = gefunden["Duktilität – 2. Lage"]
        self.assertFalse(urteil.erfuellt)
        self.assertIn("nicht machbar, weil die 2. Lage nicht definiert",
                      urteil.hinweis)
        # Ohne Verhaeltnis gibt es nichts zu vergleichen -- dann steht dort ein
        # Strich und nicht eine erfundene Null.
        self.assertIsNone(urteil.einwirkung)
        self.assertIsNone(urteil.widerstand)

    def test_nur_die_gewaehlten_lagen(self):
        aufbau, gefunden = urteile(projekt_mit((False, True, False, False)))
        namen = [n for n in gefunden if n.startswith("Duktilität")]
        self.assertEqual(namen, ["Duktilität – 2. Lage"])

    def test_ohne_gewaehlte_lage_laeuft_der_nachweis_gar_nicht(self):
        aufbau, gefunden = urteile(projekt_mit((False, False, False, False)))
        self.assertEqual(aufbau.duktilitaet, {})
        self.assertFalse([n for n in gefunden if n.startswith("Duktilität")])

    def test_das_urteil_traegt_den_raum_seiner_platte(self):
        _, gefunden = urteile(projekt_mit())
        for name, urteil in gefunden.items():
            if name.startswith("Duktilität"):
                self.assertTrue(urteil.raum.startswith("querschnitt.q1"), urteil.raum)

    def test_die_herleitung_zeigt_die_rechnung(self):
        from opencivil.core.protokoll import GleichungBlock

        aufbau = projekt_mit().aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        bloecke = [b for b in loesung.protokoll.alle_bloecke()
                   if isinstance(b, GleichungBlock)]
        titel = [b.titel for b in bloecke]
        for erwartet in ("Kräftegleichgewicht bei M_Ed = 0", "Bedingung",
                         "Druckzonenhöhe bei reiner Biegung",
                         "Bezogene Druckzonenhöhe"):
            self.assertIn(erwartet, titel)
        # Die Zahlen stehen mit drin, nicht bloss die Formel.
        rechnung = next(b for b in bloecke
                        if b.titel == "Druckzonenhöhe bei reiner Biegung")
        self.assertIn(r"\mathrm{mm}^{2}", rechnung.latex)


class TestVorgabeUndAblage(unittest.TestCase):
    def test_vorgabe_sind_die_beiden_aeusseren_lagen(self):
        self.assertEqual(Projekt.beispiel().querschnitt("q1").duktilitaet,
                         [True, False, False, True])

    def test_eine_beschreibung_ohne_das_feld_bekommt_die_vorgabe(self):
        """Eine Datei aus der Zeit vor diesem Nachweis muss weiter laufen."""
        d = Projekt.beispiel().als_dict()
        for q in d["querschnitte"]:
            q.pop("duktilitaet", None)
        projekt = Projekt.aus_dict(d)
        self.assertEqual(projekt.querschnitt("q1").duktilitaet,
                         [True, False, False, True])

    def test_eine_zu_kurze_liste_wird_ergaenzt(self):
        d = Projekt.beispiel().als_dict()
        d["querschnitte"][0]["duktilitaet"] = [False, True]
        projekt = Projekt.aus_dict(d)
        self.assertEqual(projekt.querschnitt("q1").duktilitaet,
                         [False, True, False, True])

    def test_die_wahl_ueberlebt_die_datei(self):
        projekt = projekt_mit((False, True, True, False))
        kopie = Projekt.aus_dict(projekt.als_dict())
        self.assertEqual(kopie.querschnitt("q1").duktilitaet,
                         [False, True, True, False])


class TestInDerZusammenfassung(unittest.TestCase):
    def test_die_zeilen_stehen_unter_den_tragsicherheitsnachweisen(self):
        antwort = dienst.bearbeite(
            "rechnen", {"projekt": Projekt.beispiel().als_dict()})
        namen = [z["zellen"][0]
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        # Erst die Tragsicherheit, dann die Duktilität, dann die Mindestbewehrung.
        self.assertTrue(all(n.startswith(r"\text{M-N") for n in namen[:6]))
        self.assertEqual(namen[6:8], [r"\text{D: 1. Lage}", r"\text{D: 4. Lage}"])
        self.assertTrue(all(n.startswith(r"\text{M\_Riss") for n in namen[8:]))

    def test_eine_unbewehrte_lage_meldet_sich_sichtbar(self):
        projekt = projekt_mit((True, True, False, True))
        lage = projekt.querschnitte[0].lagen[1]
        lage.grund.durchmesser = 0.0
        lage.zulage.durchmesser = 0.0

        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
        betroffen = next(z for z in zeilen if z["zellen"][0] == r"\text{D: 2. Lage}")
        self.assertIn("nicht machbar", betroffen["hinweis"])
        # Widerstand und Einwirkung sind Striche, keine erfundenen Nullen.
        self.assertEqual(betroffen["zellen"][1], r"\text{--}")
        self.assertEqual(betroffen["zellen"][2], r"\text{--}")
