"""
Die Beschreibung eines Balkensystems: lesen, ablegen, zeichnen ohne
Oberfläche -- und was Teilen und Umkehren mit den Lasten einer Linie tun.
"""

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
