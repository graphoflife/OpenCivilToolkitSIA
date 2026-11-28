"""
Die Wand aus Mauerwerk, Schritt 14a: das Material nach SIA 266:2015, was die
Wand davon liest und nach ihrer Wahl umrechnet, ihre Zeichnung mit Öffnungen,
Stürzen und Pfeilern, was ihr fehlt oder an ihr nicht stimmt -- und was die
Oberfläche beim Zeichnen davon bekommt.
"""

import unittest

from opencivil.core.einheiten import N_PRO_MM2
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.mauerwerk import MAUERWERKSSORTEN
from opencivil.mauerwerk.kennwerte import wandwerte
from opencivil.mauerwerk.modell import Oeffnung, Umriss, Wand, pfeiler
from opencivil.mauerwerk.pruefen import dickenhinweis, pruefen
from opencivil.projekt import Projekt
from opencivil.projekt.aufbau.kern import kennwert
from opencivil.projekt.mauerwerk import rechteck
from opencivil.web import dienst

#: SIA 266:2015, Tabelle 7 (S. 22), je Sorte: f_xd, f_yd, f_yd vollfugig in
#: N/mm², E_xd und G_d in kN/mm² -- wie gedruckt.
TABELLE_7 = {
    "MB": (3.5, 1.1, 1.6, 3.5, 1.4),
    "MBL": (0.9, 0.3, 0.5, 0.9, 0.4),
    "MC": (3.5, 1.8, 2.6, 3.5, 1.4),
    "MCL": (0.9, 0.5, 0.7, 0.9, 0.4),
    "MK": (3.5, 1.1, 1.6, 3.5, 1.4),
    "MP": (1.5, 0.5, 0.7, 1.5, 0.6),
    "MPL": (0.9, 0.3, 0.4, 0.9, 0.4),
}

#: Die Wand des Beispiels, 6 × 2.7 m.
WAND = Umriss("W1", tuple(rechteck(0, 0, 6, 2.7)))


def oeffnung(name, x0, y0, x1, y1, **felder):
    """Eine rechteckige Öffnung, in m -- mit dem Sturz der Vorgabe: 200 mm hoch, a = 150 mm."""
    return Oeffnung(name, tuple(rechteck(x0, y0, x1, y1)), **felder)


def meldungen(*oeffnungen, umrisse=(WAND,)):
    """Je Meldung der Zeichnung ihr Text und ob sie rot ist."""
    return [(m.text, m.fehler) for m in pruefen(Wand(umrisse=umrisse, oeffnungen=oeffnungen))]


def material(sorte):
    """Die Werte eines Standardmauerwerks, wie das Projekt sie rechnet -- in N/mm², ohne Einheit."""
    p = Projekt(name="Probe")
    m = p.mauerwerk(sorte)
    aufbau = p.aufbauen()
    stoff = aufbau.baustoffe[m.kennung]
    werte = {k: kennwert(aufbau, stoff, k).in_einheit(N_PRO_MM2)
             for k in ("f_xk", "f_xd", "f_yd", "f_yd_v", "E_xd", "G_d")}
    return {**werte, **{k: kennwert(aufbau, stoff, k).zahl for k in ("gamma_M", "mu_d")}}


def beispielwand(p, **felder):
    """
    Die Wand des Beispiels: Kalksandstein, Verband, vollfugig, eine Türe und
    zwei Fenster, das mittlere mit vorfabriziertem Sturz.
    """
    w = p.wand("Wand", **{"t": 175, "mauerung": "verband", "stossfugen": "vollfugig", **felder})
    w.wand(rechteck(0, 0, 6, 2.7))
    w.oeffnung(rechteck(0.8, 0, 1.8, 2.1))
    w.oeffnung(rechteck(2.8, 0.9, 4.0, 2.1), sturz="vorfabriziert", h_St=250)
    w.oeffnung(rechteck(4.9, 0.9, 5.5, 2.1))
    return w


def befund(p, w):
    """Was die Rechnung der Wand ``w`` findet."""
    aufbau = p.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.materialziele(), *aufbau.ziele_von(w.kennung))
    return loesung.befunde[aufbau.mauerwerke[w.kennung].rechnung.id]


def zeichnung(p, w):
    """Was die Oberfläche unter die Zeichnung der Wand legt."""
    antwort = dienst.bearbeite("mauerwerk_zeichnung",
                               {"projekt": p.als_dict(), "kennung": w.kennung})
    assert antwort.status == 200, antwort.daten
    return antwort.daten["uebersicht"]


class TestMaterial(unittest.TestCase):

    def test_die_sorten_in_der_folge_der_tabelle(self):
        self.assertEqual(list(MAUERWERKSSORTEN), list(TABELLE_7))

    def test_die_bemessungswerte_der_tabelle_7(self):
        """Gl. (3) mit γ_M = 2.0, E_xk = 1000 f_xk und G_k = 0.4 E_xk ergeben die Tabelle."""
        for sorte, (f_xd, f_yd, f_yd_v, E_xd, G_d) in TABELLE_7.items():
            with self.subTest(sorte=sorte):
                w = material(sorte)
                self.assertEqual((w["gamma_M"], w["mu_d"]), (2.0, 0.6))
                self.assertAlmostEqual(w["f_xd"], w["f_xk"] / 2.0)
                self.assertAlmostEqual(w["f_xd"], f_xd)
                self.assertAlmostEqual(w["f_yd"], f_yd)
                self.assertAlmostEqual(w["f_yd_v"], f_yd_v)
                self.assertAlmostEqual(w["E_xd"] / 1000.0, E_xd)
                # Die Tabelle rundet auf eine Stelle: MBL hat G_d = 0.36 kN/mm², gedruckt 0.4.
                self.assertAlmostEqual(round(w["G_d"] / 1000.0, 1), G_d)

    def test_die_art(self):
        art = MATERIALARTEN["mauerwerk"]
        self.assertEqual((art.neu, art.eigen, art.einen, art.keinen, art.kennung, art.eigene),
                         ("Neues Mauerwerk", "Eigenes Mauerwerk", "ein Mauerwerk",
                          "kein Mauerwerk", "mw", "MW"))
        self.assertEqual((art.aus_norm, art.mit_satz), (True, False))


class TestWandwerte(unittest.TestCase):
    """Wie die Wahl der Wand die Werte ihres Mauerwerks ändert (SIA 266:2015, 4.2.1.1)."""

    MK = {"f_xd": 3.5, "f_yd": 1.1, "f_yd_v": 1.6, "E_xd": 3500.0, "G_d": 1400.0, "mu_d": 0.6}

    def test_einsteinmauerwerk_wie_die_tabelle(self):
        w = wandwerte(self.MK, verband=False, vollfugig=False)
        self.assertEqual((w.faktor, w.f_xd, w.f_yd, w.E_xd, w.G_d, w.mu_d),
                         (1.0, 3.5, 1.1, 3500.0, 1400.0, 0.6))

    def test_vollfugig_das_f_yd_dieser_zeile(self):
        self.assertEqual(wandwerte(self.MK, verband=False, vollfugig=True).f_yd, 1.6)

    def test_im_verband_alles_mal_085_nur_mu_d_nicht(self):
        w = wandwerte(self.MK, verband=True, vollfugig=True)
        self.assertEqual(w.faktor, 0.85)
        for ist, soll in ((w.f_xd, 2.975), (w.f_yd, 1.36), (w.E_xd, 2975.0), (w.G_d, 1190.0)):
            self.assertAlmostEqual(ist, soll)
        self.assertEqual(w.mu_d, 0.6)


class TestPfeiler(unittest.TestCase):

    @staticmethod
    def pfeiler(*oeffnungen):
        """Je Pfeiler Name, Ränder in m und die Öffnungen links und rechts."""
        return [(e.name, round(e.x0, 6), round(e.x1, 6), e.links, e.rechts)
                for e in pfeiler(WAND.rechteck, oeffnungen)]

    def test_die_wand_des_beispiels(self):
        """Eine Türe 0.8–1.8 m, Fenster 2.8–4.0 und 4.9–5.5 m: vier Pfeiler."""
        self.assertEqual(self.pfeiler(oeffnung("O1", 0.8, 0, 1.8, 2.1),
                                      oeffnung("O2", 2.8, 0.9, 4.0, 2.1),
                                      oeffnung("O3", 4.9, 0.9, 5.5, 2.1)),
                         [("P1", 0.0, 0.8, (), ("O1",)), ("P2", 1.8, 2.8, ("O1",), ("O2",)),
                          ("P3", 4.0, 4.9, ("O2",), ("O3",)), ("P4", 5.5, 6.0, ("O3",), ())])

    def test_ein_fenster_ueber_einer_tuere_ist_eine_luecke(self):
        """Sie überdecken sich in der Breite: dazwischen steht kein Pfeiler."""
        self.assertEqual(self.pfeiler(oeffnung("O1", 1.0, 0, 2.0, 2.0),
                                      oeffnung("O2", 1.5, 2.3, 2.5, 2.5)),
                         [("P1", 0.0, 1.0, (), ("O1",)), ("P2", 2.5, 6.0, ("O2",), ())])

    def test_ohne_oeffnung_ist_die_ganze_wand_ein_pfeiler(self):
        self.assertEqual(self.pfeiler(), [("P1", 0.0, 6.0, (), ())])

    def test_eine_oeffnung_am_ende_der_wand(self):
        self.assertEqual(self.pfeiler(oeffnung("O1", 5.0, 0, 6.0, 2.1)),
                         [("P1", 0.0, 5.0, (), ("O1",))])


class TestPruefen(unittest.TestCase):
    """Was fehlt, steht grau; was falsch ist, rot -- je mit den Namen der Teile."""

    def test_eine_richtige_wand_ohne_meldung(self):
        self.assertEqual(meldungen(oeffnung("O1", 0.8, 0, 1.8, 2.1)), [])

    def test_ohne_wand_fehlt_sie_nur(self):
        self.assertEqual([(m.text, m.fehler, m.haelt_an) for m in pruefen(Wand())],
                         [("Noch keine Wand – ihren Umriss mit dem Werkzeug «Wand» zeichnen.",
                           False, True)])

    def test_eine_schraege_krone_rechnet_das_werkzeug_noch_nicht(self):
        giebel = Umriss("W1", ((0, 0), (6, 0), (6, 2.7), (0, 3.2)))
        self.assertEqual(meldungen(umrisse=(giebel,)),
                         [("Die Wand W1 ist kein Rechteck mit waagrechten und senkrechten Seiten "
                           "– eine schräge Krone, etwa die eines Giebels, rechnet das Werkzeug "
                           "noch nicht.", True)])

    def test_eine_schraege_oeffnung(self):
        schraeg = Oeffnung("O1", ((1, 0), (2, 0), (2, 2), (1, 1.8)))
        self.assertEqual(meldungen(schraeg),
                         [("Die Öffnung O1 ist kein Rechteck mit waagrechten und senkrechten "
                           "Seiten.", True)])

    def test_ein_umriss_zu_viel(self):
        zweite = Umriss("W2", tuple(rechteck(7, 0, 9, 2.7)))
        self.assertEqual(meldungen(umrisse=(WAND, zweite)),
                         [("Eine Wand hat einen Umriss: W2 ist einer zu viel.", True)])

    def test_ein_umriss_der_sich_kreuzt(self):
        kreuz = Umriss("W1", ((0, 0), (6, 2.7), (6, 0), (0, 2.7)))
        [m] = pruefen(Wand(umrisse=(kreuz,)))
        self.assertEqual((m.fehler, m.elemente), (True, ("W1",)))

    def test_eine_oeffnung_ueber_den_rand(self):
        self.assertEqual(meldungen(oeffnung("O1", 5.5, 0.9, 6.5, 2.1)),
                         [("Die Öffnung O1 reicht über die Wand hinaus.", True)])

    def test_zwei_oeffnungen_ueberschneiden_sich(self):
        self.assertEqual(meldungen(oeffnung("O1", 0.8, 0, 1.8, 2.1),
                                   oeffnung("O2", 1.5, 0.9, 2.5, 2.1)),
                         [("Die Öffnungen O1 und O2 überschneiden sich.", True)])

    def test_ein_sturz_ueber_den_rand(self):
        """Der Sturz liegt 150 mm auf jeder Seite auf und ist 200 mm hoch."""
        self.assertEqual(meldungen(oeffnung("O1", 0.1, 0, 1.0, 2.1)),
                         [("Der Sturz über O1 reicht über die Wand hinaus: links.", True)])
        self.assertEqual(meldungen(oeffnung("O1", 0.05, 0.9, 1.0, 2.6)),
                         [("Der Sturz über O1 reicht über die Wand hinaus: oben und links.",
                           True)])

    def test_ein_sturz_in_eine_andere_oeffnung(self):
        self.assertEqual(meldungen(oeffnung("O1", 1.0, 0, 2.0, 2.0),
                                   oeffnung("O2", 1.0, 2.1, 2.0, 2.5)),
                         [("Der Sturz über O1 reicht in die Öffnung O2.", True)])

    def test_zwei_stuerze_ueberschneiden_sich(self):
        self.assertEqual(meldungen(oeffnung("O1", 0.5, 0, 1.5, 2.1),
                                   oeffnung("O2", 1.7, 0, 2.7, 2.1)),
                         [("Die Stürze über O1 und O2 überschneiden sich.", True)])


class TestMauerwerkUndDicke(unittest.TestCase):
    """Was zu Mauerwerk und Dicke zu sagen ist -- in der Maske bei ihren Feldern."""

    def test_deklariertes_mauerwerk_unter_den_mindestwerten(self):
        """SIA 266:2015, 3.1.3.1 -- rot, die Pfeiler stehen trotzdem da."""
        p = Projekt(name="Probe")
        mw = p.eigenes_mauerwerk("MB")
        mw.abweichungen["f_xk"] = 1.5
        w = p.wand("Wand", material=mw.kennung)
        w.wand(rechteck(0, 0, 6, 2.7))
        b = befund(p, w)
        self.assertEqual([(m.text, m.fehler) for m in b.zum_mauerwerk],
                         [("Das Mauerwerk «MW1» hat f_xk = 1.5 N/mm² – SIA 266:2015, 3.1.3.1 "
                           "verlangt mindestens 1.8 N/mm².", True),
                          ("Das Mauerwerk «MW1» hat E_xk = 1500 N/mm² – SIA 266:2015, 3.1.3.1 "
                           "verlangt mindestens 1800 N/mm².", True)])
        self.assertFalse(b.bereit)
        self.assertEqual([e.name for e in b.pfeiler], ["P1"])

    def test_eine_uebliche_dicke_ohne_hinweis(self):
        self.assertIsNone(dickenhinweis("MK", 175))

    def test_eine_unuebliche_dicke_grau(self):
        m = dickenhinweis("MK", 180)
        self.assertEqual((m.text, m.fehler, m.haelt_an),
                         ("Kalksandsteine sind meist 100, 120, 150, 175, 200 oder 250 mm dick – "
                          "eine Wand von 180 mm ist unüblich.", False, False))

    def test_die_unuebliche_dicke_haelt_die_wand_nicht_an(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        b = befund(p, beispielwand(p, t=180))
        self.assertTrue(b.bereit)
        self.assertEqual([m.fehler for m in b.zum_mauerwerk], [False])
        self.assertAlmostEqual(b.t, 0.18)


class TestDieZeichnung(unittest.TestCase):
    """Die Anfrage `mauerwerk_zeichnung`: was die Oberfläche unter die Teile legt."""

    def test_die_wand_des_beispiels(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        u = zeichnung(p, beispielwand(p))
        self.assertTrue(u["bereit"])
        self.assertEqual(u["meldungen"], [])
        self.assertEqual([(e["name"], round(e["b"], 6)) for e in u["pfeiler"]],
                         [("P1", 0.8), ("P2", 1.0), ("P3", 0.9), ("P4", 0.5)])
        self.assertEqual([(s["oeffnung"], s["sturz"], round(s["x0"], 6), round(s["y1"], 6))
                          for s in u["stuerze"]],
                         [("O1", "beton", 0.65, 2.3), ("O2", "vorfabriziert", 2.65, 2.35),
                          ("O3", "beton", 4.75, 2.3)])

    def test_eine_falsche_zeichnung_ohne_pfeiler_und_stuerze(self):
        p = Projekt(name="Probe")
        p.mauerwerk("MK")
        w = beispielwand(p)
        w.oeffnung(rechteck(5.5, 0.9, 6.5, 2.1))
        u = zeichnung(p, w)
        self.assertFalse(u["bereit"])
        self.assertEqual([(m["text"], m["elemente"], m["fehler"]) for m in u["meldungen"]],
                         [("Die Öffnung O4 reicht über die Wand hinaus.", ["O4"], True)])
        self.assertEqual((u["pfeiler"], u["stuerze"]), ([], []))

    def test_ohne_mauerwerk_fehlt_es_nur(self):
        """Grau, kein Fehler des Projekts: die Wand sagt, was fehlt."""
        p = Projekt(name="Probe")
        u = zeichnung(p, p.wand("Wand"))
        self.assertEqual([(m["text"], m["fehler"], m["unfertig"]) for m in u["meldungen"]],
                         [("Mauerwerk: noch kein Material gewählt.", False, True)])
        self.assertEqual(u["urteile"], {})


if __name__ == "__main__":
    unittest.main()
