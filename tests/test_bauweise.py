"""
Tests fuer die Bauweise eines gezeichneten Querschnitts (Benutzer,
2026-11-25): eine Flaeche ist aus Beton, Baustahl oder Holz, und woraus der
Querschnitt besteht, sagt der Kern -- Stahlbeton, Stahl, Verbund oder Holz.
Eine andere Mischung rechnet er nicht und sagt grau, mit Namen, warum.

Von Hand, das Rechteck 200 × 400 mm: A = 80 000 mm², I_y = 200 · 400³ / 12
= 1 066.67 · 10⁶ mm⁴. Aus C24 mit E_0,mean = 11 000 N/mm² (SIA 265:2012,
Tabelle 6): EI = 11 000 · 10⁶ N/m² · 1.0667 · 10⁻³ m⁴ = 11.73 MNm².
"""

import unittest

from opencivil.material.basis import Baustoffart
from opencivil.projekt import Projekt, QuerschnittsanalyseEintrag
from opencivil.projekt.aufbau.kern import materialgrund
from opencivil.projekt.lesen import feldangaben
from opencivil.projekt.querschnittsanalyse import FlaecheEintrag, StabEintrag
from opencivil.projekt.spannglieder import SpanngliedEintrag
from opencivil.projekt.staebe import MATERIAL_DES_QUERSCHNITTS
from opencivil.querschnitt.bauweise import BEWEHRT, Bauweise, Mischung, bauweise
from opencivil.web import dienst
from opencivil.web.api import katalog
from tests.traeger import traeger
from tests.unfertig import grund

RECHTECK = [[0, 0], [200, 0], [200, 400], [0, 400]]
#: Ein Blech mitten im Rechteck -- im Verbund der Baustahl im Beton.
BLECH = [[50, 100], [150, 100], [150, 300], [50, 300]]
A = 200 * 400 * 1e-6
I_Y = 200 * 400 ** 3 / 12 * 1e-12

BETON, BETONSTAHL, BAUSTAHL, SPANNSTAHL, HOLZ = (
    Baustoffart.BETON, Baustoffart.BETONSTAHL, Baustoffart.BAUSTAHL, Baustoffart.SPANNSTAHL,
    Baustoffart.HOLZ)


def projekt():
    """Je ein Material jeder Art: b1, s1, st1, sp1, h1 -- dazu ein zweites Holz, h2."""
    p = Projekt(name="Bauweisen")
    p.beton("C30/37")
    p.stahl("B500B")
    p.baustahl("S355")
    p.spannstahl("Y1860")
    p.holz("C24")
    p.holz("GL24h")
    return p


def analyse(p, name, *flaechen, staebe=()):
    """Eine Analyse aus ``flaechen`` -- je (Ecken, Material) -- und Staeben (y, z) aus B500B."""
    a = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name=name)
    for ecken, material in flaechen:
        a.polygon(ecken, material=material)
    for y, z in staebe:
        a.stab(y, z, durchmesser=20, stahl="s1")
    a.lastfall("LF1", M_y_Ed=10.0)
    p.querschnittsanalysen.append(a)
    return a


def zeichnung(p, a):
    """Was das Zeichenfenster vom Kern erfaehrt."""
    return dienst.geometrie({"projekt": p.als_dict(), "kennung": a.kennung})


def meldungen(antwort):
    """Die Meldungen zur Zeichnung -- je Text und ob er rot steht."""
    return [(m["text"], m["fehler"]) for m in antwort["meldungen"]]


class TestRegel(unittest.TestCase):
    """Die Tabelle des Benutzers vom 2026-11-25."""

    def test_die_vier_bauweisen(self):
        for stoffe, erwartet in (
                ([(BETON, "C30/37")], Bauweise.STAHLBETON),               # ohne Bewehrung, wie bisher
                ([(BETON, "C30/37"), (BETONSTAHL, "B500B"), (SPANNSTAHL, "Y1860")],
                 Bauweise.STAHLBETON),
                ([(BAUSTAHL, "S355")], Bauweise.STAHL),
                ([(BETON, "C30/37"), (BAUSTAHL, "S355"), (BETONSTAHL, "B500B")],
                 Bauweise.VERBUND),
                ([(HOLZ, "C24"), (HOLZ, "GL24h")], Bauweise.HOLZ)):
            with self.subTest(erwartet=erwartet):
                self.assertIs(bauweise(stoffe), erwartet)
        self.assertIsNone(bauweise([]))

    def test_eine_mischung_nennt_jede_art_mit_ihren_materialien(self):
        for stoffe, text in (
                ([(HOLZ, "C24"), (BETON, "C30/37"), (BETON, "C25/30"), (HOLZ, "C24")],
                 "Einen Querschnitt aus Holz («C24») und Beton («C30/37», «C25/30») rechnet "
                 "das Werkzeug nicht."),
                ([(BAUSTAHL, "S355"), (SPANNSTAHL, "Y1860")],
                 "Einen Querschnitt aus Baustahl («S355») und Spannstahl («Y1860») rechnet das "
                 "Werkzeug nicht."),
                ([(BAUSTAHL, "S355"), (BETONSTAHL, "B500B")],
                 "Einen Querschnitt aus Baustahl («S355») und Betonstahl («B500B») rechnet das "
                 "Werkzeug nicht.")):
            with self.subTest(text=text):
                with self.assertRaises(Mischung) as fehler:
                    bauweise(stoffe)
                self.assertEqual(str(fehler.exception), text)

    def test_norm_und_name(self):
        self.assertEqual([(b.querschnitt, b.norm) for b in Bauweise], [
            ("Stahlbetonquerschnitt", "SIA 262:2025"), ("Stahlquerschnitt", "SIA 263:2013"),
            ("Verbundquerschnitt", "SIA 264:2014"), ("Holzquerschnitt", "SIA 265:2012")])
        self.assertIs(BEWEHRT, BETON)


class TestFelder(unittest.TestCase):
    """Welche Arten ein Feld nimmt, steht an ihm -- und nur dort."""

    def test_am_feld_und_im_katalog(self):
        self.assertEqual(feldangaben(FlaecheEintrag)["material"]["stoffe"],
                         ["beton", "baustahl", "holz"])
        self.assertEqual(feldangaben(StabEintrag)["stahl"]["stoffe"], ["betonstahl"])
        self.assertEqual(feldangaben(SpanngliedEintrag)["stahl"]["stoffe"], ["spannstahl"])
        k = katalog()
        self.assertEqual(k["felder"]["flaeche"]["material"]["stoffe"], ["beton", "baustahl", "holz"])
        self.assertEqual(k["querschnittsanalyse"]["bewehrt"], "beton")

    def test_der_satz_nennt_jede_art(self):
        self.assertEqual(materialgrund("s1", ("betonstahl", "B500B"),
                                       ("beton", "baustahl", "holz")).text,
                         "«B500B» ist kein Beton, Baustahl oder Holz")
        self.assertEqual(materialgrund("s1", ("betonstahl", "B500B"), "beton").text,
                         "«B500B» ist kein Beton")
        self.assertIsNone(materialgrund("h1", ("holz", "C24"), ("beton", "baustahl", "holz")))


class TestAnalyse(unittest.TestCase):
    """
    Holz und Stahl rechnen ihre Querschnittswerte und ihren Lastfall -- ohne
    Querkraft nur Biegung und Normalkraft. Seit 2026-11-26 auch das Holz;
    eines aus mehreren Hoelzern noch nicht.
    """

    def test_holz_und_stahl_mit_nachweis(self):
        p = projekt()
        holz = analyse(p, "Holz", (RECHTECK, "h1"))
        stahl = analyse(p, "Stahl", (RECHTECK, "st1"))
        e = p.rechnen()
        for a, felder in ((holz, ["qa_holz"]), (stahl, ["qa_stahl"])):
            with self.subTest(a=a.name):
                teil = e.aufbau.teile[a.kennung]
                self.assertEqual((teil.ohne_nachweis, [f for f, _, _ in teil.nachweise]),
                                 ("", felder))
                self.assertAlmostEqual(e.wert(f"querschnittsanalyse.{a.kennung}.A").groesse.si, A)
                self.assertAlmostEqual(e.wert(f"querschnittsanalyse.{a.kennung}.I_y").groesse.si,
                                       I_Y, delta=1e-12)
        self.assertEqual([w.text for w in e.aufbau.warnungen if "noch nicht nach" in w.text], [])

    def test_mehrere_hoelzer_ohne_nachweis(self):
        """Zwei Hoelzer braeuchten einen gewichteten Querschnitt -- grau, mit ihren Namen."""
        p = projekt()
        a = analyse(p, "Zwei Hölzer", (RECHTECK, "h1"),
                    ([[0, 400], [200, 400], [200, 600], [0, 600]], "h2"))
        e = p.rechnen()
        text = ("einen Holzquerschnitt aus mehreren Hölzern («C24», «GL24h») weist das Werkzeug "
                "nach SIA 265:2012 noch nicht nach")
        teil = e.aufbau.teile[a.kennung]
        self.assertEqual((teil.ohne_nachweis, teil.nachweise), (text, []))
        self.assertIn(f"Querschnittsanalyse 'Zwei Hölzer': {text} → kein Nachweis.",
                      [w.text for w in e.aufbau.warnungen])

    def test_die_diagramme_sagen_warum(self):
        """Statt Interaktionsdiagramm und Lastfaellen der Satz -- das Bild des Querschnitts bleibt."""
        p = projekt()
        holz = analyse(p, "Holz", (RECHTECK, "h1"))
        stahl = analyse(p, "Stahl", (RECHTECK, "st1"))
        beton = analyse(p, "Stahlbeton", (RECHTECK, "b1"), staebe=[(100, 50)])
        d = p.als_dict()

        def diagramme(a):
            antwort = dienst.bearbeite("analysediagramme", {"projekt": d, "kennung": a.kennung})
            return antwort.daten["diagramme"]

        h = diagramme(holz)
        self.assertEqual(h["ohne_diagramm"], "Kein Interaktionsdiagramm: für einen "
                                             "Holzquerschnitt zeichnet das Werkzeug noch keines. "
                                             "Seine Lastfälle weist es trotzdem nach.")
        self.assertEqual((h["interaktion"], h["faelle"]), (None, []))
        self.assertEqual([f["material"] for f in h["zeichnung"]["polygone"]], ["holz"])
        s = diagramme(stahl)
        self.assertEqual(s["ohne_diagramm"], "Kein Interaktionsdiagramm: für einen "
                                             "Stahlquerschnitt zeichnet das Werkzeug noch keines. "
                                             "Seine Lastfälle weist es trotzdem nach.")
        self.assertEqual((s["interaktion"], s["faelle"]), (None, []))
        b = diagramme(beton)
        self.assertEqual(b["ohne_diagramm"], "")
        self.assertIsNotNone(b["interaktion"])

    def test_verbund_ohne_nachweis(self):
        p = projekt()
        a = analyse(p, "Verbund", (RECHTECK, "b1"), (BLECH, "st1"), staebe=[(100, 50)])
        self.assertEqual(p.rechnen().aufbau.teile[a.kennung].ohne_nachweis,
                         "einen Verbundquerschnitt weist das Werkzeug nach SIA 264:2014 noch "
                         "nicht nach")

    def test_eine_mischung_rechnet_nicht(self):
        p = projekt()
        a = analyse(p, "Mischung", (RECHTECK, "b1"), (BLECH, "h1"))
        self.assertIn("Einen Querschnitt aus Beton («C30/37») und Holz («C24») rechnet das "
                      "Werkzeug nicht", grund(p, a.kennung))

    def test_kein_stab_im_holz(self):
        p = projekt()
        a = analyse(p, "Holz mit Stab", (RECHTECK, "h1"), staebe=[(100, 50)])
        self.assertIn("Stab 1 (y = 100, z = 50 mm) liegt nicht ganz im Beton", grund(p, a.kennung))


class TestZeichnung(unittest.TestCase):
    """Was das Zeichenfenster erfaehrt -- alle Meldungen auf einmal, grau oder rot."""

    def test_der_satz_fuer_die_kacheln(self):
        p = projekt()
        self.assertEqual(zeichnung(p, analyse(p, "Holz", (RECHTECK, "h1")))["ohne_nachweise"], "")
        zwei = analyse(p, "Zwei Hölzer", (RECHTECK, "h1"),
                       ([[0, 400], [200, 400], [200, 600], [0, 600]], "h2"))
        self.assertEqual(zeichnung(p, zwei)["ohne_nachweise"],
                         "Einen Holzquerschnitt aus mehreren Hölzern («C24», «GL24h») weist das "
                         "Werkzeug nach SIA 265:2012 noch nicht nach.")
        self.assertEqual(zeichnung(p, analyse(p, "Stahlbeton", (RECHTECK, "b1"),
                                              staebe=[(100, 50)]))["ohne_nachweise"], "")

    def test_mischung_grau_und_ohne_element(self):
        p = projekt()
        antwort = zeichnung(p, analyse(p, "Mischung", (RECHTECK, "b1"), (BLECH, "h1")))
        self.assertFalse(antwort["gueltig"])
        self.assertEqual(antwort["meldungen"], [{
            "text": "Einen Querschnitt aus Beton («C30/37») und Holz («C24») rechnet das "
                    "Werkzeug nicht.", "elemente": [], "fehler": False}])
        self.assertEqual(antwort["ohne_nachweise"], "")

    def test_falsche_art_rot_geloeschte_grau(self):
        p = projekt()
        falsch = zeichnung(p, analyse(p, "Falsch", (RECHTECK, "s1"), staebe=[(100, 50)]))
        self.assertEqual(meldungen(falsch), [("Polygon 1: «B500B» ist kein Beton, Baustahl oder "
                                              "Holz.", True)])
        # Ein geloeschtes Material fehlt nur; der Stab darin gilt bis dahin als im Beton.
        geloescht = zeichnung(p, analyse(p, "Gelöscht", (RECHTECK, "b9"), staebe=[(100, 50)]))
        self.assertEqual(meldungen(geloescht), [("Polygon 1: das gewählte Material gibt es "
                                                 "nicht mehr – eines wählen.", False)])

    def test_im_verbund_nicht_im_blech(self):
        p = projekt()
        gut = zeichnung(p, analyse(p, "Verbund", (RECHTECK, "b1"), (BLECH, "st1"),
                                   staebe=[(100, 50)]))
        self.assertEqual((gut["gueltig"], gut["meldungen"]), (True, []))
        im_blech = zeichnung(p, analyse(p, "Stab im Blech", (RECHTECK, "b1"), (BLECH, "st1"),
                                        staebe=[(100, 200)]))
        self.assertEqual(meldungen(im_blech), [("Stab 1 (y = 100, z = 200 mm) liegt nicht ganz im "
                                                "Beton. Bewehrung muss im Beton liegen.", True)])

    def test_die_ueberdeckung_haelt_abstand_vom_blech(self):
        """Im Verbund: ein ⌀20 bei z = 90, 10 mm unter dem Blech, mit c = 20 nach z = 70."""
        p = projekt()
        a = analyse(p, "Verbund", (RECHTECK, "b1"), (BLECH, "st1"), staebe=[(100, 90)])
        a.flaechen[1].ueberdeckung = 20.0
        y, z = zeichnung(p, a)["staebe"][0]["ueberdeckt"]
        self.assertAlmostEqual(y, 100.0)
        self.assertAlmostEqual(z, 70.0)


class TestBezuege(unittest.TestCase):
    """Was andere Bauteile von einer Analyse aus Holz oder Stahl nehmen."""

    def balken(self):
        """Der Traeger, sein Stab mit dem Querschnitt «Holz» und dessen Material."""
        p = traeger()
        p.holz("C24")
        a = analyse(p, "Holzbalken", (RECHTECK, "h1"))
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Holz", "analyse", a)
        s.linien[0].querschnitt = q.kennung
        s.linien[0].material = MATERIAL_DES_QUERSCHNITTS
        return p, q

    def test_gemaess_querschnitt_mit_e_0_mean(self):
        p, q = self.balken()
        EI = p.rechnen().wert(f"balkensystem.r1.{q.kennung}.{MATERIAL_DES_QUERSCHNITTS}.EI")
        self.assertAlmostEqual(EI.groesse.si, 11000e6 * I_Y, delta=1e-6 * 11000e6 * I_Y)

    def test_kein_e_eq(self):
        p, q = self.balken()
        q.e_modul = "e_eq"
        texte = [m.text for m in p.rechnen().balkensystem("r1").ergebnis.meldungen]
        self.assertEqual(texte, ["Querschnitt «Holz»: kein E_eq – das gibt es bisher nur für "
                                 "einen Stahlbetonquerschnitt, und «Holzbalken» ist ein "
                                 "Holzquerschnitt."])

    def test_keine_wand_aus_holz(self):
        p = projekt()
        a = analyse(p, "Holzwand", ([[0, 0], [5000, 0], [5000, 250], [0, 250]], "h1"))
        h = p.gebaeude("Haus", zone="Z2")
        h.geschoss("Dach", h=3.0, G_k=2500.0)
        h.wand("W1", a.kennung)
        self.assertIn("Erdbeben 'Haus': die Querschnittsanalyse «Holzwand» ist ein "
                      "Holzquerschnitt – eine Wand rechnet das Werkzeug nur aus Stahlbeton "
                      "(«W1») → kein Nachweis.", [w.text for w in p.rechnen().aufbau.warnungen])


class TestVorlage(unittest.TestCase):
    """Eine Vorlage aus Holz: ihre Flaeche aus dem gewaehlten Material, ohne Bewehrung."""

    def test_ein_rechteck_aus_holz(self):
        p = projekt()
        a = analyse(p, "Leer")
        d = dienst.bearbeite("vorlage_einsetzen", {
            "projekt": p.als_dict(), "kennung": a.kennung, "material": "h1", "stahl": "s1",
            "wahl": {"art": "rechteck", "bewehrung": False, "schubwaende": False},
            "ursprung": [0, 0]}).daten
        self.assertEqual([f["material"] for f in d["elemente"]["flaechen"]], ["h1"])
        self.assertEqual((d["elemente"]["staebe"], d["elemente"]["stablinien"]), ([], []))


if __name__ == "__main__":
    unittest.main()
