"""
Tests für das Rechnen ohne Oberfläche.

Die Fassade legt dieselben Einträge an wie die Maske und rechnet dieselben
Ziele. Geprüft wird darum vor allem das: dass sie nichts anderes baut und
nichts anderes rechnet -- und dass ein Tippfehler auffällt, statt still ein
anderes Projekt zu ergeben.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from opencivil.projekt import (
    GebrauchsfallEintrag, KnickEintrag, KombinationEintrag, Projekt, ProjektFehler,
)

WURZEL = Path(__file__).resolve().parents[1]


def einfach() -> Projekt:
    projekt = Projekt("Probe")
    projekt.beton("C30/37")
    projekt.stahl("B500B")
    return projekt


class TestAnlegen(unittest.TestCase):
    def test_baustoffe_bekommen_kennungen(self):
        projekt = einfach()
        self.assertEqual([(m.kennung, m.art, m.sorte) for m in projekt.materialien],
                         [("b1", "beton", "C30/37"), ("s1", "betonstahl", "B500B")])

    def test_eine_unbekannte_sorte_faellt_sofort_auf(self):
        """An der Zeile, in der sie steht -- nicht erst beim Rechnen."""
        with self.assertRaises(ProjektFehler) as fehler:
            Projekt().beton("C31/37")
        self.assertIn("C31/37", str(fehler.exception))

    def test_dieselbe_normsorte_zweimal(self):
        projekt = einfach()
        with self.assertRaises(ProjektFehler):
            projekt.beton("C30/37")

    def test_x_innen_liegt_auf_der_zweiten_und_dritten_lage(self):
        q = einfach().platte("P", x=[18, 14], y=[10, 8])
        durchmesser = [(q.richtung_von(n).value, l.grund.durchmesser)
                       for n, l in enumerate(q.lagen, start=1)]
        self.assertEqual(durchmesser,
                         [("y", 10.0), ("x", 18.0), ("x", 14.0), ("y", 8.0)])

    def test_x_aussen(self):
        q = einfach().platte("P", x=[18, 14], y=[10, 8], x_innen=False)
        durchmesser = [(q.richtung_von(n).value, l.grund.durchmesser)
                       for n, l in enumerate(q.lagen, start=1)]
        self.assertEqual(durchmesser,
                         [("x", 18.0), ("y", 10.0), ("y", 8.0), ("x", 14.0)])

    def test_zulage_und_teilung(self):
        q = einfach().platte("P", x=[18, 12], x_zulage=[12, 0], teilung=200)
        zweite = q.lagen[1]
        self.assertEqual((zweite.grund.durchmesser, zweite.grund.abstand), (18.0, 200.0))
        self.assertEqual((zweite.zulage.durchmesser, zweite.zulage.abstand), (12.0, 200.0))
        self.assertTrue(all(l.stahl == "s1" for l in q.lagen))

    def test_ohne_startlast(self):
        """Die Vorlage der Oberfläche bringt «Feld» mit -- die Fassade nicht."""
        self.assertEqual(einfach().platte("P").kombinationen, [])

    def test_weitere_felder_als_stichwort(self):
        q = einfach().platte("P", b=800, rissanforderung="hoch", duktilitaet=True)
        self.assertEqual((q.b, q.rissanforderung, q.duktilitaet), (800, "hoch", True))

    def test_ein_vertipptes_feld_wird_gemeldet(self):
        with self.assertRaises(ProjektFehler) as fehler:
            einfach().platte("P", riss_anforderung="hoch")
        self.assertIn("rissanforderung", str(fehler.exception))

    def test_falsche_anzahl_durchmesser(self):
        with self.assertRaises(ProjektFehler) as fehler:
            einfach().platte("P", x=[18])
        self.assertIn("zwei Durchmesser", str(fehler.exception))

    def test_ohne_beton_oder_mit_zweien(self):
        with self.assertRaises(ProjektFehler) as fehler:
            Projekt().platte("P")
        self.assertIn("projekt.beton(", str(fehler.exception))

        projekt = einfach()
        projekt.beton("C25/30")
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.platte("P")
        self.assertIn("beton=", str(fehler.exception))
        q = projekt.platte("P", beton="b2")
        self.assertEqual(q.beton, "b2")

    def test_lastfaelle_landen_in_ihrer_liste(self):
        q = einfach().platte("P")
        self.assertIsInstance(q.einwirkung("Feld", M_Ed=10, V_Ed=5), KombinationEintrag)
        self.assertIsInstance(q.haeufig.lastfall("H", M_Ed=7), GebrauchsfallEintrag)
        q.quasistaendig.lastfall("Q", M_Ed=6)
        knick = q.knickfall("K", N_Ed=-500, laenge=4)
        self.assertEqual([k.name for k in q.kombinationen], ["Feld"])
        self.assertEqual(q.haeufig.faelle, [GebrauchsfallEintrag("H", M_Ed=7)])
        self.assertEqual(q.quasistaendig.faelle, [GebrauchsfallEintrag("Q", M_Ed=6)])
        self.assertIsInstance(knick, KnickEintrag)
        self.assertEqual(knick.knicklaenge, 4, "ohne Angabe gleich der Länge")

    def test_das_beispiel_ist_mit_der_fassade_gebaut(self):
        """
        Der Schnappschuss-Test rechnet das Beispiel -- damit prüft er die
        Fassade mit. Hier nur, dass es wirklich über sie entsteht.
        """
        q = Projekt.beispiel().querschnitte[0]
        self.assertEqual(q.querkraftbewehrung.stahl, "s1")
        self.assertEqual([k.name for k in q.kombinationen],
                         ["Feld", "Feld mit Druck", "Stütze"])


class TestRechnen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ergebnis = Projekt.beispiel().rechnen()

    def test_dasselbe_wie_die_oberflaeche(self):
        """Dieselben Urteile mit denselben Graden wie der Webdienst."""
        from opencivil.web import dienst

        web = dienst.rechnen({"projekt": Projekt.beispiel().als_dict()})
        self.assertEqual(
            [(u["name"], u["erfuellungsgrad"]) for u in web["urteile"]],
            [(u.name, u.gradtext()) for u in self.ergebnis.urteile])

    def test_urteile_je_platte(self):
        self.assertEqual(self.ergebnis.urteile_von("q1"),
                         self.ergebnis.urteile_von("Decke über EG"))
        with self.assertRaises(KeyError):
            self.ergebnis.urteile_von("Dach")

    def test_die_zusammenfassung(self):
        text = self.ergebnis.zusammenfassung()
        self.assertTrue(text.startswith("Decke über EG\n"))
        self.assertIn("Biegung und Normalkraft  Feld mit Druck", text)
        self.assertIn("Alle geführten Nachweise erfüllt.", text)
        # Der still verfehlte Nachweis steht darunter, knapp unter eins.
        self.assertIn("Nicht geführt, geht aber nicht auf", text)
        self.assertIn("0.996", text)
        self.assertEqual(str(self.ergebnis), text)

    def test_zwei_platten_zwei_tabellen(self):
        projekt = Projekt.beispiel()
        dach = projekt.platte("Dach", h=200, x=[10, 10])
        dach.einwirkung("Feld", M_Ed=300)
        ergebnis = projekt.rechnen()
        text = ergebnis.zusammenfassung()
        dachteil = text[text.index("Dach\n"):]
        self.assertIn("NICHT ERFÜLLT", dachteil)
        self.assertNotIn("NICHT ERFÜLLT", text[:text.index("Dach\n")])
        self.assertIn("Mindestens ein Nachweis ist NICHT erfüllt.", text)
        self.assertFalse(ergebnis.erfuellt)

    def test_oberflaeche_und_konsole_fuehren_dieselben_zeilen(self):
        """
        Beide setzen dieselbe Zusammenfassung, nur anders. Vorher baute jede
        ihre Zeilen selbst -- und ein still verfehlter Nachweis hiess in der
        Oberflaeche anders als auf der Konsole.
        """
        from opencivil.bericht import konsole
        from opencivil.bericht.zusammenfassung import zusammenfassen
        from opencivil.web import api

        projekt = Projekt.beispiel()
        dach = projekt.platte("Dach", h=200, x=[10, 10])
        dach.einwirkung("Feld", M_Ed=300)
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_ziele())
        web = api.zusammenfassungen(loesung, aufbau)
        text = konsole.zusammenfassung(zusammenfassen(aufbau, loesung))

        self.assertEqual(sorted(web), ["q1", "q2"])
        for kennung, tabelle in web.items():
            with self.subTest(platte=kennung):
                name = projekt.querschnitt(kennung).name
                teil = text[text.index(f"{name}\n"):]
                for zeile in tabelle["zeilen"]:
                    self.assertIn(zeile["zellen"][4]["mathe"], teil)
                for still in tabelle["stille"]:
                    self.assertIn(f"{still['nachweis']} – {still['fall']}: "
                                  f"α_eff = {still['grad']}", teil)
                self.assertTrue(tabelle["stille"], "die Probe braucht einen stillen")

    def test_eine_platte_ohne_einwirkung(self):
        projekt = einfach()
        projekt.platte("Leer")
        text = projekt.rechnen().zusammenfassung()
        self.assertIn("Kein Nachweis geführt.", text)
        self.assertIn("keine Schnittgrössen angegeben", text)

    def test_bericht_und_latex(self):
        self.assertIn("Herleitung", self.ergebnis.bericht())
        with tempfile.TemporaryDirectory() as ordner:
            ausgabe = self.ergebnis.latex(Path(ordner) / "probe")
            tex = Path(ordner, "probe.tex").read_text(encoding="utf-8")
        self.assertEqual(ausgabe.tex_pfad.name, "probe.tex")
        # Die Nachweise je Platte, mit derselben Tabelle wie der Bildschirm.
        self.assertIn(r"\section{Nachweise}", tex)
        self.assertIn("Nachweis & Bezeichnung & Widerstand & Einwirkung", tex)

    def test_die_analysen_ohne_oberflaeche(self):
        """
        Die Spannung-Dehnung-Analyse war nur ueber die Schnittstelle zu
        haben. Jetzt liefert das Ergebnis sie selbst -- dieselben, die die
        Oberflaeche zeichnet.
        """
        from opencivil.projekt import SpannungsfallEintrag
        from opencivil.web import diagrammdaten

        projekt = Projekt.beispiel()
        projekt.querschnitte[0].spannungsfaelle = [
            SpannungsfallEintrag("Feld", M_Ed=80.0),
            SpannungsfallEintrag("Linie", art="moment_kruemmung")]
        ergebnis = projekt.rechnen()
        feld, linie = ergebnis.analysen()["q1"]
        self.assertAlmostEqual(feld.bild.M / 1e3, 80.0, places=3)
        self.assertGreater(linie.kurve.M_Rd, linie.kurve.M_Riss)
        bilder = diagrammdaten.spannungsanalysen(ergebnis.aufbau, ergebnis.loesung)["q1"]
        self.assertAlmostEqual(bilder[0]["bild"]["M"], feld.bild.M / 1e3)

    def test_ein_wert_mit_herkunft(self):
        wert = self.ergebnis.wert("beton.b1.f_cd")
        self.assertEqual(wert.formatiert(), "20")


class TestEinstieg(unittest.TestCase):
    def test_from_opencivil_import_projekt(self):
        from opencivil import Projekt as P

        self.assertIs(P, Projekt)

    def test_der_kern_zieht_die_nachweise_nicht_nach(self):
        """``Projekt`` wird erst beim Zugriff geladen."""
        ausgabe = subprocess.run(
            [sys.executable, "-c",
             "import sys, opencivil.core.einheiten; "
             "print('opencivil.projekt' in sys.modules)"],
            cwd=WURZEL, capture_output=True, text=True, check=True)
        self.assertEqual(ausgabe.stdout.strip(), "False")

    def test_die_vorfuehrung_laeuft(self):
        import demo_nachweis

        with tempfile.TemporaryDirectory() as ordner:
            from contextlib import redirect_stdout
            from io import StringIO

            with redirect_stdout(StringIO()) as text:
                demo_nachweis.main(Path(ordner))
            self.assertTrue(Path(ordner, "decke_ueber_eg.tex").exists())
            gespeichert = Projekt.laden(Path(ordner, "decke_ueber_eg.json"))
        self.assertIn("Zusammenfassung", text.getvalue())
        self.assertEqual(gespeichert.querschnitte[0].rissanforderung, "erhoeht")


if __name__ == "__main__":
    unittest.main()
