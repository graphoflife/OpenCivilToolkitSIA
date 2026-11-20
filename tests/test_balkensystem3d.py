"""
Das 3D-Balkensystem: die Beschreibung, ihr Baukasten, Teilen und Umkehren,
gerechnet von der Beschreibung bis zur Herleitung -- gegen Handrechnungen
und gegen das 2D-Balkensystem --, und was die Oberflaeche davon bekommt:
Katalog, Zeichendaten, Verlaeufe, Teilen ueber den Dienst.
"""

import math
import unittest

from opencivil.core.protokoll import TabellenBlock
from opencivil.projekt import BalkensystemEintrag, Projekt, ProjektFehler
from opencivil.projekt.aufbau import BALKENSYSTEM3D
from opencivil.projekt.aufbau import balkensystem3d as aufbau3d
from opencivil.projekt.balkensystem3d import Balkensystem3dEintrag
from opencivil.projekt.staebe import MATERIAL_DES_QUERSCHNITTS
from opencivil.stabwerk.rechnung import STABKENNWERTE
from opencivil.stabwerk3d.modell import Richtung
from opencivil.stabwerk3d.rechnung import RAUMKENNWERTE
from opencivil.web import api, dienst


def gerechnet(projekt: Projekt, s: Balkensystem3dEintrag):
    """Das System und seine Loesung -- mit den Baustoffen des Projekts."""
    aufbau = projekt.aufbauen()
    teil = BALKENSYSTEM3D.bauen(BALKENSYSTEM3D, s, aufbau)
    loesung = aufbau.werk.loese(*teil.weitere_ziele)
    return loesung.befunde.get(teil.objekt.rechnung.id), loesung


def kragarm(stahl="st1", **querschnitt):
    """Ein Kragarm von 4 m in x, eingespannt, von Hand: A, I_y, I_z, I_T."""
    s = Balkensystem3dEintrag(kennung="u1", name="Kragarm")
    q = s.querschnitt_mit_kennwerten("Hand", **(querschnitt or dict(
        A=10000.0, I_y=100.0, I_z=50.0, I_T=20.0)))
    s.linie((0, 0, 0), (4, 0, 0), querschnitt=q, material=s.baustahl(stahl))
    s.lager_an((0, 0, 0), "eingespannt")
    return s


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        s = kragarm()
        l = s.linien[0]
        s.stablast(s.lastfall("G"), l, wert=3.0, richtung="quer_y", wert_b=5.0)
        s.knotenlast("LF1", (4, 0, 0), 2.0, art="moment", richtung="z")
        self.assertEqual(Balkensystem3dEintrag.aus_dict(s.als_dict()), s)

    def test_knoten_im_raum_werden_geteilt(self):
        s = Balkensystem3dEintrag(kennung="u1", name="S")
        s.linie((0, 0, 0), (0, 0, 3))
        s.linie((0, 0, 3), (4, 2, 3))
        self.assertEqual([(k.x, k.y, k.z) for k in s.knoten],
                         [(0.0, 0.0, 0.0), (0.0, 0.0, 3.0), (4.0, 2.0, 3.0)])
        self.assertEqual(s.linien[1].von, s.linien[0].bis)
        self.assertAlmostEqual(s.laenge(s.linien[1]), math.sqrt(20.0))
        self.assertAlmostEqual(s.stelle_auf("L2", (2, 1, 5)), math.sqrt(5.0))

    def test_lagerarten_halten_im_raum(self):
        s = Balkensystem3dEintrag(kennung="u1", name="S")
        a = s.lager_an((0, 0, 0), "gelenkig", phi_x="fest")
        b = s.lager_an((1, 0, 0), "verschieblich")
        felder = ("x", "y", "z", "phi_x", "phi_y", "phi_z")
        self.assertEqual([getattr(a, f) for f in felder], ["fest"] * 4 + ["frei"] * 2)
        self.assertEqual([getattr(b, f) for f in felder], ["frei", "frei", "fest"] + ["frei"] * 3)

    def test_neu_mit_den_diagrammen_des_raums(self):
        s = Balkensystem3dEintrag.neu("u1", "Raum")
        self.assertEqual([(d.fall, d.groesse) for d in s.diagramme],
                         [("LK1", "M_y"), ("LK1", "M_z"), ("LK1", "N"), ("LK2", "verschiebung")])

    def test_nur_was_der_raum_kennt(self):
        s = Balkensystem3dEintrag(kennung="u1", name="S")
        with self.assertRaisesRegex(ProjektFehler, "Möglich sind: senkrecht, x, y, z"):
            s.knotenlast("LF1", (0, 0, 0), richtung="laengs")
        with self.assertRaisesRegex(
                ProjektFehler, "Möglich sind: vorlage, profil, kennwerte, platte, analyse"):
            Balkensystem3dEintrag.aus_dict({"kennung": "u1", "name": "S",
                                            "querschnitte": [{"art": "zeichnung"}]})
        with self.assertRaisesRegex(ProjektFehler, "'M' gibt es als 'groesse' nicht"):
            s.diagramm("LF1", "M")

    def test_kennwerte_von_hand(self):
        s = Balkensystem3dEintrag(kennung="u1", name="S")
        self.assertIsNone(s.querschnitt_mit_kennwerten("Q", A=1.0, I_y=1.0, I_z=1.0,
                                                       I_T=1.0).fehler())
        self.assertEqual(s.querschnitt_mit_kennwerten("Q", A=1.0, I_y=1.0).fehler(),
                         "Flächenträgheitsmoment um z I_z muss grösser als null sein, "
                         "angegeben ist 0 ·10⁶ mm⁴.")
        self.assertIn("einen Kennwert «I» gibt es nicht",
                      s.querschnitt_mit_kennwerten("Q", A=1.0, I=1.0).fehler())

    def test_ein_eigenes_material_mit_schubmodul(self):
        s = Balkensystem3dEintrag(kennung="u1", name="S")
        m = s.eigenes_material("Holz", E=11000.0, rho=500.0, G=690.0)
        self.assertEqual((m.E, m.rho, m.G), (11000.0, 500.0, 690.0))
        with self.assertRaisesRegex(ProjektFehler, "'G'"):
            BalkensystemEintrag(kennung="r1", name="S").eigenes_material("Holz", G=690.0)


class TestTeilenUndUmkehren(unittest.TestCase):
    def system(self):
        s = Balkensystem3dEintrag(kennung="u1", name="S")
        l = s.linie((0, 0, 3), (6, 0, 3), drehung=30.0, gelenk_ende=True)
        lf = s.lastfall("G")
        for richtung in ("senkrecht", "y", "laengs", "quer_y", "quer_z"):
            s.stablast(lf, l, wert=2.0, wert_b=4.0, richtung=richtung)
        s.stablast(lf, l, "moment", wert=1.0, stelle=25.0, richtung="laengs")
        s.stablast(lf, l, "moment", wert=1.0, stelle=25.0, richtung="quer_z")
        return s, l

    def test_umkehren_dreht_den_querschnitt_mit(self):
        """Der Querschnitt steht wie vorher: β wird -β, und was an y und x des Stabs haengt, kehrt um."""
        s, l = self.system()
        s.umkehren(l.kennung)
        self.assertEqual((l.von, l.bis, l.drehung, l.gelenk_anfang), ("K2", "K1", -30.0, True))
        self.assertEqual([(last.richtung.value, last.wert_a, last.wert_b) for last in l.lasten[:5]],
                         [("senkrecht", 4.0, 2.0), ("y", 4.0, 2.0), ("laengs", -4.0, -2.0),
                          ("quer_y", -4.0, -2.0), ("quer_z", 4.0, 2.0)])
        self.assertEqual([(last.stelle, last.wert_a) for last in l.lasten[5:]],
                         [(75.0, -1.0), (75.0, 1.0)])

    def test_lotrecht_wird_beta_zu_180_minus_beta(self):
        s = Balkensystem3dEintrag(kennung="u1", name="S")
        l = s.linie((0, 0, 0), (0, 0, 3), drehung=30.0)
        s.umkehren(l.kennung)
        self.assertEqual(l.drehung, 150.0)

    def test_teilen_behaelt_den_drehwinkel(self):
        s, l = self.system()
        zweite = s.teilen(l.kennung, 2.0)
        self.assertEqual((zweite.drehung, zweite.gelenk_ende, l.gelenk_ende), (30.0, True, False))
        self.assertEqual(s.knoten[-1].x, 2.0)


class TestRechnen(unittest.TestCase):
    def setUp(self):
        self.projekt = Projekt(name="Raum")
        self.projekt.baustahl("S355")

    def test_kragarm_in_alle_richtungen(self):
        """Am Ende 10 kN nach unten, 5 kN in y und 2 kNm um x -- gegen die Handrechnung."""
        s = kragarm()
        lf = s.lastfall("P")
        s.knotenlast(lf, (4, 0, 0), 10.0)
        s.knotenlast(lf, (4, 0, 0), 5.0, richtung="y")
        s.knotenlast(lf, (4, 0, 0), 2.0, art="moment", richtung="x")
        befund, _ = gerechnet(self.projekt, s)
        self.assertTrue(befund.ergebnis.gueltig)
        E, G, L = 210000e6, 81000e6, 4.0
        ux, uy, uz, phi_x, _, _ = befund.ergebnis.fall("P").verschiebungen["K2"]
        self.assertAlmostEqual(uz, -10e3 * L ** 3 / (3 * E * 100e-6), places=12)
        self.assertAlmostEqual(uy, 5e3 * L ** 3 / (3 * E * 50e-6), places=12)
        self.assertAlmostEqual(phi_x, 2e3 * L / (G * 20e-6), places=12)
        anfang = befund.verlaeufe("P")["L1"].bei(0.0)
        # M_y zieht an +z, unten: der Kragarm zieht oben. y des Stabs ist -y des Systems.
        for groesse, soll in (("M_y", -40e3), ("M_z", 20e3), ("T", 2e3), ("V_z", 10e3)):
            self.assertAlmostEqual(anfang[groesse], soll, places=6)
        (zeile,) = befund.lagerkraefte(befund.ergebnis.fall("P"))
        self.assertEqual(zeile.wo, "A1 (K1)")
        for ist, soll in zip(zeile.werte, (0.0, -5e3, 10e3, -2e3, -40e3, -20e3)):
            self.assertAlmostEqual(ist, soll, places=6)

    def test_steifigkeiten_aus_dem_baustahl(self):
        _, loesung = gerechnet(self.projekt, kragarm())
        for kurz, soll in (("EA", 210000e6 * 0.01), ("EI_y", 210000e6 * 100e-6),
                           ("EI_z", 210000e6 * 50e-6), ("GI_T", 81000e6 * 20e-6)):
            self.assertAlmostEqual(loesung.werte[f"balkensystem3d.u1.Q1.M1.{kurz}"].groesse.si,
                                   soll, delta=1e-9 * soll)

    def test_ein_stahlprofil_mit_seiner_torsion(self):
        """HEB 300 nach den Tabellen: I_y 25170 cm⁴, I_z 8563 cm⁴, I_T 185 cm⁴."""
        s = Balkensystem3dEintrag(kennung="u1", name="P")
        s.linie((0, 0, 0), (4, 0, 0), querschnitt=s.stahlprofil("Träger", "HEB 300"),
                material=s.baustahl("st1"))
        s.lager_an((0, 0, 0), "eingespannt")
        _, loesung = gerechnet(self.projekt, s)
        for kurz, soll in (("I_y", 25170e-8), ("I_z", 8563e-8), ("I_T", 185e-8)):
            self.assertAlmostEqual(loesung.werte[f"balkensystem3d.u1.Q1.{kurz}"].groesse.si,
                                   soll, delta=0.002 * soll)

    def test_beton_mit_seinem_schubmodul(self):
        self.projekt.beton("C30/37")
        s = Balkensystem3dEintrag(kennung="u1", name="B")
        q = s.querschnitt("R", "rechteck", b=300.0, h=600.0)
        s.linie((0, 0, 0), (4, 0, 0), querschnitt=q, material=s.beton("b1"))
        s.lager_an((0, 0, 0), "eingespannt")
        _, loesung = gerechnet(self.projekt, s)
        G = loesung.werte["beton.b1.G_cm"].groesse.si
        self.assertAlmostEqual(G, loesung.werte["beton.b1.E_cm"].groesse.si / 2.4, delta=1.0)
        I_T = loesung.werte["balkensystem3d.u1.Q1.I_T"].groesse.si
        self.assertAlmostEqual(loesung.werte["balkensystem3d.u1.Q1.M1.GI_T"].groesse.si,
                               G * I_T, delta=1e-9 * G * I_T)

    def test_eigenes_material_mit_g_von_hand(self):
        s = kragarm()
        s.linien[0].material = s.eigenes_material("Holz", E=11000.0, rho=500.0, G=690.0).kennung
        _, loesung = gerechnet(self.projekt, s)
        self.assertEqual(loesung.werte["balkensystem3d.u1.M2.G"].groesse.si, 690e6)
        self.assertAlmostEqual(loesung.werte["balkensystem3d.u1.Q1.M2.GI_T"].groesse.si,
                               690e6 * 20e-6, delta=1e-6)

    def test_eigengewicht_senkrecht(self):
        """7850 kg/m³ · 10 m/s² · 0.01 m² = 785 N/m, auf 4 m 3.14 kN und 6.28 kNm."""
        s = kragarm()
        s.lastfall("Eigengewicht", eigengewicht=True)
        befund, _ = gerechnet(self.projekt, s)
        (zeile,) = befund.lagerkraefte(befund.ergebnis.fall("Eigengewicht"))
        self.assertAlmostEqual(zeile.werte[2], 3140.0, places=6)
        self.assertAlmostEqual(zeile.werte[4], -6280.0, places=6)

    def test_wie_das_2d_balkensystem(self):
        """Ein Einfeldträger in x, mit Gabel: M_y wie M der Ebene, w wie dort."""
        self.projekt.beton("C30/37")
        p2 = Projekt(name="Eben")
        p2.beton("C30/37")
        eben = p2.balkensystem("T")
        q = eben.querschnitt("R", "rechteck", b=300.0, h=600.0)
        eben.linie((0, 0), (6, 0), querschnitt=q, material=eben.beton("b1"))
        eben.lager_an((0, 0), "gelenkig")
        eben.lager_an((6, 0), "verschieblich")
        eben.stablast(eben.lastfall("G"), "L1", wert=10.0)
        s = Balkensystem3dEintrag(kennung="u1", name="T")
        q = s.querschnitt("R", "rechteck", b=300.0, h=600.0)
        s.linie((0, 0, 0), (6, 0, 0), querschnitt=q, material=s.beton("b1"))
        s.lager_an((0, 0, 0), "gelenkig", phi_x="fest")
        s.lager_an((6, 0, 0), "verschieblich", y="fest")
        s.stablast(s.lastfall("G"), "L1", wert=10.0)
        befund, _ = gerechnet(self.projekt, s)
        v2 = p2.rechnen().balkensystem("T").verlaeufe("G")["L1"]
        v3 = befund.verlaeufe("G")["L1"]
        for x in (0.0, 1.5, 3.0):
            for g in ("M_y", "V_z"):
                self.assertAlmostEqual(v3.bei(x)[g], v2.bei(x)[g], places=6)
            self.assertAlmostEqual(v3.bei(x)["f_z"], v2.bei(x)["f_z"], places=12)

    def test_meldungen_wie_in_der_ebene(self):
        s = kragarm()
        s.linien[0].material = ""
        s.lager[0].phi_x, s.lager[0].k_phi_x = "feder", 0.0
        modell = aufbau3d.modell_von(s)
        self.assertEqual([(m.text, m.fehler) for m in modell.meldungen if m.haelt_an],
                         [("L1 ist ein Stab, hat aber noch kein Material.", False),
                          ("A1: eine Feder braucht eine Steifigkeit grösser als null.", True)])

    def test_drehwinkel_in_rad(self):
        s = kragarm()
        s.linien[0].drehung = 90.0
        self.assertAlmostEqual(aufbau3d.modell_von(s).system.staebe[0].drehung, math.pi / 2)

    def test_herleitung(self):
        s = kragarm()
        s.knotenlast(s.lastfall("P"), (4, 0, 0), 10.0)
        _, loesung = gerechnet(self.projekt, s)
        titel = [b.titel for b in loesung.protokoll.bloecke if isinstance(b, TabellenBlock)]
        self.assertEqual(titel, ["Stäbe", "Lager", "Verschiebungen der Knoten",
                                 "Schnittgrössen an den Stabenden", "Lagerkräfte, auf das Tragwerk",
                                 "Extremwerte", "Gleichgewichtsprobe (Moment um den Ursprung)"])


class TestAusEinerPlatte(unittest.TestCase):
    """
    Ein Querschnitt aus einer Platte, wie in der Ebene (Benutzer,
    2026-11-18): der Streifen b × h, b waagrecht -- und ein Stab «gemäss
    Querschnitt» mit ihrem Beton, G_cm für die Torsion.
    """

    def projekt(self, **eq):
        """Ein Kragarm von 4 m aus dem Streifen der Platte «Decke», h = 250 mm, b = 1000 mm."""
        p = Projekt(name="Raum")
        p.beton("C30/37")
        p.stahl("B500B")
        s = p.balkensystem3d("Rahmen")
        q = s.querschnitt_aus("Streifen", "platte", p.platte("Decke", h=250),
                              **({"E_eq": eq} if eq else {}))
        s.linie((0, 0, 0), (4, 0, 0), querschnitt=q, material=MATERIAL_DES_QUERSCHNITTS)
        s.lager_an((0, 0, 0), "eingespannt")
        lf = s.lastfall("P")
        s.knotenlast(lf, (4, 0, 0), 10.0)
        return p, s, q

    def wert(self, e, s, q, kurz):
        return e.wert(f"balkensystem3d.{s.kennung}.{q.kennung}.{kurz}").groesse.si

    def test_der_streifen_mit_seinem_beton(self):
        p, s, q = self.projekt()
        e = p.rechnen()
        self.assertTrue(e.balkensystem("Rahmen").ergebnis.gueltig,
                        e.balkensystem("Rahmen").ergebnis.meldungen)
        b, h = 1.0, 0.25
        for kurz, soll in (("A", b * h), ("I_y", b * h ** 3 / 12), ("I_z", h * b ** 3 / 12)):
            self.assertAlmostEqual(self.wert(e, s, q, kurz), soll, delta=1e-9 * soll)
        # I_T wie das Rechteck nach Vorlage mit denselben Massen.
        vergleich = Balkensystem3dEintrag(kennung="u9", name="R")
        r = vergleich.querschnitt("R", "rechteck", b=1000.0, h=250.0)
        vergleich.linie((0, 0, 0), (4, 0, 0), querschnitt=r, material=vergleich.beton("b1"))
        vergleich.lager_an((0, 0, 0), "eingespannt")
        _, loesung = gerechnet(p, vergleich)
        I_T = loesung.werte["balkensystem3d.u9.Q1.I_T"].groesse.si
        self.assertAlmostEqual(self.wert(e, s, q, "I_T"), I_T, delta=1e-12)
        _, material = e.aufbau.balkensysteme3d[s.kennung].paare["L1"]
        self.assertEqual(material.stoff.name, "C30/37")
        G = e.wert("beton.b1.G_cm").groesse.si
        self.assertAlmostEqual(self.wert(e, s, q, f"{MATERIAL_DES_QUERSCHNITTS}.GI_T"),
                               G * I_T, delta=1e-9 * G * I_T)
        self.assertEqual(s.bezuege(), ["q1"])
        self.assertEqual(e.aufbau.balkensysteme3d[s.kennung].bezuege, ["q1"])

    def test_e_eq_fuer_die_biegung_g_fuer_die_torsion(self):
        """Gerissen bei M = 40 kNm: E_eq in EA, EI_y und EI_z, G_cm bleibt in GI_T."""
        p, s, q = self.projekt(M=40.0)
        e = p.rechnen()
        self.assertTrue(e.balkensystem("Rahmen").ergebnis.gueltig,
                        e.balkensystem("Rahmen").ergebnis.meldungen)
        E = self.wert(e, s, q, "E")
        self.assertLess(E, e.wert("beton.b1.E_cm").groesse.si)
        for steifigkeit, kennwert in (("EA", "A"), ("EI_y", "I_y"), ("EI_z", "I_z")):
            soll = E * self.wert(e, s, q, kennwert)
            self.assertAlmostEqual(
                self.wert(e, s, q, f"{MATERIAL_DES_QUERSCHNITTS}.{steifigkeit}"), soll,
                delta=1e-9 * soll)
        soll = e.wert("beton.b1.G_cm").groesse.si * self.wert(e, s, q, "I_T")
        self.assertAlmostEqual(self.wert(e, s, q, f"{MATERIAL_DES_QUERSCHNITTS}.GI_T"), soll,
                               delta=1e-9 * soll)


class TestAusEinerAnalyse(unittest.TestCase):
    """
    Ein Querschnitt aus einer Querschnittsanalyse, wie in der Ebene (Benutzer,
    2026-11-18): A, I_y und I_z ihres Bruttoquerschnitts, dazu ein I_T, das
    sie dafür numerisch rechnet -- nur, wenn ein Stab im Raum es braucht.
    """

    def projekt(self, im_raum=True):
        """Ein Kragarm von 4 m aus der Analyse «Balken», dem Rechteck 300 × 600 mm."""
        p = Projekt(name="Raum")
        p.beton("C30/37")
        p.stahl("B500B")
        a = p.analyse("Balken")
        s = p.balkensystem3d("Rahmen") if im_raum else p.balkensystem("Rahmen")
        q = s.querschnitt_aus("Balken", "analyse", a)
        anfang, ende = ((0, 0, 0), (4, 0, 0)) if im_raum else ((0, 0), (4, 0))
        s.linie(anfang, ende, querschnitt=q, material=MATERIAL_DES_QUERSCHNITTS)
        s.lager_an(anfang, "eingespannt")
        s.knotenlast(s.lastfall("P"), ende, 10.0)
        return p, a, s, q

    def test_die_kennwerte_der_analyse_und_ihr_I_T(self):
        p, a, s, q = self.projekt()
        e = p.rechnen()
        self.assertTrue(e.balkensystem("Rahmen").ergebnis.gueltig,
                        e.balkensystem("Rahmen").ergebnis.meldungen)
        analyse = e.aufbau.querschnittsanalysen[a.kennung]

        def wert(kurz):
            return e.wert(f"balkensystem3d.{s.kennung}.{q.kennung}.{kurz}").groesse.si

        for kurz in ("A", "I_y", "I_z", "I_T"):
            self.assertEqual(wert(kurz), e.wert(analyse.id_von(kurz)).groesse.si)
        b, h = 0.3, 0.6
        self.assertAlmostEqual(wert("I_y"), b * h ** 3 / 12, delta=1e-12)
        self.assertAlmostEqual(wert("I_z"), h * b ** 3 / 12, delta=1e-12)
        # I_T des Rechtecks nach der Reihe von St. Venant: 3704.64 · 10⁶ mm⁴.
        self.assertAlmostEqual(wert("I_T") / 3704.64e-6, 1.0, delta=1e-4)
        G = e.wert("beton.b1.G_cm").groesse.si
        self.assertAlmostEqual(wert(f"{MATERIAL_DES_QUERSCHNITTS}.GI_T"), G * wert("I_T"),
                               delta=1e-9 * G * wert("I_T"))
        self.assertEqual(s.bezuege(), [a.kennung])

    def test_ein_winkel_bekommt_einen_hinweis(self):
        """
        y und z gelten als Hauptachsen (Benutzer, 2026-11-19): ist der
        Querschnitt unsymmetrisch, sagt es ein Hinweis -- gerechnet wird
        trotzdem. Unten rechts ein Flansch 400 × 100 mm am Rechteck.
        """
        p, a, s, q = self.projekt()
        a.polygon([[300, 0], [700, 0], [700, 100], [300, 100]], material=a.flaechen[0].material)
        e = p.rechnen()
        ergebnis = e.balkensystem("Rahmen").ergebnis
        self.assertTrue(ergebnis.gueltig, ergebnis.meldungen)
        hinweise = [m for m in ergebnis.meldungen if "keine Hauptachsen" in m.text]
        self.assertEqual(len(hinweise), 1, ergebnis.meldungen)
        self.assertFalse(hinweise[0].fehler)
        self.assertEqual(hinweise[0].elemente, (q.kennung, "L1"))
        I_yz = e.wert(f"balkensystem3d.{s.kennung}.{q.kennung}.I_yz").groesse.si
        self.assertEqual(I_yz, e.wert(e.aufbau.querschnittsanalysen[a.kennung].id_von("I_yz"))
                         .groesse.si)
        self.assertNotEqual(I_yz, 0.0)
        self.assertIn("Hinweis", str(e.bericht()))

    def test_ein_rechteck_bekommt_keinen(self):
        p, a, s, q = self.projekt()
        meldungen = p.rechnen().balkensystem("Rahmen").ergebnis.meldungen
        self.assertFalse(any("Hauptachsen" in m.text for m in meldungen), meldungen)

    def test_in_der_ebene_wird_I_T_nicht_gerechnet(self):
        """Die Ebene braucht kein I_T -- und das Rechenwerk rechnet nur, was ein Ziel braucht."""
        p, a, s, q = self.projekt(im_raum=False)
        e = p.rechnen()
        self.assertTrue(e.balkensystem("Rahmen").ergebnis.gueltig)
        self.assertNotIn(e.aufbau.querschnittsanalysen[a.kennung].id_von("I_T"),
                         e.loesung.werte)


class TestMaterialkennwerte(unittest.TestCase):
    def test_der_raum_nimmt_dazu_den_schubmodul(self):
        self.assertEqual(RAUMKENNWERTE["beton"], {**STABKENNWERTE["beton"], "G": "G_cm"})
        self.assertEqual(RAUMKENNWERTE["baustahl"], {**STABKENNWERTE["baustahl"], "G": "G_a"})

    def test_richtungen_am_knoten(self):
        from opencivil.projekt.balkensystem3d import KNOTENRICHTUNGEN
        self.assertEqual(KNOTENRICHTUNGEN, (Richtung.SENKRECHT, Richtung.X, Richtung.Y, Richtung.Z))


def im_projekt():
    """Der Kragarm im Projekt, mit 10 kN am Ende -- wie die Oberflaeche ihn schickt."""
    p = Projekt(name="Raum")
    p.baustahl("S355")
    s = kragarm()
    s.knotenlast(s.lastfall("P"), (4, 0, 0), 10.0)
    p.balkensysteme3d.append(s)
    return p


class TestImProjekt(unittest.TestCase):
    def test_ueber_die_fassade_und_zurueck(self):
        p = Projekt(name="Raum")
        s = p.balkensystem3d("Rahmen")
        self.assertEqual((s.kennung, p.bauteil("u1")), ("u1", s))
        self.assertEqual(Projekt.aus_dict(p.als_dict()).balkensysteme3d, [s])

    def test_das_ergebnis_findet_es(self):
        e = im_projekt().rechnen()
        befund = e.balkensystem("Kragarm")
        uz = befund.ergebnis.fall("P").verschiebungen["K2"][2]
        self.assertAlmostEqual(uz, -10e3 * 4.0 ** 3 / (3 * 210000e6 * 100e-6), places=12)


class TestFuerDieOberflaeche(unittest.TestCase):
    def test_derselbe_katalog_wie_in_der_ebene(self):
        k = api.katalog()
        eben, raum = k["balkensystem"], k["balkensystem3d"]
        self.assertEqual(sorted(eben), sorted(raum))
        self.assertEqual(raum["achsen"], ["x", "y", "z"])
        richtungen = {r["wert"]: (r["vektor"], r["stabachse"]) for r in raum["richtungen"]}
        self.assertEqual(richtungen["senkrecht"], ([0.0, 0.0, -1.0], None))
        self.assertEqual(richtungen["quer_y"], (None, "y"))
        self.assertEqual({r["wert"]: r["stabachse"] for r in eben["richtungen"]}["quer"], "z")
        self.assertEqual(raum["profilachsen"], [])
        self.assertEqual(raum["laufrichtungen"], [])        # wie gezeichnet
        self.assertEqual([q["wert"] for q in raum["querschnittsarten"]],
                         ["vorlage", "profil", "kennwerte", "platte", "analyse"])
        self.assertEqual(raum["lagerarten"][0], {"wert": "gelenkig", "x": "fest", "y": "fest",
                                                 "z": "fest", "phi_x": "frei", "phi_y": "frei",
                                                 "phi_z": "frei"})
        self.assertEqual(raum["klassen"]["linie"], "raumlinie")
        self.assertIn("raumlinie", k["vorlagen"])

    def test_zeichendaten_mit_den_achsen_der_linien(self):
        antwort = dienst.bearbeite("rechnen", {"projekt": im_projekt().als_dict()})
        self.assertEqual(antwort.status, 200)
        daten = antwort.daten["zeichendaten"]["u1"]
        self.assertTrue(daten["uebersicht"]["gueltig"])
        # Laengs in x, z nach unten, y = z × x ist -y des Systems.
        self.assertEqual(daten["achsen"]["L1"], {"x": [1.0, 0.0, 0.0], "y": [0.0, -1.0, 0.0],
                                                 "z": [0.0, 0.0, -1.0]})
        (zeile,) = daten["uebersicht"]["faelle"][0]["lagerkraefte"]
        self.assertEqual([round(zeile[g], 6) for g in ("R_x", "R_y", "R_z", "M_x", "M_y", "M_z")],
                         [0.0, 0.0, 10.0, 0.0, -40.0, 0.0])
        extrem = daten["uebersicht"]["faelle"][0]["staebe"]["L1"]["M_y"]
        self.assertAlmostEqual(extrem["kleinst"][1], -40.0)
        grenzen = daten["uebersicht"]["faelle"][0]["grenzen"]
        self.assertEqual(grenzen["M_y"]["massgebend"],
                         {"stab": "L1", "x": extrem["kleinst"][0], "wert": extrem["kleinst"][1]})

    def test_verlauf_im_raum(self):
        antwort = dienst.bearbeite("balkensystem_verlauf",
                                   {"projekt": im_projekt().als_dict(), "kennung": "u1", "fall": "P"})
        self.assertEqual(antwort.status, 200)
        verlauf = antwort.daten["verlauf"]
        stab = verlauf["staebe"]["L1"]
        self.assertEqual((stab["L"], stab["anfang"]), (4.0, [0.0, 0.0, 0.0]))
        self.assertEqual(stab["achsen"]["z"], [0.0, 0.0, -1.0])
        ende = stab["proben"][-1]
        uz = -10e3 * 4.0 ** 3 / (3 * 210000e6 * 100e-6) * 1e3
        self.assertAlmostEqual(ende["u"][2], uz, places=6)
        self.assertAlmostEqual(verlauf["groesste_verschiebung"], -uz, places=6)
        self.assertAlmostEqual(stab["proben"][0]["M_y"], -40.0, places=6)
        knoten = verlauf["knoten"]["K2"]
        self.assertEqual(knoten["lage"], [4.0, 0.0, 0.0])
        self.assertEqual(len(knoten["phi"]), 3)
        self.assertIn("L1", antwort.daten["achsen"])

    def test_teilen_mit_einem_punkt_im_raum(self):
        d = im_projekt().als_dict()
        antwort = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "u1", "aktion": "teilen", "linie": "L1",
            "punkt": [1.0, 0.5, -0.5]})
        self.assertEqual((antwort.status, antwort.daten["neu"]), (200, ["L2"]))
        knoten = {k["kennung"]: (k["x"], k["y"], k["z"])
                  for k in antwort.daten["balkensystem"]["knoten"]}
        self.assertEqual(knoten["K3"], (1.0, 0.0, 0.0))
        falsch = dienst.bearbeite("balkensystem_bearbeiten", {
            "projekt": d, "kennung": "u1", "aktion": "teilen", "linie": "L1", "punkt": [1.0, 0.5]})
        self.assertEqual(falsch.status, 400)
        self.assertIn("3 Zahlen", falsch.daten["fehler"])


if __name__ == "__main__":
    unittest.main()
