"""Tests für den Duktilitätsnachweis."""

import unittest

from opencivil.core.einheiten import EINHEITSLOS
from opencivil.nachweis import duktilitaet
from opencivil.projekt import Projekt
from opencivil.web import dienst


def projekt_mit(an: bool = True, **abweichungen) -> Projekt:
    projekt = Projekt.beispiel()
    q = projekt.querschnitte[0]
    q.duktilitaet = an
    for name, wert in abweichungen.items():
        setattr(q, name, wert)
    return projekt


def x_lagen(projekt: Projekt):
    """Die beiden Lagen, die nachgewiesen werden -- im Beispiel 2 und 3."""
    q = projekt.querschnitte[0]
    return [n for n in (1, 2, 3, 4) if q.richtung_von(n).value == "x"]


def urteile(projekt: Projekt):
    """
    Aufbau und die Urteile, wie sie in der Tabelle stehen.

    `gefuehrte_urteile` und nicht `urteile`: gerechnet wird jede Lage, und
    die rohe Liste traegt sie auch. In die Zusammenfassung kommt je Nachweis
    nur die schlechteste -- und danach fragen diese Tests.
    """
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, {u.name: u for u in loesung.gefuehrte_urteile}


def alle_urteile(projekt: Projekt):
    """Jede Lage einzeln -- so, wie die Bewehrungssuche sie zaehlt."""
    aufbau = projekt.aufbauen()
    return aufbau.werk.loese(*aufbau.alle_nachweisziele()).urteile


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
        2. Lage, x: Grund ⌀18@150 (A = 1696 mm²) und Zulage ⌀12@150
        (A = 754 mm²). Sie liegt innen -- unter ihr die y-Lage ⌀12 --, darum
        ist der Hebel kleiner als bei einer aussen liegenden Lage.

            A_s = 2450 mm²
            d   = z = 248.1 mm     (untere Lage -> gedrückt ist oben)
            x   = 62.7 mm          (hängt nur von A_s ab, nicht von d)
            x/d = 0.253 ≤ 0.35     -> erfüllt
            α   = 0.35/0.253 = 1.39
        """
        aufbau, gefunden = urteile(projekt_mit())
        erg = aufbau.duktilitaet["q1"].ergebnisse[0]
        self.assertEqual(erg.lage.nummer, 2)
        self.assertAlmostEqual(erg.a_s * 1e6, 2450.0, delta=2.0)
        self.assertAlmostEqual(erg.d * 1e3, 248.1, delta=0.2)
        self.assertAlmostEqual(erg.x * 1e3, 62.7, delta=0.2)
        self.assertAlmostEqual(erg.verhaeltnis, 0.253, delta=0.002)
        self.assertTrue(erg.erfuellt)
        self.assertAlmostEqual(erg.erfuellungsgrad, 1.39, delta=0.02)

    def test_der_erfuellungsgrad_ist_die_grenze_durch_das_verhaeltnis(self):
        aufbau, _ = urteile(projekt_mit())
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
        projekt = projekt_mit()
        aufbau, _ = urteile(projekt)
        nach_lage = {e.lage.nummer: e for e in aufbau.duktilitaet["q1"].ergebnisse}
        h = 0.300
        untere, obere = x_lagen(projekt)

        unten = nach_lage[untere]
        self.assertAlmostEqual(unten.d, unten.z)

        oben = nach_lage[obere]
        self.assertAlmostEqual(oben.d, h - oben.z)
        self.assertLess(oben.z, h / 2)          # liegt wirklich oben
        self.assertGreater(oben.d, h / 2)

    def test_eine_lage_zaehlt_mit_ihrem_schwerpunkt(self):
        """
        Grundbewehrung und Zulage liegen auf leicht verschiedenen Höhen, sind
        aber eine Lage. Gerechnet wird mit dem gemeinsamen Schwerpunkt.
        """
        ohne = projekt_mit()
        untere = x_lagen(ohne)[0]
        ohne.querschnitte[0].lagen[untere - 1].zulage.durchmesser = 0.0
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
        untere = x_lagen(projekt)[0]
        lage = projekt.querschnitte[0].lagen[untere - 1]
        lage.grund.durchmesser = 34.0
        lage.grund.abstand = 75.0
        aufbau, gefunden = urteile(projekt)
        erg = aufbau.duktilitaet["q1"].ergebnisse[0]
        self.assertGreater(erg.verhaeltnis, duktilitaet.GRENZE)
        self.assertFalse(erg.erfuellt)
        self.assertLess(
            gefunden[f"Duktilität – {untere}. Lage"].erfuellungsgrad.si, 1.0)

    def test_eingeschaltet_aber_unbewehrt(self):
        """
        Kein Fehler der Beschreibung, sondern ein Urteil mit Hinweis. Ohne
        Bewehrung gibt es keine Druckzone, deren Höhe sich begrenzen liesse.
        """
        projekt = projekt_mit()
        untere = x_lagen(projekt)[0]
        lage = projekt.querschnitte[0].lagen[untere - 1]
        lage.grund.durchmesser = 0.0
        lage.zulage.durchmesser = 0.0

        aufbau, gefunden = urteile(projekt)
        urteil = gefunden[f"Duktilität – {untere}. Lage"]
        self.assertFalse(urteil.erfuellt)
        self.assertIn(f"nicht machbar, weil die {untere}. Lage nicht definiert",
                      urteil.hinweis)
        # Ohne Verhaeltnis gibt es nichts zu vergleichen -- dann steht dort ein
        # Strich und nicht eine erfundene Null.
        self.assertIsNone(urteil.einwirkung)
        self.assertIsNone(urteil.widerstand)

    def test_ein_urteil_und_zwar_das_schlechtere(self):
        """
        Gerechnet werden beide x-Lagen, in der Zusammenfassung steht eine
        Zeile. Vier Zeilen für eine Frage waren drei zuviel -- beantwortet
        wird sie ohnehin von der schlechteren Lage.
        """
        projekt = projekt_mit()
        aufbau, gefunden = urteile(projekt)
        self.assertEqual(len(aufbau.duktilitaet["q1"].ergebnisse), 2)

        dukt = [u for n, u in gefunden.items() if n.startswith("Duktilität")]
        self.assertEqual(len(dukt), 1)
        grade = [e.erfuellungsgrad
                 for e in aufbau.duktilitaet["q1"].ergebnisse]
        self.assertAlmostEqual(dukt[0].erfuellungsgrad.si, min(grade), places=9)

    def test_ausgeschaltet_rechnet_er_still_mit(self):
        projekt = projekt_mit(False)
        aufbau, gefunden = urteile(projekt)
        self.assertTrue(aufbau.duktilitaet["q1"].still)
        # In der Tabelle steht er nicht ...
        self.assertFalse([n for n in gefunden if n.startswith("Duktilität")])
        # ... gerechnet wird er trotzdem, für jede x-Lage.
        dukt = [u for u in alle_urteile(projekt) if u.art == "D"]
        self.assertEqual(len(dukt), 2)
        self.assertTrue(all(u.still for u in dukt))

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
    def test_vorgegeben_ist_er_aus(self):
        """
        Der Nachweis läuft von selbst mit, gefordert ist er nicht: er steht in
        der Norm nicht für jede Platte, und wer ihn führen will, schaltet ihn
        ein. Ungefragt in der Tabelle stünde er sonst bei jeder Platte.
        """
        self.assertIs(Projekt.beispiel().querschnitt("q1").duktilitaet, False)

    def test_eine_beschreibung_ohne_das_feld_bekommt_die_vorgabe(self):
        """Eine Datei aus der Zeit vor diesem Nachweis muss weiter laufen."""
        d = Projekt.beispiel().als_dict()
        for q in d["querschnitte"]:
            q.pop("duktilitaet", None)
        projekt = Projekt.aus_dict(d)
        self.assertIs(projekt.querschnitt("q1").duktilitaet, False)

    def test_eine_alte_liste_wird_zum_schalter(self):
        """
        Früher war das eine Wahl je Lage. Eine Datei von damals bringt die
        Liste noch mit: war irgendein Haken gesetzt, gilt der Nachweis als
        eingeschaltet -- das ist die Lesart, die nichts wegnimmt.
        """
        for liste, erwartet in (([False, True], True),
                                ([True, False, False, True], True),
                                ([False] * 4, False),
                                ([], False)):
            d = Projekt.beispiel().als_dict()
            d["querschnitte"][0]["duktilitaet"] = liste
            with self.subTest(liste=liste):
                self.assertIs(
                    Projekt.aus_dict(d).querschnitt("q1").duktilitaet, erwartet)

    def test_die_wahl_ueberlebt_die_datei(self):
        projekt = projekt_mit(True)
        kopie = Projekt.aus_dict(projekt.als_dict())
        self.assertIs(kopie.querschnitt("q1").duktilitaet, True)


class TestInDerZusammenfassung(unittest.TestCase):
    def test_die_zeile_steht_unter_den_tragsicherheitsnachweisen(self):
        projekt = projekt_mit()
        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        paare = [(z["zellen"][0], z["zellen"][1])
                 for z in antwort.daten["zusammenfassungen"]["q1"]["zeilen"]]
        # Eine Zeile, nicht vier: die ungünstigere der beiden x-Lagen.
        dukt = [pa for pa in paare if pa[0] == r"\text{Duktilität}"]
        self.assertEqual(len(dukt), 1)
        self.assertGreater(
            paare.index(dukt[0]),
            paare.index((r"\text{Biegung und Normalkraft}", r"\text{Feld}")))

    def test_eine_unbewehrte_lage_meldet_sich_sichtbar(self):
        projekt = projekt_mit()
        untere = x_lagen(projekt)[0]
        lage = projekt.querschnitte[0].lagen[untere - 1]
        lage.grund.durchmesser = 0.0
        lage.zulage.durchmesser = 0.0

        antwort = dienst.bearbeite("rechnen", {"projekt": projekt.als_dict()})
        zeilen = antwort.daten["zusammenfassungen"]["q1"]["zeilen"]
        # Die leere Lage ist die schlechtere und steht damit in der Tabelle.
        betroffen = next(z for z in zeilen
                         if z["zellen"][0] == r"\text{Duktilität}")
        self.assertEqual(betroffen["zellen"][1], rf"\text{{{untere}. Lage}}")
        self.assertIn("nicht machbar", betroffen["hinweis"])
        # Widerstand und Einwirkung sind Striche, keine erfundenen Nullen.
        self.assertEqual(betroffen["zellen"][2], r"\text{--}")
        self.assertEqual(betroffen["zellen"][3], r"\text{--}")
