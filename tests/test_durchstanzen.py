"""
Der Durchstanznachweis ohne Durchstanzbewehrung (opencivil.durchstanzen.nachweis).

Eine Innenstütze gegen die Gleichungen (58) bis (60) von Hand, die Näherungen
für k_e je Lage, die Ovalstütze, Decke und Bodenplatte, die Wand in
Näherungsstufe 2, Aussparungen aus Knoten, die Prüfungen der Eingabe und was
die Oberflaeche davon zu sehen bekommt.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import angaben, nachweistabelle, zusammenfassen
from opencivil.projekt import DurchstanzEintrag, Projekt, ProjektFehler
from opencivil.web import dienst
from opencivil.web.api import katalog

#: C30/37 und B500B nach SIA 262 -- τ_cd = 0.3·√f_ck / γ_c, f_yd = f_sk / γ_s.
TAU_CD = 0.3 * math.sqrt(30.0) / 1.5
F_YD = 500.0 / 1.15
E_S = 200000.0


def projekt(**felder):
    """Ein Projekt mit einer Durchstanzstelle -- C30/37, B500B, sonst die Vorgaben."""
    p = Projekt(name="Probe")
    beton, stahl = p.beton("C30/37"), p.stahl("B500B")
    p.durchstanzen("S", beton.kennung, stahl.kennung, **felder)
    return p


def rechnen(p):
    """Aufbau, Lösung, Befund und Urteil der ersten Durchstanzstelle."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
    nachweis = aufbau.feld("durchstanzen")[p.durchstanzstellen[0].kennung]
    urteil = next(u for u in loesung.urteile if u.raum == nachweis.id)
    return aufbau, loesung, loesung.befunde[nachweis.id], urteil


def texte(loesung):
    """Was das Protokoll in Worten sagt -- Titel, Erklärungen und Hinweise."""
    return " ".join(str(getattr(b, "titel", "") or getattr(b, "text", ""))
                    for b in loesung.protokoll.bloecke)


class TestInnenstuetzeVonHand(unittest.TestCase):
    """400 × 400 mm, h = 280 mm, ⌀16 @ 150 in x aussen, Näherungsstufe 1."""

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung, cls.befund, cls.urteil = rechnen(
            projekt(b_x=400, b_y=400, stufe="1", V_d=800.0))

    def test_statische_hoehe(self):
        """d_x = 280 − 30 − 8, d_y = 280 − 30 − 16 − 8; d ist ihr Mittel, d_v = d."""
        self.assertAlmostEqual(self.befund.d, (0.242 + 0.226) / 2)
        self.assertAlmostEqual(self.befund.d_v, self.befund.d)

    def test_nachweisschnitt_mit_k_e(self):
        """u = k_e · (2·(b_x + b_y) + π·d_v), k_e = 0.9 für Innenstützen."""
        self.assertEqual(self.befund.k_e, 0.9)
        self.assertAlmostEqual(self.befund.u, 0.9 * (1.6 + math.pi * 0.234), places=4)

    def test_rotation_in_stufe_1(self):
        """ψ = 1.5 · r_s/d · f_yd/E_s mit r_s = 0.22 · l (60)."""
        psi = 1.5 * 0.22 * 7.0 / 0.234 * F_YD / E_S
        self.assertAlmostEqual(self.befund.psi, psi, places=6)

    def test_widerstand(self):
        """k_r nach (59) mit k_g = 1.2 (D_max = 32), V_Rd,c = k_r · τ_cd · d_v · u (58)."""
        psi = 1.5 * 0.22 * 7.0 / 0.234 * F_YD / E_S
        k_r = 1.0 / (0.45 + 0.18 * psi * 234.0 * 1.2)
        self.assertAlmostEqual(self.befund.k_r, k_r, places=5)
        V_Rd = k_r * TAU_CD * 234.0 * 0.9 * (1600.0 + math.pi * 234.0)
        self.assertAlmostEqual(self.befund.V_Rd_c, V_Rd, delta=1.0)

    def test_urteil(self):
        """Der Erfüllungsgrad ist der Widerstand durch die Querkraft -- hier nicht erfüllt."""
        self.assertFalse(self.urteil.erfuellt)
        self.assertAlmostEqual(self.urteil.erfuellungsgrad.si, self.befund.V_Rd_c / 800e3, places=6)
        self.assertEqual(self.urteil.name, "Durchstanzen – ohne Durchstanzbewehrung")


class TestFormenUndLagen(unittest.TestCase):

    def test_k_e_nach_der_naeherung(self):
        """4.3.6.2.5: innen 0.9, Rand 0.7, Ecke 0.65, Wandende und Wandecke 0.75."""
        for lage, k_e in (("innen", 0.9), ("rand", 0.7), ("ecke", 0.65),
                          ("wandende", 0.75), ("wandecke", 0.75)):
            with self.subTest(lage=lage):
                self.assertEqual(rechnen(projekt(lage=lage, V_d=100.0))[2].k_e, k_e)

    def test_ovalstuetze(self):
        """Zwei Geraden b_x − b_y und zwei Halbkreise mit dem Radius b_y/2 + d_v/2."""
        befund = rechnen(projekt(form="oval", b_x=900, b_y=300, V_d=100.0))[2]
        soll = 2 * 0.6 + math.pi * (0.3 + befund.d_v)
        self.assertAlmostEqual(befund.schnitt.massgebend.in_der_platte, soll, places=3)
        self.assertAlmostEqual(befund.u, 0.9 * soll, places=3)

    def test_rundstuetze(self):
        befund = rechnen(projekt(form="rund", D=400, V_d=100.0))[2]
        self.assertAlmostEqual(befund.u, 0.9 * math.pi * (0.4 + befund.d_v), places=3)

    def test_bodenplatte_zieht_die_bodenpressung_ab(self):
        """4.3.6.2.6: V_d,red = V_d − q_d · A im Schnitt; die Zugbewehrung liegt unten."""
        _, loesung, befund, _ = rechnen(projekt(plattenart="bodenplatte", V_d=1000.0, q_d=200.0))
        A = befund.schnitt.massgebend.flaeche
        self.assertAlmostEqual(befund.V_d_red, 1000e3 - 200e3 * A, places=3)
        self.assertIn("Bodenpressung innerhalb des Nachweisschnitts", texte(loesung))
        self.assertIn("Überdeckung der Zugbewehrung unten", texte(loesung))

    def test_wand_rechnet_in_stufe_2_wie_in_stufe_1(self):
        """Für Wände nennt 4.3.6.4.7 keine Momente: ψ wie in Stufe 1, und e fragt niemand."""
        zwei = rechnen(projekt(lage="wandende", stufe="2", V_d=300.0))
        eins = rechnen(projekt(lage="wandende", stufe="1", V_d=300.0))
        self.assertAlmostEqual(zwei[2].psi, eins[2].psi)
        self.assertIn("gerechnet wie in Näherungsstufe 1", texte(zwei[1]))
        stelle = zwei[0].teile["d1"].objekt
        self.assertNotIn("e_x", stelle.eingaben())

    def test_stufe_3_mit_momenten_von_hand(self):
        """1.2 statt 1.5 vor der Klammer, r_s und m_sd wie eingegeben."""
        befund = rechnen(projekt(stufe="3", r_sx=1.6, r_sy=1.6, m_sdx=100.0, m_sdy=100.0,
                                 V_d=500.0))[2]
        x = next(r for r in befund.rotationen if r.richtung.value == "x")
        self.assertAlmostEqual(x.psi, 1.2 * 1.6 / befund.d * F_YD / E_S
                               * (x.m_sd / x.m_Rd) ** 1.5, places=8)


class TestAussparungen(unittest.TestCase):

    def test_aussparung_im_schatten(self):
        """Eine Aussparung neben der Stütze mindert u; k_e wie bei grossen Aussparungen 0.7."""
        p = projekt(V_d=500.0)
        p.durchstanzstellen[0].aussparung([[250, -100], [450, -100], [450, 100], [250, 100]])
        befund = rechnen(p)[2]
        self.assertGreater(befund.schnitt.massgebend.hinter_aussparungen, 0.1)
        self.assertEqual(befund.k_e, 0.7)
        self.assertEqual(len(befund.aussparungen), 1)

    def test_gleiche_ecken_sind_ein_knoten(self):
        """Zwei Aussparungen an derselben Ecke teilen sich den Knoten -- wie im Zeichenfenster."""
        d = projekt().durchstanzstellen[0]
        d.aussparung([[500, 0], [700, 0], [700, 200]])
        d.aussparung([[700, 200], [900, 200], [900, 400]])
        self.assertEqual(len(d.knoten), 5)
        self.assertEqual([a.kennung for a in d.aussparungen], ["A1", "A2"])

    def test_aussparung_mit_zwei_ecken(self):
        p = projekt()
        p.durchstanzstellen[0].aussparung([[500, 0], [700, 0]])
        with self.assertRaises(ProjektFehler) as fehler:
            p.aufbauen()
        self.assertIn("Aussparung A1", str(fehler.exception))

    def test_aussparung_mit_fehlendem_knoten(self):
        p = projekt()
        d = p.durchstanzstellen[0]
        d.aussparung([[500, 0], [700, 0], [700, 200]])
        d.aussparungen[0].knoten.append("K99")
        with self.assertRaises(ProjektFehler) as fehler:
            p.aufbauen()
        self.assertIn("die Knoten K99 gibt es nicht", str(fehler.exception))


class TestEingaben(unittest.TestCase):

    def test_neu_ohne_einwirkung(self):
        neu = DurchstanzEintrag.neu(kennung="d1", name="S")
        self.assertEqual((neu.V_d, neu.q_d), (0.0, 0.0))
        self.assertEqual((neu.lage, neu.form), ("innen", "rechteck"))

    def test_unmoegliche_zahlen_vor_dem_rechnen(self):
        for felder, satz in (({"h": 0.0}, "Plattendicke h muss grösser als null sein"),
                             ({"V_d": -1.0}, "Auflagerkraft V_d kann nicht negativ sein"),
                             ({"b_x": 0.0}, "Stütze b_x muss grösser als null sein")):
            with self.subTest(felder=felder):
                with self.assertRaises(ProjektFehler) as fehler:
                    projekt(**felder).aufbauen()
                self.assertIn(satz, str(fehler.exception))

    def test_eine_lage_die_es_nicht_gibt(self):
        with self.assertRaises(ProjektFehler) as fehler:
            projekt(lage="mitte")
        self.assertIn("'mitte' gibt es als 'lage' nicht", str(fehler.exception))

    def test_datei_hin_und_zurueck(self):
        p = projekt(lage="ecke", a_x=50, a_y=80, form="oval", b_x=600, b_y=300)
        p.durchstanzstellen[0].aussparung([[500, 0], [700, 0], [700, 200]])
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.als_dict(), p.als_dict())
        self.assertEqual(wieder.durchstanzstellen[0].aussparungen[0].knoten, ["K1", "K2", "K3"])


class TestWasDieOberflaecheSieht(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        p = projekt(lage="rand", a_y=100, V_d=400.0)
        p.durchstanzstellen[0].aussparung([[300, 200], [500, 200], [500, 400], [300, 400]])
        cls.projekt = p
        cls.antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})

    def test_katalog(self):
        k = katalog()
        self.assertEqual(k["neue_durchstanzstelle"]["h"], 280.0)
        self.assertEqual(k["felder"]["durchstanz"]["l_x"]["einheit"], "m")
        self.assertEqual([f["wert"] for f in k["durchstanzen"]["formen"]],
                         ["rechteck", "rund", "oval"])
        self.assertEqual([f["wert"] for f in k["durchstanzen"]["lagen"]],
                         ["innen", "rand", "ecke", "wandende", "wandecke"])

    def test_grundriss_in_mm(self):
        self.assertEqual(self.antwort.status, 200)
        s = self.antwort.daten["durchstanzstellen"]["d1"]
        self.assertEqual(len(s["raender"]), 1)
        rand = s["raender"][0]
        self.assertAlmostEqual(rand["punkt"][1], -250.0)
        self.assertAlmostEqual(rand["richtung"], math.pi / 2)
        self.assertEqual(s["aussparungen"], [[[300.0, 200.0], [500.0, 200.0], [500.0, 400.0],
                                              [300.0, 400.0]]])
        self.assertTrue(any(not l["zaehlt"] for l in s["schnitt"]))
        self.assertAlmostEqual(s["u"], 1e3 * s["k_e"] * (
            sum(math.dist(p, q) for l in s["schnitt"] if l["zaehlt"]
                for p, q in zip(l["punkte"], l["punkte"][1:])) / 1e3), delta=2.0)

    def test_zusammenfassung(self):
        aufbau = self.projekt.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.alle_nachweisziele())
        teil = next(b for b in zusammenfassen(aufbau, loesung).bauteile if b.kennung == "d1")
        kopf, tabelle = angaben(aufbau, "d1", loesung)
        self.assertEqual(kopf.titel, "Angaben zur Durchstanzstelle")
        self.assertIn("Randstütze, Decke", kopf.latex)
        self.assertEqual(tabelle.zeilen[0][0], "Wirksame statische Höhe")
        self.assertEqual([z[:2] for z in nachweistabelle(teil).zeilen],
                         [["Durchstanzen", "ohne Durchstanzbewehrung"]])


if __name__ == "__main__":
    unittest.main()
