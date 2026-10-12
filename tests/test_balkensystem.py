"""
Die Beschreibung eines Balkensystems: lesen, ablegen, zeichnen ohne
Oberfläche -- und was Teilen und Umkehren mit den Lasten einer Linie tun.
"""

import json
import math
import unittest

from opencivil.projekt import (
    BAUTEILE, BalkensystemEintrag, Projekt, ProjektFehler, StablastEintrag,
)
from opencivil.web import dienst


def rahmen() -> Projekt:
    """Zwei Stützen und ein Riegel, ein Lastfall und eine Kombination."""
    p = Projekt(name="Rahmen")
    p.beton("C30/37")
    s = p.balkensystem("Rahmen")
    q = s.querschnitt("Riegel", "rechteck", b=300.0, h=600.0)
    links = s.linie((0, 0), (0, 4), querschnitt=q, material="b1")
    riegel = s.linie((0, 4), (6, 4), querschnitt=q, material="b1")
    rechts = s.linie((6, 4), (6, 0), querschnitt=q, material="b1", gelenk_anfang=True)
    s.lager_an((0, 0), "eingespannt")
    s.lager_an((6, 0), "gelenkig")
    g = s.lastfall("Eigengewicht")
    w = s.lastfall("Wind")
    s.stablast(g, riegel, wert=25.0)
    s.stablast(w, links, wert=3.0, richtung="quer")
    s.knotenlast(w, (0, 4), 10.0, richtung="waagrecht")
    s.kombination("Tragsicherheit", (g, 1.35), (w, 1.5))
    assert (links.kennung, riegel.kennung, rechts.kennung) == ("L1", "L2", "L3")
    return p


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        p = rahmen()
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)

    def test_knoten_werden_geteilt(self):
        s = rahmen().balkensysteme[0]
        self.assertEqual([k.kennung for k in s.knoten], ["K1", "K2", "K3", "K4"])
        self.assertEqual(s.linien[1].von, s.linien[0].bis)
        self.assertEqual(s.lager[0].knoten, "K1")
        self.assertEqual((s.lager[0].x, s.lager[0].z, s.lager[0].phi), ("fest", "fest", "fest"))
        self.assertEqual(s.knotenlasten[0].knoten, "K2")

    def test_kennungen_und_suche(self):
        p = rahmen()
        self.assertEqual(p.balkensysteme[0].kennung, "r1")
        self.assertIs(p.bauteil("r1"), p.balkensysteme[0])
        self.assertEqual(p.freie_kennung("r"), "r2")
        with self.assertRaises(ProjektFehler):
            p.bauteil("r7")

    def test_neu_ist_ein_einfeldtraeger(self):
        s = BalkensystemEintrag.neu("r1", "Träger", "b1")
        self.assertEqual(len(s.linien), 1)
        self.assertTrue(s.linien[0].stab)
        self.assertEqual(s.laenge(s.linien[0]), 6.0)
        self.assertEqual([(l.x, l.z, l.phi) for l in s.lager],
                         [("fest", "fest", "frei"), ("frei", "fest", "frei")])
        self.assertEqual(s.linien[0].lasten[0].lastfall, s.lastfaelle[0].kennung)

    def test_eine_datei_nur_mit_systemen_ist_ein_projekt(self):
        self.assertIn("balkensysteme", BAUTEILE)
        roh = {"balkensysteme": [BalkensystemEintrag.neu("r1", "T", "").als_dict()]}
        self.assertEqual(len(dienst.pruefen({"projekt": roh})["projekt"]["balkensysteme"]), 1)


class TestPruefen(unittest.TestCase):
    def test_gleiche_namen(self):
        p = rahmen()
        p.balkensysteme[0].lastfall("Wind")
        with self.assertRaises(ProjektFehler):
            p.pruefen()

    def test_lastfall_und_kombination_heissen_gleich(self):
        p = rahmen()
        p.balkensysteme[0].kombination("Wind")
        with self.assertRaisesRegex(ProjektFehler, "Lastfall und eine Kombination"):
            p.pruefen()

    def test_unbekannte_wahl(self):
        for roh in ({"art": "flaechenlast"}, {"richtung": "schraeg"}):
            with self.subTest(roh=roh):
                with self.assertRaises(ProjektFehler):
                    StablastEintrag.aus_dict(roh)
        with self.assertRaises(ProjektFehler):
            BalkensystemEintrag.aus_dict({"kennung": "r", "lager": [{"x": "halb"}]})

    def test_fassade_meldet_tippfehler(self):
        p = rahmen()
        with self.assertRaisesRegex(ProjektFehler, "beschreibung"):
            p.balkensystem("Zwei", beschreibng="…")
        with self.assertRaisesRegex(ProjektFehler, "ellipse"):
            p.balkensysteme[0].querschnitt("E", "ellipse")
        with self.assertRaisesRegex(ProjektFehler, "Lagerart"):
            p.balkensysteme[0].lager_an((6, 4), "halb")


class TestTeilen(unittest.TestCase):
    def setUp(self):
        self.s = BalkensystemEintrag.neu("r1", "Träger", "b1")
        self.linie = self.s.linien[0]
        self.lf = self.s.lastfaelle[0]
        self.linie.lasten = []

    def last(self, **felder):
        return self.s.stablast(self.lf, self.linie, **felder)

    def test_gleichlast_wird_zwei(self):
        self.last(wert=10.0)
        zweite = self.s.teilen("L1", 2.0)
        self.assertEqual(self.s.netz().lage(zweite.von), (2.0, 0.0))
        self.assertEqual(self.s.laenge(self.linie), 2.0)
        self.assertEqual(self.s.laenge(zweite), 4.0)
        for linie in (self.linie, zweite):
            (last,) = linie.lasten
            self.assertEqual((last.von, last.bis, last.wert_a, last.wert_b), (0.0, None, 10.0, None))

    def test_trapez_mit_dem_wert_am_schnitt(self):
        """Von 0 auf 12 kN/m über 6 m, geteilt bei 2 m: 0 → 4 und 4 → 12."""
        self.last(wert=0.0, wert_b=12.0)
        zweite = self.s.teilen("L1", 2.0)
        a, b = self.linie.lasten[0], zweite.lasten[0]
        self.assertEqual((a.von, a.bis, a.wert_a), (0.0, None, 0.0))
        self.assertAlmostEqual(a.wert_b, 4.0)
        self.assertEqual((b.von, b.bis, b.wert_b), (0.0, None, 12.0))
        self.assertAlmostEqual(b.wert_a, 4.0)

    def test_teilstrecke_und_einzellasten(self):
        self.last(wert=5.0, von=1.0, bis=3.0)
        self.last(art="einzellast", wert=20.0, von=4.0)
        self.last(art="moment", wert=7.0, von=1.0)
        zweite = self.s.teilen("L1", 2.0)
        self.assertEqual([(l.art, l.von, l.bis) for l in self.linie.lasten],
                         [("linienlast", 1.0, None), ("moment", 1.0, None)])
        self.assertEqual([(l.art, l.von, l.bis) for l in zweite.lasten],
                         [("linienlast", 0.0, 1.0), ("einzellast", 2.0, None)])

    def test_eine_last_hinter_dem_ende_bleibt_hinter_dem_ende(self):
        """Sie wird gemeldet, nicht beim Teilen still gekürzt."""
        self.last(wert=5.0, von=1.0, bis=7.0)
        zweite = self.s.teilen("L1", 2.0)
        self.assertEqual(zweite.lasten[0].bis, 5.0)

    def test_gelenk_am_ende_wandert_mit(self):
        self.linie.gelenk_anfang = self.linie.gelenk_ende = True
        zweite = self.s.teilen("L1", 3.0)
        self.assertEqual((self.linie.gelenk_anfang, self.linie.gelenk_ende), (True, False))
        self.assertEqual((zweite.gelenk_anfang, zweite.gelenk_ende), (False, True))

    def test_ein_knoten_am_schnitt_wird_genommen(self):
        k = self.s.netz().an(2.0, 0.0)
        zweite = self.s.teilen("L1", 2.0)
        self.assertEqual(zweite.von, k)
        self.assertEqual(len(self.s.knoten), 3)

    def test_nur_dazwischen(self):
        for stelle in (0.0, 6.0, 7.5):
            with self.subTest(stelle=stelle):
                with self.assertRaises(ProjektFehler):
                    self.s.teilen("L1", stelle)


class TestUmkehren(unittest.TestCase):
    def setUp(self):
        self.s = BalkensystemEintrag.neu("r1", "Träger", "b1")
        self.linie = self.s.linien[0]
        self.linie.lasten = []
        lf = self.s.lastfaelle[0]
        self.s.stablast(lf, self.linie, wert=2.0, wert_b=8.0, von=1.0)
        self.s.stablast(lf, self.linie, wert=3.0, richtung="quer", bis=4.0)
        self.s.stablast(lf, self.linie, art="einzellast", wert=5.0, von=1.5, richtung="laengs")
        self.s.stablast(lf, self.linie, art="moment", wert=7.0, von=2.0)
        self.linie.gelenk_anfang = True

    def test_lasten_bleiben_wo_sie_wirken(self):
        vorher = [l.als_dict() for l in self.linie.lasten]
        self.s.umkehren("L1")
        self.assertEqual((self.linie.von, self.linie.bis), ("K2", "K1"))
        self.assertEqual((self.linie.gelenk_anfang, self.linie.gelenk_ende), (False, True))
        senkrecht, quer, einzel, moment = self.linie.lasten
        self.assertEqual((senkrecht.von, senkrecht.bis, senkrecht.wert_a, senkrecht.wert_b),
                         (0.0, 5.0, 8.0, 2.0))
        self.assertEqual((quer.von, quer.bis, quer.wert_a, quer.wert_b), (2.0, None, -3.0, None))
        self.assertEqual((einzel.von, einzel.wert_a), (4.5, -5.0))
        self.assertEqual((moment.von, moment.wert_a), (4.0, 7.0))
        self.s.umkehren("L1")
        self.assertEqual([l.als_dict() for l in self.linie.lasten], vorher)


if __name__ == "__main__":
    unittest.main()


# ===========================================================================
# Zum Rechnen
# ===========================================================================


def traeger(**masse) -> Projekt:
    """Ein Einfeldträger von 6 m mit 10 kN/m -- max M = 45 kNm."""
    p = Projekt(name="Träger")
    p.beton("C30/37")
    p.stahl("B500B")
    s = p.balkensystem("Träger")
    q = s.querschnitt("R", "rechteck", **(masse or {"b": 300.0, "h": 600.0}))
    linie = s.linie((0, 0), (6, 0), querschnitt=q, material="b1")
    s.lager_an((0, 0), "gelenkig")
    s.lager_an((6, 0), "verschieblich")
    s.stablast(s.lastfall("G"), linie, wert=10.0)
    return p


class TestModell(unittest.TestCase):
    def test_einheiten_und_richtungen(self):
        p = rahmen()
        modell = p.balkensysteme[0].modell()
        self.assertTrue(modell.gueltig, modell.meldungen)
        g, w = modell.system.lastfaelle
        self.assertEqual(g.lasten[0].wert_a, 25e3)
        knotenlast = next(l for l in w.lasten if not hasattr(l, "stab"))
        self.assertEqual((knotenlast.Fx, knotenlast.Fz), (10e3, 0.0))
        self.assertEqual(modell.system.kombinationen[0].faktoren,
                         {"Eigengewicht": 1.35, "Wind": 1.5})
        self.assertEqual(modell.paare, {"L1": ("Q1", "b1"), "L2": ("Q1", "b1"),
                                        "L3": ("Q1", "b1")})

    def test_senkrecht_zeigt_nach_unten(self):
        s = BalkensystemEintrag.neu("r1", "T", "b1")
        s.knotenlast(s.lastfaelle[0], (6, 0), 5.0)
        s.knotenlast(s.lastfaelle[0], (6, 0), 2.0, art="moment")
        lasten = s.modell().system.lastfaelle[0].lasten
        self.assertEqual(lasten[-2].Fz, -5e3)
        self.assertEqual(lasten[-1].M, 2e3)

    def test_federn(self):
        s = BalkensystemEintrag.neu("r1", "T", "b1")
        s.lager[1].x, s.lager[1].k_x = "feder", 5000.0
        s.linien[0].quer, s.linien[0].k_quer = "feder", 2000.0
        modell = s.modell()
        self.assertEqual(modell.system.lager[1].x, 5e6)
        self.assertEqual(modell.system.staebe[0].quer, 2e6)
        s.lager[1].k_x = 0.0
        self.assertFalse(s.modell().gueltig)

    def test_fehler_der_beschreibung(self):
        for aendern, wort, elemente in (
                (lambda s: setattr(s.linien[0], "querschnitt", ""), "keinen Querschnitt", {"L1"}),
                (lambda s: setattr(s.linien[0], "material", ""), "kein Material", {"L1"}),
                (lambda s: s.querschnitte[0].masse.__setitem__("h", 0.0), "Höhe",
                 {"Q1", "L1"})):
            with self.subTest(wort=wort):
                s = BalkensystemEintrag.neu("r1", "T", "b1")
                aendern(s)
                modell = s.modell()
                fehler = [m for m in modell.meldungen if m.fehler]
                self.assertEqual(len(fehler), 1)
                self.assertIn(wort, fehler[0].text)
                self.assertEqual(set(fehler[0].elemente), elemente)
                self.assertEqual(modell.paare, {})

    def test_last_ohne_lastfall_bleibt_mit_hinweis_weg(self):
        s = BalkensystemEintrag.neu("r1", "T", "b1")
        s.linien[0].lasten[0].lastfall = "LF9"
        modell = s.modell()
        self.assertTrue(modell.gueltig)
        self.assertIn("keinem Lastfall", modell.meldungen[0].text)
        self.assertEqual(modell.system.lastfaelle[0].lasten, [])


class TestRechnen(unittest.TestCase):
    def test_einfeldtraeger(self):
        e = traeger().rechnen()
        system = e.balkensystem("Träger")
        self.assertTrue(system.ergebnis.gueltig)
        x, M = system.verlaeufe("G")["L1"].extrem("M").groesst
        self.assertAlmostEqual(x, 3.0, places=9)
        self.assertAlmostEqual(M, 45e3, places=4)
        E = e.wert("beton.b1.E_cm").groesse.si
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.b1.EI").groesse.si,
                               E * 0.3 * 0.6 ** 3 / 12, delta=1e-6 * E)
        self.assertEqual(e.wert("balkensystem.r1.n").groesse.si, 3)

    def test_stahl_mit_E_s(self):
        p = traeger()
        s = p.balkensysteme[0]
        s.querschnitte[0].vorlage, s.querschnitte[0].masse = "kreis", {"d": 100.0}
        s.linien[0].material = "s1"
        e = p.rechnen()
        EA = e.wert("betonstahl.s1.E_s").groesse.si * math.pi * 0.05 ** 2
        self.assertAlmostEqual(e.wert("balkensystem.r1.Q1.s1.EA").groesse.si, EA,
                               delta=1e-12 * EA)

    def test_aus_platte_und_analyse(self):
        p = traeger()
        decke = p.platte("Decke", h=250)
        unterzug = p.analyse("Unterzug")
        s = p.balkensysteme[0]
        aus_platte = s.querschnitt_aus("Streifen", "platte", decke)
        aus_analyse = s.querschnitt_aus("Unterzug", "analyse", unterzug)
        s.linie((6, 0), (9, 0), querschnitt=aus_platte, material="b1")
        s.linie((9, 0), (12, 0), querschnitt=aus_analyse, material="b1")
        s.lager_an((12, 0), "verschieblich")
        e = p.rechnen()
        self.assertTrue(e.balkensystem("r1").ergebnis.gueltig,
                        e.balkensystem("r1").ergebnis.meldungen)
        self.assertEqual(e.wert(f"balkensystem.r1.{aus_platte.kennung}.A").groesse.si,
                         1.0 * 0.25)
        self.assertEqual(e.wert(f"balkensystem.r1.{aus_analyse.kennung}.I").groesse.si,
                         e.wert("querschnittsanalyse.a1.I_y").groesse.si)
        self.assertEqual(e.aufbau.balkensysteme["r1"].bezuege, ["a1", "q1"])

    def test_ein_fremder_verweis_scheitert_hart(self):
        p = traeger()
        p.balkensysteme[0].querschnitt_aus("Weg", "platte", "q7")
        with self.assertRaisesRegex(ProjektFehler, "q7"):
            p.aufbauen()

    def test_beweglich_ist_eine_meldung(self):
        p = traeger()
        p.balkensysteme[0].lager[0].x = "frei"
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200)
        uebersicht = antwort.daten["balkensysteme"]["r1"]
        self.assertFalse(uebersicht["gueltig"])
        self.assertIn("beweglich", uebersicht["meldungen"][0]["text"])
        self.assertTrue(uebersicht["beweglich"])
        verlauf = dienst.bearbeite("balkensystem_verlauf",
                                   {"projekt": p.als_dict(), "kennung": "r1", "fall": "G"})
        self.assertEqual((verlauf.status, verlauf.daten["verlauf"]), (200, None))

    def test_unbestimmte_drehung(self):
        """Ein Fachwerkknoten: alle Stäbe gelenkig, die Drehung ist gestrichen."""
        p = traeger()
        s = p.balkensysteme[0]
        q = s.querschnitte[0]
        s.linie((0, 0), (3, 3), querschnitt=q, material="b1", gelenk_ende=True)
        s.linie((6, 0), (3, 3), querschnitt=q, material="b1", gelenk_ende=True)
        e = p.rechnen()
        self.assertEqual(e.balkensystem("r1").ergebnis.unbestimmt(), ["K3"])
        antwort = dienst.bearbeite("balkensystem_verlauf",
                                   {"projekt": p.als_dict(), "kennung": "r1", "fall": "G"})
        knoten = antwort.daten["verlauf"]["knoten"]["K3"]
        self.assertTrue(knoten["unbestimmt"])
        self.assertIsNone(knoten["phi"])

    def test_herleitung(self):
        text = str(traeger().rechnen().bericht())
        for wort in ("Balkensystem: Träger", "nach Vorgabe, nicht nachgeschlagen",
                     "Gleichgewichtsprobe", "Extremwerte", "Lagerkräfte"):
            self.assertIn(wort, text)


class TestTeilenUndUmkehrenRechnenGleich(unittest.TestCase):
    """Teilen und Umkehren ändern die Beschreibung, nicht das Tragwerk."""

    def lagerkraefte(self, p):
        fall = p.rechnen().balkensystem("Rahmen").ergebnis.faelle[-1]
        return {k: tuple(round(v / 1e3, 6) for v in werte)
                for k, werte in fall.lagerkraefte.items()}

    def test_teilen(self):
        p = rahmen()
        s = p.balkensysteme[0]
        s.linien[1].lasten.append(StablastEintrag(lastfall="LF2", art="linienlast",
                                                  wert_a=2.0, wert_b=8.0, von=1.0))
        vorher = self.lagerkraefte(p)
        s.teilen("L2", 2.5)
        self.assertEqual(self.lagerkraefte(p), vorher)

    def test_umkehren(self):
        p = rahmen()
        vorher = self.lagerkraefte(p)
        for linie in ("L1", "L2", "L3"):
            p.balkensysteme[0].umkehren(linie)
        self.assertEqual(self.lagerkraefte(p), vorher)


class TestZwischenspeicher(unittest.TestCase):
    def beschreibung(self):
        p = traeger()
        unterzug = p.analyse("Unterzug")
        decke = p.platte("Decke", h=250)
        decke.einwirkung("Feld", M_Ed=20.0)
        s = p.balkensysteme[0]
        q = s.querschnitt_aus("Unterzug", "analyse", unterzug)
        s.linien[0].querschnitt = q.kennung
        return p.als_dict()

    def rechnen(self, d, frisch):
        if frisch:
            dienst.SPEICHER.leeren()
        return dienst.bearbeite("rechnen", {"projekt": d})

    def test_eine_geaenderte_analyse_rechnet_das_system_neu(self):
        d = self.beschreibung()
        self.rechnen(d, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        d["querschnittsanalysen"][0]["knoten"][2]["z"] = 700.0
        mit = self.rechnen(d, frisch=False)
        self.assertEqual((dienst.SPEICHER.treffer, dienst.SPEICHER.fehlgriffe), (1, 2))
        ohne = self.rechnen(d, frisch=True)
        self.assertEqual(json.dumps(mit.daten, sort_keys=True, default=str),
                         json.dumps(ohne.daten, sort_keys=True, default=str))

    def test_eine_fremde_platte_nicht(self):
        d = self.beschreibung()
        self.rechnen(d, frisch=True)
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        d["querschnitte"][0]["h"] = 260.0
        self.rechnen(d, frisch=False)
        self.assertEqual((dienst.SPEICHER.treffer, dienst.SPEICHER.fehlgriffe), (2, 1))

    def test_die_bilder_kommen_aus_dem_speicher(self):
        d = self.beschreibung()
        self.rechnen(d, frisch=True)
        dienst.SPEICHER.treffer = 0
        antwort = dienst.bearbeite("balkensystem_verlauf",
                                   {"projekt": d, "kennung": "r1", "fall": "G"})
        self.assertEqual(antwort.status, 200)
        self.assertEqual(dienst.SPEICHER.treffer, 1)
        self.assertIn("L1", antwort.daten["verlauf"]["staebe"])


class TestBearbeiten(unittest.TestCase):
    def test_teilen_mit_punkt_und_umkehren(self):
        d = traeger().als_dict()
        antwort = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "r1", "aktion": "teilen", "linie": "L1",
            "punkt": [2.0, 0.4]})
        self.assertEqual((antwort.status, antwort.daten["neu"]), (200, ["L2"]))
        knoten = {k["kennung"]: (k["x"], k["z"]) for k in antwort.daten["balkensystem"]["knoten"]}
        self.assertEqual(knoten["K3"], (2.0, 0.0))
        d["balkensysteme"][0] = antwort.daten["balkensystem"]
        antwort = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "r1", "aktion": "umkehren", "linien": ["L1", "L2"]})
        linien = antwort.daten["balkensystem"]["linien"]
        self.assertEqual([(l["von"], l["bis"]) for l in linien], [("K3", "K1"), ("K2", "K3")])

    def test_teilen_in_der_mitte_und_uebersicht_ohne_fall(self):
        d = traeger().als_dict()
        antwort = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "r1", "aktion": "teilen", "linie": "L1", "anteil": 0.5})
        knoten = {k["kennung"]: (k["x"], k["z"]) for k in antwort.daten["balkensystem"]["knoten"]}
        self.assertEqual(knoten["K3"], (3.0, 0.0))
        antwort = dienst.bearbeite("balkensystem_verlauf", {"projekt": d, "kennung": "r1"})
        self.assertEqual(antwort.status, 200)
        self.assertIsNone(antwort.daten["verlauf"])
        self.assertTrue(antwort.daten["uebersicht"]["gueltig"])

    def test_falsche_anfragen(self):
        d = traeger().als_dict()
        for rumpf in ({"kennung": "q1", "aktion": "umkehren"},
                      {"kennung": "r1", "aktion": "drehen"},
                      {"kennung": "r1", "aktion": "teilen", "linie": "L1", "stelle": "mitte"},
                      {"kennung": "r1", "aktion": "teilen", "linie": "L1", "stelle": 9.0}):
            with self.subTest(rumpf=rumpf):
                antwort = dienst.bearbeite("balkensystem_bearbeiten", {"projekt": d, **rumpf})
                self.assertEqual(antwort.status, 400)
