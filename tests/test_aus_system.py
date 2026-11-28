"""
Die Nachweise einer Querschnittsanalyse aus einem Balkensystem (Plan vom
2026-11-27, Schritt 12): je Kombination die massgebenden Stellen der Stäbe
als Lastfälle -- gegen die Handrechnung, mit ihren Vorzeichen im Raum, und
was am Ort steht, wenn etwas fehlt.
"""

import unittest

from opencivil.projekt import Projekt
from opencivil.projekt.aus_system import Stabwahl
from opencivil.stabwerk.stellen import IN_DER_ANALYSE
from opencivil.web import dienst
from tests.traeger import traeger


def mit_system(kombination: bool = True):
    """
    Der Einfeldträger von 6 m mit 10 kN/m, sein Querschnitt die Analyse
    «Träger» -- und die nimmt die Stellen dieses Systems: kein Kreis, die
    Werte der Analyse hängen an ihrer Zeichnung, nicht an ihren Lastfällen.
    """
    p = traeger()
    a = p.analyse("Träger")
    s = p.balkensysteme[0]
    s.linien[0].querschnitt = s.querschnitt_aus("Träger", "analyse", a).kennung
    if kombination:
        s.kombination("GZT", (s.lastfaelle[0], 1.35))
    a.aus_system.system = s.kennung
    return p, a, s


def aus_dem_system(p: Projekt, a):
    return p.aufbauen().bauteil(a.kennung).aus_system


class TestStellen(unittest.TestCase):
    def test_einfeldtraeger_gegen_die_handrechnung(self):
        """max M = 1.35 · 10 · 6²/8 = 60.75 kNm in der Mitte, max V = 1.35 · 30 = 40.5 kN am Lager."""
        p, a, _ = mit_system()
        aus = aus_dem_system(p, a)
        self.assertEqual(aus.staebe, ["L1"])
        self.assertEqual([n for n, _ in aus.stellen],
                         ["GZT, L1 bei x = 3.00 m", "GZT, L1 bei x = 0.00 m"])
        self.assertEqual([s.gruende for _, s in aus.stellen], [("max M_y",), ("max |V_z|",)])
        feld, lager = aus.lastfaelle
        self.assertAlmostEqual(feld.M_y_Ed, 60.75, places=9)
        self.assertAlmostEqual(feld.V_z_Ed, 0.0, places=9)
        self.assertAlmostEqual(lager.V_z_Ed, 40.5, places=9)
        self.assertAlmostEqual(lager.M_y_Ed, 0.0, places=9)
        for fall in aus.lastfaelle:
            for feld_ in ("N_Ed", "M_z_Ed", "V_y_Ed", "T_Ed"):
                self.assertEqual(getattr(fall, feld_), 0.0)

    def test_eine_stelle_mit_mehreren_gruenden(self):
        """Am Kragarm sind das kleinste M und das grösste |V| an der Einspannung: eine Stelle."""
        p, a, s = mit_system()
        s.lager.clear()
        s.lager_an((0, 0), "eingespannt")
        (name, stelle), = aus_dem_system(p, a).stellen
        self.assertEqual(name, "GZT, L1 bei x = 0.00 m")
        self.assertEqual(stelle.gruende, ("min M_y", "max |V_z|"))
        self.assertAlmostEqual(stelle.werte["M_y"], -1.35 * 10e3 * 6 ** 2 / 2, delta=1e-6)
        self.assertAlmostEqual(abs(stelle.werte["V_z"]), 1.35 * 10e3 * 6, delta=1e-6)

    def test_an_einem_sprung_die_seite(self):
        """
        30 kNm in der Mitte: M springt dort von -15 auf +15 kNm oder umgekehrt
        -- je Seite eine Stelle, und der Name sagt die Seite. V ist überall
        5 kN: die vorderste Stelle, wo nichts springt.
        """
        p, a, s = mit_system(kombination=False)
        s.lastfaelle[0].name = "M"
        s.linien[0].lasten.clear()
        s.stablast(s.lastfaelle[0], s.linien[0], art="moment", wert=30.0, stelle=50.0)
        s.kombination("GZT", (s.lastfaelle[0], 1.0))
        stellen = dict(aus_dem_system(p, a).stellen)
        mitte = "GZT, L1 bei x = 3.00 m"
        self.assertEqual(set(stellen), {f"{mitte} links", f"{mitte} rechts", "GZT, L1 bei x = 0.00 m"})
        links, rechts = stellen[f"{mitte} links"], stellen[f"{mitte} rechts"]
        self.assertAlmostEqual(abs(links.werte["M_y"]), 15e3, delta=1e-6)
        self.assertAlmostEqual(links.werte["M_y"], -rechts.werte["M_y"], delta=1e-6)
        self.assertEqual({links.gruende, rechts.gruende}, {("max M_y",), ("min M_y",)})
        self.assertEqual(stellen["GZT, L1 bei x = 0.00 m"].gruende, ("max |V_z|",))
        self.assertAlmostEqual(abs(stellen["GZT, L1 bei x = 0.00 m"].werte["V_z"]), 5e3, delta=1e-6)

    def test_unter_einer_einzellast_beide_seiten(self):
        """
        40 kN bei 1.5 m: M = 0.75 · 40 · 1.5 = 45 kNm, links davon V = 30 kN,
        rechts -10 kN. Das grösste M gilt mit beiden.
        """
        p, a, s = mit_system(kombination=False)
        s.linien[0].lasten.clear()
        s.stablast(s.lastfaelle[0], s.linien[0], art="einzellast", wert=40.0, stelle=25.0)
        s.kombination("GZT", (s.lastfaelle[0], 1.0))
        stellen = dict(aus_dem_system(p, a).stellen)
        links, rechts = (stellen[f"GZT, L1 bei x = 1.50 m {s}"] for s in ("links", "rechts"))
        for stelle, v in ((links, 30e3), (rechts, -10e3)):
            self.assertEqual(stelle.gruende[0], "max M_y")
            self.assertAlmostEqual(stelle.werte["M_y"], 45e3, delta=1e-6)
            self.assertAlmostEqual(abs(stelle.werte["V_z"]), abs(v), delta=1e-6)
        self.assertAlmostEqual(links.werte["V_z"], -3 * rechts.werte["V_z"], delta=1e-6)

    def test_nur_die_kombinationen(self):
        """Die Lastfälle des Systems geben keine Stelle -- ohne Kombination steht es grau da."""
        p, a, _ = mit_system(kombination=False)
        aus = aus_dem_system(p, a)
        self.assertEqual(aus.stellen, [])
        self.assertEqual(aus.hinweise, ["Das Balkensystem «Träger» hat noch keine Kombination."])

    def test_im_raum_kehren_sich_m_z_und_v_y_um(self):
        """
        Ein Kragarm von 4 m im Raum: am Ende 10 kN nach unten, 5 kN in y und
        2 kNm um x. An der Einspannung zieht M_z des Stabs, 20 kNm, seine
        Seite +y -- vom Anfang her gesehen rechts. In der Analyse zieht ein
        positives M_z links: dort sind es -20 kNm.
        """
        p = Projekt(name="Raum")
        p.beton("C30/37")
        p.stahl("B500B")
        a = p.analyse("Kragarm")
        s = p.balkensystem3d("Kragarm")
        q = s.querschnitt_aus("Kragarm", "analyse", a)
        s.linie((0, 0, 0), (4, 0, 0), querschnitt=q, material=s.beton("b1"))
        s.lager_an((0, 0, 0), "eingespannt")
        lf = s.lastfall("P")
        s.knotenlast(lf, (4, 0, 0), 10.0)
        s.knotenlast(lf, (4, 0, 0), 5.0, richtung="y")
        s.knotenlast(lf, (4, 0, 0), 2.0, art="moment", richtung="x")
        s.kombination("GZT", (lf, 1.0))
        a.aus_system.system = s.kennung
        aufbau = p.aufbauen()
        (name, stelle), = aufbau.bauteil(a.kennung).aus_system.stellen
        self.assertEqual(name, "GZT, L1 bei x = 0.00 m")
        self.assertEqual(stelle.gruende, ("min M_y", "min M_z", "max |V_z|", "max |V_y|", "max |T|"))
        for groesse, soll in (("M_y", -40e3), ("M_z", -20e3), ("T", 2e3), ("V_z", 10e3)):
            self.assertAlmostEqual(stelle.werte[groesse], soll, delta=1e-6)
        befund = aufbau.befund_im_aufbau(aufbau.bauteil(s.kennung).objekt.rechnung.id)
        roh = befund.verlaeufe("GZT")["L1"].bei(0.0)
        for groesse, vorzeichen in IN_DER_ANALYSE.items():
            self.assertEqual(stelle.werte[groesse], vorzeichen * roh[groesse] + 0.0)
        self.assertAlmostEqual(abs(stelle.werte["V_y"]), 5e3, delta=1e-6)


class TestNachweise(unittest.TestCase):
    def test_die_nachweise_laufen_ueber_die_stellen(self):
        """Neben dem eigenen Lastfall stehen die beiden Stellen in der Biegung."""
        p, a, _ = mit_system()
        a.lastfall("Von Hand", M_y_Ed=10.0)
        e = p.rechnen()
        faelle = {u.fall for u in e.loesung.urteile
                  if u.raum == "querschnittsanalyse.a1.nachweis.mn"}
        self.assertEqual(faelle, {"Von Hand", "GZT, L1 bei x = 3.00 m", "GZT, L1 bei x = 0.00 m"})

    def test_die_herleitung_steht_vor_den_nachweisen(self):
        p, a, _ = mit_system()
        aufbau = p.aufbauen()
        teil = aufbau.bauteil(a.kennung)
        self.assertEqual(teil.vorab, ["querschnittsanalyse.a1.aus_system"])
        ziele = aufbau.berichtsziele()
        erster = min(ziele.index(n.id) for _, _, n in teil.nachweise)
        self.assertEqual(ziele.index(teil.vorab[0]), erster - 1)
        self.assertEqual(teil.ziele()[0], teil.vorab[0])

    def test_ein_eigener_name_bleibt_der_eigene(self):
        """Heisst ein eigener Lastfall wie eine Stelle, bekommt die Stelle eine Nummer."""
        p, a, _ = mit_system()
        a.lastfall("GZT, L1 bei x = 3.00 m", M_y_Ed=10.0)
        namen = [n for n, _ in aus_dem_system(p, a).stellen]
        self.assertEqual(namen[0], "GZT, L1 bei x = 3.00 m (2)")

    def test_ohne_system_nichts(self):
        p, a, _ = mit_system()
        a.aus_system.system = ""
        teil = p.aufbauen().bauteil(a.kennung)
        self.assertIsNone(teil.aus_system)
        self.assertEqual(teil.vorab, [])


class TestAmOrt(unittest.TestCase):
    """Was fehlt, steht grau an der Analyse -- sie rechnet mit ihren eigenen Lastfällen weiter."""

    def test_ein_geloeschtes_system(self):
        p, a, _ = mit_system()
        a.aus_system.system = "r9"
        aufbau = p.aufbauen()
        satz = "Das gewählte Balkensystem gibt es nicht mehr – ein anderes wählen."
        self.assertEqual(aufbau.bauteil(a.kennung).aus_system.hinweise, [satz])
        self.assertIn(f"Querschnittsanalyse 'Träger': {satz}", [w.text for w in aufbau.warnungen])

    def test_ein_gewaehlter_stab_der_keiner_mehr_ist(self):
        p, a, _ = mit_system()
        a.aus_system.stabwahl = Stabwahl.GEWAEHLT
        a.aus_system.staebe = ["L1", "L9"]
        aus = aus_dem_system(p, a)
        self.assertEqual(aus.hinweise, ["L9 ist im System kein Stab mehr."])
        self.assertEqual(len(aus.stellen), 2)
        self.assertEqual(aus.kandidaten, [("L1", "Träger")])

    def test_kein_stab_mit_diesem_querschnitt(self):
        p, a, s = mit_system()
        s.linien[0].querschnitt = s.querschnitte[0].kennung
        self.assertEqual(aus_dem_system(p, a).hinweise,
                         ["Im System hat noch kein Stab «Träger» als Querschnitt."])

    def test_noch_kein_stab_gewaehlt(self):
        p, a, _ = mit_system()
        a.aus_system.stabwahl = Stabwahl.GEWAEHLT
        self.assertEqual(aus_dem_system(p, a).hinweise, ["Noch kein Stab gewählt."])


class TestZwischenspeicher(unittest.TestCase):
    def test_eine_analyse_im_system_rechnet_die_stellen_neu(self):
        """
        «Stellen» nimmt die Stellen des gewählten Stabs, dessen Querschnitt
        die Analyse «Träger» ist. Ändert sich nur «Träger», gilt auch
        «Stellen» nicht mehr -- über zwei Stufen.
        """
        p, a, s = mit_system()
        a.aus_system.system = ""
        stellen = p.analyse("Stellen")
        stellen.aus_system.system = s.kennung
        stellen.aus_system.stabwahl = Stabwahl.GEWAEHLT
        stellen.aus_system.staebe = ["L1"]
        self.assertEqual(p.bezuege_von(stellen.kennung), [a.kennung, s.kennung])
        d = p.als_dict()
        dienst.SPEICHER.leeren()
        dienst.bearbeite("rechnen", {"projekt": d})
        dienst.SPEICHER.treffer = dienst.SPEICHER.fehlgriffe = 0
        d["querschnittsanalysen"][0]["knoten"][2]["z"] = 700.0
        antwort = dienst.bearbeite("rechnen", {"projekt": d})
        self.assertEqual((dienst.SPEICHER.treffer, dienst.SPEICHER.fehlgriffe), (0, 3))
        daten = antwort.daten["zeichendaten"][stellen.kennung]["aus_system"]
        self.assertEqual([(z["name"], z["gruende"]) for z in daten["stellen"]],
                         [("GZT, L1 bei x = 3.00 m", "max M_y"),
                          ("GZT, L1 bei x = 0.00 m", "max |V_z|")])
        self.assertAlmostEqual(daten["stellen"][0]["M_y_Ed"], 60.75, places=9)


if __name__ == "__main__":
    unittest.main()
