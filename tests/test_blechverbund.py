"""
Tests fuer die Blechverbunddecke nach SIA 264:2014, 5.4 (Plan vom
2026-11-25, Schritt 14d): ihre Form, ihre Kennzahlen, die Nachweise je
Lastfall, was der Laengsschub braucht, und was die Oberflaeche vom Kern
liest.

Von Hand, an der Decke nach Vorgabe -- fuenf offene Rippen im Abstand
b_s = 200 mm, h_p = 60 mm hoch, oben 120 und unten 70 mm breit,
A_p = 1100 mm² je Meter, unter h = 140 mm aus C25/30, das Blech SE 350 G
mit f_yp = 350 N/mm² und γ = 1.05:

* Der Steg ist √(60² + 25²) = 65 lang, ein Blech je Rippe s = 70 + 2 · 65
  + 80 = 280 mm, also t = 1100 · 0.2/280. Sein Schwerpunkt liegt
  e = (30 · 130 + 60 · 80)/280 ueber der Unterkante, d_p = h - e;
  b_0 = (120 + 70)/2 = 95 (Figur 18).
* Beton: 1000 · 80 + 5 · 95 · 60 = 108 500 mm². Zug traegt das Blech,
  A_p f_yp/γ, Druck der Beton mit 0.85 f_cd.
* M_Rd unten: die Druckzone x = T/(0.85 f_cd b) liegt in der Platte, der
  Hebel ist d_p - x/2. Oben zaehlt das Blech nicht (5.4.3.2): ohne
  Betonstahl traegt nichts Zug.
* (26): 0.8 τ_cd d_p b_0/b_s je mm Breite, τ_cd = 0.3 √25/1.5 = 1.0.
* (28) mit m = 150 und k = 0.1 N/mm², L = 3 m im Einfeld: L_s = L/4.
"""

import math
import unittest

from opencivil.bericht.markdown import als_markdown
from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.core.sprache import aufgezaehlt
from opencivil.material.basis import Baustoffart
from opencivil.nachweis.qa_blechverbund import EINE_RICHTUNG, NICHT_GERECHNET, OHNE_BLECH, OHNE_ZUG
from opencivil.projekt.blechdecken import BlechdeckeEintrag
from opencivil.projekt.lesen import feldangaben
from opencivil.projekt.projekt import Projekt
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.querschnitt.bauweise import Bauweise, Mischung, bauweise
from opencivil.querschnitt.biegung import EINACHSIG
from opencivil.verbund.blechdecke import Belastung, Feld, Laengsschub
from opencivil.web import dienst
from tests.unfertig import grund

#: Die Form der Decke nach Vorgabe, in mm -- siehe Dateikopf.
S = 70.0 + 2.0 * 65.0 + 80.0
E = (30.0 * 130.0 + 60.0 * 80.0) / S
D_P = 140.0 - E
B_0 = 95.0

#: f_yp/γ des Blechs und 0.85 f_cd von C25/30, in N/mm².
F_YP = 350.0 / 1.05
F_C = 0.85 * 25.0 / 1.5

#: Das Blech gezogen, in N.
T = 1100.0 * F_YP

#: (26) ueber die Breite von 1000 mm, in N.
V_RD = 0.8 * 1.0 * D_P * B_0 / 200.0 * 1000.0

#: Was der Laengsschub nach Vorgabe der Tests braucht: m, k und L.
MK = {"blech_m": 150.0, "blech_k": 0.1, "blech_L": 3.0}


def v_l_rd(L_s, m=150.0, k=0.1, d_p=D_P):
    """(28) ueber die Breite von 1000 mm mit 1100 mm² Blech, in N -- ``L_s`` in mm."""
    return 1000.0 * d_p * (m * 1100.0 / (1000.0 * L_s) + k) / 1.25


def projekt(beton="C25/30"):
    """Ein Projekt mit Beton b1, Betonstahl s1 und dem Profilblechstahl pb1."""
    p = Projekt(name="Decke")
    p.beton(beton)
    p.stahl("B500B")
    p.profilblech("SE 350 G")
    return p


def decke(p, schub=None, faelle=None, **masse):
    """
    Eine Analyse mit einer Decke an der Ecke (0, 0) -- ``masse`` ihre Felder,
    ``schub`` die Felder des Laengsschubs an der Analyse, ``faelle`` die
    Lastfaelle.
    """
    a = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name="Decke")
    a.blechdecke(0.0, 0.0, beton="b1", blech="pb1", **masse)
    for feld, wert in (schub or {}).items():
        setattr(a, feld, wert)
    for name, werte in (faelle or {}).items():
        a.lastfall(name, **werte)
    p.querschnittsanalysen.append(a)
    return a


def rechnen(p, a):
    """Die Kennzahlen in ihrer Einheit, die Urteile je (Art, Fall), der Bericht und der Aufbau."""
    aufbau = p.aufbauen()
    teil = aufbau.teile[a.kennung]
    loesung = aufbau.werk.loese(*teil.ziele())
    werte = {}
    for k in teil.kennzahlen:
        w = loesung.wert(k.definition.id)
        werte[k.definition.id.rsplit(".", 1)[1]] = w.in_einheit(w.einheit)
    urteile = {(u.art, u.fall): u for u in loesung.urteile}
    return werte, urteile, als_markdown(loesung), aufbau


def geometrie(p, a):
    """Was das Zeichenfenster zur Analyse ``a`` vom Kern liest."""
    return dienst.geometrie({"projekt": p.als_dict(), "kennung": a.kennung})


def grad(urteil):
    return urteil.erfuellungsgrad.si


class TestForm(unittest.TestCase):
    """Was aus den Massen folgt -- wie das Zeichenfenster es liest."""

    def test_offenes_blech(self):
        p = projekt()
        g = geometrie(p, decke(p))
        self.assertEqual(g["bauweise"], "blechverbund")
        d = g["blechdecken"][0]
        self.assertFalse(d["hinterschnitten"])
        w = d["werte"]
        self.assertAlmostEqual(w["b"], 1000.0)
        self.assertAlmostEqual(w["t"], 1100.0 * 0.2 / S)
        self.assertAlmostEqual(w["e"], E)
        self.assertAlmostEqual(w["d_p"], D_P)
        self.assertAlmostEqual(w["b_0"], B_0)
        self.assertAlmostEqual(w["A"], 1100.0)

    def test_hinterschnittenes_blech(self):
        """Unten breiter: b_0 ist die schmalste Breite, oben (Figur 18)."""
        p = projekt()
        d = geometrie(p, decke(p, h=200.0, b_o=70.0, b_u=120.0))["blechdecken"][0]
        s = 120.0 + 2.0 * 65.0 + 130.0
        self.assertTrue(d["hinterschnitten"])
        self.assertAlmostEqual(d["werte"]["b_0"], 70.0)
        self.assertAlmostEqual(d["werte"]["t"], 220.0 / s)
        self.assertAlmostEqual(d["werte"]["d_p"], 200.0 - (30.0 * 130.0 + 60.0 * 130.0) / s)

    def test_rippe_im_bild(self):
        """Die Rippe mit ihren Massen kommt mit der Zeichnung -- fuer das Fenster."""
        p = projekt()
        d = geometrie(p, decke(p))["blechdecken"][0]
        self.assertTrue(d["rippe"]["polygone"])
        self.assertEqual(d["fang"], d["umriss"][0])


class TestKennzahlen(unittest.TestCase):
    """Die Decke nach Vorgabe im Einfeld, von Hand -- siehe Dateikopf."""

    @classmethod
    def setUpClass(cls):
        p = projekt()
        cls.k, cls.urteile, cls.text, _ = rechnen(p, decke(p, MK, {
            "Feld": {"M_y_Ed": 30.0, "V_z_Ed": 20.0},
            "Stütze": {"M_y_Ed": -10.0, "V_z_Ed": -25.0},
            "Zug": {"N_Ed": 150.0},
        }))

    def test_normalkraft(self):
        """Zug traegt nur das Blech, Druck nur der Beton."""
        self.assertAlmostEqual(self.k["N_Rd_zug"], T / 1e3, places=6)
        beton = 1000.0 * 80.0 + 5 * B_0 * 60.0
        self.assertAlmostEqual(beton, 108500.0)
        self.assertAlmostEqual(self.k["N_Rd_druck"], -beton * F_C / 1e3, places=6)

    def test_moment_unten(self):
        x = T / (F_C * 1000.0)
        self.assertLess(x, 80.0)
        self.assertAlmostEqual(self.k["M_Rd_unten"], T * (D_P - x / 2.0) / 1e6, places=6)

    def test_moment_oben_ohne_blech(self):
        """Ohne Betonstahl traegt oben nichts Zug: das Blech zaehlt dort nicht."""
        self.assertEqual(self.k["M_Rd_oben"], 0.0)

    def test_querkraft(self):
        self.assertAlmostEqual(self.k["V_Rd"], V_RD / 1e3, places=6)

    def test_laengsschub(self):
        self.assertAlmostEqual(self.k["V_L_Rd"], v_l_rd(750.0) / 1e3, places=6)

    def test_schlankheit(self):
        """L/d_p ueber 26: die Durchbiegung muesste gerechnet werden."""
        self.assertAlmostEqual(self.k["L_d_p"], 3000.0 / D_P, places=6)
        self.assertGreater(self.k["L_d_p"], 26.0)

    def test_feld(self):
        x = T / (F_C * 1000.0)
        M_Rd = T * (D_P - x / 2.0)
        self.assertAlmostEqual(grad(self.urteile["M-N", "Feld"]), M_Rd / 30e6, places=6)
        self.assertAlmostEqual(grad(self.urteile["V", "Feld"]), V_RD / 20e3, places=6)
        self.assertAlmostEqual(grad(self.urteile["V_L", "Feld"]), v_l_rd(750.0) / 20e3, places=6)
        self.assertTrue(all(self.urteile[art, "Feld"].erfuellt for art in ("M-N", "V", "V_L")))

    def test_stuetze_ohne_bewehrung(self):
        """Negatives Moment ohne Betonstahl: null, rot, und warum -- die Querkraft als Betrag."""
        u = self.urteile["M-N", "Stütze"]
        self.assertEqual((u.erfuellt, grad(u), u.begruendung), (False, 0.0, OHNE_ZUG))
        self.assertAlmostEqual(grad(self.urteile["V", "Stütze"]), V_RD / 25e3, places=6)
        self.assertAlmostEqual(grad(self.urteile["V_L", "Stütze"]), v_l_rd(750.0) / 25e3,
                               places=6)

    def test_reiner_zug_mit_blech(self):
        """Ohne Moment zaehlt das Blech gezogen."""
        u = self.urteile["M-N", "Zug"]
        self.assertAlmostEqual(grad(u), T / 150e3, places=6)
        self.assertEqual(u.begruendung, "Reine Normalkraft.")

    def test_ohne_querkraft_kein_schub(self):
        """Der Zug hat keine Querkraft: dort sagt das Urteil, dass es nichts nachweist."""
        for art in ("V", "V_L"):
            u = self.urteile[art, "Zug"]
            self.assertEqual((u.erfuellt, u.begruendung), (True, OHNE_EINWIRKUNG))

    def test_bericht(self):
        """Was die Decke annimmt und nicht rechnet, steht in der Herleitung."""
        for text in (EINE_RICHTUNG.split(":")[0], NICHT_GERECHNET, OHNE_BLECH, OHNE_ZUG):
            self.assertIn(text, self.text)


class TestHinterschnitten(unittest.TestCase):
    """
    200 mm auf hinterschnittenen Rippen (oben 70, unten 120 mm breit), oben
    ⌀10 @ 150 bei z = 170 -- sieben Staebe --, ein Innenfeld unter zwei
    Einzellasten im Abstand a = 0.9 m.
    """

    S = 120.0 + 2.0 * 65.0 + 130.0
    D_P = 200.0 - (30.0 * 130.0 + 60.0 * 130.0) / S

    @classmethod
    def setUpClass(cls):
        p = projekt()
        a = decke(p, {"blech_m": 180.0, "blech_k": 0.05, "blech_L": 3.6,
                      "blech_feld": Feld.INNENFELD, "blech_last": Belastung.EINZELLASTEN,
                      "blech_a": 0.9},
                  {"Stütze": {"M_y_Ed": -15.0, "V_z_Ed": 30.0}},
                  h=200.0, b_o=70.0, b_u=120.0)
        a.stablinie([20, 170], [980, 170], art="teilung", durchmesser=10, teilung=150,
                    stahl="s1")
        cls.k, cls.urteile, cls.text, _ = rechnen(p, a)

    def test_stuetze_mit_betonstahl(self):
        """
        Der Betonstahl zieht, der Beton drueckt unten in den Rippen, die nach
        oben schmaler werden: 5 · (120 x - 50/60 · x²/2) · 0.85 f_cd = T_s.
        """
        T_s = 7 * math.pi * 5.0 ** 2 * 500.0 / 1.15
        a2, a1 = F_C * 5 * 50.0 / 60.0 / 2.0, F_C * 5 * 120.0
        x = (a1 - math.sqrt(a1 ** 2 - 4.0 * a2 * T_s)) / (2.0 * a2)
        self.assertLess(x, 60.0)
        z = (60.0 * x ** 2 - 50.0 / 60.0 * x ** 3 / 3.0) / (120.0 * x - 50.0 / 60.0 * x ** 2 / 2.0)
        M_Rd = T_s * (170.0 - z)
        self.assertAlmostEqual(self.k["M_Rd_oben"], -M_Rd / 1e6, places=4)
        self.assertAlmostEqual(grad(self.urteile["M-N", "Stütze"]), M_Rd / 15e6, places=4)

    def test_querkraft_ueber_150(self):
        """d_p ueber 150 mm: (26) gilt nicht -- keine Kennzahl, und das Urteil sagt warum."""
        self.assertGreater(self.D_P, 150.0)
        self.assertNotIn("V_Rd", self.k)
        u = self.urteile["V", "Stütze"]
        self.assertFalse(u.erfuellt)
        self.assertIn("SIA 262", u.hinweis)

    def test_schublaenge_ist_der_abstand(self):
        """Mit zwei Einzellasten ist L_s = a -- das Innenfeld aendert sie nicht."""
        self.assertAlmostEqual(self.k["V_L_Rd"],
                               v_l_rd(900.0, m=180.0, k=0.05, d_p=self.D_P) / 1e3, places=6)

    def test_schlankheit_mit_der_eingegebenen_spannweite(self):
        self.assertAlmostEqual(self.k["L_d_p"], 3600.0 / self.D_P, places=6)


class TestLaengsschub(unittest.TestCase):
    """Was (28) ausser dem Querschnitt braucht: die Kachel «Längsschub»."""

    def kennzahlen(self, beton="C25/30", **schub):
        p = projekt(beton)
        k, urteile, _, _ = rechnen(p, decke(p, schub, {"Feld": {"M_y_Ed": 30.0, "V_z_Ed": 20.0}}))
        return k, urteile

    def test_endfeld_und_innenfeld(self):
        """Durchlaufend gilt das Einfeld mit 0.9 L oder 0.8 L; L/d_p bleibt mit L."""
        k, _ = self.kennzahlen(**MK, blech_feld=Feld.ENDFELD)
        self.assertAlmostEqual(k["V_L_Rd"], v_l_rd(0.9 * 3000.0 / 4.0) / 1e3, places=6)
        self.assertAlmostEqual(k["L_d_p"], 3000.0 / D_P, places=6)
        k, _ = self.kennzahlen(**MK, blech_feld=Feld.INNENFELD)
        self.assertAlmostEqual(k["V_L_Rd"], v_l_rd(0.8 * 3000.0 / 4.0) / 1e3, places=6)

    def test_tau_cd_des_betons(self):
        k, _ = self.kennzahlen("C30/37", **MK)
        tau_cd = 0.3 * math.sqrt(30.0) / 1.5
        self.assertAlmostEqual(k["V_Rd"], 0.8 * tau_cd * D_P * B_0 / 200.0, places=6)

    def test_ohne_beiwerte(self):
        """Ohne m und k: keine Kennzahl, das Urteil sagt, was fehlt -- der Rest rechnet."""
        k, urteile = self.kennzahlen(blech_L=3.0)
        self.assertNotIn("V_L_Rd", k)
        self.assertIn("L_d_p", k)
        u = urteile["V_L", "Feld"]
        self.assertFalse(u.erfuellt)
        self.assertEqual(u.hinweis, "Für den Längsschub fehlt noch der Beiwert m und der "
                                    "Beiwert k – in der Kachel «Längsschub».")
        self.assertTrue(urteile["V", "Feld"].erfuellt)

    def test_ohne_spannweite(self):
        k, _ = self.kennzahlen(blech_m=150.0, blech_k=0.1)
        self.assertNotIn("V_L_Rd", k)
        self.assertNotIn("L_d_p", k)

    def test_abstand_hoechstens_die_halbe_spannweite(self):
        p = projekt()
        a = decke(p, {**MK, "blech_last": Belastung.EINZELLASTEN, "blech_a": 2.0})
        self.assertEqual(grund(p, a.kennung), "Abstand a darf nicht grösser sein als "
                                              "0.5 · Spannweite L, angegeben sind 2 m und 3 m")

    def test_was_fehlt(self):
        self.assertEqual(Laengsschub(None, None, None).fehlt_kurz, "m, k und L fehlen")
        self.assertEqual(Laengsschub(150.0, None, 3.0).fehlt_kurz, "k fehlt")
        self.assertEqual(Laengsschub(150.0, 0.1, 3.0).fehlt_kurz, "")
        einzeln = Laengsschub(150.0, 0.1, None, last=Belastung.EINZELLASTEN)
        self.assertEqual(einzeln.fehlt, ["a"])
        self.assertEqual(einzeln.fehlt_in_worten, "der Abstand a der Last vom Auflager")
        self.assertEqual(Laengsschub(150.0, 0.1, None, last=Belastung.EINZELLASTEN, a=0.9).L_s,
                         900.0)

    def test_kachel_liest_was_fehlt(self):
        p = projekt()
        self.assertEqual(geometrie(p, decke(p))["laengsschub_fehlt"], "m, k und L fehlen")
        p = projekt()
        self.assertEqual(geometrie(p, decke(p, MK))["laengsschub_fehlt"], "")


class TestRegeln(unittest.TestCase):
    """Was eine Decke verlangt und was sie nicht rechnet."""

    def test_bauweise(self):
        blech, beton = (Baustoffart.PROFILBLECH, "SE 350 G"), (Baustoffart.BETON, "C25/30")
        stahl = (Baustoffart.BETONSTAHL, "B500B")
        self.assertIs(bauweise([blech, beton]), Bauweise.BLECHVERBUND)
        self.assertIs(bauweise([blech, beton, stahl]), Bauweise.BLECHVERBUND)
        for falsch in ([blech], [blech, beton, (Baustoffart.BAUSTAHL, "S355")]):
            with self.assertRaises(Mischung):
                bauweise(falsch)

    def test_mit_baustahl(self):
        p = projekt()
        p.baustahl("S355")
        a = decke(p)
        a.polygon([(1100, 0), (1200, 0), (1200, 100), (1100, 100)], material="st1")
        self.assertEqual(grund(p, a.kennung),
                         "Einen Querschnitt aus Baustahl («S355»), Beton («C25/30») und "
                         "Profilblechstahl («SE 350 G») rechnet das Werkzeug nicht")

    def test_eine_decke_je_analyse(self):
        p = projekt()
        a = decke(p)
        a.blechdecke(2000.0, 0.0, beton="b1", blech="pb1")
        text = ("Blechverbunddecke 1, Blechverbunddecke 2: eine Analyse rechnet eine "
                "Blechverbunddecke – die übrigen löschen")
        self.assertEqual(grund(p, a.kennung), text)
        meldung, = geometrie(p, a)["meldungen"]
        self.assertEqual((meldung["text"], meldung["elemente"], meldung["fehler"]),
                         (f"{text}.", ["B1", "B2"], True))

    def test_einachsig(self):
        """Die Decke traegt in einer Richtung: einachsig, auch wenn die Analyse es nicht ist."""
        p = projekt()
        a = decke(p)
        self.assertFalse(a.einachsig)
        self.assertIs(p.aufbauen().teile[a.kennung].objekt.biegung, EINACHSIG)

    def test_quer_zur_richtung(self):
        """M_z, V_y oder T: eine Warnung mit den Faellen -- nachgewiesen wird der Rest."""
        p = projekt()
        a = decke(p, MK, {"Schief": {"M_y_Ed": 10.0, "M_z_Ed": 3.0},
                          "Dreh": {"M_y_Ed": 10.0, "T_Ed": 1.0},
                          "Feld": {"M_y_Ed": 10.0}})
        _, urteile, _, aufbau = rechnen(p, a)
        self.assertEqual([w.text for w in aufbau.warnungen],
                         [f"Querschnittsanalyse 'Decke', Schief, Dreh: {EINE_RICHTUNG}"])
        self.assertTrue(urteile["M-N", "Schief"].erfuellt)


class TestOberflaeche(unittest.TestCase):
    """Was die Maske und die Vorlage vom Kern lesen."""

    def test_zeichen_und_grenzen(self):
        f = feldangaben(BlechdeckeEintrag)
        self.assertEqual((f["h_p"]["zeichen"], f["h_p"]["heisst"]), ("h_p", "Höhe der Rippe h_p"))
        self.assertEqual(f["h_p"]["bis_feld"]["feld"], "h")
        self.assertTrue(f["h_p"]["bis_feld"]["offen"])
        self.assertEqual([x["feld"] for x in f["b_s"]["ab_felder"]], ["b_o", "b_u"])
        self.assertEqual(f["A_p"]["einheit"], "mm²/m")
        self.assertEqual(f["blech"]["stoffe"], ["profilblech"])

    def test_abstand_gegen_spannweite(self):
        f = feldangaben(QuerschnittsanalyseEintrag)
        self.assertEqual(f["blech_a"]["bis_feld"],
                         {"feld": "blech_L", "faktor": 0.5,
                          "satz": "Abstand a darf nicht grösser sein als 0.5 · Spannweite L"})
        self.assertEqual(f["blech_L"]["ab_felder"][0]["faktor"], 2.0)

    def test_vorlage(self):
        v = dienst.vorlage({"wahl": {"art": "blechdecke"}})
        self.assertIsNone(v["fehler"])
        self.assertTrue(v["teile"]["polygone"])
        self.assertTrue(v["rippe"]["masslinien"])

    def test_vorlage_mit_falschen_massen(self):
        v = dienst.vorlage({"wahl": {"art": "blechdecke", "h": 140, "h_p": 160}})
        self.assertEqual(v, {"fehler": "Höhe der Rippe h_p muss kleiner sein als Dicke h, "
                                       "angegeben sind 160 mm und 140 mm.", "teile": None})


class TestAufgezaehlt(unittest.TestCase):
    """Die Aufzaehlung in Saetzen -- die Decke sagt damit, was ihr fehlt."""

    def test_aufgezaehlt(self):
        self.assertEqual(aufgezaehlt(["m"]), "m")
        self.assertEqual(aufgezaehlt(["m", "k"]), "m und k")
        self.assertEqual(aufgezaehlt(["m", "k", "L"]), "m, k und L")
        self.assertEqual(aufgezaehlt(["m", "k", "L"], "oder"), "m, k oder L")


if __name__ == "__main__":
    unittest.main()
