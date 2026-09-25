"""Tests für den Rechendienst, den Server und die Brücke zu Pyodide."""

import json
import tempfile
import unittest
from pathlib import Path

from opencivil.projekt import Projekt
from opencivil.web import bruecke, dienst, server


class TestDienst(unittest.TestCase):
    """Der Rechendienst -- ohne Server, ohne Browser, ohne Dateisystem."""

    def rumpf(self, **zusatz):
        return {"projekt": Projekt.beispiel().als_dict(), **zusatz}

    def test_rechnen(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf())
        self.assertEqual(antwort.status, 200)
        self.assertTrue(antwort.daten["vollstaendig"])
        # Nur die gefuehrten Nachweise -- die stillen stehen als Hinweis unter
        # der Zusammenfassung, nicht in dieser Liste.
        # 3 M-N-Fälle in x; mehr ist im Beispiel nicht eingeschaltet.
        self.assertEqual(len(antwort.daten["urteile"]), 3)
        self.assertTrue(antwort.daten["alle_nachweise_erfuellt"])

    def test_rechnen_mit_einzelziel(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf(ziele=["beton.b1.f_cd"]))
        self.assertEqual(set(antwort.daten["werte"]), {
            "beton.b1.eta_fc", "beton.b1.f_ck", "beton.b1.f_cd", "beton.b1.gamma_c",
        })
        self.assertEqual(antwort.daten["reihenfolge"][-1], "beton.b1.f_cd")

    def test_unbekanntes_ziel(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf(ziele=["gibt.es.nicht"]))
        self.assertEqual(antwort.status, 400)
        self.assertIn("gibt.es.nicht", antwort.daten["fehler"])

    def mit_querkraft(self):
        projekt = Projekt.beispiel()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 120.0
        return {"projekt": projekt.als_dict()}

    def test_querkraftkurven_ohne_angabe(self):
        """Ohne gewählte Normalkraft gilt die des ersten Falls der Richtung."""
        antwort = dienst.bearbeite("querkraftkurven", self.mit_querkraft())
        kurven = antwort.daten["querkraftkurven"]
        self.assertEqual(sorted(kurven), ["q1.x"])
        self.assertEqual(kurven["q1.x"]["N_Ed"], 0.0)
        self.assertEqual(len(kurven["q1.x"]["aeste"]), 2)

    def test_querkraftkurven_mit_gewaehlter_normalkraft(self):
        rumpf = {**self.mit_querkraft(), "n_ed": {"q1.x": -300.0}}
        kurven = dienst.bearbeite("querkraftkurven", rumpf).daten["querkraftkurven"]
        self.assertEqual(kurven["q1.x"]["N_Ed"], -300.0)
        self.assertEqual(sorted(kurven), ["q1.x"])   # in y wird nichts geführt

    def test_eine_normalkraft_die_keine_zahl_ist(self):
        """
        Kam als roher ValueError mit Status 500 beim Benutzer an. Die Anfrage
        stammt zwar aus der eigenen Oberfläche, aber das ist keine
        Zusicherung -- sie steht offen im Netz.
        """
        rumpf = {**self.mit_querkraft(), "n_ed": {"q1.x": "viel"}}
        antwort = dienst.bearbeite("querkraftkurven", rumpf)
        self.assertEqual(antwort.status, 400)
        self.assertIn("q1.x", antwort.daten["fehler"])
        self.assertIn("viel", antwort.daten["fehler"])

    def test_leere_normalkraft_faellt_auf_die_vorgabe_zurueck(self):
        for wert in (None, ""):
            rumpf = {**self.mit_querkraft(), "n_ed": {"q1.x": wert}}
            antwort = dienst.bearbeite("querkraftkurven", rumpf)
            self.assertEqual(antwort.status, 200)
            self.assertEqual(antwort.daten["querkraftkurven"]["q1.x"]["N_Ed"], 0.0)

    def test_unbekannte_anfrage(self):
        antwort = dienst.bearbeite("gibtesnicht", {})
        self.assertEqual(antwort.status, 404)
        # Die Meldung soll weiterhelfen, nicht bloss abweisen.
        self.assertIn("rechnen", antwort.daten["fehler"])

    def test_katalog_und_beispiel_brauchen_keinen_rumpf(self):
        self.assertIn("betonsorten", dienst.bearbeite("katalog").daten)
        self.assertTrue(dienst.bearbeite("beispiel").daten["materialien"])

    def test_bericht_schreibt_nichts(self):
        antwort = dienst.bearbeite("bericht", self.rumpf())
        self.assertIn(r"\documentclass", antwort.daten["tex"])
        # Kein Pfad in der Antwort: der Dienst fasst die Platte nicht an.
        self.assertNotIn("tex_pfad", antwort.daten)

    def test_bericht_auch_als_markdown(self):
        """Derselbe Bericht: dieselben Abschnitte, dieselbe Plattentabelle."""
        daten = dienst.bearbeite("bericht", self.rumpf()).daten
        name = Projekt.beispiel().name
        self.assertTrue(daten["markdown"].startswith(f"# {name}\n"))
        for abschnitt in ("Herleitung", "Nachweise", "Werte"):
            self.assertIn(f"\n## {abschnitt}\n", daten["markdown"])
            self.assertIn(rf"\section{{{abschnitt}}}", daten["tex"])
        self.assertIn("| Nachweis | Bezeichnung | Widerstand | Einwirkung |",
                      daten["markdown"])

    def test_pruefen_meldet_kaputte_beschreibung(self):
        kaputt = Projekt.beispiel().als_dict()
        kaputt["materialien"][0]["name"] = kaputt["materialien"][1]["name"]
        antwort = dienst.bearbeite("pruefen", {"projekt": kaputt})
        self.assertEqual(antwort.status, 400)

    def test_pruefen_weist_fremde_dateien_ab(self):
        """
        Projekt.aus_dict ist mit Absicht nachsichtig und macht aus jedem dict
        notfalls ein leeres Projekt. Beim Öffnen einer Datei wäre das fatal:
        eine beliebige JSON-Datei würde die Arbeit wortlos durch nichts
        ersetzen.
        """
        for fremd in ({}, {"foo": 1}, {"einkaufsliste": ["Brot"]}, [1, 2, 3], "text", None):
            with self.subTest(fremd=fremd):
                antwort = dienst.bearbeite("pruefen", {"projekt": fremd})
                self.assertEqual(antwort.status, 400)

    def test_pruefen_nimmt_auch_unvollstaendiges(self):
        """Ein Projekt ohne Querschnitte ist erlaubt -- man fängt ja irgendwo an."""
        antwort = dienst.bearbeite("pruefen", {"projekt": {"name": "Leer"}})
        self.assertEqual(antwort.status, 200)
        self.assertEqual(antwort.daten["projekt"]["name"], "Leer")

    def test_fehler_bringt_den_dienst_nicht_um(self):
        """Auch Unerwartetes kommt als Antwort zurueck, nicht als Ausnahme."""
        antwort = dienst.bearbeite("rechnen", {"projekt": {"materialien": "kein Feld"}})
        self.assertGreaterEqual(antwort.status, 400)
        self.assertIn("fehler", antwort.daten)


class TestDienstUeberJson(unittest.TestCase):
    """Der Weg, den die Bruecke im Browser nimmt."""

    def test_umschlag(self):
        roh = dienst.bearbeite_json(
            "rechnen", json.dumps({"projekt": Projekt.beispiel().als_dict()}))
        umschlag = json.loads(roh)
        self.assertEqual(umschlag["status"], 200)
        self.assertTrue(umschlag["daten"]["vollstaendig"])

    def test_kaputtes_json(self):
        umschlag = json.loads(dienst.bearbeite_json("rechnen", "{nicht json"))
        self.assertEqual(umschlag["status"], 400)

    def test_rumpf_muss_ein_objekt_sein(self):
        umschlag = json.loads(dienst.bearbeite_json("rechnen", "[1, 2, 3]"))
        self.assertEqual(umschlag["status"], 400)

    def test_kein_rumpf(self):
        umschlag = json.loads(dienst.bearbeite_json("katalog"))
        self.assertEqual(umschlag["status"], 200)


class TestServerHuelle(unittest.TestCase):
    """Was der Server über den Dienst hinaus beisteuert."""

    def test_ohne_pdf_bleibt_die_platte_unberuehrt(self):
        antwort = server.bericht_mit_pdf(
            {"projekt": Projekt.beispiel().als_dict(), "pdf": False})
        self.assertIn(r"\documentclass", antwort.daten["tex"])
        self.assertNotIn("tex_pfad", antwort.daten)

    def test_mit_pdf_wird_das_tex_abgelegt(self):
        alt = server.AUSGABE_ORDNER
        try:
            with tempfile.TemporaryDirectory() as ordner:
                server.AUSGABE_ORDNER = Path(ordner)
                antwort = server.bericht_mit_pdf(
                    {"projekt": Projekt.beispiel().als_dict()})
                abgelegt = Path(antwort.daten["tex_pfad"])
                self.assertTrue(abgelegt.is_file())
                # Auf der Platte steht genau das, was auch der Browser bekäme.
                self.assertEqual(
                    abgelegt.read_text(encoding="utf-8"), antwort.daten["tex"])
        finally:
            server.AUSGABE_ORDNER = alt

    def test_statische_pfade_bleiben_im_projekt(self):
        for pfad in ("/../../etc/passwd", "/daten/projekt.json", "/.git/config",
                     "/gibtesnicht", "/tests/test_dienst.py",
                     "/web/../daten/projekt.json"):
            with self.subTest(pfad=pfad):
                self.assertIsNone(server.aufloesen(pfad))

        for pfad in ("/", "/index.html", "/web/index.html",
                     "/opencivil/projekt/projekt.py", "/opencivil/web/dienst.py"):
            with self.subTest(pfad=pfad):
                self.assertIsNotNone(server.aufloesen(pfad))

    def test_der_kern_ist_ueber_das_netz_erreichbar(self):
        """
        Die Brücke im Browser lädt den Rechenkern als ``.py``-Dateien nach.
        Läge ``opencivil/`` nicht im ausgelieferten Baum, bliebe die Seite
        stumm -- lokal wie auf GitHub Pages.
        """
        self.assertIn("opencivil", server.OEFFENTLICH)
        for datei in bruecke.kerndateien():
            with self.subTest(datei=datei):
                self.assertIsNotNone(server.aufloesen("/" + datei))


class TestBruecke(unittest.TestCase):
    """Das Manifest, aus dem der Browser den Rechenkern zusammenliest."""

    def test_manifest_ist_auf_dem_stand_der_quellen(self):
        self.assertTrue(
            bruecke.stimmt_ueberein(),
            "web/kern/dateien.json passt nicht mehr zu den Dateien unter "
            "opencivil/. Bitte 'python3 -m opencivil.web.bruecke' laufen lassen -- "
            "sonst lädt die Seite einen veralteten Kern.")

    def test_der_dienst_ist_im_manifest(self):
        dateien = bruecke.kerndateien()
        self.assertIn("opencivil/web/dienst.py", dateien)
        self.assertIn("opencivil/projekt/projekt.py", dateien)

    def test_kein_zwischenstand_im_manifest(self):
        self.assertFalse(
            [d for d in bruecke.kerndateien() if "__pycache__" in d])

    def test_schreiben_ist_wiederholbar(self):
        """Zweimal geschrieben ergibt zeichengleich dasselbe -- sonst rauscht das Diff."""
        with tempfile.TemporaryDirectory() as ordner:
            a = bruecke.schreiben(Path(ordner) / "a.json").read_text(encoding="utf-8")
            b = bruecke.schreiben(Path(ordner) / "b.json").read_text(encoding="utf-8")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
