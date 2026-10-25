"""
Der Verformungsnachweis der Platte: w_eff = ω_w · w gegen w_max = L/350.

ω_w ist der Vergrösserungsfaktor der Durchbiegung, SIA 262:2025, 4.4.3.2.5:

    ω_w = (1 - 20 rho') / (10 rho^0.7) · (0.75 + 0.1 phi) · (h/d)^3

In x, je gezogene Seite mit x-Bewehrung, immer -- ω_w unten, ω_w' oben, als
Kennzahl der Platte (2026-10-16); der Nachweis liest ihn. rho' ist das rho
der Gegenseite, mit d' vom gezogenen Rand bis zur Gegenlage. phi gehört der
Verformung der Platte, Vorgabe 2.
"""

import math
import unittest

from opencivil.bericht.zusammenfassung import zusammenfassen
from opencivil.projekt import (
    Projekt, ProjektFehler, QuerschnittEintrag, VerformungEintrag, VerformungsfallEintrag,
)

RAUM = "querschnitt.{}.nachweis.verformung"
FAKTOR = "querschnitt.{}.vergroesserung.omega_w_{}"


def rechnen(projekt):
    aufbau = projekt.aufbauen()
    return aufbau, aufbau.werk.loese(*aufbau.berichtsziele())


def faktor(loesung, kennung, seite):
    wert = loesung.werte.get(FAKTOR.format(kennung, seite))
    return None if wert is None else wert.groesse.si


def urteile(loesung, kennung):
    return {u.fall: u for u in loesung.urteile if u.raum == RAUM.format(kennung)}


def beispiel(*faelle, kriechzahl=None):
    """Die Platte des Beispiels mit diesen Fällen statt ihres eigenen: (Name, w, L, Seite)."""
    projekt = Projekt.beispiel()
    platte = projekt.querschnitte[0]
    platte.verformung.faelle = []
    if kriechzahl is not None:
        platte.verformung.kriechzahl = kriechzahl
    for name, w, laenge, seite in faelle:
        platte.verformungsfall(name, w=w, laenge=laenge, zugseite=seite)
    return projekt


def platte_mit(x, *faelle):
    """Eine Platte mit diesen x-Durchmessern, unten und oben, und diesen Fällen."""
    projekt = Projekt()
    projekt.beton("C30/37")
    projekt.stahl("B500B")
    platte = projekt.platte("Platte", h=250, x=x, y=[10, 10])
    platte.einwirkung("Feld", M_Ed=30)
    for name, w, laenge, seite in faelle:
        platte.verformungsfall(name, w=w, laenge=laenge, zugseite=seite)
    return projekt, platte


class TestFaktor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.loesung = rechnen(beispiel(("Feld", 3.5, 6.0, "unten"),
                                          ("Kragarm", 1.0, 2.5, "oben")))

    def test_die_zahlen_des_beispiels(self):
        """Unten 2450 mm² in 248.1 mm, oben 754 mm² in 252 mm, φ = 2 -- wie vorher w/w_c."""
        self.assertEqual(round(faktor(self.loesung, "q1", "unten"), 2), 4.00)
        self.assertEqual(round(faktor(self.loesung, "q1", "oben"), 2), 7.52)

    def test_von_hand(self):
        """⌀18 + ⌀12 je @150 unten in 249 und 246 mm, ⌀12@150 oben in 48 mm."""
        a18, a12 = (math.pi * d * d / 4 * 1000 / 150 for d in (18, 12))
        d_u = (a18 * 249 + a12 * 246) / (a18 + a12)
        rho_u, rho_o = (a18 + a12) / (1000 * d_u), a12 / (1000 * 252)
        unten = (1 - 20 * rho_o) / (10 * rho_u ** 0.7) * (0.75 + 0.2) * (300 / d_u) ** 3
        oben = (1 - 20 * rho_u) / (10 * rho_o ** 0.7) * (0.75 + 0.2) * (300 / 252) ** 3
        self.assertAlmostEqual(faktor(self.loesung, "q1", "unten"), unten, places=9)
        self.assertAlmostEqual(faktor(self.loesung, "q1", "oben"), oben, places=9)

    def test_die_normstelle_steht_in_der_herleitung(self):
        bloecke = [b for b in self.loesung.protokoll.alle_bloecke()
                   if "Vergrösserungsfaktor" in getattr(b, "titel", "")]
        self.assertTrue(bloecke)
        self.assertTrue(all(b.referenz == "SIA 262:2025, 4.4.3.2.5" for b in bloecke))

    def test_die_statische_hoehe_heisst_wie_in_den_nachweisen_der_lagen(self):
        """
        248.1 mm sind d_{2,x}, wie in den Nachweisen der Lagen -- bis
        2026-10-18 hiessen sie hier d_u, dieselbe Zahl unter zwei Namen.
        """
        hoehen = {b.wert_id: b.latex for b in self.loesung.protokoll.alle_bloecke()
                  if getattr(b, "wert_id", "").startswith("querschnitt.q1.vergroesserung.")
                  and b.wert_id.endswith(".d")}
        self.assertEqual(hoehen, {
            "querschnitt.q1.vergroesserung.unten.d": r"d_{2,x} = z_{2,x} = 248.1\,\mathrm{mm}",
            "querschnitt.q1.vergroesserung.oben.d":
                r"d_{3,x,g} = h - z_{3,x,g} = 300\,\mathrm{mm} - 48\,\mathrm{mm} = 252\,\mathrm{mm}",
        })

    def test_beide_seiten_immer_auch_ohne_fall(self):
        """Einmal je bewehrte Seite, als Kennzahl -- auch ohne Verformungsfall."""
        aufbau, loesung = rechnen(beispiel())
        self.assertEqual(aufbau.feld("verformung"), {})
        self.assertAlmostEqual(faktor(loesung, "q1", "unten"),
                               faktor(self.loesung, "q1", "unten"), places=12)
        self.assertAlmostEqual(faktor(loesung, "q1", "oben"),
                               faktor(self.loesung, "q1", "oben"), places=12)

    def test_die_zeichen_omega_w_und_omega_w_strich(self):
        self.assertEqual(self.loesung.werte[FAKTOR.format("q1", "unten")].symbol, r"\omega_w")
        self.assertEqual(self.loesung.werte[FAKTOR.format("q1", "oben")].symbol, r"\omega_w'")

    def test_die_kriechzahl_wirkt_linear(self):
        _, null = rechnen(beispiel(("Feld", 3.5, 6.0, "unten"), kriechzahl=0.0))
        self.assertAlmostEqual(
            faktor(null, "q1", "unten") / faktor(self.loesung, "q1", "unten"),
            0.75 / 0.95, places=12)

    def test_ohne_obere_x_lage_ist_rho_strich_null(self):
        projekt, platte = platte_mit([12, 0], ("Feld", 2.0, 5.0, "unten"))
        _, loesung = rechnen(projekt)
        k = platte.kennung
        a_s = loesung.werte[f"querschnitt.{k}.lage.2g.a_s"].groesse.si
        d = loesung.werte[f"querschnitt.{k}.lage.2g.z"].groesse.si
        rho = a_s / (1.0 * d)
        erwartet = 1.0 / (10 * rho ** 0.7) * (0.75 + 0.1 * 2.0) * (0.25 / d) ** 3
        self.assertAlmostEqual(faktor(loesung, k, "unten"), erwartet, places=9)

    def test_ohne_gezogene_x_lage_kein_faktor_und_kein_nachweis(self):
        """Zug oben ohne obere x-Bewehrung: eine Zeile mit Grad null und dem Grund."""
        projekt, platte = platte_mit([12, 0], ("Kragarm", 2.0, 2.0, "oben"))
        _, loesung = rechnen(projekt)
        self.assertIsNone(faktor(loesung, platte.kennung, "oben"))
        u = urteile(loesung, platte.kennung)["Kragarm"]
        self.assertFalse(u.erfuellt)
        self.assertEqual(u.erfuellungsgrad.si, 0.0)
        self.assertIn("ohne x-Bewehrung", u.hinweis)
        self.assertIsNone(u.einwirkung)
        self.assertIsNone(u.widerstand)

    def test_ohne_x_kein_nachweis_aber_eine_warnung(self):
        projekt, platte = platte_mit([0, 0], ("Feld", 2.0, 5.0, "unten"))
        aufbau, _ = rechnen(projekt)
        self.assertEqual(aufbau.feld("verformung"), {})
        self.assertIn("Platte 'Platte': ohne x-Bewehrung kein Verformungsnachweis.",
                      aufbau.warnungen)


class TestNachweis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aufbau, cls.loesung = rechnen(beispiel(("Feld", 3.5, 6.0, "unten"),
                                                   ("Kragarm", 1.0, 2.5, "oben"),
                                                   ("Ohne", 0.0, 4.0, "unten")))
        cls.urteile = urteile(cls.loesung, "q1")

    def test_w_eff_gegen_w_max(self):
        """w_eff = ω_w · w, w_max = L/350, der Grad ist ihr Verhältnis."""
        u = self.urteile["Feld"]
        omega = faktor(self.loesung, "q1", "unten")
        self.assertAlmostEqual(u.einwirkung.groesse.si, omega * 3.5e-3, places=12)
        self.assertAlmostEqual(u.widerstand.groesse.si, 6.0 / 350, places=12)
        self.assertAlmostEqual(u.erfuellungsgrad.si, (6.0 / 350) / (omega * 3.5e-3), places=9)
        self.assertTrue(u.erfuellt)
        self.assertEqual(u.art, "w")

    def test_zug_oben_nimmt_den_oberen_faktor(self):
        """7.52 · 1 mm = 7.5 mm gegen 2.5 m / 350 = 7.1 mm: nicht erfüllt."""
        u = self.urteile["Kragarm"]
        omega = faktor(self.loesung, "q1", "oben")
        self.assertAlmostEqual(u.einwirkung.groesse.si, omega * 1.0e-3, places=12)
        self.assertFalse(u.erfuellt)
        self.assertLess(u.erfuellungsgrad.si, 1.0)

    def test_ohne_durchbiegung_ist_der_grad_unendlich(self):
        u = self.urteile["Ohne"]
        self.assertTrue(u.erfuellt)
        self.assertEqual(u.erfuellungsgrad.si, float("inf"))

    def test_jeder_fall_hat_sein_urteil_und_sein_ziel(self):
        self.assertEqual(sorted(self.urteile), ["Feld", "Kragarm", "Ohne"])
        for u in self.urteile.values():
            self.assertIn(u.ziel, self.loesung.werte)
            self.assertEqual(u.name, f"Verformung x – {u.fall}")

    def test_in_der_zusammenfassung(self):
        platte = next(b for b in zusammenfassen(self.aufbau, self.loesung).bauteile
                      if b.kennung == "q1")
        zeilen = [z for z in platte.zeilen if z.nachweis == "Verformung"]
        self.assertEqual([z.fall for z in zeilen], ["Feld", "Kragarm", "Ohne"])
        self.assertEqual(zeilen[0].einwirkung.symbol, "w_{eff}")
        self.assertEqual(zeilen[0].widerstand.symbol, "w_{max}")

    def test_ausgeschaltet_rechnet_er_nicht(self):
        projekt = beispiel(("Feld", 3.5, 6.0, "unten"))
        projekt.querschnitte[0].verformung.faelle[0].aktiv = False
        aufbau, _ = rechnen(projekt)
        self.assertEqual(aufbau.feld("verformung"), {})

    def test_die_vorgabe_steht_in_der_herleitung(self):
        """L/350 ist nach Vorgabe eingebaut -- das steht da, nicht nur im Code."""
        texte = [getattr(b, "text", "") for b in self.loesung.protokoll.alle_bloecke()]
        self.assertTrue(any("nach Vorgabe, nicht nachgeschlagen" in t and "E_cm" in t
                            for t in texte))


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        projekt = beispiel(("Feld", 3.5, 6.0, "unten"), ("Kragarm", 1.0, 2.5, "oben"),
                           kriechzahl=1.7)
        projekt.querschnitte[0].verformung.faelle[1].aktiv = False
        wieder = Projekt.aus_dict(projekt.als_dict())
        self.assertEqual(wieder.querschnitte[0].verformung, projekt.querschnitte[0].verformung)

    def test_eine_neue_platte_rechnet_mit_phi_zwei(self):
        platte = QuerschnittEintrag(kennung="q", name="q", beton="b")
        self.assertEqual(platte.verformung, VerformungEintrag(kriechzahl=2.0, faelle=[]))

    def test_ein_phi_an_der_platte_gibt_es_nicht_mehr(self):
        """Bis 2026-10-16 stand φ an der Platte -- eine solche Datei nennt das Feld."""
        roh = Projekt.beispiel().als_dict()
        roh["querschnitte"][0]["kriechzahl"] = 1.3
        with self.assertRaisesRegex(ProjektFehler, "'kriechzahl' gibt es nicht"):
            Projekt.aus_dict(roh)

    def test_die_fassade(self):
        projekt, platte = platte_mit([12, 12])
        fall = platte.verformungsfall("Kragarm", w=1.5, laenge=2.0, zugseite="oben")
        self.assertEqual(platte.verformung.faelle, [
            VerformungsfallEintrag("Kragarm", w=1.5, laenge=2.0, zugseite="oben")])
        self.assertIs(fall, platte.verformung.faelle[0])

    def test_unmoegliche_zahlen_melden_sich_erst_beim_rechnen(self):
        """Wie die Masse der Platte: die Datei lässt sich öffnen und korrigieren."""
        for feld, wert in (("w", -1.0), ("laenge", 0.0)):
            with self.subTest(feld=feld):
                projekt = beispiel(("Feld", 3.5, 6.0, "unten"))
                setattr(projekt.querschnitte[0].verformung.faelle[0], feld, wert)
                wieder = Projekt.aus_dict(projekt.als_dict())
                with self.assertRaises(ProjektFehler):
                    wieder.aufbauen()

    def test_was_es_nicht_gibt_meldet_sich(self):
        for aendern in (
                lambda v: setattr(v.faelle[0], "zugseite", "links"),
                lambda v: v.faelle.append(VerformungsfallEintrag("Feld")),
                lambda v: v.faelle.extend([VerformungsfallEintrag("Feld A"),
                                           VerformungsfallEintrag("Feld-A")]),
                lambda v: setattr(v, "kriechzahl", -0.5)):
            with self.subTest():
                projekt = beispiel(("Feld", 3.5, 6.0, "unten"))
                aendern(projekt.querschnitte[0].verformung)
                # Gleiche Namen erst beim Rechnen, das Übrige schon beim Öffnen --
                # das Bauen prüft beides.
                with self.assertRaises(ProjektFehler):
                    projekt.aufbauen()

    def test_eine_negative_kriechzahl_in_der_datei(self):
        roh = Projekt.beispiel().als_dict()
        roh["querschnitte"][0]["verformung"]["kriechzahl"] = -1.0
        with self.assertRaises(ProjektFehler):
            Projekt.aus_dict(roh).aufbauen()


if __name__ == "__main__":
    unittest.main()
