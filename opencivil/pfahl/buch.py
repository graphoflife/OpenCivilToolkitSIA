"""
opencivil/pfahl/buch.py -- die Zahlen des Buches zum Einzelpfahl.

VERANTWORTUNG:
Was Lang, Huder, Amann und Puzrin für Pfähle als Bild oder Beiwert geben,
als Zahlen: der Form- und Tiefenfaktor X am Pfahlfuss (Bild 12.4), der
Tragfähigkeitsfaktor N_c undrainiert (Bild 12.5), der Anteil von φ und c beim
örtlichen Abscheren (Kap. 9.2.7) und der Ruhedruckbeiwert (Kap. 2.7). Die
Bilder sind abgelesen, nicht nachgerechnet: auf etwa ±0.02 genau.

AUSSERHALB DER BILDER:
Bild 12.4 reicht von h/D = 2.5 bis 30 und von φ' = 15° bis 40°, Bild 12.5 bis
L/D = 12. Ausserhalb gilt der Wert am Rand des Bildes -- nach Vorgabe, nicht
nachgeschlagen; :func:`ausserhalb` sagt, wo das greift. Bild 12.5 endet bei
N_c = 9: höchstens so viel, sagt der Text dazu.

QUELLE:
Lang, H.-J., Huder, J., Amann, P., Puzrin, A. M.: Bodenmechanik und
Grundbau. 8. Aufl., Springer, Berlin 2007.

EINHEITEN:
Winkel in Grad, Verhältnisse ohne Einheit.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from typing import List, Sequence, Tuple

KAP_RUHEDRUCK = "Kap. 2.7"
KAP_LASTTRANSPORT = "Kap. 12.4, Bild 12.3"
KAP_SPITZE = "Kap. 12.5, Bild 12.4"
KAP_SPITZE_UNDRAINIERT = "Kap. 12.5, Bild 12.5"
KAP_MANTEL = "Kap. 12.5"
KAP_ABSCHEREN = "Kap. 9.2.7, 12.5"

# -- Bild 12.4: X über h/D, je Kurve φ' -------------------------------------------
X_H_D: Tuple[float, ...] = (2.5, 3.0, 4.0, 5.0, 7.5, 10.0, 12.5, 15.0, 20.0, 25.0, 30.0)
X_PHI: Tuple[float, ...] = (15.0, 25.0, 30.0, 32.5, 35.0, 37.5, 40.0)
X_WERTE: Tuple[Tuple[float, ...], ...] = (
    (1.60, 1.63, 1.68, 1.73, 1.80, 1.83, 1.84, 1.85, 1.87, 1.89, 1.91),
    (1.69, 1.72, 1.80, 1.86, 1.95, 2.00, 2.03, 2.04, 2.07, 2.08, 2.10),
    (1.82, 1.87, 1.96, 2.05, 2.17, 2.24, 2.28, 2.31, 2.36, 2.40, 2.43),
    (1.91, 1.96, 2.09, 2.19, 2.34, 2.45, 2.51, 2.56, 2.64, 2.67, 2.70),
    (2.04, 2.12, 2.28, 2.39, 2.60, 2.72, 2.83, 2.91, 3.03, 3.07, 3.11),
    (2.28, 2.39, 2.57, 2.71, 3.02, 3.20, 3.34, 3.45, 3.60, 3.69, 3.77),
    (2.57, 2.69, 2.94, 3.15, 3.58, 3.87, 4.08, 4.25, 4.50, 4.67, 4.80),
)

# -- Bild 12.5: N_c undrainiert über L/D (Skempton), höchstens 9 --------------------
NC_L_D: Tuple[float, ...] = (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0,
                             12.0)
NC_WERTE: Tuple[float, ...] = (6.2, 6.6, 7.0, 7.3, 7.6, 7.8, 8.1, 8.35, 8.55, 8.7, 8.8, 8.9,
                               9.0, 9.0)

# -- Kap. 9.2.7, 12.5: örtliches Abscheren -------------------------------------------
#: Auf diesen Teil sinken φ und c, wenn der Boden am Fuss nur örtlich abschert.
ABSCHEREN = 2.0 / 3.0


def _stelle(achse: Sequence[float], wert: float) -> Tuple[int, float]:
    """Der Abschnitt der Achse und der Anteil darin; am Rand festgehalten."""
    if wert <= achse[0]:
        return 0, 0.0
    if wert >= achse[-1]:
        return len(achse) - 2, 1.0
    i = bisect_right(achse, wert) - 1
    return i, (wert - achse[i]) / (achse[i + 1] - achse[i])


def faktor_x(phi_grad: float, h_durch_d: float) -> float:
    """X aus Bild 12.4, zwischen den Kurven und Stützstellen linear."""
    i, a = _stelle(X_PHI, phi_grad)
    j, b = _stelle(X_H_D, h_durch_d)

    def zeile(k: int) -> float:
        r = X_WERTE[k]
        return r[j] + b * (r[j + 1] - r[j])

    return zeile(i) + a * (zeile(i + 1) - zeile(i))


def faktor_n_c_undrainiert(l_durch_d: float) -> float:
    """N_c aus Bild 12.5."""
    i, a = _stelle(NC_L_D, l_durch_d)
    return NC_WERTE[i] + a * (NC_WERTE[i + 1] - NC_WERTE[i])


def ruhedruckbeiwert(phi: float) -> float:
    """K_0 ≈ 1 − sin φ (Kap. 2.7) -- ``phi`` in rad."""
    return 1.0 - math.sin(phi)


def ausserhalb(phi_grad: float, h_durch_d: float) -> List[str]:
    """
    Wo X die Grenzen von Bild 12.4 verlässt, je als Satz für eine Warnung.
    Unter den Grenzen ist der Wert am Rand zu gross, über ihnen zu klein.
    """
    saetze = []
    if not X_PHI[0] <= phi_grad <= X_PHI[-1]:
        saetze.append(f"φ'_k = {phi_grad:.1f}° liegt ausserhalb von Bild 12.4 "
                      f"({X_PHI[0]:g}° bis {X_PHI[-1]:g}°): X gilt am Rand"
                      + (", zu gross." if phi_grad < X_PHI[0] else "."))
    if not X_H_D[0] <= h_durch_d <= X_H_D[-1]:
        saetze.append(f"h/D = {h_durch_d:.2f} liegt ausserhalb von Bild 12.4 "
                      f"({X_H_D[0]:g} bis {X_H_D[-1]:g}): X gilt am Rand"
                      + (", zu gross." if h_durch_d < X_H_D[0] else "."))
    return saetze
