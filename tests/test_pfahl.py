"""
Der Einzelpfahl nach SIA 267:2013, Kapitel 9 (opencivil.pfahl).

Die Bilder 12.4 und 12.5 des Buches als Zahlen, das Beispiel des Abschnitts
17.15 als Ganzes, der undrainierte Boden, die Faktoren der Norm, der innere
Widerstand gegen die Handrechnung, die Prüfungen der Eingabe und was die
Oberfläche davon zu sehen bekommt.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import angaben, nachweistabelle, zusammenfassen
from opencivil.core.protokoll import HinweisBlock
from opencivil.pfahl import buch
from opencivil.projekt import PfahlEintrag, Projekt, ProjektFehler
from opencivil.web import dienst
from opencivil.web.api import katalog

#: f_yd von B500B in N/mm², f_cd von C30/37, E_s -- die Handrechnung nimmt sie so.
F_YD = 500.0 / 1.15
F_CD = 20.0
E_S = 200000.0


def projekt(**felder):
    """Ein Projekt mit C30/37 und B500B und einem Pfahl «P» mit diesen Feldern."""
    p = Projekt(name="Probe")
    beton, stahl = p.beton("C30/37").kennung, p.stahl("B500B").kennung
    return p, p.pfahl("P", stahl=stahl, beton=beton, **felder)


def rechnen(p):
    """Aufbau, Lösung und die Befunde von äusserem und innerem Widerstand des Pfahls t1."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    aussen, innen = (aufbau.feld(f)["t1"] for f in ("pfahl_aussen", "pfahl_innen"))
    return aufbau, loesung, loesung.befunde[aussen.id], loesung.befunde[innen.id]


def beispiel_17_15():
    """
    Der Probepfahl des Abschnitts 17.15: ⌀ 800, 3 m Auffüllung und 18 m Ton,
    die nicht tragen, darunter Silt mit φ' = 29°; 4 m Einbindung, K = K_a =
    0.347, δ = 2/3·φ', das Grundwasser 3 m unter Terrain, allgemeines
    Abscheren wie dort.
    """
    p, t = projekt(D=800.0, L=25.0, t_K=0.0, t_w=3.0, abscheren="allgemein")
    t.schicht("Auffüllung", d=3.0, gamma=19.7, mantel="eingeben", q_s=0.0)
    t.schicht("Ton", d=18.0, gamma=19.7, mantel="eingeben", q_s=0.0)
    t.schicht("Silt", d=10.0, gamma=20.2, phi_k=29.0, K=0.347, delta_faktor=2.0 / 3.0)
    t.kombination("Probelast", N_Ed=2500.0)
    return p


def hinweise(loesung):
    return [b.text for b in loesung.protokoll.alle_bloecke() if isinstance(b, HinweisBlock)]


class TestBilderDesBuches(unittest.TestCase):

    def test_x_an_den_stuetzstellen(self):
        self.assertEqual(buch.faktor_x(30.0, 10.0), 2.24)
        self.assertEqual(buch.faktor_x(40.0, 30.0), 4.80)
        self.assertEqual(buch.faktor_x(15.0, 2.5), 1.60)

    def test_x_dazwischen_wie_im_beispiel(self):
        """φ' = 29°, h/D = 5: der Abschnitt 17.15 liest X ≈ 2.0 ab."""
        self.assertAlmostEqual(buch.faktor_x(29.0, 5.0), 2.0, delta=0.02)

    def test_x_ausserhalb_gilt_der_rand(self):
        self.assertEqual(buch.faktor_x(10.0, 1.0), 1.60)
        self.assertEqual(buch.faktor_x(45.0, 50.0), 4.80)
        saetze = buch.ausserhalb(10.0, 1.0)
        self.assertEqual(len(saetze), 2)
        self.assertTrue(all(s.endswith("zu gross.") for s in saetze))
        self.assertEqual(buch.ausserhalb(30.0, 10.0), [])

    def test_n_c_steigt_bis_9(self):
        werte = [buch.faktor_n_c_undrainiert(x / 2.0) for x in range(0, 40)]
        self.assertEqual(werte[0], 6.2)
        self.assertEqual(max(werte), 9.0)
        self.assertEqual(werte, sorted(werte))

    def test_ruhedruck(self):
        self.assertAlmostEqual(buch.ruhedruckbeiwert(math.radians(30.0)), 0.5)


class TestBeispielDesAbschnitts1715(unittest.TestCase):
    """
    Das Buch rechnet mit N_q ≈ 16.4 und X ≈ 2.0 und kommt auf etwa 4529 kN
    an der Spitze und 310 kN am Mantel; hier steht N_q aus der Formel und X
    zwischen den Kurven -- darum ein Prozent Spiel.
    """

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung, cls.aussen, cls.innen = rechnen(beispiel_17_15())

    def test_spitze(self):
        self.assertAlmostEqual(self.aussen.R_b / 1e3, 4529.0, delta=0.01 * 4529.0)

    def test_mantel_nur_im_silt(self):
        self.assertAlmostEqual(self.aussen.R_s / 1e3, 310.0, delta=0.01 * 310.0)
        self.assertEqual([s.q_s for s in self.aussen.stuecke[:2]], [0.0, 0.0])
        silt = self.aussen.stuecke[-1]
        self.assertEqual((silt.stueck.z_o, silt.stueck.z_u), (21.0, 25.0))
        # 3 · 19.7 + 18 · 9.7 + 2 · 10.2 auf halber Einbindung, in kPa.
        self.assertAlmostEqual(silt.sigma / 1e3, 254.1, places=6)

    def test_bemessungswerte(self):
        """(42) mit η_a = 0.7, γ_M,a = 1.3 auf Druck und 1.6 auf Zug, wo nur der Mantel trägt."""
        a = self.aussen
        self.assertAlmostEqual(a.R_ak, a.R_b + a.R_s)
        self.assertAlmostEqual(a.R_ad, 0.7 * (a.R_b + a.R_s) / 1.3)
        self.assertAlmostEqual(a.R_ad_zug, 0.7 * a.R_s / 1.6)

    def test_urteil(self):
        urteil = next(u for u in self.loesung.urteile if u.langname == "Äusserer Pfahlwiderstand")
        self.assertEqual(urteil.fall, "Probelast")
        self.assertAlmostEqual(urteil.erfuellungsgrad.si, self.aussen.R_ad / 2.5e6)


class TestUndrainiert(unittest.TestCase):

    def test_mantel_und_fuss(self):
        """⌀ 1000, 10 m im Ton mit s_u = 60 kPa: q_s = 0.6 · 60, am Fuss L/D = 10, N_c = 9."""
        p, t = projekt(D=1000.0, L=10.0, t_K=0.0)
        t.schicht("Ton", d=30.0, verhalten="undrainiert", s_u=60.0, alpha=0.6)
        t.kombination("K", N_Ed=500.0)
        _, _, aussen, _ = rechnen(p)
        self.assertAlmostEqual(aussen.R_s / 1e3, math.pi * 1.0 * 10.0 * 36.0)
        self.assertAlmostEqual(aussen.q_b / 1e3, 9.0 * 60.0)
        self.assertAlmostEqual(aussen.R_b / 1e3, math.pi / 4.0 * 540.0)


class TestMantel(unittest.TestCase):

    def test_das_wasser_teilt_eine_schicht(self):
        """Je Stück die Spannung in seiner Mitte: über dem Wasser γ, darunter γ − γ_w."""
        p, t = projekt(D=600.0, L=8.0, t_K=0.0, t_w=4.0, spitze="keine")
        t.schicht("Sand", d=20.0, gamma=20.0, phi_k=30.0, K=0.5)
        t.kombination("K", N_Ed=100.0)
        _, _, aussen, _ = rechnen(p)
        self.assertEqual([(s.stueck.z_o, s.stueck.z_u) for s in aussen.stuecke],
                         [(0.0, 4.0), (4.0, 8.0)])
        self.assertEqual([s.sigma / 1e3 for s in aussen.stuecke], [40.0, 100.0])
        tan = math.tan(math.radians(30.0))
        self.assertAlmostEqual(aussen.R_s / 1e3, math.pi * 0.6 * 4.0 * 0.5 * tan * 140.0)
        self.assertIsNone(aussen.q_b)
        self.assertEqual(aussen.R_b, 0.0)

    def test_k_ueber_k_0_gibt_einen_hinweis(self):
        p, t = projekt()
        t.schicht("Kies", d=20.0, phi_k=30.0, K=0.8)
        t.kombination("K", N_Ed=100.0)
        _, loesung, _, _ = rechnen(p)
        self.assertTrue(any("K = 0.80 liegt über K_0" in h for h in hinweise(loesung)))

    def test_oertliches_abscheren_mindert_den_fuss(self):
        fuesse = {}
        for abscheren in ("oertlich", "allgemein"):
            p, t = projekt(abscheren=abscheren)
            t.schicht("Kies", d=20.0, phi_k=34.0)
            t.kombination("K", N_Ed=100.0)
            fuesse[abscheren] = rechnen(p)[2].q_b
        self.assertLess(fuesse["oertlich"], 0.5 * fuesse["allgemein"])


class TestFaktorenDerNorm(unittest.TestCase):

    def test_aus_dem_versuch(self):
        """Statischer Versuch: η_a bis 1.0; R_a,d = R_a,k/1.3 und R_a,k,Z/1.6."""
        p, t = projekt(grundlage="statisch", eta_a=1.0, R_ak=900.0, R_ak_zug=700.0)
        t.kombination("Druck", N_Ed=600.0)
        t.kombination("Zug", N_Ed=-400.0)
        _, loesung, aussen, _ = rechnen(p)
        self.assertTrue(aussen.aus_versuch)
        self.assertEqual(aussen.stuecke, [])
        self.assertAlmostEqual(aussen.R_ad / 1e3, 900.0 / 1.3)
        self.assertAlmostEqual(aussen.R_ad_zug / 1e3, 700.0 / 1.6)
        grade = {u.fall: u.erfuellungsgrad.si for u in loesung.urteile
                 if u.langname == "Äusserer Pfahlwiderstand"}
        self.assertAlmostEqual(grade["Druck"], 900.0 / 1.3 / 600.0)
        self.assertAlmostEqual(grade["Zug"], 700.0 / 1.6 / 400.0)

    def test_eta_a_hoechstens_der_grenzwert_der_grundlage(self):
        for grundlage, eta, gleichung in (("berechnung", 0.8, "(48)"), ("erfahrung", 0.95, "(46)"),
                                          ("dynamisch", 0.95, "(47)")):
            p, t = projekt(grundlage=grundlage, eta_a=eta)
            t.schicht("Kies", d=20.0)
            t.kombination("K", N_Ed=100.0)
            with self.subTest(grundlage=grundlage):
                with self.assertRaises(ProjektFehler) as fehler:
                    p.aufbauen()
                self.assertIn(f"SIA 267:2013, 9.5.2.2.5, {gleichung}", str(fehler.exception))

    def test_eta_i_ueber_0_8_mit_hinweis_hoechstens_0_9(self):
        p, t = projekt(eta_i=0.9)
        t.schicht("Kies", d=20.0)
        t.kombination("K", N_Ed=100.0)
        _, loesung, _, innen = rechnen(p)
        self.assertAlmostEqual(innen.R_id, 0.9 * innen.R_mat)
        self.assertTrue(any("9.5.2.4.9" in h for h in hinweise(loesung)))
        t.eta_i = 0.95
        with self.assertRaises(ProjektFehler) as fehler:
            p.aufbauen()
        self.assertIn("η_i", str(fehler.exception))


class TestInnererWiderstand(unittest.TestCase):

    def test_bohrpfahl_von_hand(self):
        """
        ⌀ 900 mit 12 ⌀ 20: auf Druck bis ε_c1d = 2 ‰, der Beton mit f_cd, der
        Stahl mit 2 ‰ · E_s; auf Zug nur der Stahl, mit f_yd.
        """
        p, t = projekt()
        t.schicht("Kies", d=20.0)
        t.kombination("K", N_Ed=100.0)
        _, _, _, innen = rechnen(p)
        A_c = math.pi * 900.0 ** 2 / 4.0
        A_s = 12 * math.pi * 20.0 ** 2 / 4.0
        self.assertAlmostEqual(innen.A_s * 1e6, A_s)
        sigma_s = min(0.002 * E_S, F_YD)
        self.assertAlmostEqual(innen.R_mat / 1e3, ((A_c - A_s) * F_CD + A_s * sigma_s) / 1e3,
                               delta=0.5)
        self.assertAlmostEqual(innen.R_mat_zug / 1e3, A_s * F_YD / 1e3, delta=0.5)
        self.assertAlmostEqual(innen.R_id, 0.8 * innen.R_mat)

    def test_mikropfahl_rohr_nach_abrostung(self):
        """Rohr 88.9 × 8, Δt = 1 mm aussen: d_a = 86.9, innen 72.9 mm -- nur der Stahl."""
        p, t = projekt(art="mikropfahl", D=200.0, grundlage="statisch", d_a=88.9, t_r=8.0,
                       dt=1.0)
        t.kombination("K", N_Ed=100.0)
        _, _, _, innen = rechnen(p)
        A = math.pi / 4.0 * (86.9 ** 2 - 72.9 ** 2)
        self.assertAlmostEqual(innen.R_mat / 1e3, A * F_YD / 1e3, delta=0.5)
        self.assertAlmostEqual(innen.R_mat_zug, innen.R_mat)

    def test_mikropfahl_stab(self):
        p, t = projekt(art="mikropfahl", D=150.0, grundlage="statisch", tragglied="stab",
                       d_a=40.0, dt=2.0)
        t.kombination("K", N_Ed=-100.0)
        _, _, _, innen = rechnen(p)
        self.assertAlmostEqual(innen.R_mat_zug / 1e3, math.pi / 4.0 * 36.0 ** 2 * F_YD / 1e3,
                               delta=0.5)

    def test_ein_mikropfahl_braucht_keinen_beton(self):
        p = Projekt(name="Probe")
        stahl = p.stahl("B500B").kennung
        t = p.pfahl("P", stahl=stahl, art="mikropfahl", D=200.0, grundlage="statisch")
        t.kombination("K", N_Ed=100.0)
        self.assertEqual(t.materialien(), [stahl])
        _, loesung, _, innen = rechnen(p)
        self.assertGreater(innen.R_id, 0.0)


class TestEintrag(unittest.TestCase):

    def test_neu_mit_einer_schicht_und_einer_kombination(self):
        t = PfahlEintrag.neu("t1", "Pfahl 1")
        self.assertEqual([s.name for s in t.schichten], ["Kies"])
        self.assertEqual([(k.name, k.N_Ed) for k in t.kombinationen], [("Kombination 1", 1000.0)])
        self.assertEqual((t.art, t.D, t.L, t.eta_a, t.eta_i), ("bohrpfahl", 900.0, 10.0, 0.7, 0.8))

    def test_hin_und_zurueck(self):
        p = beispiel_17_15()
        p.pfaehle[0].kombination("Zug", N_Ed=-100.0).aktiv = False
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.pfaehle, p.pfaehle)
        self.assertEqual(wieder.pfaehle[0].schichten[0].mantel, "eingeben")
        self.assertEqual(p.pfahl("Zweiter", stahl="").kennung, "t2")

    def test_ohne_kombination_kein_nachweis(self):
        p, t = projekt()
        t.schicht("Kies", d=20.0)
        aufbau = p.aufbauen()
        self.assertEqual(aufbau.feld("pfahl_aussen"), {})
        self.assertEqual(aufbau.feld("pfahl_innen"), {})
        self.assertIn("Pfahl 'P': keine Kombination → kein Nachweis.", aufbau.warnungen)

    def test_unmoegliche_zahlen_vor_dem_rechnen(self):
        faelle = {
            "ohne Schicht": ({}, None),
            "muss grösser sein als die des Wassers": ({}, {"gamma": 10.0}),
            "drainiert braucht φ'_k über null": ({}, {"phi_k": 0.0}),
            "undrainiert braucht s_u,k über null": ({}, {"verhalten": "undrainiert", "s_u": 0.0}),
            "Unter dem Fuss muss noch Boden sein": ({"L": 19.0}, {}),
            "die Stäbe haben keinen Platz": ({"D": 150.0}, {}),
            "berühren sich": ({"n": 120}, {}),
            "muss im Verpresskörper liegen": ({"art": "mikropfahl", "D": 100.0}, {}),
            "zu dick für ein Rohr": ({"art": "mikropfahl", "t_r": 60.0}, {}),
            "frisst die ganze Wand": ({"art": "mikropfahl", "dt": 10.0}, {}),
            "frisst den ganzen Stab": ({"art": "mikropfahl", "tragglied": "stab", "d_a": 10.0,
                                        "dt": 5.0}, {}),
        }
        for satz, (felder, schicht) in faelle.items():
            p, t = projekt(**felder)
            if schicht is not None:
                t.schicht("Kies", **{"d": 20.0, **schicht})
            t.kombination("K", N_Ed=100.0)
            with self.subTest(satz=satz):
                with self.assertRaises(ProjektFehler) as fehler:
                    p.aufbauen()
                self.assertIn(satz, str(fehler.exception))

    def test_kombinationen_eindeutig(self):
        p, t = projekt()
        t.schicht("Kies", d=20.0)
        t.kombination("A", N_Ed=100.0)
        t.kombination("A", N_Ed=200.0)
        with self.assertRaises(ProjektFehler):
            p.aufbauen()

    def test_ein_wort_das_es_nicht_gibt(self):
        p, t = projekt()
        with self.assertRaises(ProjektFehler) as fehler:
            t.schicht("Kies", verhalten="teilweise")
        self.assertIn("'teilweise' gibt es als 'verhalten' nicht", str(fehler.exception))


class TestWasDieOberflaecheSieht(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.antwort = dienst.bearbeite("rechnen", {"projekt": Projekt.beispiel().als_dict()})

    def test_katalog(self):
        k = katalog()
        self.assertEqual(k["neu"]["pfaehle"]["schichten"][0]["name"], "Kies")
        self.assertEqual(k["felder"]["pfahl"]["D"]["einheit"], "mm")
        self.assertEqual(k["felder"]["pfahlschicht"]["q_s"]["einheit"], "kPa")
        self.assertEqual(k["felder"]["pfahlkombination"]["N_Ed"]["einheit"], "kN")
        self.assertEqual([(g["wert"], g["grenze"], g["versuch"]) for g in k["pfahl"]["grundlagen"]],
                         [("berechnung", 0.7, False), ("erfahrung", 0.9, False),
                          ("dynamisch", 0.9, True), ("statisch", 1.0, True)])
        # Auf dem Knopf ein Wort, die Erklärung darüber.
        for liste in ("arten", "spitzen", "abscheren", "tragglieder", "verhalten", "mantel"):
            for w in k["pfahl"][liste]:
                with self.subTest(liste=liste, wert=w["wert"]):
                    self.assertLessEqual(len(w["beschriftung"]), 12)
                    self.assertGreater(len(w["titel"]), len(w["beschriftung"]))

    def test_situation(self):
        self.assertEqual(self.antwort.status, 200)
        s = self.antwort.daten["zeichendaten"]["t1"]
        self.assertEqual([(x["z_o"], x["z_u"]) for x in s["stuecke"]],
                         [(1.5, 2.0), (2.0, 3.0), (3.0, 8.0), (8.0, 13.5)])
        self.assertEqual(s["stuecke"][0]["q_s"], 0.0)
        self.assertGreater(s["q_b"], 1000.0)
        zeilen = ["".join(z.get("text") or z["mathe"] for z in zeile) for zeile in s["legende"]]
        self.assertTrue(zeilen[0].startswith("Mantel R_{s,k}"))
        self.assertTrue(zeilen[1].startswith("Auf Druck R_{a,d}"))
        self.assertEqual(zeilen[2], r"Quer, in «Tragsicherheit» R_{tr,d} = 339\,\mathrm{kN} "
                                    "(Gelenk im Pfahl).")
        self.assertTrue(zeilen[3].startswith("Massgebend: Äusserer Pfahlwiderstand, "
                                             "Tragsicherheit – erfüllt"))

    def test_ohne_kombination_nur_der_pfahl(self):
        p, t = projekt()
        t.schicht("Kies", d=20.0)
        s = dienst.rechnen({"projekt": p.als_dict()})["zeichendaten"]["t1"]
        self.assertEqual((s["stuecke"], s["q_b"]), ([], None))

    def test_zusammenfassung(self):
        p = Projekt.beispiel()
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        kopf, tabelle = angaben(aufbau, "t1", loesung)
        self.assertEqual(kopf.titel, "Angaben zum Pfahl")
        self.assertIn(r"\text{Bohrpfahl}", kopf.latex)
        self.assertEqual(tabelle.titel, "Widerstände")
        self.assertEqual([z[0] for z in tabelle.zeilen],
                         ["Mantel", "Fuss", "Äusserer, charakteristisch",
                          "Äusserer, Bemessungswert", "Querschnitt", "Innerer, Bemessungswert"])
        teil = next(b for b in zusammenfassen(aufbau, loesung).bauteile if b.kennung == "t1")
        self.assertEqual([z[:2] for z in nachweistabelle(teil).zeilen],
                         [["Äusserer Pfahlwiderstand", "Tragsicherheit"],
                          ["Innerer Pfahlwiderstand", "Tragsicherheit"],
                          ["Äusserer Pfahlwiderstand quer", "Tragsicherheit"],
                          ["Bettungskraft am Pfahl", "Tragsicherheit"],
                          ["Biegung im Pfahl", "Tragsicherheit"],
                          ["Querkraft im Pfahl", "Tragsicherheit"]])


if __name__ == "__main__":
    unittest.main()
