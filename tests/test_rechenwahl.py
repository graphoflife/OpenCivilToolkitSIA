"""
Die Rechenwahl: welche Gesetze zu Kriechzahl, Wertesatz und Rechenart gehören.

Geprüft wird die eine Stelle, an der das entschieden wird
(:mod:`opencivil.nachweis.rechenwahl`) -- dass jede Rechenart das tut, was ihr
Name sagt. Ob die Nachweise sie richtig benutzen, prüfen deren eigene Tests
und die Altdatei, die vor dem Umbau festgehalten wurde.
"""

import unittest
from types import SimpleNamespace

from opencivil.core.berechnung import Eingabebezug
from opencivil.nachweis.querschnittsloeser import Stahllage, je_seite
from opencivil.querschnitt.gesetzwahl import (
    Rechenart, Rechenarten, Rechenwahl, Werkstoffsatz, Wertesaetze, arten_text,
)
from opencivil.nachweis.rechenwahl import (
    FASERARTEN, RECHENARTEN, VERFORMUNGSARTEN, Betonkennwerte, bezuege_vereinen, gesetze,
)
from opencivil.querschnitt.werkstoffgesetz import (
    BetonUngerissen, Spannungsblock, Stahlgesetz, StahlNurZug,
)
from opencivil.querschnitt.zugseite import Zugseite

W = Betonkennwerte(f_c=20e6, E_c=33.6e9, eps_c1d=0.002, eps_c2d=0.0035)
STAHL = Stahlgesetz(E_s=200e9, f_yd=435e6, f_yd_druck=435e6, eps_ud=0.045)

LAGEN = [Stahllage(a_s=1696e-6, z=0.249, stahl=STAHL, nummer=2, seite=Zugseite.UNTEN),
         Stahllage(a_s=754e-6, z=0.243, stahl=STAHL, nummer=2, seite=Zugseite.UNTEN),
         Stahllage(a_s=754e-6, z=0.048, stahl=STAHL, nummer=3, seite=Zugseite.OBEN)]


class TestRechenarten(unittest.TestCase):
    def test_die_listen(self):
        self.assertEqual([a.value for a in RECHENARTEN], ["handrechnung", "block", "parabel"])
        self.assertEqual([a.value for a in FASERARTEN], ["block", "parabel"])
        # «elastisch» gibt es seit 2026-11-25 nicht mehr (Benutzer).
        self.assertEqual([a.value for a in Rechenart], ["handrechnung", "block", "parabel"])
        self.assertEqual(Rechenwahl().index, "Rd")
        self.assertEqual(Rechenwahl(saetze=Wertesaetze.alle(Werkstoffsatz.CHARAKTERISTISCH)).index,
                         "Rk")

    def test_aus_den_feldern_einer_beschreibung(self):
        """
        Die Felder halten schon die Wahlen -- die Rechenwahl entsteht ohne
        Umwandlung, je Material. Ein Material ohne eigene Wahl rechnet mit der
        Vorgabe seines Kapitels.
        """
        from opencivil.projekt import Projekt, RechenwahlEintrag
        stoffe = Projekt.beispiel().aufbauen().baustoffe
        eintrag = RechenwahlEintrag(kriechzahl=1.5, werkstoffsaetze={"b1": "charakteristisch"},
                                    rechenarten={"b1": "parabel"})
        wahl = eintrag.wahl(stoffe)
        self.assertEqual((wahl.kriechzahl, wahl.art), (1.5, Rechenart.PARABEL))
        self.assertIs(wahl.satz(stoffe["b1"]), Werkstoffsatz.CHARAKTERISTISCH)
        self.assertIs(wahl.satz(stoffe["s1"]), Werkstoffsatz.BEMESSUNG)
        self.assertEqual(wahl.index, "R")
        # Alle gleich: dieselbe Wahl wie ein Satz für alle -- sonst rechnete
        # ein Kapitel seine eigene Linie neben der gleichen eines anderen.
        eintrag.werkstoffsaetze = {"b1": "charakteristisch", "s1": "charakteristisch"}
        self.assertEqual(eintrag.wahl(stoffe), Rechenwahl(
            1.5, Wertesaetze.alle(Werkstoffsatz.CHARAKTERISTISCH),
            Rechenarten.alle(Rechenart.PARABEL)))


class TestWertesaetze(unittest.TestCase):
    """Je Baustoff sein Satz -- und wie eine Wahl heisst, die beide mischt."""

    class Stoff:
        def __init__(self, id):
            self.id = id

    BETON, STAHL, ANDERER = Stoff("C30/37"), Stoff("B500B"), Stoff("S355")

    def test_ein_satz_fuer_alle(self):
        for satz in Werkstoffsatz:
            with self.subTest(satz=satz.value):
                alle = Wertesaetze.alle(satz)
                self.assertEqual(Wertesaetze.je({"C30/37": satz, "B500B": satz}), alle)
                self.assertIs(alle.einheitlich, satz)
                self.assertIs(alle.von(self.ANDERER), satz)
                self.assertEqual((alle.index, alle.kuerzel), (satz.widerstandsindex, satz.kuerzel))
        # Ohne Baustoff gilt die Vorgabe.
        self.assertEqual(Wertesaetze.je({}, Werkstoffsatz.CHARAKTERISTISCH),
                         Wertesaetze.alle(Werkstoffsatz.CHARAKTERISTISCH))

    def test_gemischt(self):
        """Weder Rd noch Rk: ein Widerstand mit gemischten Werten heisst R."""
        gemischt = Wertesaetze.je({"C30/37": Werkstoffsatz.CHARAKTERISTISCH,
                                   "B500B": Werkstoffsatz.BEMESSUNG})
        self.assertIs(gemischt.von(self.BETON), Werkstoffsatz.CHARAKTERISTISCH)
        self.assertIs(gemischt.von(self.STAHL), Werkstoffsatz.BEMESSUNG)
        self.assertIs(gemischt.von(self.ANDERER), Werkstoffsatz.BEMESSUNG)
        self.assertIsNone(gemischt.einheitlich)
        self.assertEqual((gemischt.index, gemischt.kuerzel, gemischt.kurz, gemischt.beschriftung),
                         ("R", "", "gemischt", "gemischte Werte"))
        # Die Reihenfolge der Eingabe zählt nicht: dieselbe Wahl, ein Schlüssel.
        self.assertEqual(gemischt, Wertesaetze.je({"B500B": Werkstoffsatz.BEMESSUNG,
                                                   "C30/37": Werkstoffsatz.CHARAKTERISTISCH}))
        self.assertEqual(Rechenwahl(saetze=gemischt).beschriftung(),
                         "Handrechnung, gemischt")

    def test_ohne_ebene_nennt_die_wahl(self):
        """Verfehlt die Suche ihre Ebene, steht da, womit -- und was hilft."""
        self.assertEqual(Rechenart.BLOCK.ohne_ebene,
                         "Mit der 0.85·x-Vereinfachung gibt es zu dieser Einwirkung keine "
                         "Dehnungsebene – präzise rechnen.")
        self.assertEqual(Rechenart.HANDRECHNUNG.ohne_ebene,
                         "Mit der Handrechnung gibt es zu dieser Einwirkung keine "
                         "Dehnungsebene – präzise rechnen.")
        # Ohne Sprung gibt es die Ebene; verfehlt die Suche sie trotzdem, steht
        # kein Rat da, der nicht hilft.
        self.assertNotIn("präzise rechnen", Rechenart.PARABEL.ohne_ebene)

    def test_nur_praezise_haengt_an_der_kriechzahl(self):
        for art in RECHENARTEN:
            with self.subTest(art=art.value):
                weich = gesetze(Rechenwahl(2.0, arten=Rechenarten.alle(art)), W).beton(-0.0005)
                steif = gesetze(Rechenwahl(0.0, arten=Rechenarten.alle(art)), W).beton(-0.0005)
                self.assertEqual(weich != steif, art.mit_kriechzahl)


class TestRechenartJeBeton(unittest.TestCase):
    """
    Je Beton seine Rechenart (Benutzer, 2026-11-25), wie je Material sein
    Wertesatz. Ein Stahl hat keine: er rechnet in jeder Art mit seinem Gesetz.
    """

    C30 = SimpleNamespace(id="b1", name="C30/37")
    C50 = SimpleNamespace(id="b2", name="C50/60")

    def test_alle_gleich_ist_eine_fuer_alle(self):
        """Sonst rechneten zwei gleiche Wahlen zwei Linien."""
        arten = Rechenarten.je({"b1": Rechenart.BLOCK, "b2": Rechenart.BLOCK})
        self.assertEqual(arten, Rechenarten.alle(Rechenart.BLOCK))
        self.assertIs(Rechenwahl(arten=arten).art, Rechenart.BLOCK)
        self.assertEqual(Rechenarten.je({}), Rechenarten.alle(Rechenart.HANDRECHNUNG))

    def test_verschieden(self):
        wahl = Rechenwahl(kriechzahl=2.0, arten=Rechenarten.je(
            {"b1": Rechenart.BLOCK, "b2": Rechenart.PARABEL}))
        self.assertIs(wahl.art_von(self.C30), Rechenart.BLOCK)
        self.assertIs(wahl.art_von(self.C50), Rechenart.PARABEL)
        self.assertIsNone(wahl.arten.einheitlich)
        with self.assertRaises(ValueError):
            wahl.art
        # Einer haengt am Modul, einer rechnet als Block -- und wo die Ebene
        # fehlt, hilft es, praezise zu rechnen.
        self.assertTrue(wahl.arten.mit_kriechzahl)
        self.assertTrue(wahl.arten.mit_block)
        self.assertEqual(wahl.arten.ohne_ebene, Rechenart.BLOCK.ohne_ebene)
        betone = (self.C30, self.C50)
        self.assertEqual(arten_text(wahl, betone), "C30/37 0.85·x, C50/60 präzise")
        self.assertEqual(wahl.beschriftung(betone),
                         "C30/37 0.85·x, C50/60 präzise, φ = 2, Bemessung")

    def test_eine_linie_je_wahl_aller_betone(self):
        block = Rechenwahl(arten=Rechenarten.je({"b1": Rechenart.BLOCK, "b2": Rechenart.PARABEL}))
        anders = Rechenwahl(arten=Rechenarten.je({"b1": Rechenart.PARABEL, "b2": Rechenart.BLOCK}))
        self.assertFalse(block.gleiche_linie(anders))
        self.assertTrue(block.gleiche_linie(Rechenwahl(arten=Rechenarten.je(
            {"b2": Rechenart.PARABEL, "b1": Rechenart.BLOCK}))))

    def test_aus_den_feldern_nur_die_betone(self):
        """Die Wahl eines Stahls in ``rechenarten`` zaehlt nicht -- er hat keine."""
        from opencivil.projekt import Projekt, RechenwahlEintrag
        stoffe = Projekt.beispiel().aufbauen().baustoffe
        wahl = RechenwahlEintrag(rechenarten={"b1": "block", "s1": "parabel"}).wahl(stoffe)
        self.assertEqual(wahl.arten, Rechenarten.alle(Rechenart.BLOCK))


class TestGesetze(unittest.TestCase):
    def test_handrechnung_block_stahl_nur_auf_zug_je_seite_eine_lage(self):
        g = gesetze(Rechenwahl(arten=Rechenarten.alle(Rechenart.HANDRECHNUNG)), W)
        self.assertIsInstance(g.beton, Spannungsblock)
        self.assertEqual(g.stahl(STAHL)(-0.01), 0.0)
        self.assertAlmostEqual(g.stahl(STAHL)(0.01), 435e6)
        self.assertIsNotNone(g.beton.mittel, "der Block springt: über jede Faser gemittelt")
        self.assertFalse(g.verdraengt)
        lagen = g.lagen(LAGEN)
        self.assertEqual(len(lagen), 2)
        self.assertAlmostEqual(lagen[0].a_s, 2450e-6)
        self.assertAlmostEqual(lagen[0].z, (1696 * 0.249 + 754 * 0.243) / 2450)

    def test_block_genau_mit_druckstahl(self):
        g = gesetze(Rechenwahl(arten=Rechenarten.alle(Rechenart.BLOCK)), W)
        self.assertIsInstance(g.beton, Spannungsblock)
        self.assertAlmostEqual(g.stahl(STAHL)(-0.01), -435e6)
        self.assertIsNotNone(g.beton.mittel, "der Block springt: über jede Faser gemittelt")
        self.assertTrue(g.verdraengt)
        self.assertEqual(g.lagen(LAGEN), LAGEN)

    def test_parabel(self):
        parabel = gesetze(Rechenwahl(arten=Rechenarten.alle(Rechenart.PARABEL)), W)
        self.assertIsNone(parabel.beton.mittel)
        self.assertAlmostEqual(parabel.beton(-0.002) / 1e6, -20.0)

    def test_der_ungerissene_zustand_ersetzt_nur_den_beton(self):
        wahl = Rechenwahl(2.0, arten=Rechenarten.alle(Rechenart.HANDRECHNUNG))
        g = gesetze(wahl, W, ungerissen=True)
        self.assertEqual(g.beton, BetonUngerissen(E_c=33.6e9 / 3))
        loeser = g.loeser(h=0.3, b=1.0, lagen=LAGEN)
        self.assertEqual(len(loeser.lagen), 2)
        # Der Stahl bleibt der der Wahl: nur auf Zug.
        self.assertEqual([s.gesetz(-0.01) for s in loeser.querschnitt.staebe], [0.0, 0.0])


class TestStahl(unittest.TestCase):
    def test_eigenes_druckplateau(self):
        gesetz = Stahlgesetz(E_s=200e9, f_yd=435e6, f_yd_druck=400e6, eps_ud=0.045)
        self.assertAlmostEqual(gesetz(0.01), 435e6)
        self.assertAlmostEqual(gesetz(-0.01), -400e6)
        self.assertEqual(gesetz(0.05), 0.0)

    def test_gleiche_plateaus_rechnen_wie_getrennte(self):
        """
        Bei den Normsorten sind beide gleich -- dann rechnet das Gesetz mit dem
        Betrag, Bit für Bit wie Zug und Druck getrennt.
        """
        gesetz = Stahlgesetz(E_s=200e9, f_yd=435e6, f_yd_druck=435e6, eps_ud=0.045)
        for eps in (-0.05, -0.003, -1e-4, -0.0, 0.0, 1e-4, 0.003, 0.05):
            getrennt = (0.0 if abs(eps) > 0.045 else
                        min(eps * 200e9, 435e6) if eps >= 0.0 else -min(-eps * 200e9, 435e6))
            self.assertEqual(gesetz(eps), getrennt)

    def test_nur_zug(self):
        gesetz = StahlNurZug(E_s=200e9, f_yd=435e6, f_yd_druck=435e6, eps_ud=0.045)
        self.assertEqual(gesetz(-0.001), 0.0)
        self.assertAlmostEqual(gesetz(0.001), 200e6)
        self.assertAlmostEqual(gesetz(0.01), 435e6)
        self.assertEqual(gesetz(0.05), 0.0)

    def test_je_seite_nur_mit_bekannter_seite(self):
        """
        Die Seite sagt die Lage, nicht die Tiefe -- ohne ``seite`` ist
        es ein Fehler. Bis 2026-11-10 entschied dann die Tiefe gegen h/2,
        die Handrechnung aber nie.
        """
        with self.assertRaisesRegex(ValueError, "ihre Seite"):
            je_seite([Stahllage(a_s=1e-3, z=0.25, stahl=STAHL),
                      Stahllage(a_s=5e-4, z=0.05, stahl=STAHL)])

    def test_je_seite_mit_namen_und_teilen(self):
        seiten = je_seite(LAGEN)
        self.assertEqual(list(seiten), [Zugseite.UNTEN, Zugseite.OBEN])
        self.assertEqual(seiten[Zugseite.UNTEN].teile, tuple(LAGEN[:2]))
        self.assertEqual(seiten[Zugseite.OBEN].teile, (LAGEN[2],))


class TestBezuege(unittest.TestCase):
    def test_dieselbe_eingabe_einmal(self):
        a = [Eingabebezug("E_s", "stahl.s1.E_s"), Eingabebezug("h", "q.h")]
        b = [Eingabebezug("E_s", "stahl.s1.E_s"), Eingabebezug("f_yk", "stahl.s1.f_yk")]
        self.assertEqual([x.name for x in bezuege_vereinen(a, b)], ["E_s", "h", "f_yk"])

    def test_ein_name_mit_zwei_zahlen_ist_ein_fehler(self):
        with self.assertRaises(ValueError):
            bezuege_vereinen([Eingabebezug("E_s", "stahl.s1.E_s")],
                             [Eingabebezug("E_s", "stahl.s2.E_s")])


class TestJederNachweis(unittest.TestCase):
    """
    Im Prüfprojekt «Jeder Nachweis» kommt jede Rechenart und jeder
    Wertesatz einmal laut vor -- so steht jede Herleitung im Schnappschuss
    und in der Formelsammlung.
    """

    @classmethod
    def setUpClass(cls):
        from opencivil.projekt import Projekt
        cls.projekt = Projekt.jeder_nachweis()

    def test_tragsicherheit_jede_rechenart_und_beide_werte(self):
        aufbau = self.projekt.aufbauen()
        wahlen = [n.wahl for n in aufbau.feld("nachweise").values()]
        self.assertEqual({w.art for w in wahlen}, set(RECHENARTEN))
        # Beide Sätze für alle, und einmal gemischt.
        self.assertEqual({w.saetze.einheitlich for w in wahlen}, {*Werkstoffsatz, None})

    def test_stahlspannung_jede_rechenart(self):
        arten = {liste.wahl.von("rechenarten", q.beton) for q in self.projekt.querschnitte
                 for liste in (q.haeufig, q.quasistaendig) if liste.faelle}
        self.assertEqual(arten, set(RECHENARTEN))

    def test_knicken_mit_geteilter_und_eigener_linie(self):
        aufbau = self.projekt.aufbauen()
        self.assertEqual({k.linienquelle.eigen for k in aufbau.feld("knicken").values()}, {True, False})
        # Die Verformung kennt nur eine Rechenart, darum beide Wertesaetze.
        self.assertEqual({k.verformung.art for k in aufbau.feld("knicken").values()},
                         set(VERFORMUNGSARTEN))
        self.assertEqual({k.verformung.saetze.einheitlich for k in aufbau.feld("knicken").values()},
                         set(Werkstoffsatz))


if __name__ == "__main__":
    unittest.main()
