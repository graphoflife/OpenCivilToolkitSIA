"""
Das Fachwerkmodell, Schritt 11b: die Suche nach dem leichtesten Fachwerk
(Ground Structure), Runde um Runde über den Dienst, nachgerechnet von der
Rechnung -- gegen Handrechnungen geprüft.
"""

import math
import unittest
from dataclasses import asdict

from opencivil.core.protokoll import GleichungBlock, HinweisArt, HinweisBlock, TabellenBlock
from opencivil.fachwerkmodell.grundstruktur import ZuVieleKnoten, grundstruktur
from opencivil.fachwerkmodell.nachrechnung import nachrechnen
from opencivil.fachwerkmodell.suche import Einstellung, Suchzustand, _zusammengelegt, ganz_suchen, runde
from opencivil.fachwerkmodell.werk import UNLESBAR, VERALTET
from opencivil.projekt import Projekt, beispiele
from opencivil.projekt.aufbau.fachwerkmodell import einstellung_von, modell_von
from opencivil.projekt.fachwerkmodell import FachwerkstabEintrag, GefundenesFachwerk
from opencivil.projekt.lesen import ProjektFehler
from opencivil.web import dienst

from tests.test_fachwerkmodell import wandscheibe


def konsole(rasterweite: float = 0.5, w_Z: float = 1.0) -> Projekt:
    """
    Eine Konsole 1 × 2 m, an der linken Kante bei (0, 0) und (0, 2) fest,
    100 kN nach unten bei (1, 1).
    """
    p = Projekt(name="Konsole")
    f = p.fachwerkmodell("Konsole")
    f.rasterweite, f.w_Z = rasterweite, w_Z
    f.scheibe([(0, 0), (1, 0), (1, 2), (0, 2)])
    f.lager_setzen((0, 0))
    f.lager_setzen((0, 2))
    f.last((1, 1), F_v=100)
    return p


def gesucht(p: Projekt, kennung: str = "f1") -> dict:
    """Runde um Runde über den Dienst, wie die Seite -- die Antwort der letzten."""
    zustand, runden = None, 0
    while True:
        antwort = dienst.bearbeite("fachwerk_suchen",
                                   {"projekt": p.als_dict(), "kennung": kennung, "zustand": zustand})
        assert antwort.status == 200, antwort.daten
        runden += 1
        if antwort.daten["fertig"]:
            return antwort.daten
        zustand = antwort.daten["zustand"]


def uebersicht(p: Projekt, kennung: str = "f1") -> dict:
    antwort = dienst.bearbeite("fachwerk_zeichnung", {"projekt": p.als_dict(), "kennung": kennung})
    return antwort.daten["uebersicht"]


def befund_von(p: Projekt, kennung: str = "f1"):
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.ziele_von(kennung))
    return loesung, loesung.befunde[aufbau.fachwerkmodelle[kennung].rechnung.id]


class TestKonsole(unittest.TestCase):
    """
    Die Handrechnung: zwei Stäbe von je √2 m zur Last, oben Zug, unten Druck.
    Am Knoten der Last: waagrecht heben sich die beiden auf, senkrecht tragen
    sie je 100/2 kN, also N = 50 · √2 = 70.71 kN. V = 2 · √2 · 70.71 = 200
    kNm; mit w_Z = 2 zählt der Zug doppelt: 300 kNm. Die virtuellen
    Verschiebungen u = (0, −2x) beweisen, dass es kein leichteres gibt --
    in jedem Raster.
    """

    def test_zwei_staebe_gegen_die_handrechnung(self):
        for weite in (1.0, 0.5, 0.25):
            with self.subTest(weite=weite):
                fw = gesucht(konsole(weite))["fachwerk"]
                kraefte = sorted(s["N"] for s in fw["staebe"])
                self.assertEqual(len(kraefte), 2)
                self.assertAlmostEqual(kraefte[0], -50 * math.sqrt(2), places=3)
                self.assertAlmostEqual(kraefte[1], 50 * math.sqrt(2), places=3)
                self.assertAlmostEqual(fw["V"], 200.0, places=3)

    def test_zug_doppelt(self):
        fw = gesucht(konsole(0.5, w_Z=2.0))["fachwerk"]
        self.assertEqual(len(fw["staebe"]), 2)
        self.assertAlmostEqual(fw["V"], 300.0, places=3)

    def test_oben_zug_unten_druck(self):
        fw = gesucht(konsole())["fachwerk"]
        for s in fw["staebe"]:
            oben = max(fw["knoten"][s["von"]]["y"], fw["knoten"][s["bis"]]["y"])
            self.assertEqual(s["N"] > 0, oben == 2.0)

    def test_lagerkraefte(self):
        """Das obere Lager zieht nach links und hält 50 kN, das untere drückt nach rechts."""
        fw = gesucht(konsole())["fachwerk"]
        kraefte = {r["lager"]: (r["R_x"], r["R_y"]) for r in fw["lagerkraefte"]}
        self.assertAlmostEqual(kraefte["A1"][0], 50.0, places=3)
        self.assertAlmostEqual(kraefte["A1"][1], 50.0, places=3)
        self.assertAlmostEqual(kraefte["A2"][0], -50.0, places=3)
        self.assertAlmostEqual(kraefte["A2"][1], 50.0, places=3)


class TestWandscheibe(unittest.TestCase):
    """Die Wand 6 × 3 m mit Türe: das Fachwerk trägt die Lasten im Gleichgewicht zu den Lagern."""

    def test_raster_halber_meter(self):
        """12 Runden, 58 Stäbe, V = 6818.9 kNm."""
        antwort = gesucht(wandscheibe())
        self.assertEqual(antwort["stand"], {"runde": 12, "im_modell": 333, "moeglich": 1526, "dazu": 0})
        self.assertEqual(len(antwort["fachwerk"]["staebe"]), 58)
        self.assertAlmostEqual(antwort["fachwerk"]["V"], 6818.91, places=1)
        self.assertEqual(antwort["meldungen"], [])

    def test_lagerkraefte_gegen_die_handrechnung(self):
        """
        Momente um A1: R_A2 · 6 = 300 · 2 + 200 · 5 + 50 · 3, also R_A2 =
        291.67 kN; A1 trägt den Rest der 500 kN und hält die 50 kN quer.
        """
        p = wandscheibe()
        p.fachwerkmodelle[0].rasterweite = 1.0
        kraefte = {r["lager"]: (r["R_x"], r["R_y"]) for r in gesucht(p)["fachwerk"]["lagerkraefte"]}
        self.assertAlmostEqual(kraefte["A2"][1], 1750 / 6, places=3)
        self.assertAlmostEqual(kraefte["A1"][1], 500 - 1750 / 6, places=3)
        self.assertAlmostEqual(kraefte["A1"][0], -50.0, places=3)
        self.assertAlmostEqual(kraefte["A2"][0], 0.0, places=6)

    def test_duenne_staebe_fallen_auch_bei_04_weg(self):
        """
        Im Raster von 0.4 m geht es ohne alle Stäbe unter 1 % nicht auf; die
        halbe Schwelle reicht nicht, ein Viertel schon: 74 Stäbe. Ohne das
        Halbieren blieben alle 89 stehen, gleich leicht.
        """
        p = wandscheibe()
        p.fachwerkmodelle[0].rasterweite = 0.4
        fw = gesucht(p)["fachwerk"]
        self.assertEqual(len(fw["staebe"]), 74)
        self.assertAlmostEqual(fw["V"], 6836.6, places=1)

    def test_jede_runde_im_gleichgewicht(self):
        """Auch wer nach der dritten Runde anhält, hat ein Fachwerk, das die Lasten trägt."""
        p = wandscheibe()
        f = p.fachwerkmodelle[0]
        f.rasterweite = 1.0
        modell, _ = modell_von(f)
        einstellung = einstellung_von(f)
        zustand = None
        for _ in range(3):
            r = runde(modell, einstellung, zustand)
            zustand = r.zustand
            self.assertTrue(nachrechnen(modell, r.ergebnis.fachwerk, 1.0).im_gleichgewicht)
        self.assertEqual(r.ergebnis.runden, 3)
        self.assertFalse(r.ergebnis.fertig)


class TestZustand(unittest.TestCase):
    def setUp(self):
        self.p = wandscheibe()
        self.p.fachwerkmodelle[0].rasterweite = 1.0
        self.modell, _ = modell_von(self.p.fachwerkmodelle[0])
        self.einstellung = einstellung_von(self.p.fachwerkmodelle[0])

    def test_anderes_modell_beginnt_von_vorn(self):
        erste = runde(self.modell, self.einstellung, None)
        anders = Einstellung(weite=1.0, w_Z=2.0, N_min=0.01)
        self.assertEqual(runde(self.modell, anders, erste.zustand).ergebnis.runden, 1)
        self.assertEqual(runde(self.modell, self.einstellung, erste.zustand).ergebnis.runden, 2)

    def test_staebe_die_es_nicht_gibt(self):
        """Ein Zustand, den nicht der Kern schrieb: von vorn, statt abzustürzen."""
        erste = runde(self.modell, self.einstellung, None)
        z = erste.zustand
        for aktiv in ((10 ** 6,), z.aktiv + z.aktiv[:1]):
            with self.subTest(aktiv=aktiv[:3]):
                fremd = Suchzustand(z.abdruck, z.runde, aktiv)
                self.assertEqual(runde(self.modell, self.einstellung, fremd).ergebnis.runden, 1)

    def test_unlesbarer_zustand(self):
        antwort = dienst.bearbeite("fachwerk_suchen", {
            "projekt": self.p.als_dict(), "kennung": "f1", "zustand": {"abdruck": 1}})
        self.assertEqual(antwort.status, 400)
        self.assertIn("Der Zustand der Suche ist nicht lesbar.", str(antwort.daten))

    def test_kein_fachwerkmodell(self):
        p = beispiele.jeder_nachweis()
        antwort = dienst.bearbeite("fachwerk_suchen", {
            "projekt": p.als_dict(), "kennung": p.querschnitte[0].kennung, "zustand": None})
        self.assertEqual(antwort.status, 400)


class TestGrenzen(unittest.TestCase):
    def test_zu_feines_raster(self):
        p = wandscheibe()
        p.fachwerkmodelle[0].rasterweite = 0.05
        antwort = gesucht(p)
        self.assertIsNone(antwort["fachwerk"])
        self.assertEqual(len(antwort["meldungen"]), 1)
        self.assertRegex(antwort["meldungen"][0]["text"],
                         r"^Mit der Rasterweite 0\.05 m lägen \d+ Knoten in der Scheibe – mehr als "
                         r"600 sucht das Werkzeug nicht\. Bitte die Rasterweite mindestens 0\.2 m "
                         r"wählen\.$")
        modell, _ = modell_von(p.fachwerkmodelle[0])
        grundstruktur(modell, 0.2)
        with self.assertRaises(ZuVieleKnoten):
            grundstruktur(modell, 0.15)

    def test_unfertiges_modell_sucht_nicht(self):
        p = wandscheibe()
        p.fachwerkmodelle[0].lasten.clear()
        antwort = gesucht(p)
        self.assertIsNone(antwort["fachwerk"])
        self.assertEqual([m["text"] for m in antwort["meldungen"]], ["Keine Last → kein Fachwerk."])
        with self.assertRaises(ProjektFehler):
            p.fachwerkmodelle[0].suchen()

    def test_last_ohne_weg_zum_lager(self):
        """Eine zweite Scheibe ohne Lager: ihre Last bleibt offen -- rot, mit ihrem Namen."""
        p = konsole(1.0)
        f = p.fachwerkmodelle[0]
        f.scheibe([(3, 0), (4, 0), (4, 1), (3, 1)])
        f.last((4, 1), F_v=20)
        antwort = gesucht(p)
        self.assertEqual([(m["text"], m["fehler"], m["elemente"]) for m in antwort["meldungen"]], [
            ("Die Last F2 lässt sich nicht ganz zu den Lagern tragen: 20.0 kN bleiben offen.",
             True, ["F2"])])


class TestRaender(unittest.TestCase):
    """Ein Stab auf einem Rand braucht Material auf einer Seite."""

    def setUp(self):
        modell, _ = modell_von(wandscheibe().fachwerkmodelle[0])
        gs = grundstruktur(modell, 1.0)
        self.staebe = {(gs.knoten[a], gs.knoten[b]) for a, b in gs.staebe}
        self.staebe |= {(b, a) for a, b in self.staebe}

    def test_kein_stab_unter_der_tuere(self):
        """
        Die Schwelle der Türe liegt auf dem Rand der Scheibe: darunter ist
        keine Scheibe, darüber die Türe. Bis 2026-11-28 trug dort ein Band,
        im Beispiel mit 135 kN.
        """
        unten = [(a, b) for a, b in self.staebe if a[1] == 0.0 == b[1]]
        self.assertIn(((3.0, 0.0), (3.5, 0.0)), unten)
        self.assertFalse([(a, b) for a, b in unten if min(a[0], b[0]) < 4.5 and max(a[0], b[0]) > 3.5])

    def test_auf_dem_rand_mit_material_daneben(self):
        """Längs der Türe, über ihr und an den Rändern der Scheibe."""
        for a, b in (((3.5, 0.0), (3.5, 2.2)), ((4.5, 0.0), (4.5, 2.2)), ((3.5, 2.2), (4.5, 2.2)),
                     ((5.0, 0.0), (6.0, 0.0)), ((0.0, 0.0), (1.0, 0.0)), ((6.0, 2.0), (6.0, 3.0))):
            with self.subTest(von=a, bis=b):
                self.assertIn((a, b), self.staebe)


class TestNachbearbeitung(unittest.TestCase):
    def test_zwei_staebe_in_einer_flucht_werden_einer(self):
        knoten = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (2.0, 0.0)]
        staebe = [(0, 1, -10.0), (1, 2, -10.0), (2, 3, 5.0)]
        self.assertEqual(_zusammengelegt(knoten, staebe, fest=set()),
                         [(2, 3, 5.0), (0, 2, -10.0)])
        # An einem Knoten mit Last oder Lager bleiben es zwei.
        self.assertEqual(_zusammengelegt(knoten, staebe, fest={1}), staebe)

    def test_geknickt_bleiben_es_zwei(self):
        knoten = [(0.0, 0.0), (1.0, 1.0), (2.0, 1.0)]
        staebe = [(0, 1, -10.0), (1, 2, -10.0)]
        self.assertEqual(_zusammengelegt(knoten, staebe, fest=set()), staebe)


class TestAblage(unittest.TestCase):
    """Was die Suche fand, steht im Projekt; die Rechnung rechnet es nach und erkennt, ob es noch passt."""

    def test_abgelegt_nachgerechnet(self):
        p = konsole()
        p.fachwerkmodelle[0].suchen()
        u = uebersicht(p)
        self.assertEqual((u["stand"], u["meldungen"], u["zum_fachwerk"]), ("gefunden", [], []))
        self.assertAlmostEqual(u["fachwerk"]["V"], 200.0, places=3)
        self.assertTrue(u["fachwerk"]["fertig"])

    def test_wie_die_seite_es_ablegt(self):
        """Die Seite legt ab, was die letzte Runde als ``gefunden`` gab."""
        p = konsole()
        daten = gesucht(p)
        f = p.fachwerkmodelle[0]
        roh = p.als_dict()
        roh["fachwerkmodelle"][0]["fachwerk"] = daten["gefunden"]
        u = dienst.bearbeite("fachwerk_zeichnung", {"projekt": roh, "kennung": f.kennung})
        self.assertEqual(u.daten["uebersicht"]["stand"], "gefunden")
        self.assertEqual(u.daten["uebersicht"]["abdruck"], daten["abdruck"])

    def test_veraltet_nach_einer_aenderung(self):
        for aendern in (lambda f: setattr(f, "rasterweite", 0.25), lambda f: setattr(f, "w_Z", 2.0),
                        lambda f: setattr(f.lasten[0], "F_v", 120.0),
                        lambda f: setattr(f.knoten[0], "x", 0.1)):
            with self.subTest():
                p = konsole()
                f = p.fachwerkmodelle[0]
                f.suchen()
                aendern(f)
                loesung, befund = befund_von(p)
                self.assertEqual((befund.stand, befund.gefunden), ("veraltet", None))
                self.assertEqual([(m.text, m.fehler) for m in befund.zum_fachwerk], [(VERALTET, False)])

    def test_unlesbar_steht_rot(self):
        p = konsole()
        f = p.fachwerkmodelle[0]
        f.suchen()
        f.fachwerk.staebe.append(FachwerkstabEintrag(0, 99, 1.0))
        loesung, befund = befund_von(p)
        self.assertEqual(befund.stand, "unlesbar")
        self.assertEqual([(m.text, m.fehler) for m in befund.zum_fachwerk], [(UNLESBAR, True)])

    def test_angehalten(self):
        p = wandscheibe()
        f = p.fachwerkmodelle[0]
        f.rasterweite = 1.0
        modell, _ = modell_von(f)
        r = runde(modell, einstellung_von(f), None)
        roh = p.als_dict()
        roh["fachwerkmodelle"][0]["fachwerk"] = asdict(GefundenesFachwerk.aus(r.ergebnis))
        p = Projekt.aus_dict(roh)
        loesung, befund = befund_von(p)
        self.assertEqual(befund.stand, "gefunden")
        self.assertIn("Die Suche wurde nach Runde 1 angehalten: das Fachwerk trägt die Lasten, "
                      "ist aber womöglich nicht das leichteste.", [m.text for m in befund.zum_fachwerk])

    def test_ganz_suchen_ist_die_letzte_runde(self):
        p = konsole()
        f = p.fachwerkmodelle[0]
        modell, _ = modell_von(f)
        e = ganz_suchen(modell, einstellung_von(f))
        self.assertTrue(e.fertig)
        self.assertEqual(e.fachwerk, f.suchen().ergebnis().fachwerk)


class TestHerleitung(unittest.TestCase):
    """Das Prüfprojekt hat das Fachwerk der Wand, wie «Fachwerk suchen» es findet."""

    def test_tabellen_und_ziel(self):
        p = beispiele.jeder_nachweis()
        f = next(x for x in p.fachwerkmodelle if x.name == "Wandscheibe mit Türe")
        loesung, befund = befund_von(p, f.kennung)
        self.assertEqual((befund.stand, befund.zum_fachwerk), ("gefunden", []))
        bloecke = loesung.protokoll.alle_bloecke()
        tabellen = {b.titel: b for b in bloecke if isinstance(b, TabellenBlock)}
        self.assertIn("Stäbe – 22, nach der Grösse ihrer Kraft", tabellen)
        self.assertEqual([z[0] for z in tabellen["Lagerkräfte"].zeilen], ["A1", "A2"])
        formeln = [b for b in bloecke if isinstance(b, GleichungBlock)]
        self.assertIn("Leichtestes Fachwerk", [b.name for b in formeln])
        warnungen = [b for b in bloecke if isinstance(b, HinweisBlock) and b.art is HinweisArt.WARNUNG]
        self.assertEqual(warnungen, [])

    def test_vorgaben_im_katalog(self):
        katalog = dienst.bearbeite("katalog").daten
        gruppen = katalog["vorgaben"]["fachwerkmodell"]
        self.assertEqual([g["titel"] for g in gruppen], ["Verfahren"])
        felder = [f["feld"] for f in next(iter(gruppen[0]["felder"].values()))]
        self.assertEqual(felder, ["rasterweite", "w_Z", "N_min"])


if __name__ == "__main__":
    unittest.main()
