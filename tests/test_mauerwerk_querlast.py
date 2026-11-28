"""
Die Wand aus Mauerwerk, Schritt 14d: quer zu ihrer Ebene. Die Ersatzkraft
des Erdbebens nach SIA 261:2020, Gl. (49), gegen die Handrechnung, das
lotrechte Gewölbe nach Theorie 2. Ordnung gegen die Grenze 1. Ordnung, das
waagrechte nach Gl. (19) und (20), die Breite, von der ein Pfeiler Querlast
bekommt, das Normalkraftniveau nach SIA 266:2015, Gl. (27), und was die
Oberfläche davon zeigt.
"""

import unittest

from opencivil.core.nachweis import OHNE_EINWIRKUNG
from opencivil.erdbeben.ersatzkraft import Baugrundklasse, Bauwerksklasse, Erdbebenzone
from opencivil.mauerwerk import knicken, querlast
from opencivil.mauerwerk.knicken import AUSMITTE, STABILITAET
from opencivil.mauerwerk.lasten import Abtrag
from opencivil.mauerwerk.modell import Erdbebenquer, Querlast, Verhaltensbeiwert
from opencivil.projekt import Projekt
from opencivil.projekt.mauerwerk import rechteck
from opencivil.web.mauerwerkdaten import katalog
from tests.test_mauerwerk import befund, beispielwand, zeichnung
from tests.test_mauerwerk_nachweise import urteile
from tests.test_mauerwerk_schub import wand_mit_wind

#: Das Eigengewicht der Wand aus Kalksandstein, 175 mm: 1800 kg/m³ · 10 m/s² · 0.175 m, in N/m².
G_K = 3150.0


def erdbeben(**felder):
    """Eine Querlast aus dem Erdbeben -- Zone Z2, Baugrund C, Klasse II, z_a 1.35 m in 6 m."""
    vorgabe = {"zone": Erdbebenzone.Z2, "baugrund": Baugrundklasse.C,
               "bauwerksklasse": Bauwerksklasse.II, "z_a": 1.35, "h": 6.0}
    return Querlast("QL1", erdbeben=Erdbebenquer(**{**vorgabe, **felder}))


def schmale_wand(p, b=2.4, tuere=False, **felder):
    """
    Eine Wand aus Kalksandstein im Verband, vollfugig, 175 mm dick, ``b`` ×
    2.7 m, am Fuss eingespannt, links und rechts gehalten: 40 kN/m mittig
    auf der Krone, im Lastfall «Wind» 1 kN/m² quer -- in «GZT Wind» mit
    1.0 · Eigengewicht + 1.0 · Auflast + 1.5 · Wind.
    """
    p.mauerwerk("MK")
    w = p.wand("Wand", **{"t": 175, "mauerung": "verband", "stossfugen": "vollfugig",
                          "fuss": "eingespannt", "links": "gehalten", "rechts": "gehalten",
                          **felder})
    w.wand(rechteck(0, 0, b, 2.7))
    if tuere:
        w.oeffnung(rechteck(0.8, 0, 1.6, 2.1))
    w.standardfaelle()
    eigengewicht, auflast, _ = w.lastfaelle
    w.linienlast(auflast, (0, 2.7), (b, 2.7), wert=40, e=0)
    wind = w.lastfall("Wind")
    w.querlast(wind, wert=1.0)
    w.kombination("GZT Wind", (eigengewicht, 1.0), (auflast, 1.0), (wind, 1.5))
    return w


def mit_erdbeben(p, **felder):
    """
    Die Wand von :func:`wand_mit_wind` mit 20 mm Ausmitte, dazu ein Lastfall
    «Erdbeben» mit seiner Querlast und die Kombination «GZT Erdbeben» --
    Lastfall und Kombination heissen verschieden, das verlangt der Kern.
    """
    w = wand_mit_wind(p, e=20.0, H=20.0)
    eb = w.lastfall("Erdbeben")
    w.querlast(eb, **{"art": "erdbeben", "zone": "Z2", "baugrund": "C", "bauwerksklasse": "II",
                      "q": "1.5", "z_a": 1.35, "h": 6.0, **felder})
    eigengewicht, auflast = w.lastfaelle[0], w.lastfaelle[1]
    w.kombination("GZT Erdbeben", (eigengewicht, 1.0), (auflast, 1.0), (eb, 1.0))
    return w


class TestErsatzkraft(unittest.TestCase):
    """SIA 261:2020, 16.7.2, Gl. (49), mit T_a = T_1 und q_a = 1.5."""

    def test_die_handrechnung(self):
        """
        1.2 · 1.0 m/s² · 1.45 · 3.15 kN/m² / (10 m/s² · 1.5) · [3 · (1 + 1.35/6) − 0.5]
        = 0.3654 · 3.175 = 1.160 kN/m².
        """
        self.assertAlmostEqual(querlast.p_E(G_K, 10.0, erdbeben()), 1160.1, delta=0.1)

    def test_die_klammer(self):
        """Am Fundament 2.5, zuoberst 5.5 -- die untere Grenze 1 gilt nie."""
        self.assertAlmostEqual(querlast.klammer(0.0, 6.0), 2.5)
        self.assertAlmostEqual(querlast.klammer(6.0, 6.0), 5.5)

    def test_zone_baugrund_und_klasse(self):
        """Z3b, Baugrund A, Klasse III: 1.5 · 1.6 · 1.0 statt 1.2 · 1.0 · 1.45."""
        stark = erdbeben(zone=Erdbebenzone.Z3B, baugrund=Baugrundklasse.A,
                         bauwerksklasse=Bauwerksklasse.III)
        self.assertAlmostEqual(querlast.p_E(G_K, 10.0, stark) / querlast.p_E(G_K, 10.0, erdbeben()),
                               2.4 / 1.74)

    def test_die_herleitung_im_projekt(self):
        """Dieselbe Zahl in der Wand: g_k aus Dichte, g und Dicke."""
        p = Projekt(name="Probe")
        b = befund(p, mit_erdbeben(p))
        self.assertAlmostEqual(b.g_k, G_K)
        self.assertAlmostEqual(b.querlasten["QL1"], 1160.1, delta=0.1)


class TestLotrechtesGewoelbe(unittest.TestCase):
    """Die Querlast, unter der die Wand nach Theorie 2. Ordnung noch hält (knicken.querlast)."""

    def test_gedrungen_die_grenze_erster_ordnung(self):
        """
        h/t = 3, mittig: die Ausmitte in halber Höhe erreicht 0.375 t, wenn
        λ/(8 · n) = 0.375 -- also λ = 8 · 0.2 · 0.375 = 0.6, fast ohne
        Effekte 2. Ordnung.
        """
        erg = knicken.querlast(3, 0.0, 0.0, 1000.0, 0.2, 1)
        self.assertAlmostEqual(erg.lam, 0.6, delta=0.006)
        self.assertLess(erg.lam, 0.6)
        self.assertEqual(erg.grund, AUSMITTE)

    def test_schlank_weniger(self):
        """h/t = 15: die Effekte 2. Ordnung nehmen gut 15 % weg."""
        self.assertLess(knicken.querlast(15, 0.0, 0.0, 1000.0, 0.2, 1).lam, 0.52)

    def test_mittig_in_beiden_richtungen_gleich(self):
        self.assertAlmostEqual(knicken.querlast(15, 0.0, 0.0, 1000.0, 0.2, 1).lam,
                               knicken.querlast(15, 0.0, 0.0, 1000.0, 0.2, -1).lam)

    def test_mit_der_ausmitte_schwaecher(self):
        """Ausmitte und Querlast zur selben Seite: die Wand trägt halb so viel wie gegen sie."""
        mit = knicken.querlast(15, 0.1, 0.1, 1000.0, 0.2, 1).lam
        gegen = knicken.querlast(15, 0.1, 0.1, 1000.0, 0.2, -1).lam
        self.assertLess(mit, 0.6 * gegen)

    def test_ohne_normalkraft_kein_gewoelbe(self):
        self.assertEqual(knicken.querlast(15, 0.0, 0.0, 1000.0, 0.0, 1),
                         knicken.Querergebnis(0.0, STABILITAET, None))


class TestWaagrechtesGewoelbe(unittest.TestCase):
    """Ohne Öffnung, beide Ränder gehalten, vollfugig, Gl. (19) und (20) mit L."""

    def widerstand(self, **felder):
        p = Projekt(name="Probe")
        return urteile(p, schmale_wand(p, **felder))["Querlast – P1 – GZT Wind"].widerstand

    def test_der_bogen_mit_drei_gelenken(self):
        """
        L = 2.4 m ≤ 15 · 0.175 = 2.625 m; w_d = 5 · 1.5 · 2.4⁴ / (32 · 2975 · 0.175³)
        = 0.49 mm ≤ 4.8 mm. p_Rd,h = 2 · 1.36 N/mm² · 175² / 2400² = 14.46 kN/m².
        """
        w = self.widerstand()
        self.assertEqual(w.symbol, "p_{Rd}")
        self.assertAlmostEqual(w.groesse.si, 2 * 1.36e6 * 0.175 ** 2 / 2.4 ** 2, delta=0.1)

    def test_wo_es_nicht_traegt(self):
        """Ein freier Rand, offene Stossfugen, eine Türe, 6 m Spannweite: nur das lotrechte."""
        for felder in ({"links": "frei"}, {"stossfugen": "nicht_vollfugig"}, {"tuere": True},
                       {"b": 6.0}):
            with self.subTest(**felder):
                w = self.widerstand(**felder)
                self.assertEqual(w.symbol, "p_{Rd,v}")
                self.assertLess(w.groesse.si, 4000.0)

    def test_der_grund_in_worten(self):
        p = Projekt(name="Probe")
        b = befund(p, schmale_wand(p, tuere=True))
        self.assertIn("Öffnungen", querlast.waagrechtes_gewoelbe(b))
        p = Projekt(name="Probe")
        self.assertIsNone(querlast.waagrechtes_gewoelbe(befund(p, schmale_wand(p))))


class TestQuerlastnachweis(unittest.TestCase):
    """Je Pfeiler und Kombination mit Querlast -- in beiden Richtungen, wo das Erdbeben wirkt."""

    def test_die_einwirkung(self):
        """1.5 · 1 kN/m² im GZT Wind."""
        p = Projekt(name="Probe")
        u = urteile(p, schmale_wand(p))["Querlast – P1 – GZT Wind"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, 1500.0)
        self.assertTrue(u.erfuellt)

    def test_nur_wo_eine_querlast_wirkt(self):
        p = Projekt(name="Probe")
        namen = urteile(p, schmale_wand(p))
        self.assertNotIn("Querlast – P1 – GZT", namen)
        self.assertNotIn("Normalkraftniveau – P1 – GZT Wind", namen)

    def test_die_breite_bis_zur_mitte_der_oeffnungen(self):
        """Türe 0.8–1.8 m, Fenster 2.8–4.0 und 4.9–5.5 m: bis zu ihren Mitten, am Ende bis dort."""
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = beispielwand(p, fuss="eingespannt")
        w.standardfaelle()
        b = befund(p, w)
        breiten = [querlast.einzugsbreite(b, pf) for pf in b.pfeiler]
        for (links, rechts), soll in zip(breiten, [(0.0, 1.3), (1.3, 3.4), (3.4, 5.2), (5.2, 6.0)]):
            self.assertAlmostEqual(links, soll[0])
            self.assertAlmostEqual(rechts, soll[1])

    def test_die_einwirkungen_je_richtung(self):
        """Von Hand mit Vorzeichen, das Erdbeben dazu und davon -- ohne beide keine."""
        for p, p_E, soll in ((1000.0, 500.0, [1500.0, 500.0]), (0.0, 500.0, [500.0, -500.0]),
                             (-300.0, 0.0, [-300.0]), (0.0, 0.0, [])):
            with self.subTest(p=p, p_E=p_E):
                self.assertEqual(querlast.einwirkungen(Abtrag(p=p, p_E=p_E)), soll)

    def test_im_erdbeben_beide_richtungen(self):
        """p_E = 1.16 kN/m²; mit 20 mm Ausmitte am Kopf trägt die Wand zu einer Seite weniger."""
        p = Projekt(name="Probe")
        u = urteile(p, mit_erdbeben(p))["Querlast – P1 – GZT Erdbeben"]
        self.assertAlmostEqual(u.einwirkung.groesse.si, 1160.1, delta=0.1)
        self.assertTrue(u.erfuellt)

    def test_lasten_gegeneinander(self):
        """+1 und −1 kN/m² mit demselben Beiwert: «Keine Einwirkung → kein Nachweis.»"""
        p = Projekt(name="Probe")
        w = schmale_wand(p)
        sog = w.lastfall("Sog")
        w.querlast(sog, wert=-1.0)
        w.kombinationen[-1].faktoren[sog.kennung] = 1.5
        self.assertEqual(urteile(p, w)["Querlast – P1 – GZT Wind"].begruendung, OHNE_EINWIRKUNG)

    def test_ohne_druck(self):
        """
        Nur Querlast, ohne lotrechte Last: das lotrechte Gewölbe trägt nichts,
        das waagrechte braucht keine Normalkraft -- ohne es ist die Wand rot.
        """
        for felder, erfuellt in (({}, True), ({"links": "frei"}, False)):
            with self.subTest(**felder):
                p = Projekt(name="Probe")
                w = schmale_wand(p, **felder)
                w.kombination("Nur Wind", (w.lastfaelle[3], 1.5))
                u = urteile(p, w)["Querlast – P1 – Nur Wind"]
                self.assertEqual((u.erfuellt, u.verfehlt), (erfuellt, not erfuellt))

    def test_eine_querlast_ohne_lastfall(self):
        """Sie bleibt weg, grau, und sagt es mit ihrem Namen."""
        p = Projekt(name="Probe")
        w = schmale_wand(p)
        w.querlast("LF99", wert=2.0)
        meldungen = [m for m in befund(p, w).meldungen if "QL2" in m.text]
        self.assertEqual(len(meldungen), 1)
        self.assertFalse(meldungen[0].fehler)


class TestNormalkraftniveau(unittest.TestCase):
    """Gl. (27), nur wo das Gebäude im Erdbeben mit q = 2.0 rechnet."""

    def test_nur_mit_q_2(self):
        for q, da in (("1.5", False), ("2.0", True), ("2.5", False)):
            with self.subTest(q=q):
                p = Projekt(name="Probe")
                namen = urteile(p, mit_erdbeben(p, q=q))
                self.assertEqual("Normalkraftniveau – P1 – GZT Erdbeben" in namen, da)
                self.assertNotIn("Normalkraftniveau – P1 – GZT Wind", namen)

    def test_die_handrechnung(self):
        """
        N_xd = 3.15 · 16.2 + 40 · 6 = 291.0 kN;
        n_d = 291.0 / (6 m · 0.175 m · 2.975 N/mm²) = 0.093.
        """
        p = Projekt(name="Probe")
        u = urteile(p, mit_erdbeben(p, q="2.0"))["Normalkraftniveau – P1 – GZT Erdbeben"]
        n_d = (G_K * 16.2 + 240e3) / (6.0 * 0.175 * 2.975e6)
        self.assertAlmostEqual(u.einwirkung.groesse.si, n_d, delta=1e-4)
        self.assertAlmostEqual(u.widerstand.groesse.si, 0.20)
        self.assertTrue(u.erfuellt)


class TestHinweise(unittest.TestCase):
    """Was das Werkzeug zum Erdbeben nicht prüft, sagt es grau (4.7.1.4, 4.7.2)."""

    def hinweise(self, **felder):
        p = Projekt(name="Probe")
        return befund(p, mit_erdbeben(p, **felder)).zum_erdbeben

    def test_erhoehtes_verformungsvermoegen(self):
        for felder, anzahl in (({"bauwerksklasse": "III"}, 1), ({"zone": "Z3a"}, 1),
                               ({"zone": "Z3b", "bauwerksklasse": "I"}, 0), ({}, 0),
                               ({"q": "2.5"}, 1)):
            with self.subTest(**felder):
                hinweise = self.hinweise(**felder)
                self.assertEqual(len(hinweise), anzahl)
                self.assertTrue(all(not m.fehler and m.text.startswith("QL1: ") for m in hinweise))

    def test_der_fall_steht_im_satz(self):
        text, = [m.text for m in self.hinweise(zone="Z3a")]
        self.assertIn("Bauwerksklasse II und Zone Z3a", text)


class TestWasDieOberflaecheZeigt(unittest.TestCase):

    def test_die_ersatzkraft_nur_im_erdbeben(self):
        p = Projekt(name="Probe")
        daten = zeichnung(p, mit_erdbeben(p, bauwerksklasse="III"))
        self.assertEqual(list(daten["ersatzkraefte"]), ["QL1"])
        self.assertAlmostEqual(daten["ersatzkraefte"]["QL1"], 1.160 * 1.5 / 1.2, delta=0.001)
        self.assertEqual(len(daten["zum_erdbeben"]), 1)
        self.assertEqual(daten["zum_mauerwerk"], [])

    def test_die_schalter(self):
        k = katalog()
        self.assertEqual([s["wert"] for s in k["querlastarten"]], ["von_hand", "erdbeben"])
        self.assertEqual([s["beschriftung"] for s in k["verhaltensbeiwerte"]],
                         [q.value for q in Verhaltensbeiwert])
        self.assertEqual(k["vorsilben"]["querlasten"], "QL")


if __name__ == "__main__":
    unittest.main()
