"""Tests für Spannungsbegrenzung und Knicknachweis."""

import unittest

from opencivil.nachweis import knicken as knick_modul
from opencivil.projekt import KnickEintrag, Projekt
from opencivil.web import dienst


def urteile(projekt: Projekt):
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    return aufbau, {u.name: u for u in loesung.urteile}



def setzen(ziel, pfad: str, wert) -> None:
    """
    ``haeufig__anteil`` setzt ``ziel.haeufig.anteil`` -- fuer die Stichworte
    der Helfer. Ein Feld, das es nicht gibt, ist ein Fehler im Test: setattr
    legte es sonst still neu an, und der Test pruefte nichts.
    """
    *vorne, letztes = pfad.split("__")
    for teil in vorne:
        ziel = getattr(ziel, teil)
    if not hasattr(ziel, letztes):
        raise AttributeError(f"{type(ziel).__name__} hat kein Feld '{letztes}'.")
    setattr(ziel, letztes, wert)

class TestSpannungsbegrenzung(unittest.TestCase):
    def projekt(self, anforderung="hoch", **abweichungen) -> Projekt:
        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        q.rissanforderung = anforderung
        for name, wert in abweichungen.items():
            setzen(q, name, wert)
        return projekt

    def test_bei_normaler_anforderung_entfaellt_er(self):
        """
        In Tabelle 17 steht dort ein Strich. Gemeint ist nur der Nachweis
        gegen Fliessen -- der aus der Rissbreite läuft trotzdem, und das
        prüft seine eigene Klasse.
        """
        aufbau, gefunden = urteile(self.projekt("normal"))
        self.assertEqual(aufbau.spannung, {})
        self.assertFalse([u for u in gefunden.values()
                          if u.langname == "Stahlspannung gegen Fliessen"])

    def test_bei_erhoehter_anforderung_laeuft_er(self):
        """
        Er läuft -- still, solange die 70 % nicht eingeschaltet sind. Die
        Abschätzung ist bequem, aber nicht selbstverständlich; sie ungefragt
        in die Tabelle zu stellen hiesse, sie zur Norm zu erklären.
        """
        aufbau, gefunden = urteile(self.projekt("erhoeht"))
        self.assertEqual(sorted(aufbau.spannung), ["q1.x"])
        self.assertTrue([n for n in gefunden if n.startswith("Stahlspannung")])
        self.assertTrue(all(n.still for n in aufbau.spannung.values()))

    def test_mit_den_siebzig_prozent_wird_er_laut(self):
        aufbau, _ = urteile(
            self.projekt("erhoeht", haeufig__aus_tragsicherheit=True))
        laut = [u.fall for u in aufbau.spannung["q1.x"].urteile if not u.still]
        self.assertIn("Feld (70 %)", laut)

    def test_die_grenze_ist_f_yd_minus_80(self):
        aufbau, _ = urteile(self.projekt("hoch"))
        urteil = aufbau.spannung["q1.x"].urteile[0]
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
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = self.projekt("hoch")
        q = projekt.querschnitte[0]
        q.haeufig.aus_tragsicherheit = False
        q.haeufig.faelle = [GebrauchsfallEintrag("Gebrauch", M_Ed=60.0, N_Ed=0.0)]
        aufbau, _ = urteile(projekt)
        spannung = aufbau.spannung["q1.x"]
        self.assertEqual([u.fall for u in spannung.urteile if not u.still],
                         ["Gebrauch"])
        self.assertIn("Feld (70 %)", [e.fall.name for e in spannung.ergebnisse])

    def test_ohne_moment_ist_der_grad_unendlich(self):
        """Nichts wirkt, also nichts zu begrenzen -- ∞, keine Zahl aus dem Rundungsrest."""
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = self.projekt("hoch")
        q = projekt.querschnitte[0]
        q.haeufig.aus_tragsicherheit = False
        q.haeufig.faelle = [GebrauchsfallEintrag("Leer", M_Ed=0.0, N_Ed=0.0)]
        aufbau, _ = urteile(projekt)
        leer = next(e for e in aufbau.spannung["q1.x"].ergebnisse if e.fall.name == "Leer")
        self.assertEqual(leer.erfuellungsgrad, float("inf"))
        self.assertTrue(leer.erfuellt)

    def test_mehr_moment_gibt_mehr_spannung(self):
        wenig = self.projekt("hoch")
        viel = self.projekt("hoch")
        for k in viel.querschnitte[0].kombinationen:
            k.M_Ed *= 1.5
        a, _ = urteile(wenig)
        b, _ = urteile(viel)
        self.assertLess(a.spannung["q1.x"].ergebnisse[0].sigma_s,
                        b.spannung["q1.x"].ergebnisse[0].sigma_s)



class TestStahlspannungAusRissbreite(unittest.TestCase):
    """
    Der Nachweis unter quasi-ständiger Einwirkung: dieselbe Rechnung wie
    gegen Fliessen, aber mit 60 % und gegen σ_s,adm aus der Rissanforderung.
    """

    def projekt(self, anforderung="normal", *eigene, **abweichungen) -> Projekt:
        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        q.rissanforderung = anforderung
        q.quasistaendig.faelle = list(eigene)
        for name, wert in abweichungen.items():
            setzen(q, name, wert)
        return projekt

    def nachweis(self, projekt):
        aufbau, _ = urteile(projekt)
        return aufbau.spannung_riss["q1.x"]

    def test_er_laeuft_auch_bei_normaler_anforderung(self):
        """Dort ist die Grenze f_yk -- auch dann darf nichts fliessen."""
        nachweis = self.nachweis(self.projekt("normal"))
        self.assertAlmostEqual(nachweis.ergebnisse[0].sigma_s_adm / 1e6, 500.0)

    def test_bei_hoher_anforderung_begrenzt_die_rissbreite(self):
        """
        √(9 · E_s · f_ctm · w_nom / ⌀) mit dem dicksten Stab der Tragrichtung
        -- im Beispiel die ⌀18 der 2. Lage, nicht die ⌀12 der 3.
        """
        nachweis = self.nachweis(self.projekt("hoch"))
        erwartet = (9 * 200000 * 2.9 * 0.2 / 18) ** 0.5
        self.assertAlmostEqual(nachweis.ergebnisse[0].sigma_s_adm / 1e6,
                               erwartet, places=3)

    def test_die_sechzig_prozent_kommen_aus_dem_kern(self):
        faelle = {e.fall.name: e.fall
                  for e in self.nachweis(self.projekt()).ergebnisse}
        self.assertIn("Feld (60 %)", faelle)
        self.assertAlmostEqual(faelle["Feld (60 %)"].M_Ed.si / 1e3, 60.0)

    def test_der_anteil_ist_einstellbar(self):
        """Und er steht im Namen -- sonst wüsste niemand, womit gerechnet wurde."""
        nachweis = self.nachweis(self.projekt(quasistaendig__anteil=50.0))
        faelle = {e.fall.name: e.fall for e in nachweis.ergebnisse}
        self.assertEqual(sorted(faelle), ["Feld (50 %)", "Feld mit Druck (50 %)",
                                          "Stütze (50 %)"])
        self.assertAlmostEqual(faelle["Stütze (50 %)"].M_Ed.si / 1e3, -25.0)

    def test_der_haeufige_anteil_ist_einstellbar(self):
        projekt = self.projekt("hoch", haeufig__anteil=80.0)
        aufbau, _ = urteile(projekt)
        faelle = {e.fall.name: e.fall for e in aufbau.spannung["q1.x"].ergebnisse}
        self.assertAlmostEqual(faelle["Feld (80 %)"].M_Ed.si / 1e3, 80.0)

    def test_ohne_schalter_still_mit_schalter_laut(self):
        still = self.nachweis(self.projekt())
        self.assertTrue(still.still)
        laut = self.nachweis(self.projekt(quasistaendig__aus_tragsicherheit=True))
        self.assertEqual([u.fall for u in laut.urteile if not u.still],
                         ["Feld (60 %)", "Feld mit Druck (60 %)", "Stütze (60 %)"])

    def test_eigene_faelle_sind_laut_die_abgeleiteten_nicht(self):
        from opencivil.projekt import GebrauchsfallEintrag

        nachweis = self.nachweis(self.projekt(
            "normal", GebrauchsfallEintrag("Dauerlast", M_Ed=80.0)))
        self.assertEqual([u.fall for u in nachweis.urteile if not u.still],
                         ["Dauerlast"])

    def test_zwei_nachweise_zwei_zeilen(self):
        """
        Gegen Fliessen und aus Rissbreite stehen nebeneinander in derselben
        Tabelle -- mit gleichem Namen wären sie nicht zu unterscheiden.
        """
        projekt = self.projekt("hoch", haeufig__aus_tragsicherheit=True,
                               quasistaendig__aus_tragsicherheit=True)
        aufbau, gefunden = urteile(projekt)
        namen = {u.langname for u in gefunden.values() if not u.still}
        self.assertIn("Stahlspannung gegen Fliessen", namen)
        self.assertIn("Stahlspannung aus Rissbreite", namen)
        self.assertNotEqual(aufbau.spannung["q1.x"].id,
                            aufbau.spannung_riss["q1.x"].id)

    def test_elastisch_ist_es_der_spannungsvergleich(self):
        erg = self.nachweis(self.projekt("hoch")).ergebnisse[0]
        self.assertFalse(erg.fliesst)
        self.assertEqual(erg.erfuellungsgrad, erg.sigma_s_adm / erg.sigma_s)

    def test_fliessen_ist_nicht_gerade_noch_erfuellt(self):
        """
        Bei normaler Anforderung ist die Grenze f_yk, und dort liegt auch das
        Fliessplateau. Wer an der Spannung misst, bekäme 500 gegen 500 --
        erfüllt, mit 1.00. Gemessen wird darum an der Dehnung, und die wächst
        auf dem Plateau weiter.
        """
        from opencivil.core.einheiten import PROMILLE
        from opencivil.projekt import GebrauchsfallEintrag

        nachweis = self.nachweis(self.projekt(
            "normal", GebrauchsfallEintrag("fliesst", M_Ed=262.0)))
        erg = nachweis.ergebnisse[-1]
        urteil = nachweis.urteile[-1]
        self.assertTrue(erg.konvergiert)
        self.assertTrue(erg.fliesst)
        self.assertAlmostEqual(erg.sigma_s / 1e6, 500.0)
        self.assertFalse(erg.erfuellt)
        self.assertLess(erg.erfuellungsgrad, 0.9)
        # In der Tabelle Dehnungen, nicht zweimal 500 N/mm².
        self.assertIs(urteil.einwirkung.definition.einheit, PROMILLE)
        self.assertGreater(urteil.einwirkung.groesse.si,
                           urteil.widerstand.groesse.si)

    def test_mehr_dehnung_heisst_kleinerer_erfuellungsgrad(self):
        """Auch jenseits des Fliessens -- sonst fände die Suche keine Richtung."""
        from opencivil.projekt import GebrauchsfallEintrag

        nachweis = self.nachweis(self.projekt(
            "normal", *(GebrauchsfallEintrag(f"M{m}", M_Ed=float(m))
                        for m in (258, 262, 266, 270))))
        grade = [e.erfuellungsgrad for e in nachweis.ergebnisse[-4:]]
        self.assertEqual(grade, sorted(grade, reverse=True))
        self.assertTrue(all(e.fliesst for e in nachweis.ergebnisse[-4:]))

    def test_die_mitschrift_nennt_das_fliessen(self):
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = self.projekt("normal", GebrauchsfallEintrag("fliesst", M_Ed=262.0))
        aufbau = projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        text = " ".join(
            getattr(b, "text", "") + getattr(b, "latex", "")
            for b in loesung.protokoll.alle_bloecke())
        self.assertIn("Die Bewehrung fliesst", text)
        self.assertIn(r"\varepsilon_{s,adm}", text)



class TestFallnamenInSymbolen(unittest.TestCase):
    """
    Ein Fallname steht als Text im Symbol, nicht als Wert-ID.

    Aus «Feld (60 %)» wurde vorher ``Feld__60___`` -- zwei Unterstriche
    hintereinander sind in LaTeX ein doppelter Index, KaTeX brach ab, und in
    der Werteliste stand der rohe Quelltext. Seit der quasi-ständige Nachweis
    immer läuft, stand das schon im Beispielprojekt.
    """

    def test_kein_symbol_enthaelt_einen_doppelten_index(self):
        from opencivil.projekt import GebrauchsfallEintrag, KnickEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        q.rissanforderung = "hoch"
        q.kombinationen[0].V_Ed = 50.0
        q.knickfaelle = [KnickEintrag("Stütze (EG)", N_Ed=-500.0, M_Ed_1=10.0,
                                      laenge=3.0, knicklaenge=3.0)]
        q.haeufig.faelle = [GebrauchsfallEintrag("Dauer_1 (a)", M_Ed=40.0)]
        werk = projekt.aufbauen().werk
        schlecht = [(wid, werk.definition(wid).symbol)
                    for wid in werk.bekannte_werte
                    if "__" in werk.definition(wid).symbol]
        self.assertEqual(schlecht, [])

    def test_der_name_steht_als_text_da(self):
        aufbau = Projekt.beispiel().aufbauen()
        symbole = [d.symbol for d in
                   aufbau.spannung_riss["q1.x"].d_ausnutzung.values()]
        self.assertIn(r"\alpha_{eff,\sigma,w,x,\text{Feld (60 \%)}}", symbole)


class TestGebrauchsfallPruefung(unittest.TestCase):
    """Was an der Maske eingegeben wird und nicht stimmen kann."""

    def fehler(self, **abweichungen) -> str:
        from opencivil.projekt import ProjektFehler

        projekt = Projekt.beispiel()
        for name, wert in abweichungen.items():
            setzen(projekt.querschnitte[0], name, wert)
        with self.assertRaises(ProjektFehler) as fehler:
            projekt.aufbauen()
        return str(fehler.exception)

    def test_ein_eigener_fall_heisst_wie_ein_abgeleiteter(self):
        from opencivil.projekt import GebrauchsfallEintrag

        meldung = self.fehler(quasistaendig__faelle=[
            GebrauchsfallEintrag("Feld (60 %)", M_Ed=10.0)])
        self.assertIn("quasi-ständige Lastfall 'Feld (60 %)'", meldung)

    def test_gleiche_namen_in_beiden_listen_sind_erlaubt(self):
        """Sie landen in zwei Nachweisen und damit in zwei ID-Räumen."""
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        q.rissanforderung = "hoch"
        q.haeufig.faelle = [GebrauchsfallEintrag("Dauer", M_Ed=50.0)]
        q.quasistaendig.faelle = [GebrauchsfallEintrag("Dauer", M_Ed=40.0)]
        aufbau, _ = urteile(projekt)
        self.assertIn("Dauer", [e.fall.name for e in aufbau.spannung["q1.x"].ergebnisse])
        self.assertIn("Dauer", [e.fall.name
                                for e in aufbau.spannung_riss["q1.x"].ergebnisse])

    def test_namen_die_auf_dieselbe_kennung_fallen(self):
        """«Feld A» und «Feld-A» werden beide zu Feld_A."""
        from opencivil.projekt import GebrauchsfallEintrag

        meldung = self.fehler(quasistaendig__faelle=[
            GebrauchsfallEintrag("Feld A", M_Ed=10.0),
            GebrauchsfallEintrag("Feld-A", M_Ed=20.0)])
        self.assertIn("'Feld A' und 'Feld-A'", meldung)

    def test_ein_anteil_ausserhalb_von_null_bis_hundert(self):
        for feld, wert in (("quasistaendig__anteil", 0.0),
                           ("quasistaendig__anteil", -10.0),
                           ("haeufig__anteil", 700.0)):
            with self.subTest(feld=feld, wert=wert):
                self.assertIn("zwischen 0 und 100 %",
                              self.fehler(**{feld: wert}))

    def test_die_felder_ueberleben_die_datei(self):
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = Projekt.beispiel()
        q = projekt.querschnitte[0]
        q.quasistaendig.faelle = [GebrauchsfallEintrag(
            "Dauer", M_Ed=40.0, N_Ed=-5.0, aktiv=False)]
        q.quasistaendig.aus_tragsicherheit = True
        q.quasistaendig.anteil = 55.0
        q.haeufig.anteil = 75.0
        zurueck = Projekt.aus_dict(projekt.als_dict()).querschnitte[0]
        self.assertEqual(zurueck.quasistaendig, q.quasistaendig)
        self.assertEqual(zurueck.haeufig.anteil, 75.0)

    def test_eine_datei_ohne_die_listen_bekommt_die_vorgaben(self):
        daten = Projekt.beispiel().als_dict()
        for feld in ("haeufig", "quasistaendig"):
            daten["querschnitte"][0].pop(feld)
        q = Projekt.aus_dict(daten).querschnitte[0]
        self.assertEqual((q.haeufig.anteil, q.quasistaendig.anteil), (70.0, 60.0))
        self.assertEqual(q.quasistaendig.faelle, [])

    def test_eine_datei_mit_den_alten_flachen_feldern(self):
        """
        Vor der Gebrauchsliste standen die drei Angaben einzeln an der Platte.
        Solche Dateien gibt es -- sie werden gelesen und neu geschrieben.
        """
        daten = Projekt.beispiel().als_dict()
        platte = daten["querschnitte"][0]
        for feld in ("haeufig", "quasistaendig"):
            platte.pop(feld)
        platte.update({
            "haeufige": [{"name": "Gebrauch", "M_Ed": 70.0}],
            "haeufige_aus_tragsicherheit": True,
            "haeufige_anteil": 75.0,
            "quasistaendige": [{"name": "Dauer", "M_Ed": 40.0, "aktiv": False}],
            "quasistaendige_anteil": 55.0,
        })
        q = Projekt.aus_dict(daten).querschnitte[0]
        self.assertEqual((q.haeufig.anteil, q.haeufig.aus_tragsicherheit), (75.0, True))
        self.assertEqual([f.name for f in q.haeufig.faelle], ["Gebrauch"])
        self.assertEqual((q.quasistaendig.anteil, q.quasistaendig.aus_tragsicherheit),
                         (55.0, False))
        self.assertFalse(q.quasistaendig.faelle[0].aktiv)

        geschrieben = Projekt.aus_dict(daten).als_dict()["querschnitte"][0]
        for alt in ("haeufige", "haeufige_aus_tragsicherheit", "haeufige_anteil",
                    "quasistaendige", "quasistaendige_aus_tragsicherheit",
                    "quasistaendige_anteil"):
            self.assertNotIn(alt, geschrieben)
        self.assertEqual(geschrieben["haeufig"]["anteil"], 75.0)

    def test_ohne_lastfaelle_leert_jede_lastfallliste(self):
        """
        Die Regel heisst «alle». Gefunden werden die Listen ueber die Typen
        der Felder -- auch in einer Gebrauchsliste --, damit eine neue Liste,
        die in ohne_lastfaelle() fehlt, hier auffaellt, statt dass die Suche
        «ohne Kraefte» still mit Kraeften rechnet.
        """
        import dataclasses
        import typing

        def ist_lastfall(klasse) -> bool:
            return dataclasses.is_dataclass(klasse) and any(
                f.name in ("M_Ed", "N_Ed") for f in dataclasses.fields(klasse))

        def listen(objekt, pfad=""):
            hinweise = typing.get_type_hints(type(objekt))
            for f in dataclasses.fields(objekt):
                typ, wert = hinweise[f.name], getattr(objekt, f.name)
                if typing.get_origin(typ) is list:
                    (element,) = typing.get_args(typ)
                    if ist_lastfall(element):
                        yield f"{pfad}{f.name}", objekt, f.name, element
                elif dataclasses.is_dataclass(wert):
                    yield from listen(wert, f"{pfad}{f.name}.")

        q = Projekt.beispiel().querschnitte[0]
        gefunden = list(listen(q))
        # Die Probe muss die Listen auch finden -- sonst prueft sie nichts.
        self.assertEqual(
            sorted(pfad for pfad, *_ in gefunden),
            ["haeufig.faelle", "knickfaelle", "kombinationen",
             "quasistaendig.faelle", "spannungsfaelle"])
        for _, besitzer, feld, element in gefunden:
            setattr(besitzer, feld, [element(name="probe")])

        q.ohne_lastfaelle()
        self.assertEqual(
            [pfad for pfad, besitzer, feld, _ in gefunden
             if getattr(besitzer, feld)], [])

    def test_die_suche_nimmt_dieselbe_regel(self):
        from opencivil.bewehrungssuche import _arbeitskopie
        from opencivil.projekt import GebrauchsfallEintrag

        projekt = Projekt.beispiel()
        projekt.querschnitte[0].quasistaendig.faelle = [
            GebrauchsfallEintrag("Dauer", M_Ed=40.0)]
        kopie = _arbeitskopie(projekt, "q1", kraefte=False)
        self.assertEqual(kopie.querschnitte[0].quasistaendig.faelle, [])
        self.assertEqual(kopie.querschnitte[0].kombinationen, [])


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
