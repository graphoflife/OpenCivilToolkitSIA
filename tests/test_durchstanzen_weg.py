"""
Der Schnitt durch verschiedene Dicken (opencivil.durchstanzen.weg): liegt ein
Plattenbereich neben der Stütze, ohne sie zu umschliessen, sucht das Werkzeug
den schwächsten Schnitt um sie, in dem jedes Stück mit k_r·d_v seiner Stelle
zählt (SIA 262:2025, 4.3.6.2.7) -- sein Urteil, die Kennzahl, die Randstütze,
die Aussparung, was nicht eingeht und was die Oberfläche davon sieht.

Das Beispiel: Innenstütze 400 × 400 mm, Platte 240 mm, daneben ein Streifen
600 × 1200 mm, 100 mm neben der Stütze, mit 180 mm -- C30/37, B500B,
Näherungsstufe 1, c = 30 mm, V_d = 300 kN.
"""

import time
import unittest

from opencivil.durchstanzen.bereiche import Seite
from opencivil.durchstanzen.kennwerte import kennwerttabelle
from opencivil.durchstanzen.schnitt import _ueberlappung
from opencivil.web import dienst
from opencivil.web.durchstanzdaten import situation
from tests.test_durchstanzen import MIT, TAU_CD, projekt, rechnen, texte
from tests.test_durchstanzen_bereiche import k_r
from tests.test_durchstanzen_kennzahl import kennzahl

#: Wie das Urteil am Schnitt durch verschiedene Dicken heisst.
WEG = "am Schnitt durch verschiedene Dicken"

#: Der Streifen neben der Stütze, in mm: von x = 300 bis 900, y = ±600.
STREIFEN = [[300, -600], [900, -600], [900, 600], [300, 600]]


def mit_streifen(h_B=180.0, ecken=STREIFEN, seite=Seite.STUETZE, **felder):
    """Das Beispiel, mit einem Bereich neben der Stütze."""
    p = projekt(**{"b_x": 400, "b_y": 400, "stufe": "1", "V_d": 300.0, "h": 240.0, **felder})
    p.durchstanzstellen[0].plattenbereich(ecken, h_B, seite)
    return p


def faelle(loesung, urteil):
    """Die Urteile der Stelle: je Fall, ob er erfüllt ist, und sein Grad."""
    return {u.fall: (u.erfuellt, u.erfuellungsgrad.si) for u in loesung.urteile
            if u.raum == urteil.raum}


class TestDuennerDaneben(unittest.TestCase):
    """
    Der Streifen ist dünner: d = 194 − 60 = 134 mm. Der Schnitt um die Stütze
    liegt 97 mm neben ihr, 3 mm vor dem Streifen, und rechnet überall mit
    d der Platte. Der schwächste Schnitt läuft im Streifen, nur 100 mm neben
    der Stütze -- dort genügt 0.5·134 = 67 mm.
    """

    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung, cls.befund, cls.urteil = rechnen(mit_streifen())

    def test_massgebend_269_2_kn(self):
        """Je Stelle (58) mit k_r ihres d, zusammen mit k_e = 0.9 der Innenstütze."""
        ws = self.befund.weg.schnitt
        platte, streifen = ws.stellen
        self.assertIsNone(platte.wo)
        self.assertEqual(streifen.wo.name, "B1")
        self.assertAlmostEqual(platte.d, 0.194)
        self.assertAlmostEqual(streifen.d, 0.134)
        # Im Streifen läuft der Schnitt der Seite der Stütze entlang, 400 mm,
        # und ein wenig um ihre Ecken; der Rest in der Platte um die Stütze.
        self.assertAlmostEqual(streifen.u_red, 0.42, delta=0.01)
        self.assertAlmostEqual(platte.u_red + streifen.u_red, ws.last.auswertung.u)
        self.assertAlmostEqual(ws.last.k_e, 0.9)
        hand = TAU_CD * 1e6 * 0.9 * (k_r(0.194) * 0.194 * platte.u_red
                                     + k_r(0.134) * 0.134 * streifen.u_red)
        self.assertAlmostEqual(self.befund.weg.V_Rd_c, hand, delta=5.0)
        self.assertAlmostEqual(self.befund.weg.V_Rd_c / 1e3, 269.2, delta=0.05)
        self.assertAlmostEqual(self.befund.V_Rd_c / 1e3, 275.4, delta=0.05)

    def test_eigenes_urteil(self):
        """Nach den Urteilen der Leisten (tests.test_durchstanzen_leisten_bereiche)."""
        f = faelle(self.loesung, self.urteil)
        self.assertEqual(list(f), [*MIT, WEG])
        self.assertAlmostEqual(f[WEG][1], 269.2 / 300.0, delta=1e-3)
        self.assertLess(self.befund.weg.V_Rd_c, self.befund.V_Rd_c)

    def test_herleitung(self):
        t = texte(self.loesung)
        self.assertIn("Schnitt durch verschiedene Dicken", t)
        self.assertIn("nach Vorgabe, nicht nachgeschlagen", t)
        namen = {b.wert_id.rsplit(".", 1)[-1] for b in self.loesung.protokoll.bloecke
                 if getattr(b, "wert_id", "")}
        self.assertLessEqual({"W_Pl_k_r", "W_B1_d", "W_B1_k_r", "W_V_Rd_c", "W_V_d_red"}, namen)

    def test_kennwerte(self):
        zeilen = {z[0]: str(getattr(z[2], "latex", z[2]))
                  for z in kennwerttabelle(self.befund).zeilen}
        self.assertEqual(zeilen["Widerstand am Schnitt durch verschiedene Dicken"], "269.2")
        self.assertEqual(zeilen["Querkraft im Schnitt durch verschiedene Dicken"], "300.0")

    def test_gegenseite_ebenso(self):
        """Dünner auf der Gegenseite: sein d gilt im ganzen Bereich, wie zur Stütze hin."""
        befund = rechnen(mit_streifen(seite=Seite.GEGENSEITE))[2]
        self.assertAlmostEqual(befund.weg.V_Rd_c / 1e3, 269.2, delta=0.05)


class TestKennzahl(unittest.TestCase):

    def test_am_schnitt_durch_verschiedene_dicken(self):
        """Dieser Schnitt hält am wenigsten: dort liegt der Schnittpunkt, 269.2 kN."""
        _, loesung, V = kennzahl(mit_streifen())
        self.assertAlmostEqual(V, 269.2, delta=0.05)
        self.assertIn("Massgebend ist hier der Schnitt durch verschiedene Dicken", texte(loesung))
        for V_d, erfuellt in ((V - 0.1, True), (V + 1.0, False)):
            with self.subTest(V_d=V_d):
                _, loesung, _, urteil = rechnen(mit_streifen(V_d=V_d))
                self.assertEqual(faelle(loesung, urteil)[WEG][0], erfuellt)

    def test_in_naeherungsstufe_2(self):
        """ψ wächst mit V: der Schnittpunkt liegt höher, der Weg bleibt massgebend."""
        _, loesung, V = kennzahl(mit_streifen(stufe="2"))
        self.assertAlmostEqual(V, 449.5, delta=0.05)
        self.assertIn("Massgebend ist hier der Schnitt durch verschiedene Dicken", texte(loesung))


class TestWasNichtEingeht(unittest.TestCase):

    def test_dicker_daneben_haelt_mehr(self):
        """
        320 mm daneben: zwischen Stütze und Streifen hält kein Punkt 97 mm
        Abstand zu beiden, also läuft der Schnitt im Streifen mit d = 274 mm
        -- er hält mehr als der um die Stütze.
        """
        _, loesung, befund, urteil = rechnen(mit_streifen(320.0))
        self.assertAlmostEqual(befund.weg.V_Rd_c / 1e3, 345.1, delta=0.05)
        self.assertTrue(faelle(loesung, urteil)[WEG][0])
        self.assertGreater(befund.weg.V_Rd_c, befund.V_Rd_c)

    def test_weiter_weg_derselbe_d(self):
        """400 mm neben der Stütze: der schwächste Schnitt ist der um die Stütze."""
        ecken = [[600, -300], [1200, -300], [1200, 300], [600, 300]]
        _, loesung, befund, urteil = rechnen(mit_streifen(320.0, ecken))
        self.assertIsNone(befund.weg)
        self.assertAlmostEqual(befund.V_Rd_c / 1e3, 275.4, delta=0.05)
        self.assertIn("rechnet überall mit demselben d", texte(loesung))
        self.assertEqual(list(faelle(loesung, urteil)), list(MIT))

    def test_dicker_auf_der_gegenseite(self):
        """Dicker auf der Gegenseite: die Druckseite läuft durch, der Schnitt um die Stütze gilt."""
        befund = rechnen(mit_streifen(320.0, seite=Seite.GEGENSEITE))[2]
        self.assertIsNone(befund.weg)

    def test_fern(self):
        """Mehr als 4·d neben der Stütze: der Bereich geht nicht ein."""
        ecken = [[3000, -600], [3600, -600], [3600, 600], [3000, 600]]
        _, loesung, befund, urteil = rechnen(mit_streifen(ecken=ecken))
        self.assertIsNone(befund.weg)
        self.assertIn("Bereich B1 liegt mehr als 4·d neben der Stütze", texte(loesung))
        self.assertNotIn("Schnitt durch verschiedene Dicken", texte(loesung))
        self.assertEqual(list(faelle(loesung, urteil)), list(MIT))


class TestRandUndAussparung(unittest.TestCase):

    def test_randstuetze(self):
        """
        Am Rand unten, der Streifen bis an ihn: was jenseits des Rands liegt,
        zählt nicht, und k_e ist das der Randstütze.
        """
        ecken = [[300, -200], [900, -200], [900, 800], [300, 800]]
        befund = rechnen(mit_streifen(ecken=ecken, lage="rand", a_y=0))[2]
        ws = befund.weg.schnitt
        self.assertAlmostEqual(ws.last.k_e, 0.7)
        self.assertEqual([None if s.wo is None else s.wo.name for s in ws.stellen], [None, "B1"])
        self.assertTrue(all(p[1] >= -0.2 - 1e-9 for p in ws.last.auswertung.kandidat.umschlossen))
        self.assertLess(befund.weg.V_Rd_c, befund.V_Rd_c)
        self.assertAlmostEqual(befund.weg.V_Rd_c / 1e3, 144.3, delta=0.05)

    def test_aussparung_im_streifen(self):
        """Eine Aussparung im Streifen nimmt dem Schnitt seinen Schatten (Figur 23d)."""
        p = mit_streifen()
        p.durchstanzstellen[0].aussparung([[400, 350], [600, 350], [600, 500], [400, 500]])
        befund = rechnen(p)[2]
        a = befund.weg.schnitt.last.auswertung
        self.assertGreater(a.hinter_aussparungen, 0.1)
        self.assertLess(befund.weg.V_Rd_c / 1e3, 269.2)

    def test_schnell_genug(self):
        """Der Nachweis rechnet auf der Seite: ein Bruchteil einer Sekunde, hier grosszügig."""
        p = mit_streifen()
        anfang = time.perf_counter()
        rechnen(p)
        self.assertLess(time.perf_counter() - anfang, 5.0)


class TestUeberlappung(unittest.TestCase):
    """
    Wie viel einer Aussparung in einem nicht konvexen Schnitt liegt -- der
    Schnitt durch verschiedene Dicken ist so wenig konvex wie der um eine
    Wandecke. Ein L aus drei Quadraten 1 × 1.
    """

    L = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)]

    def test_im_arm_ganz(self):
        self.assertAlmostEqual(
            _ueberlappung([(1.25, 0.25), (1.75, 0.25), (1.75, 0.75), (1.25, 0.75)], self.L), 0.25)

    def test_in_der_kerbe_nichts(self):
        self.assertAlmostEqual(
            _ueberlappung([(1.25, 1.25), (1.75, 1.25), (1.75, 1.75), (1.25, 1.75)], self.L), 0.0)

    def test_ueber_die_ecke(self):
        """Ein Quadrat 1 × 1 um die innere Ecke: drei Viertel liegen im L."""
        quadrat = [(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5)]
        self.assertAlmostEqual(_ueberlappung(quadrat, self.L), 0.75)
        self.assertAlmostEqual(_ueberlappung(quadrat, self.L[::-1]), 0.75)

    def test_alles(self):
        self.assertAlmostEqual(_ueberlappung([(-1, -1), (3, -1), (3, 3), (-1, 3)], self.L), 3.0)


class TestWasDieOberflaecheSieht(unittest.TestCase):

    def test_im_grundriss_blau(self):
        p = mit_streifen()
        aufbau, loesung, _, _ = rechnen(p)
        s = situation(aufbau, p.durchstanzstellen[0].kennung, loesung)
        self.assertTrue(s["weg"])
        self.assertTrue(any(l["zaehlt"] for l in s["weg"]))
        legende = " ".join(t.get("text", "") if isinstance(t, dict) else str(t)
                           for zeile in s["legende"] for t in zeile)
        self.assertIn("Schnitt durch verschiedene Dicken (blau)", legende)
        self.assertIn("Am Schnitt durch verschiedene Dicken", legende)

    def test_rechnet_auf_der_seite(self):
        """
        Wie die Seite rechnet, samt Formelsammlung: bis 2026-11-28 war der
        Name der letzten Formel der Kennzahl hier 105 Zeichen lang, und
        nichts rechnete.
        """
        for p in (mit_streifen(), mit_streifen(seite=Seite.GEGENSEITE, ecken=[
                [-600, -600], [600, -600], [600, 600], [-600, 600]], h_B=320.0)):
            antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
            self.assertFalse(antwort.ist_fehler, antwort.daten)

    def test_ohne_weg_leer(self):
        p = mit_streifen(320.0, [[600, -300], [1200, -300], [1200, 300], [600, 300]])
        aufbau, loesung, _, _ = rechnen(p)
        self.assertEqual(situation(aufbau, p.durchstanzstellen[0].kennung, loesung)["weg"], [])


if __name__ == "__main__":
    unittest.main()
