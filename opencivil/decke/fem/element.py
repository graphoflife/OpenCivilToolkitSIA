"""
opencivil/decke/fem/element.py -- das Dreieck der Platte und der Balken in ihr.

VERANTWORTUNG:
Die Steifigkeit eines Dreiecks der Platte nach Kirchhoff, die eines Trägers
in ihrer Mittelebene, und wie aus den Verschiebungen ihre Schnittkräfte
werden. Je Knoten drei Unbekannte: die Durchbiegung ``w``, nach unten
positiv, und ihre Neigungen ``β_x = ∂w/∂x`` und ``β_y = ∂w/∂y``.

DAS DREIECK (DKT, Batoz, Bathe und Ho 1980):
Die Neigungen ändern sich über das Dreieck quadratisch, durch ihre Werte an
den drei Ecken und den drei Mitten der Seiten. An den Ecken sind es die
Unbekannten; in einer Mitte legt sie die Kirchhoffsche Bedingung fest:

- längs der Seite ist ``w`` kubisch, durch ``w`` und die Neigung längs der
  Seite an ihren beiden Enden -- in der Mitte ist die Neigung längs
  ``β_s = 3/(2·l) · (w_j − w_i) − (β_s,i + β_s,j)/4``;
- quer zur Seite ändert sich die Neigung linear: ``β_n = (β_n,i + β_n,j)/2``.

Damit sind die Krümmungen linear über das Dreieck, und die Momente auch::

    κ = (∂β_x/∂x, ∂β_y/∂y, ∂β_x/∂y + ∂β_y/∂x)
    m = (m_x, m_y, m_xy) = −D_b · κ
    D_b = D · [[1, ν, 0], [ν, 1, 0], [0, 0, (1 − ν)/2]]      D = E·h³ / (12·(1 − ν²))

``m_x > 0`` zieht unten, wie in der Streifenmethode, und ``m_xy`` gilt so,
dass in der Richtung ``(cos φ, sin φ)`` ``m_n = m_x·cos²φ + m_y·sin²φ +
2·m_xy·sin φ·cos φ`` ist (:func:`~opencivil.decke.feld.in_xy`). Die
Steifigkeit ``K = ∫ Bᵀ·D_b·B dA`` ist mit den drei Mitten der Seiten genau,
je mit einem Drittel der Fläche: ``Bᵀ·D_b·B`` ist quadratisch.

DER BALKEN:
Ein Träger liegt als Balken in der Mittelebene der Platte, von Knoten zu
Knoten längs seiner Achse, ohne Torsionssteifigkeit (Entscheid 10 des Plans
vom 2026-11-27). Seine Durchbiegung ist kubisch, durch ``w`` und die Neigung
längs ``w' = β_x·cos α + β_y·sin α`` an beiden Enden; daher die bekannte
Steifigkeit ``EI/L³ · [[12, 6L, −12, 6L], …]``. Sein Moment ``M = −EI·w''``
zieht unten, wenn es positiv ist, und ``V = dM/ds``.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from opencivil.decke.geometrie import Punkt

Matrix = List[List[float]]

#: Die Ecken des Dreiecks in den Koordinaten ``(ξ, η)``: dort liest das Glätten die Momente.
ECKEN = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))

#: Die Punkte der Integration, die Mitten der Seiten -- je ein Drittel der Fläche.
MITTEN = ((0.5, 0.0), (0.5, 0.5), (0.0, 0.5))

#: Die Seiten, an deren Mitte die Neigungen 4, 5 und 6 stehen: 2–3, 3–1 und 1–2.
SEITEN = ((1, 2), (2, 0), (0, 1))


def steifigkeit_der_platte(E: float, h: float, nu: float) -> float:
    """``D = E·h³ / (12·(1 − ν²))``, in Nm, mit E in N/m² und h in m."""
    return E * h ** 3 / (12.0 * (1.0 - nu * nu))


def steifigkeit_des_traegers(E: float, h: float, b: float, h_T: float) -> float:
    """
    ``EI = E·b·((h + h_T)³ − h³)/12`` des Balkens eines Trägers, in Nm²: das
    Rechteck ``b × (h + h_T)`` ohne den Teil, den die Platte schon trägt
    (Entscheid 10 des Plans vom 2026-11-27).
    """
    return E * b * ((h + h_T) ** 3 - h ** 3) / 12.0


class Dreieck:
    """
    Ein Dreieck der Platte, seine Ecken im Gegenuhrzeigersinn: seine
    Steifigkeit :attr:`K` über ``(w, β_x, β_y)`` der drei Ecken und je Ecke,
    wie die Momente dort aus den Unbekannten folgen (:meth:`momente`).
    """

    def __init__(self, ecken: Sequence[Punkt], E: float, h: float, nu: float) -> None:
        (x1, y1), (x2, y2), (x3, y3) = ecken
        self.x21, self.y21 = x2 - x1, y2 - y1
        self.x31, self.y31 = x3 - x1, y3 - y1
        self.det = self.x21 * self.y31 - self.x31 * self.y21
        if self.det <= 0.0:
            raise ValueError("Ein Dreieck des Netzes hat keine Fläche oder liegt verkehrt herum.")
        self.flaeche = 0.5 * self.det
        D = steifigkeit_der_platte(E, h, nu)
        self.d = (D, D * nu, D * (1.0 - nu) / 2.0)
        self._neigungen = _neigungen(ecken)
        self.K = self._steifigkeit()
        # Je Ecke die drei Zeilen von −D_b · B, für m_x, m_y und m_xy.
        self._momente = [self._momentenzeilen(xi, eta) for xi, eta in ECKEN]

    def _b(self, xi: float, eta: float) -> Tuple[List[float], List[float], List[float]]:
        """Die drei Zeilen von ``B`` an der Stelle ``(ξ, η)``: κ_x, κ_y und κ_xy über den 9 Unbekannten."""
        l1 = 1.0 - xi - eta
        dxi = (1.0 - 4.0 * l1, 4.0 * xi - 1.0, 0.0, 4.0 * eta, -4.0 * eta, 4.0 * (l1 - xi))
        deta = (1.0 - 4.0 * l1, 0.0, 4.0 * eta - 1.0, 4.0 * xi, 4.0 * (l1 - eta), -4.0 * xi)
        kx = [0.0] * 9
        ky = [0.0] * 9
        kxy = [0.0] * 9
        x21, y21, x31, y31, det = self.x21, self.y21, self.x31, self.y31, self.det
        for m in range(6):
            nx = (y31 * dxi[m] - y21 * deta[m]) / det
            ny = (x21 * deta[m] - x31 * dxi[m]) / det
            for spalte, bx, by in self._neigungen[m]:
                kx[spalte] += nx * bx
                ky[spalte] += ny * by
                kxy[spalte] += ny * bx + nx * by
        return kx, ky, kxy

    def _steifigkeit(self) -> Matrix:
        d11, d12, d33 = self.d
        K = [[0.0] * 9 for _ in range(9)]
        gewicht = self.flaeche / 3.0
        for xi, eta in MITTEN:
            kx, ky, kxy = self._b(xi, eta)
            mx = [gewicht * (d11 * a + d12 * b) for a, b in zip(kx, ky)]
            my = [gewicht * (d12 * a + d11 * b) for a, b in zip(kx, ky)]
            mxy = [gewicht * d33 * c for c in kxy]
            for r in range(9):
                ar, br, cr = kx[r], ky[r], kxy[r]
                zeile = K[r]
                for s in range(r, 9):
                    zeile[s] += ar * mx[s] + br * my[s] + cr * mxy[s]
        for r in range(9):
            for s in range(r):
                K[r][s] = K[s][r]
        return K

    def _momentenzeilen(self, xi: float, eta: float) -> Tuple[List[float], List[float], List[float]]:
        d11, d12, d33 = self.d
        kx, ky, kxy = self._b(xi, eta)
        return ([-(d11 * a + d12 * b) for a, b in zip(kx, ky)],
                [-(d12 * a + d11 * b) for a, b in zip(kx, ky)],
                [-d33 * c for c in kxy])

    def momente(self, u: Sequence[float]) -> List[Tuple[float, float, float]]:
        """Je Ecke ``(m_x, m_y, m_xy)`` in Nm/m aus den 9 Unbekannten ``u`` des Dreiecks."""
        return [tuple(sum(a * b for a, b in zip(zeile, u)) for zeile in ecke) for ecke in self._momente]

    def gefaelle(self, werte: Sequence[float]) -> Tuple[float, float]:
        """``(∂/∂x, ∂/∂y)`` einer Grösse, die über das Dreieck linear ist, aus ihren Werten an den Ecken."""
        a, b, c = werte
        d_xi, d_eta = b - a, c - a
        return ((self.y31 * d_xi - self.y21 * d_eta) / self.det,
                (self.x21 * d_eta - self.x31 * d_xi) / self.det)


def _neigungen(ecken: Sequence[Punkt]) -> List[List[Tuple[int, float, float]]]:
    """
    Je Punkt der Neigungen -- erst die Ecken, dann die Mitten der Seiten
    2–3, 3–1, 1–2 --, wie ``β_x`` und ``β_y`` dort aus den 9 Unbekannten
    folgen: Tripel ``(Spalte, Beitrag zu β_x, Beitrag zu β_y)``.

    In der Mitte einer Seite mit der Richtung ``t`` und der Länge ``l``::

        β = 3/(2·l) · t · (w_j − w_i) + (I/2 − 3/4 · t·tᵀ) · (β_i + β_j)

    -- die Neigung längs nach der kubischen Durchbiegung, quer das Mittel.
    """
    heraus: List[List[Tuple[int, float, float]]] = [[(3 * i + 1, 1.0, 0.0), (3 * i + 2, 0.0, 1.0)]
                                                    for i in range(3)]
    for i, j in SEITEN:
        dx, dy = ecken[j][0] - ecken[i][0], ecken[j][1] - ecken[i][1]
        l2 = dx * dx + dy * dy
        c2, s2, cs = dx * dx / l2, dy * dy / l2, dx * dy / l2
        p00, p01, p11 = 0.5 - 0.75 * c2, -0.75 * cs, 0.5 - 0.75 * s2
        wx, wy = 1.5 * dx / l2, 1.5 * dy / l2
        heraus.append([(3 * i, -wx, -wy), (3 * i + 1, p00, p01), (3 * i + 2, p01, p11),
                       (3 * j, wx, wy), (3 * j + 1, p00, p01), (3 * j + 2, p01, p11)])
    return heraus


def balken(L: float, EI: float) -> Matrix:
    """Die Steifigkeit eines Balkens über ``(w_i, w'_i, w_j, w'_j)``, ``w'`` längs seiner Achse."""
    k = EI / L ** 3
    return [[12.0 * k, 6.0 * k * L, -12.0 * k, 6.0 * k * L],
            [6.0 * k * L, 4.0 * k * L * L, -6.0 * k * L, 2.0 * k * L * L],
            [-12.0 * k, -6.0 * k * L, 12.0 * k, -6.0 * k * L],
            [6.0 * k * L, 2.0 * k * L * L, -6.0 * k * L, 4.0 * k * L * L]]


def balken_in_der_platte(K4: Matrix, richtung: Punkt) -> Matrix:
    """
    Die Steifigkeit des Balkens über ``(w, β_x, β_y)`` seiner beiden Knoten:
    ``w' = β_x·cos α + β_y·sin α``, ``richtung = (cos α, sin α)``.
    """
    c, s = richtung
    T = [[1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, c, s, 0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, c, s]]
    KT = [[sum(K4[r][k] * T[k][j] for k in range(4)) for j in range(6)] for r in range(4)]
    return [[sum(T[k][i] * KT[k][j] for k in range(4)) for j in range(6)] for i in range(6)]


def balkenkraefte(K4: Matrix, u4: Sequence[float]) -> Tuple[float, float, float]:
    """
    ``(M_i, M_j, V)`` eines Balkens aus seinen vier Unbekannten: die
    Momente an seinen Enden, positiv mit Zug unten, und die Querkraft
    ``V = dM/ds`` dazwischen -- aus den Kräften an seinen Enden, ``K·u``.
    """
    f = [sum(a * b for a, b in zip(zeile, u4)) for zeile in K4]
    return f[1], -f[3], -f[0]
