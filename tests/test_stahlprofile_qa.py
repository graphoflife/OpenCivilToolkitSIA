"""
Tests fuer das Stahlprofil in der Querschnittsanalyse (Plan vom 2026-11-25,
Schritt 11): ein Profil der Tabelle an seiner Mitte, aus einem Baustahl,
gedreht und gespiegelt -- gerechnet mit seinem Umriss, wie jede gezeichnete
Flaeche.

Von Hand, HEB 300 nach der Tabelle des Benutzers: A = 149.08 cm², I_y =
25 166 cm⁴, I_z = 8 563 cm⁴. Um 90° gedreht tauschen I_y und I_z. Der Umriss
trifft das auf ein halbes Prozent (:data:`opencivil.stahlprofile.formen.BOGENECKEN`).
"""

import unittest

from opencivil.bericht.markdown import als_markdown
from opencivil.projekt import Projekt, QuerschnittsanalyseEintrag
from opencivil.projekt.lesen import ProjektFehler
from opencivil.querschnitt import geometrie as geo
from opencivil.querschnitt.bauweise import Bauweise
from opencivil.querschnitt.vorlagen import kreispunkte
from opencivil.stahlprofile import lage
from opencivil.stahlprofile.tabelle import PROFILE
from opencivil.web import dienst
from opencivil.web.api import katalog
from tests.profilwerte import WERTE

#: So weit darf der Umriss von den Kennwerten des Balkensystems abweichen --
#: beim UNP liegt I_z 0.44 % daneben (:data:`opencivil.stahlprofile.lage.IM_BERICHT`).
GRENZE = 0.005

#: Die Tabelle in cm² und cm⁴, die Analyse in mm² und mm⁴.
CM2_IN_MM2 = 1e2
CM4_IN_MM4 = 1e4

QUADRAT = [[-200, -200], [200, -200], [200, 200], [-200, 200]]


def projekt():
    """Ein Projekt mit C30/37 (b1), B500B (s1) und S355 (st1)."""
    p = Projekt(name="Stahlprofile")
    p.beton("C30/37")
    p.stahl("B500B")
    p.baustahl("S355")
    return p


def analyse(p, *profile, polygone=()):
    """Eine Analyse aus ``profile`` -- je (y, z, Name, Felder), aus S355 -- und ``polygone``."""
    a = QuerschnittsanalyseEintrag.neu(kennung=p.freie_kennung("a"), name="Profile")
    for ecken, material in polygone:
        a.polygon(ecken, material=material)
    for y, z, name, felder in profile:
        a.profil(y, z, name, **{"stahl": "st1", **felder})
    p.querschnittsanalysen.append(a)
    return a


def zeichnung(p, a):
    """Was das Zeichenfenster vom Kern erfaehrt."""
    return dienst.geometrie({"projekt": p.als_dict(), "kennung": a.kennung})


def meldungen(antwort):
    return [(m["text"], m["fehler"]) for m in antwort["meldungen"]]


def werte(teile):
    """Fläche und Trägheitsmomente der Umrisse, wie die Analyse sie summiert: ein Loch zieht ab."""
    return geo.summe([(-1.0 if i else 1.0, geo.flaechenwerte(t)) for i, t in enumerate(teile)])


class TestUmriss(unittest.TestCase):
    def test_jedes_profil_wie_im_balkensystem(self):
        """Der Umriss gegen die Formeln seiner Form -- dieselben, mit denen das Balkensystem rechnet."""
        for name, p in PROFILE.items():
            w, k = werte(lage.Profillage(name).umrisse), p.form.kennwerte(p.masse)
            for groesse, ist in (("A", w.A), ("I_y", w.I_y), ("I_z", w.I_z)):
                with self.subTest(profil=name, groesse=groesse):
                    soll = k[groesse].si * (1e6 if groesse == "A" else 1e12)
                    self.assertAlmostEqual(ist / soll, 1.0, delta=GRENZE)

    def test_und_die_tabelle_auf_ein_prozent(self):
        """Beim UNP hat die Tabelle des Benutzers nur getippte Werte mit drei Stellen: bis 0.9 %."""
        for name, (A, I_y, I_z, _, _) in WERTE.items():
            w = werte(lage.Profillage(name).umrisse)
            for groesse, ist, soll in (("A", w.A, A * CM2_IN_MM2), ("I_y", w.I_y, I_y * CM4_IN_MM4),
                                       ("I_z", w.I_z, I_z * CM4_IN_MM4)):
                with self.subTest(profil=name, groesse=groesse):
                    self.assertAlmostEqual(ist / soll, 1.0, delta=0.01)

    def test_die_mitte_ist_die_des_rahmens(self):
        """Beim U liegt der Schwerpunkt neben der Mitte, zum Ruecken hin -- links."""
        for name in ("HEB 300", "UPE 200", "ROR 219.1 x 8"):
            aussen = lage.Profillage(name, mitte=(100.0, 50.0)).umrisse[0]
            ys, zs = [p[0] for p in aussen], [p[1] for p in aussen]
            with self.subTest(profil=name):
                self.assertAlmostEqual((min(ys) + max(ys)) / 2, 100.0)
                self.assertAlmostEqual((min(zs) + max(zs)) / 2, 50.0)
        self.assertLess(werte(lage.Profillage("UPE 200").umrisse).y_S, -10.0)

    def test_erst_gespiegelt_dann_gedreht(self):
        """Gespiegelt ist der Ruecken des U rechts; um 90° gedreht unten -- es ist nach oben offen."""
        self.assertGreater(werte(lage.Profillage("UPE 200", gespiegelt=True).umrisse).y_S, 10.0)
        w = werte(lage.Profillage("UPE 200", drehung=90).umrisse)
        self.assertLess(w.z_S, -10.0)
        self.assertAlmostEqual(w.y_S, 0.0, places=6)
        # Gespiegelt und um 90° gedreht: der Ruecken oben.
        self.assertGreater(werte(lage.Profillage("UPE 200", drehung=90, gespiegelt=True).umrisse).z_S, 10.0)

    def test_drehbar_und_spiegelbar(self):
        """
        Rund- und Vierkantstahl, ein Rundrohr und ein quadratisches Rohr dreht
        nichts, gespiegelt aendert sich nur das U.
        """
        fest = {n for n, p in PROFILE.items()
                if p.reihe in ("ROR", "VKT", "RND") or (p.reihe in ("RRK", "RRW")
                                                       and p.masse["h"] == p.masse["b"])}
        self.assertEqual({n for n in PROFILE if not lage.drehbar(n)}, fest)
        self.assertEqual({n for n in PROFILE if lage.spiegelbar(n)},
                         {n for n in PROFILE if n.startswith(("UPE", "UNP"))})

    def test_beschreibung_nennt_nur_was_aendert(self):
        for (name, drehung, gespiegelt), erwartet in (
                (("UPE 200", 90, True), "UPE 200, gespiegelt, um 90° gedreht"),
                (("HEB 300", 180, True), "HEB 300, um 180° gedreht"),
                (("HEB 300", 0, True), "HEB 300"),
                (("ROR 219.1 x 8", 90, False), "ROR 219.1 x 8")):
            self.assertEqual(lage.Profillage(name, drehung=drehung, gespiegelt=gespiegelt)
                             .beschreibung, erwartet)

    def test_fangpunkte_am_rahmen(self):
        fang = lage.fangpunkte(lage.Profillage("HEB 300").umrisse)
        self.assertEqual(len(fang), 8)
        self.assertIn((0.0, 150.0), fang)     # die Mitte des Obergurts
        self.assertIn((-150.0, -150.0), fang)

    def test_skizze_mit_zwei_massen(self):
        """Breite unten, Hoehe links -- um 90° gedreht ist h die Breite; ein Rohr hat nur D."""
        texte = lambda teile: [m["text"] for m in teile.masslinien]  # noqa: E731
        self.assertEqual(texte(lage.skizze("UPE 200")), ["b = 80", "h = 200"])
        self.assertEqual(texte(lage.skizze("UPE 200", 90)), ["h = 200", "b = 80"])
        rohr = lage.skizze("ROR 219.1 x 8")
        self.assertEqual(texte(rohr), ["D = 219.1"])
        self.assertEqual([p["aussparung"] for p in rohr.polygone], [False, True])


class TestAnalyse(unittest.TestCase):
    def test_heb_300_von_hand(self):
        p = projekt()
        a = analyse(p, (0, 0, "HEB 300", {}))
        e = p.rechnen()
        A, I_y, I_z, _, _ = WERTE["HEB 300"]
        for groesse, soll in (("A", A * 1e-4), ("I_y", I_y * 1e-8), ("I_z", I_z * 1e-8)):
            with self.subTest(groesse=groesse):
                ist = e.wert(f"querschnittsanalyse.{a.kennung}.{groesse}").groesse.si
                self.assertAlmostEqual(ist / soll, 1.0, delta=GRENZE)
        self.assertEqual(e.aufbau.teile[a.kennung].ohne_nachweis, "")

    def test_um_90_grad_tauschen_I_y_und_I_z(self):
        p = projekt()
        gerade = analyse(p, (0, 0, "HEB 300", {}))
        gedreht = analyse(p, (0, 0, "HEB 300", {"drehung": 90}))
        e = p.rechnen()
        wert = lambda a, g: e.wert(f"querschnittsanalyse.{a.kennung}.{g}").groesse.si  # noqa: E731
        self.assertAlmostEqual(wert(gedreht, "I_y") / wert(gerade, "I_z"), 1.0, places=9)
        self.assertAlmostEqual(wert(gedreht, "I_z") / wert(gerade, "I_y"), 1.0, places=9)

    def test_ein_rohr_mit_beton_ist_verbund(self):
        p = projekt()
        kern = [list(q) for q in kreispunkte((0.0, 0.0), 100.0, 48)]
        a = analyse(p, (0, 0, "ROR 219.1 x 8", {}), polygone=[(kern, "b1")])
        teil = p.rechnen().aufbau.teile[a.kennung]
        self.assertEqual((teil.objekt.bauweise, teil.ohne_nachweis), (Bauweise.VERBUND, ""))

    def test_im_bericht_mit_lage_und_umriss(self):
        p = projekt()
        a = analyse(p, (0, 0, "UPE 200", {"drehung": 90, "gespiegelt": True}),
                    (0, 400, "ROR 219.1 x 8", {}))
        aufbau = p.aufbauen()
        text = als_markdown(aufbau.werk.loese(f"querschnittsanalyse.{a.kennung}.A"), aufbau=aufbau)
        self.assertIn("| Profil 1 (UPE 200, gespiegelt, um 90° gedreht) | S355 | – |", text)
        self.assertIn("| Profil 2, innen | – | Profil 2 |", text)
        self.assertIn(lage.IM_BERICHT, text)
        self.assertNotIn("-0.0", text)


class TestZeichnung(unittest.TestCase):
    """Was das Zeichenfenster vom Kern erfaehrt -- grau, was fehlt, rot, was falsch ist."""

    def test_die_antwort_zum_profil(self):
        p = projekt()
        antwort = zeichnung(p, analyse(p, (100, 50, "UPE 200", {"drehung": 90})))
        self.assertEqual(antwort["meldungen"], [])
        profil = antwort["profile"][0]
        self.assertEqual({k: profil[k] for k in ("element", "kennung", "tiefe", "lage", "beschreibung",
                                                 "drehbar", "spiegelbar")},
                         {"element": "Profil 1", "kennung": "R1", "tiefe": 0, "lage": [100.0, 50.0],
                          "beschreibung": "UPE 200, um 90° gedreht", "drehbar": True, "spiegelbar": True})
        self.assertAlmostEqual(profil["breite"], 200.0)
        self.assertAlmostEqual(profil["hoehe"], 80.0)
        self.assertAlmostEqual(profil["A"] / (WERTE["UPE 200"][0] * CM2_IN_MM2), 1.0, delta=GRENZE)
        self.assertEqual(len(profil["fang"]), 8)
        self.assertEqual(antwort["materialien"], ["st1"])

    def test_wie_tief_jedes_liegt(self):
        """Im Beton liegt das Profil darueber; im Rohr der Beton -- das Loch zaehlt nicht."""
        p = projekt()
        umhuellt = zeichnung(p, analyse(p, (0, 0, "HEB 300", {}), polygone=[(QUADRAT, "b1")]))
        self.assertEqual(([x["tiefe"] for x in umhuellt["polygone"]], umhuellt["profile"][0]["tiefe"]),
                         ([0], 1))
        kern = [list(q) for q in kreispunkte((0.0, 0.0), 100.0, 48)]
        gefuellt = zeichnung(p, analyse(p, (0, 0, "ROR 219.1 x 8", {}), polygone=[(kern, "b1")]))
        self.assertEqual(([x["tiefe"] for x in gefuellt["polygone"]], gefuellt["profile"][0]["tiefe"]),
                         ([2], 0))

    def test_ohne_baustahl_grau(self):
        p = projekt()
        self.assertEqual(meldungen(zeichnung(p, analyse(p, (0, 0, "HEB 300", {"stahl": ""})))),
                         [("Profil 1: noch kein Material gewählt.", False)])

    def test_falsches_material_rot(self):
        p = projekt()
        self.assertEqual(meldungen(zeichnung(p, analyse(p, (0, 0, "HEB 300", {"stahl": "b1"})))),
                         [("Profil 1: «C30/37» ist kein Baustahl.", True)])

    def test_unbekannter_name_rot_am_profil(self):
        """Den Namen prueft der Baukasten; aus einer Datei kann trotzdem einer kommen, den es nicht gibt."""
        p = projekt()
        a = analyse(p, (0, 0, "HEB 300", {}))
        a.profile[0].profil = "HEB 999"
        antwort = zeichnung(p, a)
        self.assertEqual(antwort["meldungen"], [{
            "text": "Profil 1: Ein Profil «HEB 999» gibt es nicht.",
            "elemente": ["R1"], "fehler": True}])
        self.assertEqual(antwort["profile"], [])

    def test_teilweise_ueberlappt(self):
        p = projekt()
        halb = [[0, -200], [400, -200], [400, 200], [0, 200]]
        texte = [t for t, rot in meldungen(zeichnung(p, analyse(p, (0, 0, "HEB 300", {}),
                                                                 polygone=[(halb, "b1")]))) if rot]
        self.assertTrue(any(t.startswith("Polygon 1 und Profil 1 überlappen sich teilweise") for t in texte),
                        texte)


class TestEintrag(unittest.TestCase):
    def test_vorlage_und_kennung(self):
        self.assertEqual(katalog()["vorlagen"]["profil"], {
            "kennung": "", "knoten": "", "profil": "IPE 300", "stahl": "", "drehung": 0,
            "gespiegelt": False})
        p = projekt()
        a = analyse(p, (0, 0, "HEB 300", {}), (0, 400, "IPE 300", {}))
        self.assertEqual([e.kennung for e in a.profile], ["R1", "R2"])
        self.assertEqual(a.materialien(), ["st1"])
        self.assertFalse(a.leer)

    def test_ein_unbekannter_name_im_baukasten(self):
        p = projekt()
        a = analyse(p)
        with self.assertRaises(ProjektFehler) as fehler:
            a.profil(0, 0, "HEB 999")
        self.assertIn("HEB 999", str(fehler.exception))

    def test_nur_eine_der_vier_drehungen(self):
        p = projekt()
        with self.assertRaises(ProjektFehler):
            analyse(p, (0, 0, "HEB 300", {"drehung": 45}))

    def test_speichern_und_laden(self):
        p = projekt()
        analyse(p, (100, 50, "UPE 200", {"drehung": 270, "gespiegelt": True}))
        wieder = Projekt.aus_dict(p.als_dict())
        self.assertEqual(wieder.querschnittsanalysen[0].profile, p.querschnittsanalysen[0].profile)


class TestVorlage(unittest.TestCase):
    """Die Vorlage «Stahlprofil»: ihre Skizze vom Kern, eingesetzt wird an der Oberflaeche."""

    def test_skizze_und_was_sich_aendert(self):
        antwort = dienst.vorlage({"wahl": {"art": "stahlprofil", "profil": "UPE 200", "drehung": 90,
                                           "gespiegelt": True}})
        self.assertEqual((antwort["fehler"], antwort["drehbar"], antwort["spiegelbar"]), (None, True, True))
        self.assertEqual([m["text"] for m in antwort["teile"]["masslinien"]], ["h = 200", "b = 80"])
        rohr = dienst.vorlage({"wahl": {"art": "stahlprofil", "profil": "ROR 219.1 x 8"}})
        self.assertEqual((rohr["drehbar"], rohr["spiegelbar"]), (False, False))

    def test_ein_unbekannter_name_ist_nur_unfertig(self):
        self.assertEqual(dienst.vorlage({"wahl": {"art": "stahlprofil", "profil": "HEB 999"}}),
                         {"fehler": "Ein Profil «HEB 999» gibt es nicht.", "teile": None})
        self.assertEqual(dienst.vorlage({"wahl": {"art": "stahlprofil", "profil": "FL 0 x 10"}}),
                         {"fehler": "Das Profil «FL 0 x 10» geht nicht: Breite b muss grösser "
                                    "als null sein, angegeben ist 0 mm.", "teile": None})

    def test_vollstahl_bemasst_seine_eigenen_masse(self):
        """Der Vierkant nur a, der Flachstahl b und h -- um 90° gedreht h unten."""
        for profil, drehung, texte, drehbar in (("VKT 40", 0, ["a = 40"], False),
                                                ("RND 12.5", 0, ["d = 12.5"], False),
                                                ("FL 60 x 8", 90, ["h = 8", "b = 60"], True)):
            with self.subTest(profil=profil):
                antwort = dienst.vorlage({"wahl": {"art": "stahlprofil", "profil": profil,
                                                   "drehung": drehung}})
                self.assertEqual([m["text"] for m in antwort["teile"]["masslinien"]], texte)
                self.assertEqual((antwort["drehbar"], antwort["spiegelbar"]), (drehbar, False))

    def test_eine_falsche_drehung_ist_eine_falsche_anfrage(self):
        with self.assertRaises(dienst.DienstFehler):
            dienst.vorlage({"wahl": {"art": "stahlprofil", "profil": "HEB 300", "drehung": 45}})

    def test_im_katalog(self):
        k = katalog()
        self.assertEqual([r["kurz"] for r in k["profilreihen"]],
                         ["IPE", "HEA", "HEB", "HEM", "UPE", "UNP", "RRK", "RRW", "ROR",
                          "VKT", "RND", "FL"])
        heb = next(r for r in k["profilreihen"] if r["kurz"] == "HEB")
        self.assertEqual((heb["profile"][0], heb["frei"]), ("HEB 100", []))
        self.assertTrue(heb["skizze"]["polygone"])
        fl = next(r for r in k["profilreihen"] if r["kurz"] == "FL")
        self.assertEqual(fl["profile"], ["FL 100 x 10"])
        self.assertEqual([(m["schluessel"], m["beschriftung"], m["vorgabe"], m["schritt"])
                          for m in fl["frei"]],
                         [("b", "Breite", 100.0, 1.0), ("h", "Dicke", 10.0, 1.0)])
        self.assertEqual(fl["frei"][0]["angabe"]["ueber"], 0.0)
        vorlage = k["querschnittsanalyse"]["profil"]
        self.assertEqual(vorlage["schluessel"], "stahlprofil")
        self.assertEqual([d["wert"] for d in vorlage["drehungen"]], [0, 90, 180, 270])


if __name__ == "__main__":
    unittest.main()
