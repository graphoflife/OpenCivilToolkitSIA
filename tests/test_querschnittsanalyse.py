"""
Die Querschnittsanalyse: Beschreibung, Aufbau und Nachweise.

Hier zuerst die Beschreibung -- was gespeichert wird und wie es sich liest.
"""

import unittest

from opencivil.projekt import (
    FlaecheEintrag, Projekt, ProjektFehler, QALastfallEintrag, QuerschnittsanalyseEintrag,
    StabEintrag,
)
from opencivil.web import api


class TestBeschreibung(unittest.TestCase):

    def neu(self):
        return QuerschnittsanalyseEintrag.neu("a1", "Balken", "b1", "s1")

    def test_rundreise(self):
        a = self.neu()
        a.lastfall("Stütze", N_Ed=-800.0, M_y_Ed=120.0, M_z_Ed=-40.0, T_Ed=15.0)
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(a.als_dict()), a)

    def test_im_projekt(self):
        p = Projekt.beispiel()
        p.querschnittsanalysen.append(self.neu())
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)
        self.assertIs(p.querschnittsanalyse("a1"), p.querschnittsanalysen[0])
        self.assertNotEqual(p.freie_kennung("a"), "a1")

    def test_die_vorlage_kommt_aus_dem_kern(self):
        vorlage = api.katalog()["neue_querschnittsanalyse"]
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(
            {**vorlage, "kennung": "a1"}).als_dict(), {**vorlage, "kennung": "a1",
                                                       "name": "a1"})
        self.assertEqual(len(vorlage["flaechen"]), 1)

    def test_materialien_und_wahl(self):
        a = self.neu()
        self.assertEqual(a.materialien(), ["b1", "s1"])
        self.assertEqual(a.wahl("b1").satz, "bemessung")
        self.assertEqual(a.wahl("b1").betongesetz, "parabel")

    def test_doppelte_lastfaelle(self):
        a = self.neu()
        a.lastfaelle.append(QALastfallEintrag(name="Tragsicherheit 1"))
        with self.assertRaisesRegex(ProjektFehler, "Querschnitt 'Balken'"):
            a.pruefen()

    def test_unbekanntes_wird_gemeldet(self):
        roh = self.neu().als_dict()
        roh["stablinien"][0]["art"] = "stueckweise"
        with self.assertRaisesRegex(ProjektFehler, "Stablinie"):
            QuerschnittsanalyseEintrag.aus_dict(roh)
        roh = self.neu().als_dict()
        roh["schubwaende"] = [{"von": [0, 0], "bis": [0, 500], "schnitte": 9}]
        with self.assertRaisesRegex(ProjektFehler, "Schnitte"):
            QuerschnittsanalyseEintrag.aus_dict(roh)
        roh = self.neu().als_dict()
        roh["flaechen"][0]["punkte"][1] = [300.0]
        with self.assertRaisesRegex(ProjektFehler, "zwei Zahlen"):
            QuerschnittsanalyseEintrag.aus_dict(roh)

    def test_namen_zaehlen_je_art(self):
        """
        Die Namen stehen in Berichten und Meldungen und werden an einer Stelle
        vergeben: je Art ab 1, eine Aussparung heisst so statt «Polygon».
        """
        a = self.neu()
        a.flaechen.append(FlaecheEintrag(punkte=[[100, 100], [200, 100], [200, 200]]))
        a.staebe.append(StabEintrag(y=150, z=300))
        e = a.elemente()
        self.assertEqual([f["name"] for f in e.polygone], ["Polygon 1", "Aussparung 2"])
        self.assertEqual([s["name"] for s in e.staebe], ["Stab 1"])
        self.assertEqual([l["name"] for l in e.linien], ["Linie 1", "Linie 2"])
        self.assertEqual(e.waende, [])
        # Jedes Element trägt eine Kennung, über die die Oberfläche es findet.
        for liste in (e.polygone, e.staebe, e.linien):
            for element in liste:
                self.assertTrue(element["kennung"])


if __name__ == "__main__":
    unittest.main()


# ===========================================================================
# Aufbau und Nachweise
# ===========================================================================

import math

from opencivil.projekt import (
    FlaecheEintrag, SchubwandEintrag, StabEintrag, StablinieEintrag,
    WerkstoffwahlEintrag,
)
from opencivil.web import dienst


def projekt(**schalter) -> Projekt:
    """Ein leeres Projekt mit C30/37, B500B und einer Analyse: Rechteck 300 × 600."""
    p = Projekt(name="Probe")
    p.beton("C30/37")
    p.stahl("B500B")
    a = QuerschnittsanalyseEintrag.neu("a1", "Balken", "b1", "s1")
    a.lastfaelle = []
    for name, wert in schalter.items():
        setattr(a, name, wert)
    p.querschnittsanalysen.append(a)
    return p


def kastenwaende(dicke=80.0):
    ecken = [[50, 50], [250, 50], [250, 550], [50, 550]]
    return [SchubwandEintrag(von=ecken[i], bis=ecken[(i + 1) % 4], dicke=dicke,
                             durchmesser=10.0, teilung=150.0, schnitte=1, stahl="s1")
            for i in range(4)]


def urteile(ergebnis, art):
    return {u.fall: u for u in ergebnis.urteile_von("a1") if u.art == art}


class TestAufbau(unittest.TestCase):

    def test_bruttoquerschnitt(self):
        e = projekt().rechnen()
        wert = lambda k: e.wert(f"querschnittsanalyse.a1.{k}").groesse
        self.assertAlmostEqual(wert("A").in_einheit(wert("A").anzeige), 180000.0)
        self.assertAlmostEqual(wert("z_S").si, 0.3)
        self.assertAlmostEqual(wert("I_y").si, 0.3 * 0.6 ** 3 / 12)

    def test_aussparung(self):
        p = projekt()
        p.querschnittsanalysen[0].flaechen.append(
            FlaecheEintrag(punkte=[[100, 200], [200, 200], [200, 400], [100, 400]]))
        e = p.rechnen()
        self.assertAlmostEqual(e.wert("querschnittsanalyse.a1.A").groesse.si,
                               0.18 - 0.1 * 0.2)

    def meldung(self, p) -> str:
        with self.assertRaises(ProjektFehler) as fehler:
            p.rechnen()
        return str(fehler.exception)

    def test_stab_ausserhalb(self):
        p = projekt()
        p.querschnittsanalysen[0].staebe.append(StabEintrag(y=5, z=300, durchmesser=20,
                                                            stahl="s1"))
        text = self.meldung(p)
        self.assertIn("Querschnittsanalyse 'Balken'", text)
        self.assertIn("Stab 1", text)
        self.assertIn("nicht ganz im Beton", text)

    def test_ueberlappung(self):
        p = projekt()
        p.querschnittsanalysen[0].flaechen.append(
            FlaecheEintrag(punkte=[[250, 0], [500, 0], [500, 100], [250, 100]], material="b1"))
        self.assertIn("überlappen", self.meldung(p))

    def test_wand_ausserhalb(self):
        p = projekt()
        p.querschnittsanalysen[0].schubwaende = [
            SchubwandEintrag(von=[150, -50], bis=[150, 550], stahl="s1")]
        self.assertIn("Wand 1", self.meldung(p))

    def test_geloeschtes_material(self):
        p = projekt()
        p.querschnittsanalysen[0].flaechen[0].material = "b7"
        self.assertIn("'b7'", self.meldung(p))


class TestBiegung(unittest.TestCase):

    def test_grad_ist_widerstand_durch_einwirkung(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=150.0)
        u = urteile(p.rechnen(), "M-N")["Feld"]
        self.assertAlmostEqual(u.erfuellungsgrad.si,
                               u.widerstand.groesse.si / u.einwirkung.groesse.si)
        self.assertEqual(u.einwirkung.groesse.si, 150e3)

    def test_einachsig_uebergeht_m_z(self):
        p = projekt(einachsig=True)
        a = p.querschnittsanalysen[0]
        a.lastfall("ohne", M_y_Ed=150.0)
        a.lastfall("mit", M_y_Ed=150.0, M_z_Ed=80.0)
        u = urteile(p.rechnen(), "M-N")
        self.assertAlmostEqual(u["ohne"].erfuellungsgrad.si, u["mit"].erfuellungsgrad.si)

    def test_schief_traegt_weniger(self):
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.lastfall("gerade", N_Ed=-500.0, M_y_Ed=150.0)
        a.lastfall("schief", N_Ed=-500.0, M_y_Ed=150.0, M_z_Ed=60.0)
        u = urteile(p.rechnen(), "M-N")
        self.assertLess(u["schief"].erfuellungsgrad.si, u["gerade"].erfuellungsgrad.si)

    def test_reine_normalkraft(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("Zug", N_Ed=200.0)
        e = p.rechnen()
        u = urteile(e, "M-N")["Zug"]
        zug = e.wert("querschnittsanalyse.a1.nachweis.mn.N_Rd_zug").groesse.si
        self.assertAlmostEqual(u.erfuellungsgrad.si, zug / 200e3)

    def test_jenseits_der_normalkraft(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("viel", N_Ed=-9000.0, M_y_Ed=10.0)
        u = urteile(p.rechnen(), "M-N")["viel"]
        self.assertFalse(u.erfuellt)

    def test_laengszugkraft_senkt_den_widerstand(self):
        def grad(laengs):
            p = projekt(schubwaende=kastenwaende(), laengszugkraft=laengs)
            p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=150.0, V_z_Ed=150.0)
            return urteile(p.rechnen(), "M-N")["Feld"].erfuellungsgrad.si
        self.assertLess(grad(True), grad(False))

    def test_charakteristisch_traegt_mehr(self):
        def grad(satz):
            p = projekt(werkstoffwahl=[WerkstoffwahlEintrag("b1", satz=satz),
                                       WerkstoffwahlEintrag("s1", satz=satz)])
            p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=150.0)
            return urteile(p.rechnen(), "M-N")["Feld"].erfuellungsgrad.si
        self.assertGreater(grad("charakteristisch"), grad("bemessung"))

    def test_spannungsblock_nahe_der_parabel(self):
        def grad(gesetz):
            p = projekt(werkstoffwahl=[WerkstoffwahlEintrag("b1", betongesetz=gesetz)])
            p.querschnittsanalysen[0].lastfall("Feld", N_Ed=-800.0, M_y_Ed=150.0)
            return urteile(p.rechnen(), "M-N")["Feld"].erfuellungsgrad.si
        self.assertAlmostEqual(grad("block") / grad("parabel"), 1.0, delta=0.05)


class TestSchub(unittest.TestCase):

    def test_zwei_stege_je_die_haelfte(self):
        p = projekt(schubwaende=kastenwaende())
        p.querschnittsanalysen[0].lastfall("Feld", V_z_Ed=150.0)
        u = urteile(p.rechnen(), "V+T")["Feld"]
        # Je Steg 75 kN auf 500 mm: 150 kN/m.
        self.assertAlmostEqual(u.einwirkung.groesse.si, 150e3, delta=1e-3)
        self.assertAlmostEqual(u.erfuellungsgrad.si,
                               u.widerstand.groesse.si / u.einwirkung.groesse.si)

    def test_ohne_wand(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("Feld", V_z_Ed=100.0)
        u = urteile(p.rechnen(), "V+T")["Feld"]
        self.assertFalse(u.erfuellt)
        self.assertIn("keine Schubwand", u.hinweis)

    def test_einachsig_ohne_v_y(self):
        p = projekt(einachsig=True)
        p.querschnittsanalysen[0].lastfall("quer", M_y_Ed=10.0, V_y_Ed=100.0)
        self.assertEqual(urteile(p.rechnen(), "V+T"), {})


class TestRichtungen(unittest.TestCase):

    def test_rissmoment_wie_bei_der_platte(self):
        """
        Rechteck 300 × 600: W = b·h²/6 und k_t aus h/3 -- dieselbe Zahl wie
        bei der Platte, um y mit h = 600, um z mit h = 300.
        """
        from opencivil.nachweis.sproedes_versagen import rissmoment
        e = projekt(sproede=True).rechnen()
        alle = {u.fall: u for u in e.loesung.urteile if u.raum.endswith("sproede")}
        f_ctm = e.wert("beton.b1.f_ctm").groesse.si
        um_y = rissmoment(h=0.6, b=0.3, f_ctm=f_ctm).M_Riss
        um_z = rissmoment(h=0.3, b=0.6, f_ctm=f_ctm).M_Riss
        for fall, erwartet in (("Zug unten", um_y), ("Zug oben", um_y),
                               ("Zug links", um_z), ("Zug rechts", um_z)):
            with self.subTest(fall=fall):
                self.assertAlmostEqual(alle[fall].einwirkung.groesse.si, erwartet,
                                       delta=1e-6 * erwartet)

    def test_duktilitaet_nur_wo_gezogen_wird(self):
        p = projekt(duktilitaet=True)
        p.querschnittsanalysen[0].stablinien = p.querschnittsanalysen[0].stablinien[:1]
        e = p.rechnen()
        # Gezeigt wird die ungünstigere Richtung; gerechnet sind alle mit Zugstab.
        alle = [u for u in e.loesung.urteile if u.raum.endswith("duktilitaet")]
        self.assertNotIn("Zug oben", [u.fall for u in alle])
        self.assertIn("Zug unten", [u.fall for u in alle])


class TestDienst(unittest.TestCase):

    def test_rechnen_ueber_den_dienst(self):
        p = projekt(schubwaende=kastenwaende(), duktilitaet=True, sproede=True)
        p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=120.0, V_z_Ed=80.0, T_Ed=10.0)
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200, antwort.daten)
        raeume = {u["raum"] for u in antwort.daten["urteile"]}
        self.assertTrue(raeume and all(r.startswith("querschnittsanalyse.a1") for r in raeume))
        self.assertIn("a1", antwort.daten["zusammenfassungen"])


class TestGeometrieEndpunkt(unittest.TestCase):
    """Was das Zeichenfenster bekommt: alle Meldungen, jede am Element."""

    def frage(self, p, kennung="a1"):
        return dienst.bearbeite("geometrie", {"projekt": p.als_dict(), "kennung": kennung})

    def test_gueltig(self):
        d = self.frage(projekt()).daten
        self.assertTrue(d["gueltig"])
        self.assertEqual(d["meldungen"], [])
        self.assertAlmostEqual(d["brutto"]["z_S"], 300.0)
        # Unten drei Stäbe auf 200 mm: zwei Felder zu 100 mm.
        self.assertEqual(d["linien"][0]["felder"], 2)
        self.assertAlmostEqual(d["linien"][0]["teilung"], 100.0)

    def test_alle_meldungen_auf_einmal(self):
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.staebe += [StabEintrag(y=5, z=300, durchmesser=20, stahl="s1"),
                     StabEintrag(y=150, z=300, durchmesser=0, stahl="s1")]
        d = self.frage(p).daten
        self.assertFalse(d["gueltig"])
        self.assertEqual([m["elemente"] for m in d["meldungen"]], [["Stab 1"], ["Stab 2"]])

    def test_ueberlappung_nennt_beide(self):
        p = projekt()
        p.querschnittsanalysen[0].flaechen.append(
            FlaecheEintrag(punkte=[[250, 0], [500, 0], [500, 100], [250, 100]], material="b1"))
        d = self.frage(p).daten
        self.assertEqual(d["meldungen"][0]["elemente"], ["Polygon 1", "Polygon 2"])

    def test_zellen_der_waende(self):
        d = self.frage(projekt(schubwaende=kastenwaende())).daten
        self.assertEqual(len(d["zellen"]), 1)
        self.assertAlmostEqual(d["zellen"][0]["flaeche"], 200 * 500)

    def test_unbekannte_analyse(self):
        self.assertEqual(self.frage(projekt(), "a9").status, 400)

    def test_zellen_wie_im_nachweis(self):
        """
        Ein Wandende, das um 0.4 µm neben der Ecke liegt: der Nachweis sieht
        eine Zelle (seine Toleranz ist 1 µm), also auch das Fenster. Gesucht
        wurde dort einmal in Millimetern, und dann fehlte die Zelle im Bild.
        """
        waende = kastenwaende()
        waende[3].bis = [50.0, 50.0004]
        p = projekt(schubwaende=waende)
        self.assertEqual(len(self.frage(p).daten["zellen"]), 1)
        p.querschnittsanalysen[0].lastfall("Torsion", T_Ed=10.0)
        self.assertTrue(urteile(p.rechnen(), "V+T")["Torsion"].erfuellt)


class TestDiagramme(unittest.TestCase):
    """
    Die Diagramme der Analyse: was sie zeigen, muss zu den Nachweisen passen.

    Am Unterzug des Beispiels -- symmetrisch, mit einer Zelle aus vier
    Wänden, M_y = 150 kNm, V_z = 150 kN, T = 15 kNm.
    """

    @classmethod
    def setUpClass(cls):
        projekt = Projekt.beispiel()
        cls.antwort = dienst.bearbeite(
            "analysediagramme", {"projekt": projekt.als_dict(), "kennung": "a1"})
        cls.d = cls.antwort.daten["diagramme"]
        cls.fall = cls.d["faelle"][0]

    def test_antwort(self):
        self.assertEqual(self.antwort.status, 200)
        self.assertEqual(self.d["name"], "Unterzug")
        z = self.d["zeichnung"]
        self.assertEqual(len(z["polygone"]), 1)
        self.assertEqual(len(z["staebe"]), 5)
        self.assertEqual(len(z["waende"]), 4)
        self.assertEqual(z["schwerpunkt"], [150.0, 300.0])

    def test_der_widerstand_des_nachweises(self):
        """Je Lastfall der Bruchzustand, gegen den gemessen wurde -- alle drei Grössen."""
        w = self.fall["widerstand"]
        self.assertAlmostEqual(w["N"], 0.0, places=3)
        self.assertAlmostEqual(w["M_y"], 211.8, places=1)
        self.assertAlmostEqual(w["M_z"], 0.0, places=3)

    def test_der_widerstand_liegt_auf_dem_diagramm(self):
        """
        Bei M_z = 0 liegt er auf dem rechten Ast; der Ast bei N = 0 ist der
        Widerstand des Nachweises. Und es gibt nur noch dieses eine
        Interaktionsdiagramm -- je Lastfall keine eigene Linie mehr.
        """
        rechts = [p for p in self.d["interaktion"]["punkte"] if p["M_y"] > 0]
        oben = min((p for p in rechts if p["N"] >= 0), key=lambda p: p["N"])
        unten = max((p for p in rechts if p["N"] < 0), key=lambda p: p["N"])
        t = oben["N"] / (oben["N"] - unten["N"])
        self.assertAlmostEqual(oben["M_y"] + t * (unten["M_y"] - oben["M_y"]),
                               self.fall["widerstand"]["M_y"], delta=0.5)
        self.assertNotIn("mn", self.fall)
        self.assertNotIn("kontur", self.fall)

    def test_bei_festem_n_rundum_wie_der_nachweis(self):
        """Bei N = N_Ed geschnitten: Zug unten ergibt dasselbe M_y wie der Nachweis."""
        i = dienst.bearbeite("analysediagramme", {
            "projekt": Projekt.beispiel().als_dict(), "kennung": "a1",
            "schnitt": {"fest": "N", "wert": 0.0}}).daten["diagramme"]["interaktion"]
        self.assertEqual(len(i["punkte"]), 72)
        self.assertAlmostEqual(max(p["M_y"] for p in i["punkte"]),
                               self.fall["widerstand"]["M_y"], places=6)
        # Symmetrisch: links wie rechts gleich viel M_z.
        m_z = [p["M_z"] for p in i["punkte"]]
        self.assertAlmostEqual(max(m_z), -min(m_z), places=3)

    def test_der_bruchzustand_im_schnitt(self):
        b = self.fall["bruch"]
        # Nulllinie waagrecht über die ganze Breite, Druckzone oben.
        (y0, z0), (y1, z1) = b["nulllinie"]
        self.assertEqual(sorted([y0, y1]), [0.0, 300.0])
        self.assertAlmostEqual(z0, z1)
        self.assertAlmostEqual(600.0 - z0, b["x"], places=6)
        self.assertAlmostEqual(b["d"], 550.0)
        unten = [s["eps"] for s in b["staebe"] if s["z"] < 300.0]
        self.assertTrue(all(e > 0.0 for e in unten))
        zone = b["druckzone"][0]["punkte"]
        self.assertTrue(all(p[1] >= z0 - 1e-9 for p in zone))

    def test_der_schubfluss_haelt_das_gleichgewicht(self):
        """Die Wandkräfte zusammen sind V_y, V_z und T um den Schwerpunkt."""
        schub = self.fall["schub"]
        f_y = f_z = moment = 0.0
        for s in schub["stuecke"]:
            dy, dz = s["bis"][0] - s["von"][0], s["bis"][1] - s["von"][1]
            laenge = math.hypot(dy, dz)
            kraft_y, kraft_z = s["q"] * dy / 1e3, s["q"] * dz / 1e3  # kN
            f_y += kraft_y
            f_z += kraft_z
            my, mz = (s["von"][0] + s["bis"][0]) / 2 - 150.0, (s["von"][1] + s["bis"][1]) / 2 - 300.0
            moment += (my * kraft_z - mz * kraft_y) / 1e3  # kNm
            self.assertGreater(laenge, 0.0)
        self.assertAlmostEqual(f_y, 0.0, places=6)
        self.assertAlmostEqual(f_z, 150.0, places=6)
        self.assertAlmostEqual(moment, 15.0, places=6)
        # Dieselbe Wand wie im Nachweis ist massgebend.
        schwach = min(schub["waende"], key=lambda w: w["v_Rd"] / w["q_max"])
        self.assertEqual(schwach["grad_text"], "1.75")

    def test_einachsig(self):
        projekt = Projekt.beispiel()
        projekt.querschnittsanalysen[0].einachsig = True
        d = dienst.bearbeite("analysediagramme", {
            "projekt": projekt.als_dict(), "kennung": "a1"}).daten["diagramme"]
        self.assertTrue(d["einachsig"])
        self.assertIsNone(d["interaktion"]["fest"])
        self.assertAlmostEqual(d["faelle"][0]["widerstand"]["M_y"], 211.8, places=1)

    def test_unbekannte_analyse(self):
        antwort = dienst.bearbeite("analysediagramme", {
            "projekt": Projekt.beispiel().als_dict(), "kennung": "a9"})
        self.assertEqual(antwort.status, 400)

    def test_interaktionsdiagramm_ohne_wahl_bei_m_z_null(self):
        i = self.d["interaktion"]
        self.assertEqual((i["fest"], i["wert"]), ("M_z", 0.0))
        self.assertTrue(all(p["M_z"] == 0.0 for p in i["punkte"]))
        # Bei N = 0 reicht er rechts bis zum Widerstand des Nachweises.
        rechts = max(p["M_y"] for p in i["punkte"] if abs(p["N"]) < 40.0)
        self.assertGreater(rechts, 200.0)

    def test_interaktionsdiagramm_mit_wahl(self):
        projekt = Projekt.beispiel().als_dict()
        for fest, wert in (("N", -500.0), ("M_y", 100.0), ("M_z", 40.0)):
            d = dienst.bearbeite("analysediagramme", {
                "projekt": projekt, "kennung": "a1",
                "schnitt": {"fest": fest, "wert": wert}}).daten["diagramme"]["interaktion"]
            with self.subTest(fest=fest):
                self.assertEqual((d["fest"], d["wert"]), (fest, wert))
                self.assertTrue(d["punkte"])
                self.assertTrue(all(abs(p[fest] - wert) < 1e-6 for p in d["punkte"]))

    def test_interaktionsdiagramm_einachsig_ohne_wahl(self):
        projekt = Projekt.beispiel()
        projekt.querschnittsanalysen[0].einachsig = True
        i = dienst.bearbeite("analysediagramme", {
            "projekt": projekt.als_dict(), "kennung": "a1",
            "schnitt": {"fest": "N", "wert": 100.0}}).daten["diagramme"]["interaktion"]
        self.assertIsNone(i["fest"])
        # Der rechte Ast bei N = 0 ist der Widerstand des Nachweises.
        rechts = [p for p in i["punkte"] if p["M_y"] > 0]
        oben = min((p for p in rechts if p["N"] >= 0), key=lambda p: p["N"])
        unten = max((p for p in rechts if p["N"] < 0), key=lambda p: p["N"])
        t = oben["N"] / (oben["N"] - unten["N"])
        self.assertAlmostEqual(oben["M_y"] + t * (unten["M_y"] - oben["M_y"]), 211.8, delta=0.5)

    def test_falscher_schnitt(self):
        antwort = dienst.bearbeite("analysediagramme", {
            "projekt": Projekt.beispiel().als_dict(), "kennung": "a1",
            "schnitt": {"fest": "T", "wert": 0}})
        self.assertEqual(antwort.status, 400)
