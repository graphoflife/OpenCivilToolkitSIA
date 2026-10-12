"""
Das Gleichungssystem des Stabwerks: Profil, Nummerierung, Singularität.

Geprüft gegen eine dichte Rechnung von Hand (Gauss mit Pivotsuche, hier im
Test) -- und daran, dass ein bewegliches System nicht eine Zahl liefert,
sondern seine Bewegung.
"""

import random
import unittest

from opencivil.stabwerk.matrix import (
    Profilmatrix, Zerlegung, dicht, nummerierung,
)


def gauss(a, b):
    """Dicht, mit Pivotsuche -- die Vergleichsrechnung."""
    n = len(b)
    m = [list(zeile) + [b[i]] for i, zeile in enumerate(a)]
    for k in range(n):
        p = max(range(k, n), key=lambda i: abs(m[i][k]))
        m[k], m[p] = m[p], m[k]
        for i in range(k + 1, n):
            f = m[i][k] / m[k][k]
            for j in range(k, n + 1):
                m[i][j] -= f * m[k][j]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = (m[i][n] - sum(m[i][j] * x[j] for j in range(i + 1, n))) / m[i][i]
    return x


def bandmatrix(n, breite, zufall):
    """Eine symmetrische, positiv definite Matrix mit Band -- als Profil und dicht."""
    gruppen = [list(range(i, min(n, i + breite))) for i in range(n)]
    K = Profilmatrix.aus_gruppen(n, gruppen)
    for g in gruppen:
        for p, i in enumerate(g):
            for j in g[:p]:
                K.addiere(i, j, zufall.uniform(-1.0, 1.0))
    for i in range(n):
        # Diagonal dominant: positiv definit.
        K.addiere(i, i, 2.0 * breite + zufall.uniform(0.0, 1.0))
    return K


def feder_kette(n, k=1000.0, boden=None):
    """Federn in einer Reihe -- mit ``boden``, einer Feder an den ersten Punkt."""
    K = Profilmatrix.aus_gruppen(n, [[i, i + 1] for i in range(n - 1)])
    for i in range(n - 1):
        K.addiere_block([i, i + 1], [[k, -k], [-k, k]])
    if boden:
        K.addiere(0, 0, boden)
    return K


class TestLoesen(unittest.TestCase):
    def test_wie_dicht_gerechnet(self):
        zufall = random.Random(7)
        K = bandmatrix(40, 5, zufall)
        f = [zufall.uniform(-1.0, 1.0) for _ in range(40)]
        z = Zerlegung(K)
        self.assertEqual(z.singulaer, [])
        x = z.loese(f)
        erwartet = gauss(dicht(K), f)
        for a, b in zip(x, erwartet):
            self.assertAlmostEqual(a, b, places=10)

    def test_eine_zerlegung_viele_lastfaelle(self):
        zufall = random.Random(11)
        K = bandmatrix(25, 4, zufall)
        z = Zerlegung(K)
        for _ in range(3):
            f = [zufall.uniform(-1.0, 1.0) for _ in range(25)]
            r = K.mal(z.loese(f))
            for a, b in zip(r, f):
                self.assertAlmostEqual(a, b, places=10)

    def test_das_profil_haelt_nur_das_band(self):
        K = bandmatrix(100, 3, random.Random(3))
        self.assertLess(K.eintraege, 100 * 3 + 1)
        with self.assertRaises(IndexError):
            K.addiere(50, 10, 1.0)

    def test_ein_block_mit_doppelter_unbekannten_wird_abgewiesen(self):
        K = Profilmatrix.aus_gruppen(2, [[0, 1]])
        with self.assertRaises(ValueError):
            K.addiere_block([1, 1], [[1.0, 0.0], [0.0, 1.0]])


class TestNummerierung(unittest.TestCase):
    def test_eine_gemischte_kette_wird_ein_band(self):
        """Eine Kette, deren Glieder durcheinander benannt sind, hat danach Bandbreite 1."""
        namen = list(range(30))
        random.Random(5).shuffle(namen)
        nachbarn = {}
        for a, b in zip(namen, namen[1:]):
            nachbarn.setdefault(a, set()).add(b)
            nachbarn.setdefault(b, set()).add(a)
        folge = nummerierung(sorted(namen), nachbarn)
        platz = {k: i for i, k in enumerate(folge)}
        self.assertEqual(sorted(folge), sorted(namen))
        self.assertEqual(max(abs(platz[a] - platz[b]) for a, b in zip(namen, namen[1:])), 1)

    def test_ein_gitter_bleibt_schmal(self):
        """Ein Gitter 10 × 4, zeilenweise benannt: die Bandbreite wird höchstens 5."""
        knoten = [(i, j) for i in range(10) for j in range(4)]
        nachbarn = {k: set() for k in knoten}
        for i, j in knoten:
            for n in ((i + 1, j), (i, j + 1)):
                if n in nachbarn:
                    nachbarn[(i, j)].add(n)
                    nachbarn[n].add((i, j))
        folge = nummerierung(knoten, nachbarn)
        platz = {k: i for i, k in enumerate(folge)}
        breite = max(abs(platz[a] - platz[b]) for a in knoten for b in nachbarn[a])
        self.assertLessEqual(breite, 5)

    def test_getrennte_teile_kommen_alle_vor(self):
        nachbarn = {1: {2}, 2: {1}, 3: {4}, 4: {3}, 5: set()}
        self.assertEqual(sorted(nummerierung([1, 2, 3, 4, 5], nachbarn)), [1, 2, 3, 4, 5])

    def test_fest_bei_gleichem_grad(self):
        nachbarn = {1: {2}, 2: {1, 3}, 3: {2}}
        self.assertEqual(nummerierung([1, 2, 3], nachbarn), nummerierung([1, 2, 3], nachbarn))


class TestSingulaer(unittest.TestCase):
    def test_ohne_halt_ist_es_eine_bewegung(self):
        """Federn ohne Boden: die ganze Kette verschiebt sich frei."""
        K = feder_kette(5)
        z = Zerlegung(K)
        self.assertTrue(z.singulaer)
        bewegung = z.bewegung()
        self.assertLess(bewegung.rest, 1e-12)
        for v in bewegung.x:
            self.assertAlmostEqual(v, 1.0, places=9)

    def test_mit_halt_keine(self):
        z = Zerlegung(feder_kette(5, boden=1000.0))
        self.assertEqual(z.singulaer, [])
        self.assertIsNone(z.bewegung())

    def test_eine_weiche_feder_ist_kein_mechanismus(self):
        """Ein Millionstel der Steifigkeit hält -- singulär ist nur, was gar nicht hält."""
        z = Zerlegung(feder_kette(4, k=1e6, boden=1.0))
        self.assertEqual(z.singulaer, [])
        x = z.loese([0.0, 0.0, 0.0, 1.0])
        self.assertAlmostEqual(x[0], 1.0, places=6)

    def test_nur_der_lose_teil_bewegt_sich(self):
        """Zwei Ketten, eine gehalten: die Bewegung betrifft nur die andere."""
        K = Profilmatrix.aus_gruppen(4, [[0, 1], [2, 3]])
        for a, b in ((0, 1), (2, 3)):
            K.addiere_block([a, b], [[10.0, -10.0], [-10.0, 10.0]])
        K.addiere(0, 0, 10.0)
        bewegung = Zerlegung(K).bewegung()
        self.assertEqual([round(abs(v), 9) for v in bewegung.x], [0.0, 0.0, 1.0, 1.0])

    def test_null_auf_der_diagonale(self):
        K = Profilmatrix(2, [0, 1])
        K.addiere(0, 0, 5.0)
        z = Zerlegung(K)
        self.assertEqual(z.singulaer, [1])
        self.assertEqual(z.loese([5.0, 0.0]), [1.0, 0.0])


if __name__ == "__main__":
    unittest.main()
