"""
Spannglieder in der Querschnittsanalyse (opencivil.querschnitt.spannglieder).

Das Beispiel von Hand: ein Rechteck 300 × 600 mm aus C30/37, ohne
Betonstahl, mit vier Litzen Y1860 ⌀15.7 bei z = 100 mm -- d = 500 mm,
e = 200 mm unter dem Schwerpunkt. Nach Vorgabe:

    A_p   = 4 · 150                  =  600 mm²
    σ_p0  = 0.70 · 1860              = 1302 N/mm²
    σ_p∞  = 0.85 · 1302              = 1106.7 N/mm²
    ε_p   = 1106.7 / 195 000         = 5.675 ‰      (Litzen: E_p = 195 kN/mm²)
    P∞    = 600 · 1106.7             = 664.02 kN

Im Bruch, mit dem Spannungsblock (f_cd = 20 N/mm², f_pd = 1600/1.15):

    mit Vordehnung     T = A_p · f_pd            = 834.8 kN
    schlaff            T = A_p · (f_pd − σ_p∞)   = 170.8 kN
    ohne Verbund       T = P∞                    = 664.0 kN
    M_Rd = T · (d − T / (2 · b · f_cd))

Und das Rissmoment, mit der Vorspannung am gezogenen Rand:

    M_Riss = (k_t · f_ctm + P∞/A + P∞ · e / W) · W     k_t = 1/(1 + 0.5 · 0.2)

Geneigt, mit einer Schubwand in der Mitte, die V_z = 300 kN ganz nimmt:

    β_p = +5°, trägt mit         300 − P∞ · sin 5°                = 242.13 kN
    β_p = −5°, mit Verbund       300 + A_p · f_pd · sin 5°        = 372.76 kN
    β_p = −5°, ohne Verbund      300 + A_p · σ_p0 · sin 5°        = 368.09 kN

Im reinen Druck, gleichmässig gedehnt, ersetzt das Glied den Beton an seiner
Stelle wie ein Stab -- A = 300 · 600 = 180 000 mm²:

    ohne Glied                  N_Rd^- = −f_cd · A               = −3600 kN
    schlaff, ohne Verbund       N_Rd^- = −f_cd · (A − A_p)       = −3588 kN
    mit Vordehnung, ohne        N_Rd^- = −f_cd · (A − A_p) + P∞  = −2923.98 kN
"""

import copy
import math
import unittest

from opencivil.material.spannstahl import SPANNSTAHLSORTEN
from opencivil.nachweis.gebrauchsebene import gebrauchsebene
from opencivil.nachweis.rissgroessen import bruttoquerschnitt, rissmoment
from opencivil.nachweis.spannungsbegrenzung import VORGABE
from opencivil.projekt import ProjektFehler
from opencivil.projekt.projekt import Projekt
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.projekt.spannglieder import SpanngliedEintrag
from opencivil.querschnitt.biegung import EINACHSIG
from opencivil.querschnitt.spannglieder import (
    ANTEIL_NACH_VERLUSTEN, ANTEIL_SPANNEN, FesteSpannung, Restfestigkeit,
    VorgedehnterSpannstahl, flaechendurchmesser, grenze_nach_spannen, grenzen_verletzt,
    guenstig, lotrecht, vorspannung,
)
from opencivil.querschnitt.werkstoffgesetz import Spannstahlgesetz
from opencivil.web import api, dienst
from tests import unfertig

F_PD = 1600e6 / 1.15
SIGMA_PINF = 0.85 * 0.70 * 1860e6
A_P = 600e-6
B, D, F_CD = 0.3, 0.5, 20e6
W = 0.3 * 0.6 ** 2 / 6
K_T = 1.0 / (1.0 + 0.5 * 0.2)


def projekt(wirkung="vordehnung", verbund="mit", *, staebe=False, rechenart="block",
            **felder) -> Projekt:
    """Das Beispiel von Hand -- mit den fünf Stäben der Vorlage, wenn ``staebe``."""
    p = Projekt(name="Spannglied")
    p.beton()
    p.stahl()
    p.spannstahl("Y1860")
    a = p.analyse("Balken", beton="b1", stahl="s1", rechenarten={"b1": rechenart}, **felder)
    if not staebe:
        a.staebe.clear()
        a.stablinien.clear()
    a.spannglied(150.0, 100.0, stahl="sp1", durchmesser=15.7, anzahl=4,
                 wirkung=wirkung, verbund=verbund)
    a.lastfall("Feld", M_y_Ed=300.0)
    return p


def urteil(ergebnis, art: str, fall: str):
    return next(u for u in ergebnis.urteile_von("a1") if u.art == art and u.fall == fall)


def biegewiderstand(T: float) -> float:
    """M_Rd in Nm mit dem Spannungsblock, wenn der Spannstahl die Kraft ``T`` trägt."""
    return T * (D - T / (2.0 * B * F_CD))


def geloest(p: Projekt):
    """Der Aufbau und die Lösung der Analyse a1 -- ohne ihre Nachweise."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.ziele_von("a1"))
    return aufbau.querschnittsanalysen["a1"], lambda kid: loesung.werte[kid].groesse.si


class TestRegeln(unittest.TestCase):
    """Die Faktoren und die Grenzen der Spannung, in N/mm²."""

    def test_vorgaben(self):
        """Ein neues Glied beginnt mit 0.70 und 0.85: 1302 und 1106.7 N/mm² bei Y1860."""
        neu = SpanngliedEintrag()
        self.assertEqual((neu.anteil_p0, neu.anteil_pinf),
                         (ANTEIL_SPANNEN, ANTEIL_NACH_VERLUSTEN))
        p0, pinf = vorspannung(1860.0, neu.anteil_p0, neu.anteil_pinf)
        self.assertAlmostEqual(p0, 1302.0)
        self.assertAlmostEqual(pinf, 1106.7)

    def test_die_faktoren_gelten(self):
        """σ_p∞ folgt σ_p0: 0.75 · 1860 = 1395, 0.80 · 1395 = 1116."""
        p0, pinf = vorspannung(1860.0, 0.75, 0.80)
        self.assertAlmostEqual(p0, 1395.0)
        self.assertAlmostEqual(pinf, 1116.0)

    def test_ein_faktor_ueber_eins_haelt_die_analyse_an(self):
        """
        Das Feld weist ihn schon ab (Katalog); bis 2026-11-27 durfte σ_p∞ nur
        σ_p0 nicht übersteigen.
        """
        p = projekt()
        p.querschnittsanalysen[0].spannglieder[0].anteil_pinf = 1.2
        self.assertEqual(unfertig.grund(p, "a1"), "Spannglied 1: σ_p∞/σ_p0 muss grösser als null "
                                                  "und höchstens 1 sein, angegeben ist 1.2")
        felder = api.katalog()["felder"]["spannglied"]
        self.assertEqual({k: (felder[k]["ueber"], felder[k]["bis"])
                          for k in ("anteil_p0", "anteil_pinf")},
                         {"anteil_p0": (0.0, 1.0), "anteil_pinf": (0.0, 1.0)})

    def test_grenze_nach_dem_spannen(self):
        """Gl. (22): min(0.75 · 1860; 0.85 · 1600) = min(1395; 1360)."""
        self.assertAlmostEqual(grenze_nach_spannen(1860.0, 1600.0), 1360.0)

    def test_die_vorgabe_haelt_die_grenzen(self):
        self.assertEqual(grenzen_verletzt(1302.0, 1106.7, 1860.0, 1600.0), [])

    def test_jede_grenze_fuer_sich(self):
        zu_hoch, = grenzen_verletzt(1400.0, 1106.7, 1860.0, 1600.0)
        self.assertIn("= 1360 N/mm² (SIA 262:2025, 4.1.5.2.2, Gl. 22)", zu_hoch)
        zu_tief, = grenzen_verletzt(1302.0, 800.0, 1860.0, 1600.0)
        self.assertIn("unter 0.45·f_pk = 837 N/mm²", zu_tief)

    def test_wo_die_vorgabe_ueber_gl_22_liegt(self):
        """
        0.70 · f_pk überschreitet Gl. (22) bei Y1100 (770 > 765) und Y1030
        (721 > 705.5) -- dort steht schon die Vorgabe rot. Offen beim Benutzer
        (TODO); bei allen anderen Sorten hält sie.
        """
        ueber = [sorte for sorte, s in SPANNSTAHLSORTEN.items()
                 if grenzen_verletzt(*vorspannung(s.f_pk, ANTEIL_SPANNEN, ANTEIL_NACH_VERLUSTEN),
                                     s.f_pk, s.f_p01k)]
        self.assertEqual(ueber, ["Y1100", "Y1030"])

    def test_gezeichnet_mit_seiner_flaeche(self):
        """Vier Litzen à 150 mm² zeichnen sich als Kreis von 600 mm²."""
        self.assertAlmostEqual(flaechendurchmesser(600.0), math.sqrt(2400.0 / math.pi))


class TestGesetze(unittest.TestCase):
    """Die Gesetze eines Glieds über der Dehnung des Querschnitts an seiner Stelle."""

    def setUp(self):
        self.stahl = Spannstahlgesetz(E_p=195e9, f_pd=F_PD, eps_ud=0.020)
        self.eps_p = SIGMA_PINF / 195e9

    def test_mit_vordehnung(self):
        g = VorgedehnterSpannstahl(stahl=self.stahl, eps_p=self.eps_p)
        self.assertAlmostEqual(g.spannung(0.0), SIGMA_PINF, delta=1.0)
        self.assertEqual(g.spannung(0.010), F_PD)
        self.assertEqual(g.spannung(-self.eps_p - 1e-4), 0.0)              # entspannt
        self.assertEqual(g.spannung(0.020 - self.eps_p + 1e-4), 0.0)       # gerissen
        self.assertAlmostEqual(g.eps_ud, 0.020 - self.eps_p)
        self.assertAlmostEqual(g.eps_yd, F_PD / 195e9 - self.eps_p)

    def test_schlaff_mit_restfestigkeit(self):
        """Um σ_p∞ gesenkt: bei null nichts, gedrückt bis −σ_p∞."""
        g = Restfestigkeit(stahl=self.stahl, eps_p=self.eps_p, sigma_pinf=SIGMA_PINF)
        self.assertAlmostEqual(g.spannung(0.0), 0.0, delta=1.0)
        self.assertAlmostEqual(g.spannung(0.010), F_PD - SIGMA_PINF)
        self.assertEqual(g.spannung(-self.eps_p - 1e-4), -SIGMA_PINF)
        self.assertAlmostEqual(g.eps_ud, 0.020 - self.eps_p)

    def test_ohne_verbund(self):
        """Die Kraft nach allen Verlusten, gleich welche Dehnung -- es fliesst nie."""
        g = FesteSpannung(sigma=SIGMA_PINF)
        for eps in (-0.003, 0.0, 0.010, 0.050):
            self.assertEqual(g.spannung(eps), SIGMA_PINF)
        self.assertEqual(g.eps_yd, math.inf)


class TestWerte(unittest.TestCase):
    """Die Werte eines Glieds, wie der Bericht sie herleitet."""

    def werte(self, p: Projekt):
        e = p.rechnen()
        return {k: e.wert(f"querschnittsanalyse.a1.P1.{k}").groesse.si
                for k in ("A_p", "sigma_p0", "sigma_pinf", "eps_p", "P_inf")}

    def test_von_hand(self):
        w = self.werte(projekt())
        self.assertAlmostEqual(w["A_p"], A_P)
        self.assertAlmostEqual(w["sigma_p0"] / 1e6, 1302.0)
        self.assertAlmostEqual(w["sigma_pinf"] / 1e6, 1106.7)
        self.assertAlmostEqual(w["eps_p"] * 1e3, 5.675, places=3)
        self.assertAlmostEqual(w["P_inf"] / 1e3, 664.02)

    def test_eingegebene_faktoren(self):
        """0.725 · 1860 = 1348.5 und 0.80 · 1348.5 = 1078.8 N/mm²."""
        p = projekt()
        g = p.querschnittsanalysen[0].spannglieder[0]
        g.anteil_p0, g.anteil_pinf = 0.725, 0.80
        w = self.werte(p)
        self.assertAlmostEqual(w["sigma_p0"] / 1e6, 1348.5)
        self.assertAlmostEqual(w["sigma_pinf"] / 1e6, 1078.8)
        self.assertAlmostEqual(w["P_inf"] / 1e3, 600.0 * 1078.8 / 1e3)
        self.assertAlmostEqual(w["eps_p"], 1078.8 / 195000.0)

    def test_der_faktor_steht_mit_seinen_stellen_da(self):
        """0.725 nicht als 0.73 -- und die Vorgabe sagt, dass sie eine ist."""
        p = projekt()
        p.querschnittsanalysen[0].spannglieder[0].anteil_p0 = 0.725
        bloecke = {b.titel: b for b in p.rechnen().loesung.protokoll.alle_bloecke()
                   if getattr(b, "titel", "").startswith("Spannglied 1: nach")}
        self.assertIn(r"= 0.725 \cdot 1860", bloecke["Spannglied 1: nach dem Spannen"].latex)
        vorgabe = bloecke["Spannglied 1: nach allen Verlusten, nach Vorgabe"]
        self.assertEqual(vorgabe.referenz, "nach Vorgabe, nicht nachgeschlagen")

    def test_draehte_mit_ihrem_modul(self):
        """30 Drähte ⌀5.0 à 19.6 mm², mit E_p = 200 kN/mm² statt 195."""
        p = projekt()
        g = p.querschnittsanalysen[0].spannglieder[0]
        g.durchmesser, g.anzahl = 5.0, 30
        w = self.werte(p)
        self.assertAlmostEqual(w["A_p"], 30 * 19.6e-6)
        self.assertAlmostEqual(w["eps_p"], 1106.7 / 200000.0)


class TestFlaeche(unittest.TestCase):
    """
    Die Fläche eingegeben statt aus einem Erzeugnis: zwölf Litzen sind
    1800 mm², als Drähte mit E_p = 200 kN/mm². Was nicht gewählt ist --
    Durchmesser und Anzahl --, bleibt stehen und zählt nicht.
    """

    def glied(self, **felder):
        p = projekt()
        g = p.querschnittsanalysen[0].spannglieder[0]
        for feld, wert in {"flaechenangabe": "flaeche", "flaeche": 1800.0, **felder}.items():
            setattr(g, feld, wert)
        return p

    def werte(self, p):
        e = p.rechnen()
        return {k: e.wert(f"querschnittsanalyse.a1.P1.{k}").groesse.si
                for k in ("A_p", "eps_p", "P_inf")}

    def test_mit_dem_modul_der_art(self):
        for art, modul in (("litze", 195000.0), ("draht", 200000.0)):
            with self.subTest(art):
                w = self.werte(self.glied(art=art))
                self.assertAlmostEqual(w["A_p"], 1800e-6)
                self.assertAlmostEqual(w["eps_p"], 1106.7 / modul)
                self.assertAlmostEqual(w["P_inf"] / 1e3, 1.8 * 1106.7)

    def test_die_herleitung_sagt_es(self):
        bloecke = [b for b in self.glied().rechnen().loesung.protokoll.alle_bloecke()
                   if getattr(b, "titel", "").startswith("Spannglied 1: Litzen")]
        self.assertEqual([b.titel for b in bloecke],
                         ["Spannglied 1: Litzen aus Y1860, die Fläche eingegeben"])
        self.assertEqual(bloecke[0].referenz, "")

    def test_eine_art_die_es_in_der_sorte_nicht_gibt_fehlt_noch(self):
        """Y1860 gibt es nicht als Stab: grau, wie ein fehlender Durchmesser."""
        p = self.glied(art="stab")
        self.assertEqual(unfertig.grund(p, "a1"),
                         "Spannglied 1: Y1860 gibt es nicht als Stab (Tabelle 7) – eine Art wählen")

    def test_was_nicht_gewaehlt_ist_bleibt(self):
        p = self.glied()
        g = p.querschnittsanalysen[0].spannglieder[0]
        self.assertEqual((g.durchmesser, g.anzahl), (15.7, 4))
        g.flaechenangabe = "erzeugnis"
        self.assertAlmostEqual(self.werte(p)["A_p"], A_P)


class TestBiegewiderstand(unittest.TestCase):
    """M_Rd von Hand mit dem Spannungsblock -- je Wirkung und Verbund, bei M_Ed = 300 kNm."""

    def grad(self, *art) -> float:
        return urteil(projekt(*art).rechnen(), "M-N", "Feld").erfuellungsgrad.si

    def test_mit_vordehnung_bis_f_pd(self):
        self.assertAlmostEqual(self.grad() * 300e3, biegewiderstand(A_P * F_PD), delta=50.0)

    def test_schlaff_nur_was_ueber_sigma_pinf_hinausgeht(self):
        self.assertAlmostEqual(self.grad("restfestigkeit") * 300e3,
                               biegewiderstand(A_P * (F_PD - SIGMA_PINF)), delta=50.0)

    def test_ohne_verbund_die_kraft_nach_allen_verlusten(self):
        self.assertAlmostEqual(self.grad("vordehnung", "ohne") * 300e3,
                               biegewiderstand(A_P * SIGMA_PINF), delta=50.0)

    def test_schlaff_ohne_verbund_traegt_nichts(self):
        self.assertEqual(self.grad("restfestigkeit", "ohne"), 0.0)


class TestVerdraengt(unittest.TestCase):
    """
    Wo das Glied liegt, ist kein Beton: es verdrängt ihn wie ein Stab, gleich
    welche Rechenart und ob es etwas trägt. Gezeigt am reinen Druck.
    """

    A = 0.3 * 0.6

    def druck(self, p: Projekt) -> float:
        return p.rechnen().wert("querschnittsanalyse.a1.kennzahlen.N_Rd_druck").groesse.si

    def test_ohne_glied_der_ganze_beton(self):
        p = projekt()
        p.querschnittsanalysen[0].spannglieder.clear()
        self.assertAlmostEqual(self.druck(p), -F_CD * self.A, delta=1.0)

    def test_ein_glied_das_nichts_traegt_nimmt_dem_beton_seine_flaeche(self):
        """Schlaff und ohne Verbund: −3588 kN statt −3600 kN, mit Block und Parabel."""
        for rechenart in ("block", "parabel"):
            with self.subTest(rechenart):
                p = projekt("restfestigkeit", "ohne", rechenart=rechenart)
                self.assertAlmostEqual(self.druck(p), -F_CD * (self.A - A_P), delta=1.0)

    def test_auch_wenn_es_zieht(self):
        """Mit P∞ ohne Verbund: −3588 + 664.02 kN, nicht −3600 + 664.02 kN."""
        self.assertAlmostEqual(self.druck(projekt("vordehnung", "ohne")),
                               -F_CD * (self.A - A_P) + A_P * SIGMA_PINF, delta=1.0)


class TestRissmoment(unittest.TestCase):
    """
    Die Vorspannung drückt den Rand, der unter dem Moment reisst -- mit oder
    ohne Verbund. Schlaff angesetzt steht sie in den Lastfällen, nicht hier.
    """

    MIT_VORSPANNUNG = (K_T * 2.9e6 + 664.02e3 / 0.18 + 664.02e3 * 0.2 / W) * W

    def rissmoment(self, *art):
        analyse, wert = geloest(projekt(*art))
        return rissmoment(bruttoquerschnitt(analyse, wert), 1.0, 0.0)

    def test_mit_vordehnung_von_hand(self):
        for verbund in ("mit", "ohne"):
            with self.subTest(verbund=verbund):
                riss = self.rissmoment("vordehnung", verbund)
                self.assertAlmostEqual(riss.M_Riss, self.MIT_VORSPANNUNG, delta=1.0)
                self.assertEqual(riss.ecke.punkt[1], 0.0)

    def test_schlaff_ohne_vorspannung(self):
        riss = self.rissmoment("restfestigkeit")
        self.assertEqual(riss.sigma_p, 0.0)
        self.assertAlmostEqual(riss.M_Riss, K_T * 2.9e6 * W, delta=1.0)

    def test_sproedes_versagen_misst_daran(self):
        grad = urteil(projekt(sproede=True).rechnen(), "Riss", "Zug unten").erfuellungsgrad.si
        self.assertAlmostEqual(grad, biegewiderstand(A_P * F_PD) / self.MIT_VORSPANNUNG,
                               delta=1e-3)


class TestOhneLast(unittest.TestCase):
    """
    Ohne Last verformt sich ein vorgespannter Querschnitt schon: er krümmt sich
    vom Glied weg, und der gestauchte Beton nimmt dem Glied etwas von σ_p∞.
    Ohne Glied bleibt die Ebene genau null.
    """

    def ebene(self, p: Projekt):
        analyse, wert = geloest(p)
        q, _, _ = analyse.querschnitt(wert, VORGABE)
        return gebrauchsebene(q, N=0.0, M_y=0.0, M_z=0.0, biegung=EINACHSIG)

    def test_mit_vordehnung(self):
        e = self.ebene(projekt())
        self.assertTrue(e.konvergiert)
        self.assertLess(e.chi, 0.0)
        self.assertAlmostEqual(e.N, 0.0, delta=10.0)
        self.assertAlmostEqual(e.M_y, 0.0, delta=10.0)
        self.assertLess(e.sigma_s[-1], SIGMA_PINF)
        self.assertGreater(e.sigma_s[-1], 0.95 * SIGMA_PINF)

    def test_ohne_glied(self):
        p = projekt(staebe=True)
        p.querschnittsanalysen[0].spannglieder.clear()
        e = self.ebene(p)
        self.assertEqual((e.eps_m, e.chi), (0.0, 0.0))


class TestNachweise(unittest.TestCase):
    """Was die Nachweise am Betonstahl mit einem Spannglied tun."""

    def test_duktilitaet_mit_spannstahl_in_der_zugzone(self):
        """4.1.4.2.5 nennt Betonstahl der Klassen B und C -- über x/d kein Nachweis."""
        u = urteil(projekt(duktilitaet=True).rechnen(), "x/d", "Zug unten")
        self.assertFalse(u.erfuellt)
        self.assertIn("Spannstahl Y1860 in der Zugzone", u.begruendung)

    def test_die_stahlspannung_gilt_dem_betonstahl(self):
        """Mit den Stäben der Vorlage begrenzt sie deren Spannung; ohne sie gibt es nichts zu begrenzen."""
        for staebe, erwartet in ((True, "Linie 1: σ_s ="), (False, "Ohne Betonstahl")):
            with self.subTest(staebe=staebe):
                p = projekt(staebe=staebe)
                p.querschnittsanalysen[0].quasistaendig.lastfall("Dauer", M_y_Ed=150.0)
                begruendungen = [u.begruendung for u in p.rechnen().urteile_von("a1")
                                 if u.fall == "Dauer"]
                self.assertEqual(len(begruendungen), 1)
                self.assertIn(erwartet, begruendungen[0])


SIN_5 = math.sin(math.radians(5.0))
P_INF = A_P * SIGMA_PINF


def geneigt(neigung, V_z=300.0, T=0.0, *, wirkung="vordehnung", verbund="mit",
            kasten=False, lage=(150.0, 100.0)) -> Projekt:
    """
    Das Beispiel mit geneigtem Glied am Auflager: eine Schubwand in der
    Mitte -- oder, mit ``kasten``, vier auf der Bügelachse, eine Zelle.
    """
    p = projekt(wirkung=wirkung, verbund=verbund)
    a = p.querschnittsanalysen[0]
    a.spannglieder.clear()
    a.spannglied(*lage, stahl="sp1", durchmesser=15.7, anzahl=4, wirkung=wirkung,
                 verbund=verbund, neigung=neigung)
    a.lastfaelle.clear()
    a.lastfall("Auflager", V_z_Ed=V_z, T_Ed=T)
    if kasten:
        ecken = [[50, 50], [250, 50], [250, 550], [50, 550]]
        for von, bis in zip(ecken, ecken[1:] + ecken[:1]):
            a.schubwand(von, bis, dicke=80.0, durchmesser=10.0, teilung=150.0, schnitte=1,
                        stahl="s1")
    else:
        a.schubwand([150, 50], [150, 550], dicke=300.0, durchmesser=10.0, teilung=150.0,
                    schnitte=2, stahl="s1")
    return p


class TestNeigung(unittest.TestCase):
    """Die lotrechte Kraft eines geneigten Glieds in der Querkraft -- von Hand."""

    def wandkraft(self, p: Projekt) -> float:
        """Die Kraft der massgebenden Wand, in N."""
        return urteil(p.rechnen(), "V+T", "Auflager").einwirkung.groesse.si

    def test_regeln(self):
        self.assertAlmostEqual(lotrecht(100.0, 30.0), 50.0)
        self.assertTrue(guenstig(5.0, 300.0))
        self.assertFalse(guenstig(-5.0, 300.0))
        self.assertTrue(guenstig(-5.0, -300.0))
        # Ohne V_z kommt die lotrechte Kraft dazu.
        self.assertFalse(guenstig(5.0, 0.0))

    def test_gleich_gerichtet_traegt_es_mit_p_unendlich(self):
        """SIA 262:2025, Gl. (50): 300 − 664.02 · sin 5° = 242.13 kN."""
        self.assertAlmostEqual(self.wandkraft(geneigt(5.0)), 300e3 - P_INF * SIN_5, delta=1.0)

    def test_entgegen_mit_verbund_bis_zur_fliessgrenze(self):
        self.assertAlmostEqual(self.wandkraft(geneigt(-5.0)), 300e3 + A_P * F_PD * SIN_5,
                               delta=1.0)

    def test_entgegen_ohne_verbund_mit_der_kraft_nach_dem_spannen(self):
        self.assertAlmostEqual(self.wandkraft(geneigt(-5.0, verbund="ohne")),
                               300e3 + A_P * 0.70 * 1860e6 * SIN_5, delta=1.0)

    def test_dreht_die_querkraft_so_wirkt_dasselbe_glied_entgegen(self):
        self.assertAlmostEqual(self.wandkraft(geneigt(5.0, V_z=-300.0)),
                               300e3 + A_P * F_PD * SIN_5, delta=1.0)

    def test_schlaff_zaehlt_die_neigung_nicht(self):
        p = geneigt(5.0, wirkung="restfestigkeit")
        self.assertAlmostEqual(self.wandkraft(p), 300e3, delta=1.0)
        self.assertNotIn("V_p", urteil(p.rechnen(), "V+T", "Auflager").begruendung)

    def test_neben_dem_schwerpunkt_dreht_es_den_kasten(self):
        """
        Bei y = 100 mm, 50 mm links vom Schwerpunkt: T_w = T − V_p · (−50 mm).
        Der rechte Steg trägt die Hälfte von V_z,w und den Umlauffluss
        T_w / (2 · A_k) über seine 500 mm, A_k = 200 · 500 mm².
        """
        V_p = P_INF * SIN_5
        T_w = 20e3 + V_p * 0.05
        steg = (300e3 - V_p) / 2.0 + T_w / (2.0 * 0.1) * 0.5
        self.assertAlmostEqual(self.wandkraft(geneigt(5.0, T=20.0, kasten=True, lage=(100.0, 100.0))),
                               steg, delta=1.0)

    def test_herleitung_und_urteil_nennen_den_anteil(self):
        u = urteil(geneigt(5.0).rechnen(), "V+T", "Auflager")
        self.assertIn(f"V_p = {P_INF * SIN_5 / 1e3:.1f} kN", u.begruendung)

    def test_zu_steil_haelt_die_analyse_an_und_sagt_warum(self):
        """Das Feld weist es schon ab (Katalog); kommt es doch an, rechnet die Analyse nicht."""
        self.assertEqual(unfertig.grund(geneigt(25.0), "a1"),
                         "Spannglied 1: β_p muss mindestens -20° und höchstens 20° sein, "
                         "angegeben ist 25°")


class TestZeichnung(unittest.TestCase):
    """Was das Zeichenfenster zu den Gliedern bekommt -- aus derselben Herleitung."""

    @classmethod
    def setUpClass(cls):
        p = Projekt(name="Spannglied")
        p.beton()
        p.stahl()
        p.spannstahl("Y1860")
        p.spannstahl("Y1030")
        a = p.analyse("Balken", beton="b1", stahl="s1")
        a.spannglied(150.0, 100.0, stahl="sp1", durchmesser=15.7, anzahl=4, neigung=5.0)
        a.spannglied(100.0, 100.0, stahl="sp2", durchmesser=15.7)
        a.spannglied(200.0, 100.0, stahl="sp1", durchmesser=12.9, anzahl=2,
                     anteil_p0=0.78, anteil_pinf=0.55)
        a.spannglied(250.0, 100.0, stahl="b1", durchmesser=15.7)
        a.spannglied(-20.0, 100.0, stahl="", durchmesser=15.7)
        a.spannglied(150.0, 300.0, stahl="sp2", flaechenangabe="flaeche", flaeche=1018.0,
                     art="stab", anteil_p0=0.65)
        a.spannglied(150.0, 400.0, stahl="sp2", flaechenangabe="flaeche", art="litze")
        cls.d = dienst.bearbeite("geometrie", {"projekt": p.als_dict(), "kennung": "a1"}).daten
        cls.glieder = {g["kennung"]: g for g in cls.d["spannglieder"]}

    def meldungen(self, kennung):
        return [(m["fehler"], m["text"]) for m in self.d["meldungen"] if kennung in m["elemente"]]

    def test_werte_des_beispiels(self):
        g = self.glieder["P1"]
        self.assertEqual(self.meldungen("P1"), [])
        self.assertEqual(g["werte"]["bezeichnung"], "Y1860S7-15.7")
        self.assertAlmostEqual(g["werte"]["P_inf"], 664.02)
        self.assertAlmostEqual(g["werte"]["eps_p"], 1106.7 / 195.0)
        self.assertAlmostEqual(g["durchmesser"], flaechendurchmesser(600.0))
        # Geneigt: was es von einem gleich gerichteten V_z trägt -- ungeneigt nichts.
        self.assertAlmostEqual(g["werte"]["V_p"], 664.02 * SIN_5)
        self.assertNotIn("V_p", self.glieder["P3"]["werte"])

    def test_ein_fehlendes_erzeugnis_ist_grau(self):
        """Y1030 gibt es nur in Stäben: es fehlt eine Wahl, gezeichnet wird mit ⌀15.7."""
        (fehler, text), = self.meldungen("P2")
        self.assertFalse(fehler)
        self.assertIn("Y1030 gibt es nicht mit ⌀15.7 mm", text)
        self.assertIsNone(self.glieder["P2"]["werte"])
        self.assertEqual(self.glieder["P2"]["durchmesser"], 15.7)
        self.assertFalse(self.d["gueltig"])

    def test_verletzte_grenzen_sind_rot_und_es_rechnet(self):
        """0.78 · 1860 = 1450.8 über 1360, 0.55 · 1450.8 = 797.9 unter 837 N/mm²."""
        meldungen = self.meldungen("P3")
        self.assertEqual([f for f, _ in meldungen], [True, True])
        self.assertIn("Gl. 22", meldungen[0][1])
        self.assertIn("0.45·f_pk", meldungen[1][1])
        self.assertAlmostEqual(self.glieder["P3"]["werte"]["P_inf"], 200.0 * 0.55 * 0.78 * 1.860)

    def test_mit_eingegebener_flaeche(self):
        """
        Ein Stab aus Y1030 mit 1018 mm², gespannt auf 0.65 · 1030 = 669.5 N/mm²
        -- unter Gl. (22), anders als die Vorgabe: E_p der Stäbe, gezeichnet
        mit seiner Fläche.
        """
        g = self.glieder["P6"]
        self.assertEqual(self.meldungen("P6"), [])
        self.assertEqual(g["werte"]["bezeichnung"], "Stäbe")
        self.assertAlmostEqual(g["werte"]["A_p"], 1018.0)
        self.assertAlmostEqual(g["werte"]["eps_p"], 0.65 * 0.85 * 1030.0 / 200.0)
        self.assertAlmostEqual(g["durchmesser"], flaechendurchmesser(1018.0))

    def test_eine_fehlende_art_ist_grau(self):
        self.assertEqual(self.meldungen("P7"), [
            (False, "Spannglied 7: Y1030 gibt es nicht als Litze (Tabelle 7) – eine Art wählen.")])
        self.assertIsNone(self.glieder["P7"]["werte"])

    def test_falsches_material_rot_fehlendes_grau(self):
        self.assertEqual(self.meldungen("P4"), [(True, "Spannglied 4: «C30/37» ist kein Spannstahl.")])
        meldungen = self.meldungen("P5")
        self.assertIn((False, "Spannglied 5: noch kein Material gewählt."), meldungen)
        self.assertTrue(any(f and "nicht ganz im Beton" in t for f, t in meldungen))
        self.assertFalse(self.glieder["P5"]["im_beton"])

    def test_meldungen_nennen_namen(self):
        for m in self.d["meldungen"]:
            self.assertNotRegex(m["text"], r"\bP\d\b")


class TestEintrag(unittest.TestCase):

    def test_rundreise(self):
        a = projekt().querschnittsanalysen[0]
        g = a.spannglieder[0]
        g.flaechenangabe, g.flaeche, g.art, g.anteil_p0 = "flaeche", 1800.0, "draht", 0.72
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(a.als_dict()), a)

    def test_die_eingegebene_flaeche_beginnt_mit_dem_erzeugnis(self):
        """Eine Litze ⌀15.7, 150 mm²: wer umschaltet, sieht dasselbe Glied."""
        neu = SpanngliedEintrag()
        self.assertEqual((neu.flaechenangabe, neu.durchmesser, neu.anzahl, neu.flaeche, neu.art),
                         ("erzeugnis", 15.7, 1, 150.0, "litze"))

    def test_kennungen_mit_p(self):
        a = projekt().querschnittsanalysen[0]
        a.spannglied(150.0, 500.0, stahl="sp1")
        self.assertEqual([g.kennung for g in a.spannglieder], ["P1", "P2"])

    def test_der_katalog(self):
        sp = api.katalog()["querschnittsanalyse"]["spannglied"]
        self.assertEqual([(w["wert"], w["kurz"], w["neigung"]) for w in sp["wirkungen"]],
                         [("vordehnung", "Vordehnung", True),
                          ("restfestigkeit", "schlaff", False)])
        self.assertEqual(set(sp["neigung"]), {"titel", "hinweis", "ohne"})
        self.assertEqual([(v["wert"], v["kurz"]) for v in sp["verbunde"]],
                         [("mit", "mit"), ("ohne", "ohne")])
        self.assertEqual([(a["wert"], a["beschriftung"]) for a in sp["angaben"]],
                         [("erzeugnis", "Erzeugnis"), ("flaeche", "Fläche A_p")])
        self.assertEqual([(a["wert"], a["beschriftung"]) for a in sp["arten"]],
                         [("draht", "Draht"), ("litze", "Litze"), ("stab", "Stab")])
        self.assertIn("E_p = 195000 N/mm² (SIA 262:2025, 3.3.2.4.2)", sp["arten"][1]["titel"])
        self.assertEqual([(f["vor"], f["feld"], f["nach"], f["spannung"]) for f in sp["faktoren"]],
                         [("σ_p0 =", "anteil_p0", "· f_pk", "sigma_p0"),
                          ("σ_p∞ =", "anteil_pinf", "· σ_p0", "sigma_pinf")])



class TestVonFrueher(unittest.TestCase):
    """
    Eine Datei von vor 2026-11-27, mit den Spannungen σ_p0 und σ_p∞ in N/mm²
    statt der Faktoren, öffnet sich und rechnet wie zuvor
    (opencivil.projekt.frueher).
    """

    def alt(self, sigma_p0, sigma_pinf, **spannstahl) -> Projekt:
        roh = copy.deepcopy(projekt().als_dict())
        next(m for m in roh["materialien"] if m["kennung"] == "sp1").update(spannstahl)
        g = roh["querschnittsanalysen"][0]["spannglieder"][0]
        del g["anteil_p0"], g["anteil_pinf"]
        g["sigma_p0"], g["sigma_pinf"] = sigma_p0, sigma_pinf
        return Projekt.aus_dict(roh)

    def spannungen(self, p: Projekt):
        e = p.rechnen()
        return tuple(e.wert(f"querschnittsanalyse.a1.P1.{k}").groesse.si / 1e6
                     for k in ("sigma_p0", "sigma_pinf"))

    def test_leer_wird_die_vorgabe(self):
        g = self.alt(None, None).querschnittsanalysen[0].spannglieder[0]
        self.assertEqual((g.anteil_p0, g.anteil_pinf), (ANTEIL_SPANNEN, ANTEIL_NACH_VERLUSTEN))

    def test_eine_zahl_wird_ihr_faktor(self):
        """1350 und 1100 N/mm² bei f_pk = 1860: k_p0 = 0.7258…, dieselben Spannungen."""
        p = self.alt(1350.0, 1100.0)
        self.assertAlmostEqual(p.querschnittsanalysen[0].spannglieder[0].anteil_p0, 1350.0 / 1860.0)
        for ist, soll in zip(self.spannungen(p), (1350.0, 1100.0)):
            self.assertAlmostEqual(ist, soll)

    def test_sigma_pinf_allein_misst_sich_an_der_vorgabe(self):
        """Leer war σ_p0 = 0.70 · 1860 = 1302: σ_p∞ = 1000 gibt k_p∞ = 1000/1302."""
        for ist, soll in zip(self.spannungen(self.alt(None, 1000.0)), (1302.0, 1000.0)):
            self.assertAlmostEqual(ist, soll)

    def test_mit_der_zugfestigkeit_eines_eigenen_spannstahls(self):
        p = self.alt(1350.0, None, eigenstaendig=True, name="SP1", abweichungen={"f_pk": 1770.0})
        for ist, soll in zip(self.spannungen(p), (1350.0, 0.85 * 1350.0)):
            self.assertAlmostEqual(ist, soll)

    def test_was_keine_zahl_ist_meldet_sich(self):
        with self.assertRaisesRegex(ProjektFehler, "ein Feld 'sigma_p0' gibt es nicht"):
            self.alt("hoch", None)

    def test_eine_neue_datei_bleibt_wie_sie_ist(self):
        p = projekt()
        self.assertEqual(Projekt.aus_dict(p.als_dict()).als_dict(), p.als_dict())


if __name__ == "__main__":
    unittest.main()
