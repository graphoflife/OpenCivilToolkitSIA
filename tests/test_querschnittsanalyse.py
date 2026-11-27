"""
Die Querschnittsanalyse: Beschreibung, Aufbau und Nachweise.

Hier zuerst die Beschreibung -- was gespeichert wird und wie es sich liest.
"""

import unittest

from opencivil.projekt import (
    Projekt, ProjektFehler, QALastfallEintrag, QuerschnittsanalyseEintrag,
)
from opencivil.projekt.lesen import inhalt_pruefen
from opencivil.querschnitt.vorlagen import rechteck_der_skripte
from opencivil.web import api
from tests.unfertig import meldung


def balken() -> QuerschnittsanalyseEintrag:
    """
    Das Rechteck 300 × 600 mm mit drei Stäben unten und zwei oben und ein
    Feldmoment -- bis 2026-10-19 die neue Analyse der Oberfläche; die beginnt
    jetzt leer. Das Rechteck der Skripte, wie die Vorlage bis 2026-11-27.
    """
    a = QuerschnittsanalyseEintrag.neu("a1", "Balken")
    a.teile_einsetzen(rechteck_der_skripte(), material="b1", stahl="s1")
    a.lastfall("Tragsicherheit 1", M_y_Ed=100.0)
    return a


class TestBeschreibung(unittest.TestCase):

    def neu(self):
        return balken()

    def test_rundreise(self):
        a = self.neu()
        a.lastfall("Stütze", N_Ed=-800.0, M_y_Ed=120.0, M_z_Ed=-40.0, T_Ed=15.0)
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(a.als_dict()), a)

    def test_im_projekt(self):
        p = Projekt.beispiel()
        p.querschnittsanalysen.append(self.neu())
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)
        self.assertIs(p.querschnittsanalyse("a1"), p.querschnittsanalysen[0])
        self.assertNotEqual(p.freie_kennung("a"), "a1")

    def test_die_vorlage_kommt_aus_dem_kern(self):
        vorlage = api.katalog()["neu"]["querschnittsanalysen"]
        neu = {**vorlage, "kennung": "a1", "name": "Balken"}
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(neu).als_dict(), neu)
        # Leer: nichts gezeichnet, kein Lastfall (Benutzer, 2026-10-19).
        self.assertEqual((vorlage["flaechen"], vorlage["stablinien"], vorlage["lastfaelle"]),
                         ([], [], []))

    def test_materialien_und_wahl(self):
        a = self.neu()
        self.assertEqual(a.materialien(), ["b1", "s1"])
        # Ohne eigene Wahl die Vorgabe: Bemessungswerte und die Parabel.
        self.assertEqual((a.werkstoffsaetze, a.rechenarten), ({}, {}))
        self.assertEqual(a.von("werkstoffsaetze", "b1"), "bemessung")
        self.assertEqual(a.von("rechenarten", "b1"), "parabel")

    def test_doppelte_lastfaelle(self):
        a = self.neu()
        a.lastfaelle.append(QALastfallEintrag(name="Tragsicherheit 1"))
        QuerschnittsanalyseEintrag.aus_dict(a.als_dict())  # Öffnen geht -- gemeldet wird vor dem Rechnen.
        with self.assertRaisesRegex(ProjektFehler,
                                    "«Tragsicherheit 1» ist als Lastfall schon vergeben"):
            inhalt_pruefen(a, "Querschnitt 'Balken'")

    def test_unbekanntes_wird_gemeldet(self):
        roh = self.neu().als_dict()
        roh["stablinien"][0]["art"] = "stueckweise"
        with self.assertRaisesRegex(ProjektFehler,
                                    "Querschnittsanalyse 'Balken', Linie 1: 'stueckweise' "
                                    "gibt es als 'art' nicht"):
            QuerschnittsanalyseEintrag.aus_dict(roh)
        roh = self.neu().als_dict()
        roh["schubwaende"] = [{"von": "K1", "bis": "K2", "schnitte": 9}]
        with self.assertRaisesRegex(ProjektFehler, "9 gibt es als 'schnitte' nicht"):
            QuerschnittsanalyseEintrag.aus_dict(roh)
        # Ein Punkt beim Zeichnen in Python: zwei Zahlen.
        with self.assertRaisesRegex(ProjektFehler, "zwei Zahlen"):
            self.neu().polygon([[0, 0], [300.0], [300, 600]])

    def test_namen_zaehlen_je_art(self):
        """
        Die Namen stehen in Berichten und Meldungen und werden an einer Stelle
        vergeben: je Art ab 1, eine Aussparung heisst so statt «Polygon».
        """
        a = self.neu()
        a.polygon([[100, 100], [200, 100], [200, 200]])
        a.stab(150, 300)
        e = a.elemente()
        self.assertEqual([f["name"] for f in e.polygone], ["Polygon 1", "Aussparung 2"])
        self.assertEqual([s["name"] for s in e.staebe], ["Stab 1"])
        self.assertEqual([l["name"] for l in e.linien], ["Linie 1", "Linie 2"])
        self.assertEqual(e.waende, [])
        # Die Kennung ist die des Elements: an ihr findet die Oberfläche es.
        self.assertEqual([f["kennung"] for f in e.polygone], ["F1", "F2"])
        self.assertEqual([s["kennung"] for s in e.staebe], ["S1"])
        self.assertEqual([l["kennung"] for l in e.linien], ["L1", "L2"])


class TestKnoten(unittest.TestCase):
    """
    Die Elemente hängen an Knoten. Gleiche Koordinaten sind ein Knoten, eine
    Kennung kommt nie wieder, und ein Verweis ins Leere wird gemeldet statt
    still übergangen.
    """

    def test_was_sich_trifft_teilt_den_knoten(self):
        """Im Unterzug enden Wände und Bewehrungslinie in denselben Punkten."""
        a = Projekt.beispiel().querschnittsanalysen[0]
        linie = a.stablinien[0]
        wand = a.schubwaende[0]
        self.assertEqual((wand.von, wand.bis), (linie.von, linie.bis))
        self.assertEqual(len({(k.y, k.z) for k in a.knoten}), len(a.knoten))

    def test_alle_linien_zaehlen_gemeinsam(self):
        a = balken()
        w = a.schubwand([150, 50], [150, 550], stahl="s1")
        h = a.hilfslinie([0, 300], [300, 300])
        self.assertEqual((w.kennung, h.kennung), ("L3", "L4"))
        a.stablinien.pop(0)
        self.assertEqual(a.stablinie([60, 60], [240, 60]).kennung, "L5")

    def test_ein_fehlender_knoten_wird_gemeldet(self):
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.stablinien[0].bis = "K99"
        d = dienst.bearbeite("geometrie", {"projekt": p.als_dict(), "kennung": "a1"}).daten
        self.assertFalse(d["gueltig"])
        self.assertEqual(d["meldungen"][0]["elemente"], ["L1"])
        self.assertIn("K99", d["meldungen"][0]["text"])
        # Die übrigen Elemente heissen weiter wie vorher.
        self.assertEqual([l["element"] for l in d["linien"]], ["Linie 2"])
        # Die Analyse rechnet nicht, das Projekt schon: der Hinweis nennt den Knoten.
        e = p.rechnen()
        self.assertIn("a1", e.aufbau.unfertige)
        self.assertTrue(any("K99" in w for w in e.warnungen), e.warnungen)

    def test_doppelte_kennung_wird_gemeldet(self):
        a = balken()
        a.stablinien[1].kennung = "L1"
        self.assertIn("dieselbe Kennung 'L1'", a.elemente().fehler[0]["text"])

    def test_die_antwort_nennt_die_materialien_der_zeichnung(self):
        """
        Die Werkstoffwahl je Material liest sie dort -- bis 2026-10-18 zählte
        die Oberfläche sie ein zweites Mal.
        """
        p = projekt()
        d = dienst.bearbeite("geometrie", {"projekt": p.als_dict(), "kennung": "a1"}).daten
        self.assertEqual(d["materialien"], p.querschnittsanalysen[0].materialien())
        self.assertEqual(d["materialien"], ["b1", "s1"])

    def test_hilfslinien_heissen_wie_alles_andere_im_kern(self):
        """Die Oberfläche nennt eine Hilfslinie so, wie die Antwort es sagt."""
        p = projekt()
        a = p.querschnittsanalysen[0]
        h = a.hilfslinie([0, 300], [300, 300])
        d = dienst.bearbeite("geometrie", {"projekt": p.als_dict(), "kennung": "a1"}).daten
        self.assertEqual(d["hilfslinien"], [{"element": "Hilfslinie 1", "kennung": h.kennung}])

    def test_das_alte_format_mit_koordinaten_wird_genannt(self):
        """Bis 2026-10-08 trugen die Elemente ihre Punkte selbst -- das liest niemand mehr."""
        alt = {"kennung": "a1", "name": "Alt",
               "flaechen": [{"punkte": [[0, 0], [300, 0], [300, 600]], "material": "b1"}]}
        with self.assertRaisesRegex(ProjektFehler, "Polygon 1: ein Feld 'punkte' gibt es nicht"):
            QuerschnittsanalyseEintrag.aus_dict(alt)


# ===========================================================================
# Aufbau und Nachweise
# ===========================================================================

import math

from opencivil.querschnitt.gesetzwahl import (
    Rechenart, Rechenarten, Rechenwahl, Werkstoffsatz, Wertesaetze,
)
from opencivil.nachweis.rechenwahl import Betonkennwerte, gesetze
from opencivil.web import dienst


def projekt(**schalter) -> Projekt:
    """Ein leeres Projekt mit C30/37, B500B und einer Analyse: Rechteck 300 × 600."""
    p = Projekt(name="Probe")
    p.beton("C30/37")
    p.stahl("B500B")
    a = balken()
    a.lastfaelle = []
    for name, wert in schalter.items():
        setattr(a, name, wert)
    p.querschnittsanalysen.append(a)
    return p


def kasten(p, dicke=80.0, letztes_ende=(50, 50)):
    """Vier Schubwände auf der Bügelachse der Analyse a1 -- eine Zelle."""
    ecken = [[50, 50], [250, 50], [250, 550], [50, 550]]
    enden = ecken[1:] + [list(letztes_ende)]
    for von, bis in zip(ecken, enden):
        p.querschnittsanalysen[0].schubwand(von, bis, dicke=dicke, durchmesser=10.0,
                                            teilung=150.0, schnitte=1, stahl="s1")
    return p


def urteile(ergebnis, art):
    return {u.fall: u for u in ergebnis.urteile_von("a1") if u.art == art}


class TestAufbau(unittest.TestCase):

    def test_bruttoquerschnitt(self):
        e = projekt().rechnen()
        wert = lambda k: e.wert(f"querschnittsanalyse.a1.{k}").groesse
        self.assertAlmostEqual(wert("A").in_einheit(wert("A").anzeige), 180000.0)
        self.assertAlmostEqual(wert("z_S").si, 0.3)
        self.assertAlmostEqual(wert("I_y").si, 0.3 * 0.6 ** 3 / 12)

    def test_aussparung(self):
        p = projekt()
        p.querschnittsanalysen[0].polygon([[100, 200], [200, 200], [200, 400], [100, 400]])
        e = p.rechnen()
        self.assertAlmostEqual(e.wert("querschnittsanalyse.a1.A").groesse.si,
                               0.18 - 0.1 * 0.2)

    def meldung(self, p) -> str:
        """
        Eine Zeichnung, die sich nicht rechnen lässt, hält nur ihre Analyse
        auf (Benutzer, 2026-11-19): sie wird kein Bauteil, ein Hinweis sagt warum.
        """
        e = p.rechnen()
        self.assertIn("a1", e.aufbau.unfertige)
        return "\n".join(e.warnungen)

    def test_stab_ausserhalb(self):
        p = projekt()
        p.querschnittsanalysen[0].stab(5, 300, durchmesser=20, stahl="s1")
        text = self.meldung(p)
        self.assertIn("Querschnittsanalyse 'Balken'", text)
        self.assertIn("Stab 1", text)
        self.assertIn("nicht ganz im Beton", text)

    def test_ueberlappung(self):
        p = projekt()
        p.querschnittsanalysen[0].polygon([[250, 0], [500, 0], [500, 100], [250, 100]],
                                          material="b1")
        self.assertIn("überlappen", self.meldung(p))

    def test_wand_ausserhalb(self):
        p = projekt()
        p.querschnittsanalysen[0].schubwand([150, -50], [150, 550], stahl="s1")
        self.assertIn("Wand 1", self.meldung(p))

    def test_geloeschtes_material(self):
        """Ein Verweis ins Leere hält die Analyse an und nennt, was fehlt -- nur sie."""
        p = projekt()
        p.querschnittsanalysen[0].flaechen[0].material = "b7"
        self.assertRegex(meldung(p), "Polygon 1: das gewählte Material gibt es nicht mehr")


class TestBiegung(unittest.TestCase):

    def test_grad_ist_widerstand_durch_einwirkung(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=150.0)
        u = urteile(p.rechnen(), "M-N")["Feld"]
        self.assertAlmostEqual(u.erfuellungsgrad.si,
                               u.widerstand.groesse.si / u.einwirkung.groesse.si)
        self.assertEqual(u.einwirkung.groesse.si, 150e3)

    def test_einachsig_uebergeht_m_z(self):
        p = projekt(einachsig=True)
        a = p.querschnittsanalysen[0]
        a.lastfall("ohne", M_y_Ed=150.0)
        a.lastfall("mit", M_y_Ed=150.0, M_z_Ed=80.0)
        u = urteile(p.rechnen(), "M-N")
        self.assertAlmostEqual(u["ohne"].erfuellungsgrad.si, u["mit"].erfuellungsgrad.si)

    def test_schief_traegt_weniger(self):
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.lastfall("gerade", N_Ed=-500.0, M_y_Ed=150.0)
        a.lastfall("schief", N_Ed=-500.0, M_y_Ed=150.0, M_z_Ed=60.0)
        u = urteile(p.rechnen(), "M-N")
        self.assertLess(u["schief"].erfuellungsgrad.si, u["gerade"].erfuellungsgrad.si)

    def test_reine_normalkraft(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("Zug", N_Ed=200.0)
        e = p.rechnen()
        u = urteile(e, "M-N")["Zug"]
        zug = e.wert("querschnittsanalyse.a1.nachweis.mn.N_Rd_zug").groesse.si
        self.assertAlmostEqual(u.erfuellungsgrad.si, zug / 200e3)

    def test_jenseits_der_normalkraft(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("viel", N_Ed=-9000.0, M_y_Ed=10.0)
        u = urteile(p.rechnen(), "M-N")["viel"]
        self.assertFalse(u.erfuellt)

    def test_laengszugkraft_senkt_den_widerstand(self):
        def grad(laengs):
            p = kasten(projekt(laengszugkraft=laengs))
            p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=150.0, V_z_Ed=150.0)
            return urteile(p.rechnen(), "M-N")["Feld"].erfuellungsgrad.si
        self.assertLess(grad(True), grad(False))

    def test_charakteristisch_traegt_mehr(self):
        def grad(satz):
            p = projekt(werkstoffsaetze={"b1": satz, "s1": satz})
            p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=150.0)
            return urteile(p.rechnen(), "M-N")["Feld"].erfuellungsgrad.si
        self.assertGreater(grad("charakteristisch"), grad("bemessung"))

    def test_spannungsblock_nahe_der_parabel(self):
        def grad(gesetz):
            p = projekt(rechenarten={"b1": gesetz})
            p.querschnittsanalysen[0].lastfall("Feld", N_Ed=-800.0, M_y_Ed=150.0)
            return urteile(p.rechnen(), "M-N")["Feld"].erfuellungsgrad.si
        self.assertAlmostEqual(grad("block") / grad("parabel"), 1.0, delta=0.05)


class TestGesetzeWieDiePlatte(unittest.TestCase):
    """
    Mit derselben Wahl rechnet der gezeichnete Querschnitt denselben Beton
    wie die Platte -- ein Modell, gebaut an einer Stelle. Bis 2026-10-16 nahm
    er den Beiwert der Parabel aus E_cd und baute ihn selbst.
    """

    def test_parabel_und_block_in_beiden_wertesaetzen(self):
        for satz in Werkstoffsatz:
            for art in (Rechenart.PARABEL, Rechenart.BLOCK):
                with self.subTest(satz=satz.value, art=art.value):
                    p = projekt(werkstoffsaetze={"b1": satz.value},
                                rechenarten={"b1": art.value})
                    aufbau = p.aufbauen()
                    analyse = aufbau.querschnittsanalysen["a1"]
                    loesung = aufbau.werk.loese(
                        *(b.wert_id for b in analyse.werkstoffbezuege()))
                    wert = lambda kid: loesung.werte[kid].groesse.si
                    werkstoffe, index = analyse.werkstoffe(wert, analyse.wahl)
                    stoff = aufbau.baustoffe["b1"]
                    w = lambda k: abs(wert(stoff.id_von(k)))
                    platte = gesetze(Rechenwahl(saetze=Wertesaetze.alle(satz),
                                                arten=Rechenarten.alle(art)), Betonkennwerte(
                        f_c=w(satz.beton), E_c=w("E_cm"), eps_c1d=w("eps_c1d"),
                        eps_c2d=w("eps_c2d"))).beton
                    self.assertEqual(werkstoffe[index(stoff)].gesetz, platte)


class TestSchub(unittest.TestCase):

    def test_zwei_stege_je_die_haelfte(self):
        p = kasten(projekt())
        p.querschnittsanalysen[0].lastfall("Feld", V_z_Ed=150.0)
        u = urteile(p.rechnen(), "V+T")["Feld"]
        # Je Steg seine ganze Kraft, 75 kN -- nicht 150 kN/m auf 500 mm.
        self.assertAlmostEqual(u.einwirkung.groesse.si, 75e3, delta=1e-3)
        self.assertEqual(u.einwirkung.einheit.name, "kN")
        self.assertAlmostEqual(u.erfuellungsgrad.si,
                               u.widerstand.groesse.si / u.einwirkung.groesse.si)

    def test_ohne_wand(self):
        p = projekt()
        p.querschnittsanalysen[0].lastfall("Feld", V_z_Ed=100.0)
        u = urteile(p.rechnen(), "V+T")["Feld"]
        self.assertFalse(u.erfuellt)
        self.assertIn("keine Schubwand", u.hinweis)

    def test_einachsig_ohne_v_y(self):
        p = projekt(einachsig=True)
        p.querschnittsanalysen[0].lastfall("quer", M_y_Ed=10.0, V_y_Ed=100.0)
        self.assertEqual(urteile(p.rechnen(), "V+T"), {})


class TestKennzahlen(unittest.TestCase):
    """
    Die Kennzahlen des gezeichneten Querschnitts, wie die der Platte -- immer
    gerechnet, auch ohne Lastfall. Am Rechteck 300 × 600 der Vorlage.
    """

    def kennzahlen(self, p):
        teil = "querschnittsanalyse.a1.kennzahlen."
        return {k[len(teil):]: w.groesse for k, w in p.rechnen().loesung.werte.items()
                if k.startswith(teil)}

    def test_ohne_lastfall_alle_vier_seiten(self):
        k = self.kennzahlen(projekt())
        for seite in ("unten", "oben", "links", "rechts"):
            self.assertIn(f"M_Rd_{seite}", k)
            self.assertIn(f"x_d_{seite}", k)
        self.assertGreater(k["M_Rd_unten"].si, 0.0)
        self.assertLess(k["M_Rd_oben"].si, 0.0)
        # Ohne Schubwand kein Widerstand gegen Querkraft.
        self.assertNotIn("V_z_Rd", k)

    def test_bewehrungsmass_und_zugwiderstand(self):
        p = projekt()
        e = p.rechnen()
        A = e.wert("querschnittsanalyse.a1.A").groesse.si
        A_s = e.wert("querschnittsanalyse.a1.A_s").groesse.si
        k = self.kennzahlen(p)
        self.assertAlmostEqual(k["bewehrungsmass"].si, A_s * 7850.0 / A)
        # Reiner Zug: jeder Stab fliesst, f_sd = 500 / 1.15.
        self.assertAlmostEqual(k["N_Rd_zug"].si, A_s * 500e6 / 1.15, delta=1.0)
        self.assertLess(k["N_Rd_druck"].si, 0.0)

    def test_einachsig_nur_unten_und_oben(self):
        k = self.kennzahlen(projekt(einachsig=True))
        self.assertIn("M_Rd_unten", k)
        self.assertNotIn("M_Rd_links", k)
        self.assertNotIn("x_d_rechts", k)

    def test_ohne_obere_bewehrung_kein_x_d_oben(self):
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.stablinien = [l for l in a.stablinien
                        if {k.z for k in a.knoten if k.kennung in (l.von, l.bis)} == {50.0}]
        k = self.kennzahlen(p)
        self.assertIn("x_d_unten", k)
        self.assertNotIn("x_d_oben", k)
        self.assertIn("M_Rd_oben", k)

    def test_querkraftwiderstand_wie_der_nachweis(self):
        """
        Mit dem Widerstand selbst als Querkraft ist der Nachweis der
        Schubwände gerade erfüllt: dieselbe Verteilung, derselbe Widerstand.
        """
        p = kasten(projekt())
        k = self.kennzahlen(p)
        for kurz in ("V_z_Rd", "V_y_Rd", "T_Rd"):
            self.assertIn(kurz, k)
        p.querschnittsanalysen[0].lastfall("V_Rd", V_z_Ed=k["V_z_Rd"].si / 1e3)
        p.querschnittsanalysen[0].lastfall("T_Rd", T_Ed=k["T_Rd"].si / 1e3)
        u = urteile(p.rechnen(), "V+T")
        self.assertAlmostEqual(u["V_Rd"].erfuellungsgrad.si, 1.0, places=6)
        self.assertAlmostEqual(u["T_Rd"].erfuellungsgrad.si, 1.0, places=6)

    def test_im_dienst(self):
        d = dienst.bearbeite("rechnen", {"projekt": projekt().als_dict()}).daten
        namen = [z["bezeichnung"] for z in d["kennzahlen"]["a1"]["zeilen"]]
        self.assertEqual(namen[:3], ["Bewehrungsmass", "Momentenwiderstand, Zug unten",
                                     "Momentenwiderstand, Zug oben"])


class TestRichtungen(unittest.TestCase):

    def test_rissmoment_wie_bei_der_platte(self):
        """
        Rechteck 300 × 600: W = b·h²/6 und k_t aus h/3 -- dieselbe Zahl wie
        bei der Platte, um y mit h = 600, um z mit h = 300.
        """
        from opencivil.nachweis.rissgroessen import rissmoment_rechteck as rissmoment
        e = projekt(sproede=True).rechnen()
        alle = {u.fall: u for u in e.loesung.urteile if u.raum.endswith("sproede")}
        f_ctm = e.wert("beton.b1.f_ctm").groesse.si
        um_y = rissmoment(h=0.6, b=0.3, f_ctm=f_ctm).M_Riss
        um_z = rissmoment(h=0.3, b=0.6, f_ctm=f_ctm).M_Riss
        for fall, erwartet in (("Zug unten", um_y), ("Zug oben", um_y),
                               ("Zug links", um_z), ("Zug rechts", um_z)):
            with self.subTest(fall=fall):
                self.assertAlmostEqual(alle[fall].einwirkung.groesse.si, erwartet,
                                       delta=1e-6 * erwartet)

    def test_duktilitaet_nur_wo_gezogen_wird(self):
        p = projekt(duktilitaet=True)
        p.querschnittsanalysen[0].stablinien = p.querschnittsanalysen[0].stablinien[:1]
        e = p.rechnen()
        # Gezeigt wird die ungünstigere Richtung; gerechnet sind alle mit Zugstab.
        alle = [u for u in e.loesung.urteile if u.raum.endswith("duktilitaet")]
        self.assertNotIn("Zug oben", [u.fall for u in alle])
        self.assertIn("Zug unten", [u.fall for u in alle])


class TestDienst(unittest.TestCase):

    def test_rechnen_ueber_den_dienst(self):
        p = kasten(projekt(duktilitaet=True, sproede=True))
        p.querschnittsanalysen[0].lastfall("Feld", M_y_Ed=120.0, V_z_Ed=80.0, T_Ed=10.0)
        antwort = dienst.bearbeite("rechnen", {"projekt": p.als_dict()})
        self.assertEqual(antwort.status, 200, antwort.daten)
        raeume = {u["raum"] for u in antwort.daten["urteile"]}
        self.assertTrue(raeume and all(r.startswith("querschnittsanalyse.a1") for r in raeume))
        self.assertIn("a1", antwort.daten["zusammenfassungen"])


class TestGeometrieEndpunkt(unittest.TestCase):
    """Was das Zeichenfenster bekommt: alle Meldungen, jede am Element."""

    def frage(self, p, kennung="a1"):
        return dienst.bearbeite("geometrie", {"projekt": p.als_dict(), "kennung": kennung})

    def test_gueltig(self):
        d = self.frage(projekt()).daten
        self.assertTrue(d["gueltig"])
        self.assertEqual(d["meldungen"], [])
        self.assertAlmostEqual(d["brutto"]["z_S"], 300.0)
        # Unten drei Stäbe auf 200 mm: zwei Felder zu 100 mm.
        self.assertEqual(d["linien"][0]["felder"], 2)
        self.assertAlmostEqual(d["linien"][0]["teilung"], 100.0)

    def test_alle_meldungen_auf_einmal(self):
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.stab(5, 300, durchmesser=20, stahl="s1")
        a.stab(150, 300, durchmesser=0, stahl="s1")
        d = self.frage(p).daten
        self.assertFalse(d["gueltig"])
        # Der Text nennt den Namen, die Meldung zeigt mit der Kennung aufs Element.
        self.assertEqual([m["elemente"] for m in d["meldungen"]], [["S1"], ["S2"]])
        self.assertTrue(d["meldungen"][0]["text"].startswith("Stab 1"))

    def test_ueberlappung_nennt_beide(self):
        p = projekt()
        p.querschnittsanalysen[0].polygon([[250, 0], [500, 0], [500, 100], [250, 100]],
                                          material="b1")
        d = self.frage(p).daten
        self.assertEqual(d["meldungen"][0]["elemente"], ["F1", "F2"])

    def test_zellen_der_waende(self):
        d = self.frage(kasten(projekt())).daten
        self.assertEqual(len(d["zellen"]), 1)
        self.assertAlmostEqual(d["zellen"][0]["flaeche"], 200 * 500)

    def test_unbekannte_analyse(self):
        self.assertEqual(self.frage(projekt(), "a9").status, 400)

    def test_ein_geloeschter_stahl_steht_am_element(self):
        """
        Zeigt eine Linie auf einen Stahl, den es nicht mehr gibt, sagt es die
        Zeichnung an ihr, mit dem Satz des Kerns -- grau, denn es fehlt nur
        eine Wahl. Bis 2026-11-19 pruefte sie nur das Material der Polygone,
        und die Linie stand still da.
        """
        p = projekt()
        linie = p.querschnittsanalysen[0].stablinien[0]
        linie.stahl = "s9"
        d = self.frage(p).daten
        self.assertFalse(d["gueltig"])
        self.assertEqual([(m["elemente"], m["fehler"]) for m in d["meldungen"]],
                         [([linie.kennung], False)])
        self.assertEqual(d["meldungen"][0]["text"],
                         "Linie 1: das gewählte Material gibt es nicht mehr – eines wählen.")

    def test_ein_beton_als_stahl_ist_falsch(self):
        p = projekt()
        p.querschnittsanalysen[0].stablinien[0].stahl = "b1"
        m = self.frage(p).daten["meldungen"][0]
        self.assertTrue(m["fehler"])
        self.assertIn("ist kein Betonstahl", m["text"])

    def test_noch_nichts_gezeichnet_meldet_nichts(self):
        """Eine neue Analyse: nichts fehlt, was eine Meldung waere -- die Liste sagt «noch nichts»."""
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.flaechen, a.staebe, a.stablinien, a.schubwaende = [], [], [], []
        self.assertEqual(self.frage(p).daten["meldungen"], [])

    def test_bewehrung_ohne_polygon_ist_unfertig_nicht_falsch(self):
        p = projekt()
        p.querschnittsanalysen[0].flaechen = []
        d = self.frage(p).daten
        self.assertEqual([(m["text"], m["fehler"]) for m in d["meldungen"]],
                         [("Es gibt kein Polygon mit Material – nichts, was trägt.", False)])

    def test_ohne_ueberdeckung_nichts_dazu(self):
        d = self.frage(projekt()).daten
        self.assertIsNone(d["polygone"][0]["ueberdeckung"])
        self.assertTrue(all(l["ueberdeckt"] is None for l in d["linien"]))

    def test_ueberdeckung(self):
        """
        c = 30 am Rechteck 300 × 600: das Hilfspolygon, und wohin die Bewehrung
        muss. Die Stäbe der Vorlage liegen 50 vom Rand, weit genug -- sie
        bleiben. Ein ⌀20 in der Ecke kommt nach (40, 40).
        """
        p = projekt()
        a = p.querschnittsanalysen[0]
        a.flaechen[0].ueberdeckung = 30.0
        a.stab(0, 0, durchmesser=20, stahl="s1")
        d = self.frage(p).daten
        self.assertEqual(sorted(map(tuple, d["polygone"][0]["ueberdeckung"])),
                         [(30, 30), (30, 570), (270, 30), (270, 570)])
        self.assertEqual(d["staebe"][0]["ueberdeckt"], [40.0, 40.0])
        lagen = {k.kennung: [k.y, k.z] for k in a.knoten}
        for l, info in zip(a.stablinien, d["linien"]):
            self.assertEqual(info["ueberdeckt"], [lagen[l.von], lagen[l.bis]])

    def test_zellen_wie_im_nachweis(self):
        """
        Ein Wandende, das um 0.4 µm neben der Ecke liegt: der Nachweis sieht
        eine Zelle (seine Toleranz ist 1 µm), also auch das Fenster. Gesucht
        wurde dort einmal in Millimetern, und dann fehlte die Zelle im Bild.
        """
        p = kasten(projekt(), letztes_ende=(50.0, 50.0004))
        self.assertEqual(len(self.frage(p).daten["zellen"]), 1)
        p.querschnittsanalysen[0].lastfall("Torsion", T_Ed=10.0)
        self.assertTrue(urteile(p.rechnen(), "V+T")["Torsion"].erfuellt)


class TestDiagramme(unittest.TestCase):
    """
    Die Diagramme der Analyse: was sie zeigen, muss zu den Nachweisen passen.

    Am Unterzug des Beispiels -- symmetrisch, mit einer Zelle aus vier
    Wänden, M_y = 150 kNm, V_z = 150 kN, T = 15 kNm.
    """

    @classmethod
    def setUpClass(cls):
        projekt = Projekt.beispiel()
        cls.antwort = dienst.bearbeite(
            "analysediagramme", {"projekt": projekt.als_dict(), "kennung": "a1"})
        cls.d = cls.antwort.daten["diagramme"]
        cls.fall = cls.d["faelle"][0]

    def test_antwort(self):
        self.assertEqual(self.antwort.status, 200)
        self.assertEqual(self.d["name"], "Unterzug")
        z = self.d["zeichnung"]
        self.assertEqual(len(z["polygone"]), 1)
        self.assertEqual(len(z["staebe"]), 5)
        self.assertEqual(len(self.fall["schub"]["waende"]), 4)
        self.assertEqual(z["schwerpunkt"], [150.0, 300.0])

    def test_das_bild_des_querschnitts_kennt_seine_baustoffe(self):
        """Je Polygon die Art und der Name seines Baustoffs, je Stab der Stahl -- für Farben und Legende."""
        z = self.d["zeichnung"]
        p = z["polygone"][0]
        self.assertEqual((p["material"], p["stoff"], p["name"]), ("beton", "C30/37", "Polygon 1"))
        self.assertEqual({s["stahl"] for s in z["staebe"]}, {"B500B"})
        self.assertTrue(all(s["name"] for s in z["staebe"]))

    def test_den_querschnitt_gibt_es_auch_ohne_lastfall(self):
        """Ohne Lastfall kein Fall, aber das Bild des Querschnitts -- es braucht keinen Nachweis."""
        d = Projekt.beispiel().als_dict()
        a1, = [q for q in d["querschnittsanalysen"] if q["kennung"] == "a1"]
        a1["lastfaelle"] = []
        antwort = dienst.bearbeite("analysediagramme", {"projekt": d, "kennung": "a1"})
        self.assertEqual(antwort.status, 200)
        diagramme = antwort.daten["diagramme"]
        self.assertEqual(diagramme["faelle"], [])
        self.assertEqual(len(diagramme["zeichnung"]["polygone"]), 1)
        self.assertEqual(diagramme["zeichnung"]["schwerpunkt"], [150.0, 300.0])

    def test_der_widerstand_des_nachweises(self):
        """Je Lastfall der Bruchzustand, gegen den gemessen wurde -- alle drei Grössen."""
        w = self.fall["widerstand"]
        self.assertAlmostEqual(w["N"], 0.0, places=3)
        self.assertAlmostEqual(w["M_y"], 211.8, places=1)
        self.assertAlmostEqual(w["M_z"], 0.0, places=3)

    def test_der_widerstand_liegt_auf_dem_diagramm(self):
        """
        Bei M_z = 0 liegt er auf dem rechten Ast; der Ast bei N = 0 ist der
        Widerstand des Nachweises. Und es gibt nur noch dieses eine
        Interaktionsdiagramm -- je Lastfall keine eigene Linie mehr.
        """
        rechts = [p for p in self.d["interaktion"]["punkte"] if p["M_y"] > 0]
        oben = min((p for p in rechts if p["N"] >= 0), key=lambda p: p["N"])
        unten = max((p for p in rechts if p["N"] < 0), key=lambda p: p["N"])
        t = oben["N"] / (oben["N"] - unten["N"])
        self.assertAlmostEqual(oben["M_y"] + t * (unten["M_y"] - oben["M_y"]),
                               self.fall["widerstand"]["M_y"], delta=0.5)
        self.assertNotIn("mn", self.fall)
        self.assertNotIn("kontur", self.fall)

    def test_bei_festem_n_rundum_wie_der_nachweis(self):
        """Bei N = N_Ed geschnitten: Zug unten ergibt dasselbe M_y wie der Nachweis."""
        i = dienst.bearbeite("analysediagramme", {
            "projekt": Projekt.beispiel().als_dict(), "kennung": "a1",
            "schnitt": {"fest": "N", "wert": 0.0}}).daten["diagramme"]["interaktion"]
        self.assertEqual(len(i["punkte"]), 72)
        self.assertAlmostEqual(max(p["M_y"] for p in i["punkte"]),
                               self.fall["widerstand"]["M_y"], places=6)
        # Symmetrisch: links wie rechts gleich viel M_z.
        m_z = [p["M_z"] for p in i["punkte"]]
        self.assertAlmostEqual(max(m_z), -min(m_z), places=3)

    def test_der_bruchzustand_im_schnitt(self):
        b = self.fall["bruch"]
        # Nulllinie waagrecht über die ganze Breite, Druckzone oben.
        (y0, z0), (y1, z1) = b["nulllinie"]
        self.assertEqual(sorted([y0, y1]), [0.0, 300.0])
        self.assertAlmostEqual(z0, z1)
        self.assertAlmostEqual(600.0 - z0, b["x"], places=6)
        self.assertAlmostEqual(b["d"], 550.0)
        unten = [s["eps"] for s in b["staebe"] if s["z"] < 300.0]
        self.assertTrue(all(e > 0.0 for e in unten))
        zone = b["druckzone"][0]["punkte"]
        self.assertTrue(all(p[1] >= z0 - 1e-9 for p in zone))

    def test_der_schubfluss_haelt_das_gleichgewicht(self):
        """Die Wandkräfte zusammen sind V_y, V_z und T um den Schwerpunkt."""
        schub = self.fall["schub"]
        f_y = f_z = moment = 0.0
        for s in schub["waende"]:
            dy, dz = s["bis"][0] - s["von"][0], s["bis"][1] - s["von"][1]
            laenge = math.hypot(dy, dz)
            kraft_y, kraft_z = s["q"] * dy / 1e3, s["q"] * dz / 1e3  # kN
            f_y += kraft_y
            f_z += kraft_z
            my, mz = (s["von"][0] + s["bis"][0]) / 2 - 150.0, (s["von"][1] + s["bis"][1]) / 2 - 300.0
            moment += (my * kraft_z - mz * kraft_y) / 1e3  # kNm
            self.assertGreater(laenge, 0.0)
        self.assertAlmostEqual(f_y, 0.0, places=6)
        self.assertAlmostEqual(f_z, 150.0, places=6)
        self.assertAlmostEqual(moment, 15.0, places=6)
        # Dieselbe Wand wie im Nachweis ist massgebend -- mit ganzen Kräften.
        schwach = min(schub["waende"], key=lambda w: w["V_Rd"] / w["V_Ed"])
        self.assertEqual(schwach["grad_text"], "1.75")

    def test_einachsig(self):
        projekt = Projekt.beispiel()
        projekt.querschnittsanalysen[0].einachsig = True
        d = dienst.bearbeite("analysediagramme", {
            "projekt": projekt.als_dict(), "kennung": "a1"}).daten["diagramme"]
        self.assertTrue(d["einachsig"])
        self.assertIsNone(d["interaktion"]["fest"])
        self.assertAlmostEqual(d["faelle"][0]["widerstand"]["M_y"], 211.8, places=1)

    def test_unbekannte_analyse(self):
        antwort = dienst.bearbeite("analysediagramme", {
            "projekt": Projekt.beispiel().als_dict(), "kennung": "a9"})
        self.assertEqual(antwort.status, 400)

    def test_interaktionsdiagramm_ohne_wahl_bei_m_z_null(self):
        i = self.d["interaktion"]
        self.assertEqual((i["fest"], i["wert"]), ("M_z", 0.0))
        self.assertTrue(all(p["M_z"] == 0.0 for p in i["punkte"]))
        # Bei N = 0 reicht er rechts bis zum Widerstand des Nachweises.
        rechts = max(p["M_y"] for p in i["punkte"] if abs(p["N"]) < 40.0)
        self.assertGreater(rechts, 200.0)

    def test_interaktionsdiagramm_mit_wahl(self):
        projekt = Projekt.beispiel().als_dict()
        for fest, wert in (("N", -500.0), ("M_y", 100.0), ("M_z", 40.0)):
            d = dienst.bearbeite("analysediagramme", {
                "projekt": projekt, "kennung": "a1",
                "schnitt": {"fest": fest, "wert": wert}}).daten["diagramme"]["interaktion"]
            with self.subTest(fest=fest):
                self.assertEqual((d["fest"], d["wert"]), (fest, wert))
                self.assertTrue(d["punkte"])
                self.assertTrue(all(abs(p[fest] - wert) < 1e-6 for p in d["punkte"]))

    def test_interaktionsdiagramm_einachsig_ohne_wahl(self):
        projekt = Projekt.beispiel()
        projekt.querschnittsanalysen[0].einachsig = True
        i = dienst.bearbeite("analysediagramme", {
            "projekt": projekt.als_dict(), "kennung": "a1",
            "schnitt": {"fest": "N", "wert": 100.0}}).daten["diagramme"]["interaktion"]
        self.assertIsNone(i["fest"])
        # Der rechte Ast bei N = 0 ist der Widerstand des Nachweises.
        rechts = [p for p in i["punkte"] if p["M_y"] > 0]
        oben = min((p for p in rechts if p["N"] >= 0), key=lambda p: p["N"])
        unten = max((p for p in rechts if p["N"] < 0), key=lambda p: p["N"])
        t = oben["N"] / (oben["N"] - unten["N"])
        self.assertAlmostEqual(oben["M_y"] + t * (unten["M_y"] - oben["M_y"]), 211.8, delta=0.5)

    def test_falscher_schnitt(self):
        antwort = dienst.bearbeite("analysediagramme", {
            "projekt": Projekt.beispiel().als_dict(), "kennung": "a1",
            "schnitt": {"fest": "T", "wert": 0}})
        self.assertEqual(antwort.status, 400)


class TestFaelleOhneBruchzustand(unittest.TestCase):
    """
    Ein Lastfall ohne Einwirkung und einer ohne Moment. Bis 2026-11-19
    fehlte der erste in der Zusammenfassung still, das Diagramm sagte
    «erfüllt, ∞», und beiden fehlte die Karte «Bruchzustand» ohne ein Wort.
    """

    @classmethod
    def setUpClass(cls):
        p = Projekt.beispiel()
        a = p.querschnittsanalysen[0]
        a.lastfall("Leer")
        a.lastfall("Nur N", N_Ed=-500.0)
        cls.projekt = p.als_dict()
        d = dienst.bearbeite("analysediagramme", {"projekt": cls.projekt, "kennung": "a1"})
        cls.faelle = {f["name"]: f for f in d.daten["diagramme"]["faelle"]}

    def test_ohne_einwirkung_steht_er_mit_seinem_satz_in_der_zusammenfassung(self):
        antwort = dienst.rechnen({"projekt": self.projekt})
        zeilen = {z["bezeichnung"]: z for z in antwort["zusammenfassungen"]["a1"]["zeilen"]}
        leer = zeilen["Biegung und Normalkraft – Leer"]
        self.assertTrue(leer["erfuellt"])
        self.assertEqual(leer["hinweis"], "Keine Einwirkung → kein Nachweis.")

    def test_das_diagramm_sagt_den_satz_statt_eines_grades(self):
        self.assertEqual(self.faelle["Leer"]["hinweis"], "Keine Einwirkung → kein Nachweis.")
        # Ohne Moment wird N gegen N_Rd verglichen: ein echter Grad, kein Satz.
        self.assertEqual(self.faelle["Nur N"]["hinweis"], "")
        self.assertEqual(self.faelle["Feld"]["hinweis"], "")

    def test_ohne_bruchzustand_sagt_er_warum(self):
        self.assertIsNone(self.faelle["Nur N"]["bruch"])
        self.assertIn("Ohne Moment gibt es keinen Bruchzustand", self.faelle["Nur N"]["ohne_bruch"])
        self.assertEqual(self.faelle["Leer"]["ohne_bruch"], "Keine Einwirkung → kein Nachweis.")
        self.assertIsNotNone(self.faelle["Feld"]["bruch"])
        self.assertEqual(self.faelle["Feld"]["ohne_bruch"], "")

    def test_ohne_schubfluss_sagt_er_warum(self):
        """
        Der Unterzug hat Schubwände: wer sie ohne Querkraft und Torsion
        belastet, sieht warum es kein Bild gibt. Bis 2026-11-19 fehlte die
        Karte «Schubfluss» ohne ein Wort.
        """
        for name in ("Leer", "Nur N"):
            with self.subTest(name):
                self.assertIsNone(self.faelle[name]["schub"])
                self.assertEqual(self.faelle[name]["ohne_schub"],
                                 "Keine Querkraft und keine Torsion → kein Schubfluss.")
        self.assertIsNotNone(self.faelle["Feld"]["schub"])
        self.assertEqual(self.faelle["Feld"]["ohne_schub"], "")


class TestFaelleOhneSchubwand(unittest.TestCase):
    """
    Derselbe Unterzug ohne Schubwände: belastet sagt der Lastfall, dass eine
    fehlt; unbelastet ist Schub kein Thema, und es gibt keinen Satz.
    """

    def test_der_grund_des_nachweises(self):
        p = Projekt.beispiel()
        a = p.querschnittsanalysen[0]
        a.schubwaende.clear()
        a.lastfall("Nur N", N_Ed=-500.0)
        d = dienst.bearbeite("analysediagramme", {"projekt": p.als_dict(), "kennung": "a1"})
        faelle = {f["name"]: f for f in d.daten["diagramme"]["faelle"]}
        self.assertIsNone(faelle["Feld"]["schub"])
        self.assertEqual(faelle["Feld"]["ohne_schub"],
                         "Es gibt keine Schubwand, die Querkraft oder Torsion aufnehmen könnte.")
        self.assertEqual(faelle["Nur N"]["ohne_schub"], "")


if __name__ == "__main__":
    unittest.main()
