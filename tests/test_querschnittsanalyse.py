"""
Die Querschnittsanalyse: Beschreibung, Aufbau und Nachweise.

Hier zuerst die Beschreibung -- was gespeichert wird und wie es sich liest.
"""

import unittest

from opencivil.projekt import (
    Projekt, ProjektFehler, QALastfallEintrag, QuerschnittsanalyseEintrag,
)
from opencivil.web import api


class TestBeschreibung(unittest.TestCase):

    def neu(self):
        return QuerschnittsanalyseEintrag.neu("a1", "Balken", "b1", "s1")

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
        vorlage = api.katalog()["neue_querschnittsanalyse"]
        self.assertEqual(QuerschnittsanalyseEintrag.aus_dict(
            {**vorlage, "kennung": "a1"}).als_dict(), {**vorlage, "kennung": "a1",
                                                       "name": "a1"})
        self.assertEqual(len(vorlage["flaechen"]), 1)

    def test_materialien_und_wahl(self):
        a = self.neu()
        self.assertEqual(a.materialien(), ["b1", "s1"])
        self.assertEqual(a.wahl("b1").satz, "bemessung")
        self.assertEqual(a.wahl("b1").betongesetz, "parabel")

    def test_doppelte_lastfaelle(self):
        a = self.neu()
        a.lastfaelle.append(QALastfallEintrag(name="Tragsicherheit 1"))
        with self.assertRaisesRegex(ProjektFehler, "Querschnitt 'Balken'"):
            a.pruefen()

    def test_unbekanntes_wird_gemeldet(self):
        roh = self.neu().als_dict()
        roh["stablinien"][0]["art"] = "stueckweise"
        with self.assertRaisesRegex(ProjektFehler, "Stablinie"):
            QuerschnittsanalyseEintrag.aus_dict(roh)
        roh = self.neu().als_dict()
        roh["schubwaende"] = [{"von": [0, 0], "bis": [0, 500], "schnitte": 9}]
        with self.assertRaisesRegex(ProjektFehler, "Schnitte"):
            QuerschnittsanalyseEintrag.aus_dict(roh)
        roh = self.neu().als_dict()
        roh["flaechen"][0]["punkte"][1] = [300.0]
        with self.assertRaisesRegex(ProjektFehler, "zwei Zahlen"):
            QuerschnittsanalyseEintrag.aus_dict(roh)


if __name__ == "__main__":
    unittest.main()
