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
        # 3 M-N-Fälle der Platte in x und ihre Verformung im Feld, dazu
        # Biegung und Querkraft mit Torsion des Unterzugs, Grundbruch und
        # Gleiten des Fundaments, seine Setzung, der äussere und innere
        # Widerstand des Pfahls, quer sein äusserer Widerstand, die
        # Bettungskraft, Biegung und Querkraft im Pfahl, beim Wohnhaus je
        # Richtung die Grenze der Grundschwingzeit; mehr ist im Beispiel
        # nicht eingeschaltet.
        self.assertEqual(len(antwort.daten["urteile"]), 17)
        self.assertTrue(antwort.daten["alle_nachweise_erfuellt"])

    def test_rechnen_mit_einzelziel(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf(ziele=["beton.b1.f_cd"]))
        self.assertEqual(set(antwort.daten["werte"]), {
            "beton.b1.eta_fc", "beton.b1.eta_t", "beton.b1.f_ck", "beton.b1.f_cd",
            "beton.b1.gamma_c",
        })
        self.assertEqual(antwort.daten["reihenfolge"][-1], "beton.b1.f_cd")

    def test_unbekanntes_ziel(self):
        antwort = dienst.bearbeite("rechnen", self.rumpf(ziele=["gibt.es.nicht"]))
        self.assertEqual(antwort.status, 400)
        self.assertIn("gibt.es.nicht", antwort.daten["fehler"])

    def mit_querkraft(self, normalkraft=None):
        projekt = Projekt.beispiel()
        for k in projekt.querschnitt("q1").kombinationen:
            k.V_Ed = 120.0
        projekt.querschnitt("q1").querkraftkurve_normalkraft = normalkraft
        return {"projekt": projekt.als_dict()}

    def kurven(self, rumpf):
        antwort = dienst.bearbeite("rechnen", rumpf)
        self.assertEqual(antwort.status, 200, antwort.daten.get("fehler"))
        return antwort.daten["querkraftkurven"]

    def test_querkraftkurven_ohne_angabe(self):
        """Ohne gewählte Normalkraft gilt die des ersten Falls der Richtung -- und das steht da."""
        kurven = self.kurven(self.mit_querkraft())
        self.assertEqual(sorted(kurven), ["q1.x"])   # in y wird nichts geführt
        self.assertEqual(kurven["q1.x"]["N_Ed"], 0.0)
        self.assertEqual(len(kurven["q1.x"]["aeste"]), 2)
        self.assertIn("Leer: die des ersten Falls", kurven["q1.x"]["hinweis"])

    def test_die_normalkraft_steht_an_der_platte(self):
        """
        Gespeichert mit dem Projekt: bis 2026-11-20 lebte sie neben ihm, und
        nach dem Neuladen galt still wieder die des ersten Falls.
        """
        rumpf = self.mit_querkraft(-300.0)
        geladen = Projekt.aus_dict(rumpf["projekt"])
        self.assertEqual(geladen.querschnitt("q1").querkraftkurve_normalkraft, -300.0)
        kurve = self.kurven({"projekt": geladen.als_dict()})["q1.x"]
        self.assertEqual(kurve["N_Ed"], -300.0)
        self.assertEqual(kurve["hinweis"], "Blass: Punkte mit anderem N.")

    def test_eine_normalkraft_die_keine_zahl_ist(self):
        """Das Projekt weist sie ab, mit Namen und Zahl -- kein Absturz."""
        rumpf = self.mit_querkraft()
        rumpf["projekt"]["querschnitte"][0]["querkraftkurve_normalkraft"] = "viel"
        antwort = dienst.bearbeite("rechnen", rumpf)
        self.assertEqual(antwort.status, 400)
        self.assertIn("viel", antwort.daten["fehler"])

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
        """Beim Öffnen die Form -- zwei gleiche Kennungen; zwei gleiche Namen erst beim Rechnen."""
        kaputt = Projekt.beispiel().als_dict()
        kaputt["materialien"][0]["kennung"] = kaputt["materialien"][1]["kennung"]
        antwort = dienst.bearbeite("pruefen", {"projekt": kaputt})
        self.assertEqual(antwort.status, 400)
        self.assertIn("dieselbe Kennung", antwort.daten["fehler"])

        gleich = Projekt.beispiel().als_dict()
        gleich["materialien"][0]["name"] = gleich["materialien"][1]["name"]
        self.assertEqual(dienst.bearbeite("pruefen", {"projekt": gleich}).status, 200)
        antwort = dienst.bearbeite("rechnen", {"projekt": gleich})
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

    def test_das_notizbuch_wird_ausgeliefert(self):
        """Auch Namen mit Leerzeichen und Umlaut -- der Browser schickt sie verschluesselt."""
        self.assertIsNotNone(server.aufloesen("/notizbuch/Start.md"))
        self.assertIsNotNone(server.aufloesen(
            "/notizbuch/Formelsammlung/Formeln/Statische%20H%C3%B6he.md"))
        self.assertIsNone(server.aufloesen("/notizbuch/%2E%2E/daten/projekt.json"))
        self.assertIsNone(server.aufloesen("/notizbuch%2F..%2F.git%2Fconfig"))
        import mimetypes
        self.assertEqual(mimetypes.guess_type("x.md")[0], "text/markdown; charset=utf-8")

    def test_der_kern_ist_ueber_das_netz_erreichbar(self):
        """
        Das Notizbuch verweist je Modul auf seinen Quelltext
        (``../../opencivil/…``). Läge ``opencivil/`` nicht im ausgelieferten
        Baum, führte jeder dieser Verweise ins Leere -- lokal wie auf GitHub
        Pages. Gerechnet wird im Browser mit dem Paket (``quellen.json``).
        """
        self.assertIn("opencivil", server.OEFFENTLICH)
        for datei in bruecke.kerndateien():
            with self.subTest(datei=datei):
                self.assertIsNotNone(server.aufloesen("/" + datei))


class TestBruecke(unittest.TestCase):
    """
    Was die Brücke für den Browser ablegt: das Manifest, aus dem er den
    Rechenkern zusammenliest, die Formelsammlung und die Versionsmarken der
    Seite.
    """

    def test_manifest_ist_auf_dem_stand_der_quellen(self):
        self.assertTrue(
            bruecke.stimmt_ueberein(),
            "web/kern/dateien.json passt nicht mehr zu den Dateien unter "
            "opencivil/. Bitte 'python3 -m opencivil.web.bruecke' laufen lassen -- "
            "sonst lädt die Seite einen veralteten Kern.")

    def test_das_paket_ist_auf_dem_stand_der_quellen(self):
        self.assertTrue(
            bruecke.quellen_stimmen(),
            "web/kern/quellen.json passt nicht mehr zu den Dateien unter "
            "opencivil/. Bitte 'python3 -m opencivil.web.bruecke' laufen lassen -- "
            "sonst rechnet die Seite mit einem veralteten Kern.")

    def test_das_paket_bringt_jede_kerndatei_und_das_manifest(self):
        """
        Was im Paket steht, legt der Faden in sein Dateisystem, so wie es im
        Repo liegt -- das Manifest auch: die Konsole liest darin, welche
        Fremdpakete beiliegen.
        """
        self.assertEqual(list(bruecke.quellen()["dateien"]),
                         [*bruecke.kerndateien(), "web/kern/dateien.json"])

    def test_notizbuch_ist_auf_dem_stand(self):
        self.assertTrue(
            bruecke.notizbuch_stimmt(),
            "Das Notizbuch (notizbuch/, web/kern/notizbuch.json) passt nicht mehr "
            "zum Kern oder zu den Notizen. Bitte 'python3 -m opencivil.web.bruecke' "
            "laufen lassen -- sonst fehlen der Seite Formeln oder neue Notizen.")

    def test_die_beiliegenden_pakete_stehen_im_manifest(self):
        """
        numpy und pandas samt dem, was pandas braucht (Benutzer, 2026-10-15) --
        gelesen aus den Dateien unter web/vendor/pyodide/, Importname zu Paket.
        """
        self.assertEqual(bruecke.mitgelieferte_pakete(), {
            "dateutil": "python-dateutil", "numpy": "numpy", "pandas": "pandas",
            "pytz": "pytz", "six": "six"})

    def test_der_dienst_ist_im_manifest(self):
        dateien = bruecke.kerndateien()
        self.assertIn("opencivil/web/dienst.py", dateien)
        self.assertIn("opencivil/projekt/projekt.py", dateien)

    def test_kein_zwischenstand_im_manifest(self):
        self.assertFalse(
            [d for d in bruecke.kerndateien() if "__pycache__" in d])

    def test_die_marke_haengt_am_inhalt(self):
        """
        Geaendert heisst neue Marke, also neue Adresse im Browser -- und kein
        alter Stand aus dem Zwischenspeicher. Windows-Zeilenenden zaehlen nicht.
        """
        with tempfile.TemporaryDirectory() as ordner:
            datei = Path(ordner) / "x.py"
            datei.write_bytes(b"a = 1\n")
            vorher = bruecke.marke(datei)
            datei.write_bytes(b"a = 1\r\n")
            self.assertEqual(bruecke.marke(datei), vorher)
            datei.write_bytes(b"a = 2\n")
            self.assertNotEqual(bruecke.marke(datei), vorher)

    def test_schreiben_ist_wiederholbar(self):
        """Zweimal geschrieben ergibt zeichengleich dasselbe -- sonst rauscht das Diff."""
        for schreiben in (bruecke.schreiben, bruecke.quellen_schreiben):
            with self.subTest(schreiben=schreiben.__name__), \
                    tempfile.TemporaryDirectory() as ordner:
                a = schreiben(Path(ordner) / "a.json").read_text(encoding="utf-8")
                b = schreiben(Path(ordner) / "b.json").read_text(encoding="utf-8")
                self.assertEqual(a, b)

    def test_versionsmarken_sind_auf_dem_stand(self):
        self.assertTrue(
            bruecke.versionsmarken_stimmen(),
            "Die Versionsmarken in web/index.html passen nicht mehr zu den Dateien. "
            "Bitte 'python3 -m opencivil.web.bruecke' laufen lassen -- sonst holt "
            "der Browser womöglich alte Module aus dem Zwischenspeicher.")

    def test_die_tafel_kennt_module_und_verzeichnisse(self):
        tafel = [p.relative_to(bruecke.WURZEL).as_posix() for p in bruecke.tafeldateien()]
        for datei in ("web/js/app.js", "web/js/kern_arbeiter.js",
                      "web/kern/quellen.json", "web/kern/notizbuch.json"):
            with self.subTest(datei=datei):
                self.assertIn(datei, tafel)

    def test_marken_schreiben_laesst_den_rest_der_seite(self):
        kopf = f"<head>\n  {bruecke.ANFANG}\n"
        fuss = f"  {bruecke.ENDE}\n</head>\n"
        with tempfile.TemporaryDirectory() as ordner:
            seite = Path(ordner) / "index.html"
            seite.write_text(kopf + "  alt\n" + fuss, encoding="utf-8")
            bruecke.versionsmarken_schreiben(seite)
            self.assertEqual(seite.read_text(encoding="utf-8"),
                             kopf + bruecke.versionsmarken() + fuss)

    def test_der_vorrat_ist_auf_dem_stand(self):
        self.assertTrue(
            bruecke.vorrat_stimmt(),
            "Der Vorrat in sw.js passt nicht mehr zu den Dateien. Bitte 'python3 -m "
            "opencivil.web.bruecke' laufen lassen -- sonst fehlt der Seite ohne Netz, "
            "was sich geändert hat.")

    def test_der_vorrat_nennt_nur_was_es_gibt(self):
        """Fehlte eine Datei, scheiterte die Installation -- und die Seite ginge ohne Netz nie auf."""
        vorrat = bruecke.vorrat()
        pfade = [*vorrat["seiten"], *vorrat["dateien"],
                 *(d for ordner in vorrat["fremd"].values() for d in ordner["dateien"])]
        for pfad in pfade:
            with self.subTest(pfad=pfad):
                datei = bruecke.WURZEL / pfad.split("?")[0]
                self.assertTrue((datei / "index.html" if pfad.endswith("/") else datei).is_file())

    def test_der_vorrat_holt_pyodide_aber_nicht_die_pakete_der_konsole(self):
        """numpy und pandas kosten 7 MB und kommen erst, wenn ein Skript sie braucht."""
        pyodide = bruecke.vorrat()["fremd"]["web/vendor/pyodide/"]["dateien"]
        self.assertIn("web/vendor/pyodide/pyodide.asm.wasm", pyodide)
        self.assertEqual([d for d in pyodide if d.endswith((".whl", ".md"))], [])

    def test_die_marke_eines_fremden_ordners_haengt_am_inhalt(self):
        """Eine Erläuterung zählt nicht: ihretwegen holte der Browser die 13 MB nicht neu."""
        with tempfile.TemporaryDirectory() as ordner:
            ordner = Path(ordner)
            (ordner / "a.js").write_bytes(b"1")
            vorher = bruecke.fremdmarke(ordner)
            (ordner / "HERKUNFT.md").write_text("woher", encoding="utf-8")
            self.assertEqual(bruecke.fremdmarke(ordner), vorher)
            (ordner / "a.js").write_bytes(b"2")
            self.assertNotEqual(bruecke.fremdmarke(ordner), vorher)

    def test_vorrat_schreiben_laesst_den_rest_des_service_workers(self):
        kopf = f"/** sw.js */\n{bruecke.SW_ANFANG}\n"
        fuss = f"{bruecke.SW_ENDE}\nself.addEventListener('fetch', () => {{}});\n"
        with tempfile.TemporaryDirectory() as ordner:
            datei = Path(ordner) / "sw.js"
            datei.write_text(kopf + "alt\n" + fuss, encoding="utf-8")
            bruecke.vorrat_schreiben(datei)
            self.assertEqual(datei.read_text(encoding="utf-8"),
                             kopf + bruecke.vorrat_marken() + fuss)

    def test_ohne_kommentare_bricht_das_schreiben_ab(self):
        """Still nichts zu schreiben hiesse: die alten Marken blieben stehen."""
        with tempfile.TemporaryDirectory() as ordner:
            seite = Path(ordner) / "index.html"
            seite.write_text("<head></head>\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                bruecke.versionsmarken_schreiben(seite)


if __name__ == "__main__":
    unittest.main()
