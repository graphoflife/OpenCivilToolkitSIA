"""
Das Fachwerkmodell, Schritt 11a: die Beschreibung einer Scheibe mit
Löchern, Lagern und Lasten, ihr Modell in SI, was ihm fehlt oder an ihm
nicht stimmt -- und was die Oberfläche beim Zeichnen davon bekommt.
"""

import unittest

from opencivil.core.latex import Mathe
from opencivil.core.protokoll import HinweisArt, HinweisBlock, TabellenBlock
from opencivil.fachwerkmodell.modell import Halt, Lager, Last, Modell, Umriss
from opencivil.fachwerkmodell.pruefen import beweglich, pruefen
from opencivil.fachwerkmodell.werk import NOCH_KEINES
from opencivil.projekt import Projekt, beispiele
from opencivil.projekt.aufbau.fachwerkmodell import modell_von
from opencivil.web import dienst
from opencivil.web.fachwerkdaten import katalog

#: Eine Wandscheibe 6 × 3 m.
WAND = Umriss("S1", ((0, 0), (6, 0), (6, 3), (0, 3)))


def wandscheibe() -> Projekt:
    """Eine Wand 6 × 3 m mit einer Türe, fest links, verschieblich rechts, zwei Lasten oben."""
    p = Projekt(name="Fachwerk")
    f = p.fachwerkmodell("Wand")
    f.scheibe([(0, 0), (6, 0), (6, 3), (0, 3)])
    f.loch([(3.5, 0), (4.5, 0), (4.5, 2.2), (3.5, 2.2)])
    f.lager_setzen((0, 0))
    f.lager_setzen((6, 0), "y")
    f.last((2, 3), F_v=300)
    f.last((5, 3), F_h=50, F_v=200)
    return p


def lager(*orte_und_halt):
    """Lager A1, A2, … aus ``((x, y), "xy")``."""
    return [Lager(f"A{i}", ort, Halt(halt)) for i, (ort, halt) in enumerate(orte_und_halt, start=1)]


def texte(modell: Modell):
    """Je Meldung ihr Text, ob sie rot ist und ob sie anhält."""
    return [(m.text, m.fehler, m.haelt_an) for m in pruefen(modell)]


def zeichnung(p: Projekt, kennung: str = "f1"):
    return dienst.bearbeite("fachwerk_zeichnung", {"projekt": p.als_dict(), "kennung": kennung})


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        p = wandscheibe()
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)

    def test_lager_an_einer_ecke_teilen_ihren_knoten(self):
        """Wer die Ecke verschiebt, verschiebt das Lager mit."""
        f = wandscheibe().fachwerkmodelle[0]
        self.assertEqual(f.lager[0].knoten, f.scheiben[0].knoten[0])
        self.assertEqual(f.lager[1].knoten, f.scheiben[0].knoten[1])
        # Vier Ecken der Scheibe, zwei neue des Lochs unten, zwei oben, zwei Orte der Lasten.
        self.assertEqual(len(f.knoten), 10)

    def test_kennungen(self):
        f = wandscheibe().fachwerkmodelle[0]
        self.assertEqual(f.kennung, "f1")
        self.assertEqual([s.kennung for s in f.scheiben], ["S1"])
        self.assertEqual([l.kennung for l in f.loecher], ["L1"])
        self.assertEqual([l.kennung for l in f.lager], ["A1", "A2"])
        self.assertEqual([x.kennung for x in f.lasten], ["F1", "F2"])


class TestModell(unittest.TestCase):
    def test_lasten_in_si_senkrecht_nach_oben(self):
        """In der Maske F_v nach unten positiv, im Modell F_y nach oben -- in N."""
        modell, meldungen = modell_von(wandscheibe().fachwerkmodelle[0])
        self.assertEqual(meldungen, [])
        self.assertEqual([(f.name, f.ort, f.F_x, f.F_y) for f in modell.lasten],
                         [("F1", (2.0, 3.0), 0.0, -300e3), ("F2", (5.0, 3.0), 50e3, -200e3)])
        self.assertEqual([(l.name, l.halt) for l in modell.lager], [("A1", Halt.XY), ("A2", Halt.Y)])

    def test_verweis_ins_leere_sagt_es_am_ort(self):
        f = wandscheibe().fachwerkmodelle[0]
        f.lasten[0].knoten = "K99"
        modell, meldungen = modell_von(f)
        self.assertEqual([x.name for x in modell.lasten], ["F2"])
        self.assertEqual([(m.text, m.elemente) for m in meldungen],
                         [("F1 zeigt auf K99 – einen solchen Knoten gibt es nicht.", ("F1",))])

    def test_material_auf_dem_rand_eines_lochs(self):
        """Im Loch ist keines, auf seinem Rand und auf dem Rand der Scheibe schon."""
        modell, _ = modell_von(wandscheibe().fachwerkmodelle[0])
        self.assertFalse(modell.im_material((4.0, 1.0)))
        self.assertTrue(modell.im_material((4.5, 1.0)))
        self.assertTrue(modell.im_material((6.0, 1.5)))
        self.assertFalse(modell.im_material((7.0, 1.5)))


class TestMeldungen(unittest.TestCase):
    def test_die_wandscheibe_ist_bereit(self):
        modell, _ = modell_von(wandscheibe().fachwerkmodelle[0])
        self.assertEqual(pruefen(modell), [])

    def test_leer_fehlt_alles_grau(self):
        self.assertEqual(texte(Modell()), [
            ("Noch keine Scheibe – ihren Umriss zeichnen.", False, True),
            ("Noch kein Lager – die Scheibe an einem Punkt halten.", False, True),
            ("Keine Last → kein Fachwerk.", False, True),
        ])

    def test_eine_last_null_ist_keine(self):
        modell = Modell(scheiben=(WAND,), lager=tuple(lager(((0, 0), "xy"), ((6, 0), "y"))),
                        lasten=(Last("F1", (3, 3), 0.0, 0.0),))
        self.assertEqual(texte(modell), [("Keine Last → kein Fachwerk.", False, True)])

    def test_last_neben_der_scheibe_und_im_loch_rot(self):
        loch = Umriss("L1", ((2, 1), (4, 1), (4, 2), (2, 2)))
        modell = Modell(scheiben=(WAND,), loecher=(loch,), lager=tuple(lager(((0, 0), "xy"), ((6, 0), "y"))),
                        lasten=(Last("F1", (3, 5), 0.0, -1e3), Last("F2", (3, 1.5), 0.0, -1e3),
                                Last("F3", (4, 1.5), 0.0, -1e3)))
        meldungen = pruefen(modell)
        self.assertEqual([(m.text, m.elemente, m.fehler) for m in meldungen], [
            ("Die Last F1 liegt bei (3.00, 5.00) neben der Scheibe.", ("F1",), True),
            ("Die Last F2 liegt im Loch L1.", ("F2",), True),
        ])

    def test_loch_neben_jeder_scheibe_ist_ein_hinweis(self):
        """Es nimmt nichts weg -- gerechnet wird trotzdem."""
        daneben = Umriss("L1", ((7, 0), (8, 0), (8, 1), (7, 1)))
        anstossend = Umriss("L2", ((6, 1), (7, 1), (7, 2), (6, 2)))
        modell = Modell(scheiben=(WAND,), loecher=(daneben, anstossend),
                        lager=tuple(lager(((0, 0), "xy"), ((6, 0), "y"))), lasten=(Last("F1", (3, 3), 0, -1e3),))
        self.assertEqual(texte(modell), [
            ("Das Loch L1 liegt neben jeder Scheibe – es nimmt nichts weg.", False, False),
            ("Das Loch L2 liegt neben jeder Scheibe – es nimmt nichts weg.", False, False),
        ])

    def test_umriss_ohne_flaeche_rot(self):
        strich = Umriss("S2", ((0, 0), (1, 0), (2, 0)))
        modell = Modell(scheiben=(WAND, strich), lager=tuple(lager(((0, 0), "xy"), ((6, 0), "y"))),
                        lasten=(Last("F1", (3, 3), 0, -1e3),))
        meldungen = pruefen(modell)
        self.assertEqual(len(meldungen), 1)
        self.assertEqual((meldungen[0].elemente, meldungen[0].fehler), (("S2",), True))

    def test_nicht_gehalten_nennt_die_lager(self):
        modell = Modell(scheiben=(WAND,), lager=tuple(lager(((0, 0), "y"), ((6, 0), "y"))),
                        lasten=(Last("F1", (3, 3), 0, -1e3),))
        meldungen = pruefen(modell)
        self.assertEqual([(m.text, m.elemente, m.fehler, m.unfertig) for m in meldungen], [
            ("Die Lager halten die Scheibe noch nicht: sie kann sich in x verschieben.", ("A1", "A2"),
             False, True)])


class TestLagerung(unittest.TestCase):
    """Wie sich die starre Scheibe trotz ihrer Lager noch bewegen kann -- leer, wenn sie gehalten ist."""

    def test_gehalten(self):
        for faelle in [(((0, 0), "xy"), ((6, 0), "y")), (((0, 0), "x"), ((0, 3), "y"), ((6, 0), "y")),
                       (((0, 0), "xy"), ((6, 0), "xy")), (((0, 0), "xy"), ((0, 3), "x"))]:
            with self.subTest(lager=faelle):
                self.assertEqual(beweglich(lager(*faelle)), "")

    def test_beweglich(self):
        for faelle, bewegung in [
            ((((0, 0), "y"), ((6, 0), "y")), "in x verschieben"),
            ((((0, 0), "x"), ((0, 3), "x")), "in y verschieben"),
            ((((0, 0), "x"), ((6, 0), "x")), "verschieben und drehen"),
            ((((0, 0), "xy"),), "um das Lager A1 drehen"),
            ((((0, 0), "x"), ((0, 3), "y")), "um das Lager A1 drehen"),
            ((((0, 0), "y"), ((3, 3), "x")), "um den Punkt (0.00, 3.00) drehen"),
            # Die Wirkungslinien der beiden Lagerkräfte schneiden sich in (6, 0) -- dort steht A2.
            ((((0, 0), "x"), ((6, 0), "y")), "um das Lager A2 drehen"),
        ]:
            with self.subTest(lager=faelle):
                self.assertEqual(beweglich(lager(*faelle)), bewegung)

    def test_unabhaengig_von_der_groesse(self):
        """Dieselbe Lagerung, tausendmal grösser oder kleiner, bewegt sich gleich."""
        for faktor in (1e-3, 1e3):
            with self.subTest(faktor=faktor):
                self.assertEqual(beweglich(lager(((0, 0), "y"), ((6 * faktor, 0), "y"))), "in x verschieben")
                self.assertEqual(beweglich(lager(((0, 0), "xy"), ((6 * faktor, 0), "y"))), "")


class TestRechnung(unittest.TestCase):
    """Der Befund im Rechenwerk und die Herleitung, solange noch kein Fachwerk gesucht ist."""

    def gerechnet(self, p: Projekt):
        aufbau = p.aufbauen()
        loesung = aufbau.werk.loese(*aufbau.ziele_von("f1"))
        return loesung, loesung.befunde[aufbau.fachwerkmodelle["f1"].rechnung.id]

    def test_bereit_sagt_dass_noch_kein_fachwerk_gesucht_ist(self):
        loesung, befund = self.gerechnet(wandscheibe())
        self.assertTrue(befund.bereit)
        self.assertEqual((befund.meldungen, befund.stand), ([], "keines"))
        self.assertEqual([(m.text, m.fehler, m.unfertig) for m in befund.zum_fachwerk],
                         [(NOCH_KEINES, False, False)])
        self.assertEqual(len(befund.abdruck), 16)
        hinweise = [b.text for b in loesung.protokoll.alle_bloecke() if isinstance(b, HinweisBlock)]
        self.assertIn(NOCH_KEINES, hinweise)

    def test_herleitung_mit_summe_der_lasten(self):
        loesung, _ = self.gerechnet(wandscheibe())
        tabellen = {b.titel: b for b in loesung.protokoll.alle_bloecke() if isinstance(b, TabellenBlock)}
        self.assertEqual(sorted(tabellen), ["Lager", "Lasten", "Löcher", "Scheiben"])
        # Ohne gefundenes Fachwerk keine Tabelle der Stäbe -- die Zahlen des Verfahrens stehen da.
        zeilen = [[z.latex if isinstance(z, Mathe) else z for z in zeile] for zeile in tabellen["Lasten"].zeilen]
        self.assertEqual(zeilen[-1], ["Summe", "", "50.0", "500.0"])
        self.assertEqual(tabellen["Scheiben"].zeilen[0][2].latex, "18.00")
        self.assertEqual([z[2] for z in tabellen["Lager"].zeilen], ["x und y", "nur y"])

    def test_unfertig_ohne_hinweis_auf_die_suche(self):
        p = wandscheibe()
        p.fachwerkmodelle[0].lasten.clear()
        loesung, befund = self.gerechnet(p)
        self.assertFalse(befund.bereit)
        self.assertEqual((befund.zum_fachwerk, befund.stand, befund.abdruck), ([], "", ""))

    def test_falsches_steht_rot_im_bericht(self):
        p = wandscheibe()
        p.fachwerkmodelle[0].last((3, 5), F_v=10)
        loesung, _ = self.gerechnet(p)
        warnungen = [b.text for b in loesung.protokoll.alle_bloecke()
                     if isinstance(b, HinweisBlock) and b.art is HinweisArt.WARNUNG]
        self.assertEqual(warnungen, ["Die Last F3 liegt bei (3.00, 5.00) neben der Scheibe."])


class TestZeichnung(unittest.TestCase):
    """Was die Oberfläche beim Zeichnen vom Kern bekommt (Anfrage `fachwerk_zeichnung`)."""

    def test_bereit(self):
        antwort = zeichnung(wandscheibe())
        self.assertEqual(antwort.status, 200)
        uebersicht = antwort.daten["uebersicht"]
        self.assertEqual(len(uebersicht.pop("abdruck")), 16)
        self.assertEqual(uebersicht, {
            "bereit": True, "verfahren": "ground_structure", "stand": "keines", "fachwerk": None,
            "form": None, "meldungen": [], "zum_fachwerk": [
                {"text": NOCH_KEINES, "elemente": [], "fehler": False, "unfertig": False}]})

    def test_unfertig(self):
        p = Projekt(name="Fachwerk")
        p.fachwerkmodell("Leer")
        uebersicht = zeichnung(p).daten["uebersicht"]
        self.assertFalse(uebersicht["bereit"])
        self.assertEqual([m["text"] for m in uebersicht["meldungen"]], [
            "Noch keine Scheibe – ihren Umriss zeichnen.",
            "Noch kein Lager – die Scheibe an einem Punkt halten.",
            "Keine Last → kein Fachwerk."])

    def test_nur_fuer_ein_fachwerkmodell(self):
        p = wandscheibe()
        decke = p.decke("Decke")
        antwort = zeichnung(p, decke.kennung)
        self.assertEqual(antwort.status, 400)
        self.assertIn(f"'{decke.kennung}' ist kein Fachwerkmodell.", str(antwort.daten))

    def test_das_beispiel_rechnet(self):
        p = beispiele.jeder_nachweis()
        f = next(x for x in p.fachwerkmodelle if x.name == "Wandscheibe mit Türe")
        self.assertTrue(zeichnung(p, f.kennung).daten["uebersicht"]["bereit"])


class TestKatalog(unittest.TestCase):
    def test_stellungen_und_vorsilben(self):
        k = katalog()
        self.assertEqual([h["wert"] for h in k["halt"]], ["xy", "x", "y"])
        self.assertTrue(all(h["beschriftung"] and h["titel"] for h in k["halt"]))
        self.assertEqual(k["vorsilben"], {"scheiben": "S", "loecher": "L", "lager": "A", "lasten": "F"})


if __name__ == "__main__":
    unittest.main()
