"""
Fasern und Dehnungsgrenzen -- der Teil, den Platte und gezeichneter
Querschnitt gemeinsam haben.

Dass die Platte nach dem Umbau dasselbe rechnet, prüfen die Schnappschüsse
des Berichts Zeichen für Zeichen. Hier steht, was das Modul für sich zusagt.
"""

import math
import unittest

from opencivil.querschnitt.fasern import (
    Dehnungsgrenze, Dehnungsgrenzen, Fasergruppe, Faserquerschnitt, Stab,
)


def platte(h=0.3, eps_druck=0.003, eps_zug=0.045):
    return Dehnungsgrenzen([
        Dehnungsgrenze(arm=-h / 2, eps_min=-eps_druck, eps_max=eps_zug),
        Dehnungsgrenze(arm=h / 2, eps_min=-eps_druck, eps_max=eps_zug)])


class TestDehnungsgrenzen(unittest.TestCase):

    def test_ohne_kruemmung_der_ganze_bereich(self):
        self.assertEqual(platte().fenster(0.0), (-0.003, 0.045))

    def test_kruemmung_verengt_das_fenster(self):
        unten, oben = platte().fenster(0.1)
        # Die Randdehnungen sind eps_m ± 0.1·0.15 = eps_m ± 0.015.
        self.assertAlmostEqual(unten, -0.003 + 0.015)
        self.assertAlmostEqual(oben, 0.045 - 0.015)
        self.assertIsNone(platte().fenster(1.0))

    def test_kruemmungsgrenze_der_platte(self):
        for positiv in (True, False):
            self.assertAlmostEqual(platte().kruemmungsgrenze(positiv=positiv),
                                   (0.003 + 0.045) / 0.3)

    def test_an_der_grenze_schliesst_sich_das_fenster(self):
        """Knapp darunter ein schmales Fenster, knapp darüber keines."""
        grenzen = platte()
        chi = grenzen.kruemmungsgrenze(positiv=True)
        unten, oben = grenzen.fenster(chi * (1 - 1e-9))
        self.assertAlmostEqual(unten, oben)
        self.assertIsNone(grenzen.fenster(chi * (1 + 1e-9)))

    def test_unsymmetrische_grenzen(self):
        """Oben nur Beton, unten auch Stahl: die beiden Richtungen sind verschieden."""
        grenzen = Dehnungsgrenzen([
            Dehnungsgrenze(arm=-0.15, eps_min=-0.0035, eps_max=math.inf),
            Dehnungsgrenze(arm=0.15, eps_min=-0.0035, eps_max=math.inf),
            Dehnungsgrenze(arm=0.12, eps_min=-0.045, eps_max=0.045),
        ])
        # Zug unten: Beton oben -3.5 ‰, Stahl unten +45 ‰ auf 0.27 m.
        self.assertAlmostEqual(grenzen.kruemmungsgrenze(positiv=True),
                               (0.045 + 0.0035) / 0.27)
        # Zug oben: oben kein Stahl, also nur der Beton unten bei -3.5 ‰
        # gegen den Stahl -- und der liegt fast unten.
        self.assertAlmostEqual(grenzen.kruemmungsgrenze(positiv=False),
                               (0.045 + 0.0035) / 0.03)

    def test_ohne_grenzen_kein_querschnitt(self):
        with self.assertRaises(ValueError):
            Dehnungsgrenzen([])


class TestFaserquerschnitt(unittest.TestCase):

    def test_gleiche_flaechen_wie_einzeln(self):
        gesetz = lambda eps: 200e9 * eps  # linear
        arme = (-0.1, 0.0, 0.1)
        einmal = Faserquerschnitt([Fasergruppe(gesetz, arme, 0.01)], [])
        einzeln = Faserquerschnitt([Fasergruppe(gesetz, arme, (0.01, 0.01, 0.01))], [])
        a, b = einmal.kraefte(0.001, 0.01), einzeln.kraefte(0.001, 0.01)
        self.assertAlmostEqual(a.N, b.N)
        self.assertAlmostEqual(a.M, b.M)

    def test_stab_verdraengt_den_beton(self):
        beton = lambda eps: -20e6 if eps < 0 else 0.0
        stahl = lambda eps: 200e9 * eps
        stab = Stab(arm=0.0, flaeche=0.001, gesetz=stahl, verdraengt=beton)
        k = Faserquerschnitt([], [stab]).kraefte(-0.001, 0.0)
        self.assertAlmostEqual(k.N, (-200e6 + 20e6) * 0.001)

    def test_moment_entlang_der_nulllinie(self):
        """Nur wer `quer` angibt, bekommt das zweite Moment."""
        gesetz = lambda eps: 1e9 * eps
        gruppe = Fasergruppe(gesetz, (0.1, 0.1), (0.5, 0.5), quer=(-0.2, 0.4))
        k = Faserquerschnitt([gruppe], []).kraefte(0.0, 1.0)
        kraft = 1e9 * 0.1 * 0.5
        self.assertAlmostEqual(k.N, 2 * kraft)
        self.assertAlmostEqual(k.M, 2 * kraft * 0.1)
        self.assertAlmostEqual(k.M_quer, kraft * (-0.2 + 0.4))


if __name__ == "__main__":
    unittest.main()
