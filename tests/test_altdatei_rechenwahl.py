"""
Eine Datei von vor der Rechenwahl rechnet wie damals -- Zahl für Zahl.

Bis 2026-10-09 hatte eine Platte genau eine Kriechzahl, und die Nachweise
rechneten fest: die Tragsicherheit mit der Handrechnung und Bemessungswerten,
die Stahlspannungen elastisch mit charakteristischen Werten, das Knicken mit
der Parabel. Seither wählt jedes Kapitel selbst, mit φ = 0 als Vorgabe. Eine
alte Datei kennt diese Felder nicht; jedes Kapitel übernimmt beim Öffnen das
φ der Platte -- und muss dann dieselben Zahlen liefern wie vorher.

Festgehalten am 2026-10-09, vor dem Umbau, in
``tests/altformat/platte_vor_rechenwahl.json``: die Platte des Beispiels mit
φ = 1.5 (nicht der alten Vorgabe 2.0 -- so zeigt sich, ob wirklich die Zahl
der Platte übernommen wird), erhöhter Rissanforderung, allen Schaltern,
eigenen häufigen und quasi-ständigen Lastfällen, einem Knickfall und vier
Analysen. Verglichen wird auf alle Stellen: jede Zahl der Lösung und jeder
Punkt der Analysen.
"""

import json
import unittest
from pathlib import Path

from opencivil.ergebnis import Ergebnis
from opencivil.projekt import Projekt

DATEI = Path(__file__).parent / "altformat" / "platte_vor_rechenwahl.json"

#: Was in dieser Datei keine Rechnung mehr braucht. Die genaue Linie der
#: Platte -- damals nur Vergleich im Diagramm -- las k_sigma des Betons, aus
#: E_cd; seit der Rechenwahl rechnet die Parabel ueberall mit E_cm/(1 + phi)
#: (mit gamma_cE = 1 dieselbe Zahl). Damit fragt hier niemand mehr nach
#: diesen drei Werten. Jede andere Zahl steht da wie damals.
ENTFALLEN = {"beton.b1.k_sigma", "beton.b1.E_cd", "beton.b1.gamma_cE"}


def gerechnet():
    daten = json.loads(DATEI.read_text(encoding="utf-8"))
    projekt = Projekt.aus_dict(daten["projekt"])
    aufbau = projekt.aufbauen()
    loesung = aufbau.werk.loese(*aufbau.berichtsziele())
    return daten, Ergebnis(projekt=projekt, aufbau=aufbau, loesung=loesung)


class TestAlteDateiRechnetWieDamals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.daten, cls.ergebnis = gerechnet()

    def test_jede_zahl_der_loesung(self):
        """Neue Werte dürfen dazukommen; jeder alte steht mit derselben Zahl da."""
        werte = self.ergebnis.loesung.werte
        for kid, soll in self.daten["werte"].items():
            if kid in ENTFALLEN:
                continue
            with self.subTest(wert=kid):
                self.assertIn(kid, werte)
                self.assertEqual(werte[kid].groesse.si, soll)

    def test_jeder_punkt_der_analysen(self):
        ist = {a.fall.name: a for liste in self.ergebnis.analysen().values() for a in liste}
        for soll in self.daten["analysen"]:
            a = ist[soll["name"]]
            with self.subTest(analyse=soll["name"]):
                if "bild" in soll:
                    b, s = a.bild, soll["bild"]
                    self.assertEqual([b.eps_m, b.chi, b.N, b.M], [s["eps_m"], s["chi"], s["N"], s["M"]])
                    self.assertEqual([x.sigma for x in b.stahl], s["stahl"])
                    self.assertEqual([x.sigma for x in b.beton], s["beton"])
                if "kurve" in soll:
                    k, s = a.kurve, soll["kurve"]
                    self.assertEqual(k.riss, s["riss"])
                    self.assertEqual([k.bruch.kraft, k.bruch.verformung,
                                      k.bruch.eps_oben, k.bruch.eps_unten], s["bruch"])
                    self.assertEqual(None if k.fliessen is None
                                     else [k.fliessen.kraft, k.fliessen.verformung], s["fliessen"])
                    self.assertEqual([[p.kraft, p.verformung] for p in k.punkte], s["punkte"])


if __name__ == "__main__":
    unittest.main()
