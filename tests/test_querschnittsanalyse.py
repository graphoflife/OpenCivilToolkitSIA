"""
Die Querschnittsanalyse: Beschreibung, Aufbau und Nachweise.

Hier zuerst die Beschreibung -- was gespeichert wird und wie es sich liest.
"""

import unittest

from opencivil.projekt import (
    Projekt, ProjektFehler, QALastfallEintrag, QuerschnittsanalyseEintrag,
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
