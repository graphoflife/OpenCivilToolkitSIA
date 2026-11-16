"""
Schnitte durch eine Decke: gespeichert wie jedes Teil, und längs jedes die
Schnittkräfte der Platte wie an einem Balken -- mit den Lagern, die er
kreuzt, und den Sprüngen an den Grenzen der Streifen. Ebenso je Unterzug
sein M und V über die ganze Breite, auf den Lagern, auf denen er liegt.
"""

import unittest

from opencivil.decke import schnitt
from opencivil.projekt import beispiele
from opencivil.decke.modell import Decke, Flaechenlast, Lastfall, Linienlager, Platte, Unterzug
from opencivil.decke.rechnung import rechnen
from opencivil.projekt import Projekt
from opencivil.projekt.aufbau.decke import modell_von
from opencivil.web import dienst


def einfeld() -> Projekt:
    """Einfeldplatte 4 × 1 m auf zwei Wänden in x, fest ganz in x, q = 10 kN/m²: m_x = 5·x·(4 − x)."""
    p = Projekt(name="Einfeld")
    d = p.decke("Einfeld", aufteilung="fest", anteil=100.0)
    d.platte([(0, 0), (4, 0), (4, 1), (0, 1)], beton=p.beton("C30/37"), h=200)
    d.lager((0, 0), (0, 1))
    d.lager((4, 0), (4, 1))
    d.plattenlast(d.lastfall("q"), "P1", 10.0)
    return p


def bild(p: Projekt, fall: str = "q", kennung: str = "e1"):
    """Das Bild des Falls, wie die Oberfläche es bekommt."""
    antwort = dienst.bearbeite("decke_ergebnis", {"projekt": p.als_dict(), "kennung": kennung, "fall": fall})
    return antwort.daten["ergebnis"]


def schnitte(p: Projekt, fall: str = "q"):
    """Die Schnitte im Bild des Falls."""
    return bild(p, fall)["schnitte"]


def mit_unterzug(von=(0, 1), bis=(4, 1)) -> Projekt:
    """
    Platte 4 × 2 m auf zwei Wänden in y, fest ganz in x, q = 10 kN/m²; längs
    ihrer Mitte ein Unterzug der Breite 0.5 m: ein Einfeldträger der
    Spannweite 4 m mit q·b = 5 kN/m, also M = 2.5·u·(4 − u) und
    V = 5·(2 − u) -- daneben trägt die Platte wie zuvor.
    """
    p = Projekt(name="Unterzug")
    d = p.decke("Unterzug", aufteilung="fest", anteil=100.0)
    d.platte([(0, 0), (4, 0), (4, 2), (0, 2)], beton=p.beton("C30/37"), h=200)
    d.lager((0, 0), (0, 2))
    d.lager((4, 0), (4, 2))
    d.unterzug(von, bis, breite=0.5)
    d.plattenlast(d.lastfall("q"), "P1", 10.0)
    return p


class TestBeschreibung(unittest.TestCase):
    def test_hin_und_zurueck(self):
        """Ein Schnitt hängt an Knoten wie jedes Teil; ein Bild zeigt auf ihn."""
        p = einfeld()
        d = p.decken[0]
        s = d.schnitt((0, 0.5), (4, 0.5))
        d.diagramm(d.lastfaelle[0], "m_x", s)
        self.assertEqual((s.kennung, d.diagramme[-1].schnitt), ("SN1", "SN1"))
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)
        self.assertEqual(d.schnittlinien(), [("SN1", (0.0, 0.5), (4.0, 0.5))])

    def test_ein_fehlender_knoten_ist_eine_meldung(self):
        """Wie bei jedem Teil -- und das Bild bekommt den Schnitt nicht."""
        d = einfeld().decken[0]
        d.schnitt((0, 0.5), (4, 0.5)).bis = "K99"
        _, meldungen = modell_von(d)
        self.assertEqual([m.elemente for m in meldungen], [("SN1",)])
        self.assertEqual(d.schnittlinien(), [])

    def test_ohne_laenge_leer(self):
        p = einfeld()
        p.decken[0].schnitt((1, 0.5), (1, 0.5))
        (s,) = schnitte(p)
        self.assertEqual((s["L"], s["stuecke"], s["stellen"], s["lager"], s["extreme"]), (0.0, [], [], [], {}))


class TestVerlauf(unittest.TestCase):
    def test_laengs_der_spannweite(self):
        """
        Von 1 m vor der Platte bis 1 m dahinter: in ihr liegt er von 1 bis
        5 m, die Wände kreuzt er dort, und m_x und v_x sind die des
        Einfeldträgers -- das grösste Moment genau in der Mitte.
        """
        p = einfeld()
        p.decken[0].schnitt((-1, 0.5), (5, 0.5))
        (s,) = schnitte(p)
        self.assertEqual((s["kennung"], s["L"], s["stuecke"]), ("SN1", 6.0, [[1.0, 5.0]]))
        self.assertEqual([(l["u"], l["art"], l["name"]) for l in s["lager"]],
                         [(1.0, "linienlager", "L1"), (5.0, "linienlager", "L2")])
        self.assertTrue(all(1.0 <= u <= 5.0 for u in s["stellen"]))
        for u, m, v in zip(s["stellen"], s["werte"]["m_x"], s["werte"]["v_x"]):
            x = u - 1.0
            self.assertAlmostEqual(m, 5.0 * x * (4.0 - x), delta=2e-3)
            self.assertAlmostEqual(v, 10.0 * (2.0 - x), delta=2e-3)
        self.assertEqual(s["extreme"]["m_x"]["groesst"], {"wert": 20.0, "u": 3.0})
        self.assertEqual(s["unterzuege"], [])

    def test_quer_zur_spannweite_gleich(self):
        """Quer zu den Streifen ändert sich m_x nicht, und eine Wand kreuzt er nicht."""
        p = einfeld()
        p.decken[0].schnitt((2, -0.5), (2, 1.5))
        (s,) = schnitte(p)
        self.assertEqual((s["stuecke"], s["lager"]), ([[0.5, 1.5]], []))
        self.assertEqual(set(s["werte"]["m_x"]), {20.0})

    def test_spruenge_an_einer_zone(self):
        """
        Platte 4 × 2 m auf vier Wänden, fest ganz in x -- in der unteren
        Hälfte eine Zone ganz in y. Bei x = 2.1 trägt dort nur der Streifen
        in y, ein Träger der Spannweite 2 m mit Last auf seiner ersten
        Hälfte: m_y = 7.5·y − 5·y², dahinter 2.5·(2 − y), am grössten 2.8125
        bei y = 0.75. m_x ist unten null und oben 5·2.1·1.9 = 19.95 -- bei
        y = 1 springt es, zwei Werte an derselben Stelle.
        """
        p = Projekt(name="Zone")
        d = p.decke("Zone", aufteilung="fest", anteil=100.0)
        d.platte([(0, 0), (4, 0), (4, 2), (0, 2)], beton=p.beton("C30/37"), h=200)
        for a, b in [((0, 0), (4, 0)), ((4, 0), (4, 2)), ((4, 2), (0, 2)), ((0, 2), (0, 0))]:
            d.lager(a, b)
        d.zone([(0, 0), (4, 0), (4, 1), (0, 1)], anteil=0.0)
        d.plattenlast(d.lastfall("q"), "P1", 10.0)
        d.schnitt((2.1, 0), (2.1, 2))
        (s,) = schnitte(p)
        self.assertEqual([(l["u"], l["name"]) for l in s["lager"]], [(0.0, "L1"), (2.0, "L3")])
        werte = list(zip(s["stellen"], s["werte"]["m_x"], s["werte"]["m_y"]))
        for y, m_x, m_y in werte:
            unten = y < 1.0 or (y == 1.0 and m_x == 0.0)
            self.assertAlmostEqual(m_x, 0.0 if unten else 19.95, delta=2e-3)
            self.assertAlmostEqual(m_y, 7.5 * y - 5.0 * y * y if y <= 1.0 else 2.5 * (2.0 - y), delta=2e-3)
        self.assertEqual(sorted(m_x for y, m_x, _ in werte if y == 1.0), [0.0, 19.95])
        self.assertEqual(s["extreme"]["m_y"]["groesst"], {"wert": 2.812, "u": 0.75})

    def test_lager_und_unterzug(self):
        """
        Durch die zwei Felder: die Wände an beiden Enden, die Stütze im
        zweiten Feld und das Band des Unterzugs über der gemeinsamen Kante.
        """
        p = Projekt(name="Decke")
        beton = p.beton("C30/37")
        d = p.decke("Zwei Felder")
        d.platte([(0, 0), (4, 0), (4, 3), (0, 3)], beton=beton, h=200)
        d.platte([(4, 0), (8, 0), (8, 3), (4, 3)], beton=beton, h=250)
        for a, b in [((0, 0), (8, 0)), ((8, 0), (8, 3)), ((8, 3), (0, 3)), ((0, 3), (0, 0))]:
            d.lager(a, b)
        d.unterzug((4, 0), (4, 3), breite=0.5)
        d.stuetze((6, 1.5))
        d.plattenlast(d.lastfall("q"), "P1", 10.0)
        d.schnitt((0, 1.5), (8, 1.5))
        (s,) = schnitte(p)
        self.assertEqual(s["stuecke"], [[0.0, 8.0]])
        self.assertEqual([(l["u"], l["art"], l["name"]) for l in s["lager"]],
                         [(0.0, "linienlager", "L4"), (6.0, "stuetze", "S1"), (8.0, "linienlager", "L2")])
        self.assertEqual(s["unterzuege"], [{"von": 3.75, "bis": 4.25, "name": "U1"}])

    def test_nie_auf_dem_rand_eines_unterzugs(self):
        """
        Auf dem Rand eines Unterzugs zählten er und der Feldstreifen daneben
        zugleich: dort sieht der Schnitt nicht hin -- auch schief nicht, wo
        der Rand und die Grenze zweier Feldstreifen nur in der Rundung
        verschieden sind. Er sieht knapp davor und knapp danach hin.
        """
        ecken = ((0.0, 0.0), (6.0, 0.0), (6.0, 4.0), (0.0, 4.0))
        decke = Decke(platten=[Platte("P1", ecken, 0.22, 30e9, 25e3)],
                      linienlager=[Linienlager(f"W{i}", ecken[i], ecken[(i + 1) % 4]) for i in range(4)],
                      unterzuege=[Unterzug("U1", (3.0, 0.0), (3.0, 4.0), 1.0)],
                      lastfaelle=[Lastfall("q", [Flaechenlast("q", 10e3, platte="P1")])])
        e = rechnen(decke)
        v = schnitt.verlauf(e, e.fall("q"), (0.0, 1.0), (6.0, 3.0))
        self.assertEqual([round(u0 * 6.0 / v.L, 9) for u0, _, _ in v.unterzuege], [2.5])
        orte = [(6.0 * u / v.L, 1.0 + 2.0 * u / v.L) for u, _ in v.proben]
        for x, _ in orte:
            self.assertGreater(min(abs(x - 2.5), abs(x - 3.5)), 1e-7)
        for kante in (2.5, 3.5):
            self.assertEqual(sum(1 for x, _ in orte if abs(x - kante) < 2e-6), 2)


class TestUnterzug(unittest.TestCase):
    def test_einfeldtraeger(self):
        """
        M und V über seine ganze Breite, in kNm und kN, die Wände an seinen
        Enden. Längs seiner Achse zeigt ein Schnitt dasselbe je Meter:
        m_x = M/b, in der Mitte 10/0.5 = 20 kNm/m.
        """
        p = mit_unterzug()
        p.decken[0].schnitt((0, 1), (4, 1))
        e = bild(p)
        (u,) = e["unterzuege"]
        self.assertEqual((u["kennung"], u["L"], u["stuecke"], u["unterzuege"]), ("U1", 4.0, [[0.0, 4.0]], []))
        self.assertEqual([(l["u"], l["art"], l["name"]) for l in u["lager"]],
                         [(0.0, "linienlager", "L1"), (4.0, "linienlager", "L2")])
        for s, m, v in zip(u["stellen"], u["werte"]["M"], u["werte"]["V"]):
            self.assertAlmostEqual(m, 2.5 * s * (4.0 - s), delta=2e-3)
            self.assertAlmostEqual(v, 5.0 * (2.0 - s), delta=2e-3)
        self.assertEqual(u["extreme"]["M"]["groesst"], {"wert": 10.0, "u": 2.0})
        self.assertEqual((e["einheiten"]["M"], e["einheiten"]["V"]), ("kNm", "kN"))
        (s,) = e["schnitte"]
        self.assertEqual(s["extreme"]["m_x"]["groesst"], {"wert": 20.0, "u": 2.0})

    def test_gegen_die_richtung_der_streifen(self):
        """
        Von rechts nach links gezeichnet: die Stelle s läuft ab seinem
        Anfang, die Wände kommen umgekehrt, und V bleibt dM/ds -- an seinem
        Anfang positiv.
        """
        (u,) = bild(mit_unterzug((4, 1), (0, 1)))["unterzuege"]
        self.assertEqual([(l["u"], l["name"]) for l in u["lager"]], [(0.0, "L2"), (4.0, "L1")])
        self.assertEqual(u["stellen"], sorted(u["stellen"]))
        for s, m, v in zip(u["stellen"], u["werte"]["M"], u["werte"]["V"]):
            self.assertAlmostEqual(m, 2.5 * s * (4.0 - s), delta=2e-3)
            self.assertAlmostEqual(v, 5.0 * (2.0 - s), delta=2e-3)

    def test_ohne_last_null(self):
        """Liegt die Last neben ihm, rechnet der Fall ihn nicht: M und V sind null, seine Lager bleiben."""
        p = mit_unterzug()
        d = p.decken[0]
        d.platten[0].lasten.clear()
        d.flaechenlast(d.lastfaelle[0], [(0, 0), (4, 0), (4, 0.5), (0, 0.5)], wert=10.0)
        (u,) = bild(p)["unterzuege"]
        self.assertEqual((u["stuecke"], len(u["lager"])), ([[0.0, 4.0]], 2))
        self.assertEqual((set(u["werte"]["M"]), set(u["werte"]["V"])), ({0.0}, {0.0}))

    def test_auf_unterzuegen(self):
        """
        Im Kolloquium 4 liegt U4 auf den drei Unterzügen höherer Stufe -- sie
        sind seine Lager; das Beispiel zeigt sein M und V.
        """
        p = beispiele.jeder_nachweis()
        d = next(d for d in p.decken if d.name == "Kolloquium 4")
        self.assertEqual([(z.groesse, z.schnitt) for z in d.diagramme if z.schnitt], [("M", "U4"), ("V", "U4")])
        u4 = next(u for u in bild(p, "q_d", d.kennung)["unterzuege"] if u["kennung"] == "U4")
        self.assertEqual([(l["u"], l["art"], l["name"]) for l in u4["lager"]],
                         [(0.5, "unterzug", "U1"), (4.5, "unterzug", "U2"), (8.5, "unterzug", "U3")])
        # Über dem mittleren Lager zieht es oben.
        self.assertEqual(u4["extreme"]["M"]["kleinst"]["u"], 4.5)
        self.assertLess(u4["extreme"]["M"]["kleinst"]["wert"], 0.0)

    def test_ein_bild_zeigt_auf_ihn(self):
        """Wie auf einen Schnitt -- der Katalog sagt, welche Grössen einem Unterzug gehören."""
        p = mit_unterzug()
        d = p.decken[0]
        d.diagramm(d.lastfaelle[0], "M", d.unterzuege[0])
        self.assertEqual((d.diagramme[-1].groesse, d.diagramme[-1].schnitt), ("M", "U1"))
        self.assertEqual(Projekt.aus_dict(p.als_dict()), p)
        katalog = dienst.bearbeite("katalog", {}).daten["decke"]["diagrammgroessen"]
        self.assertEqual([g["wert"] for g in katalog if g["unterzug"]], ["M", "V"])


if __name__ == "__main__":
    unittest.main()
