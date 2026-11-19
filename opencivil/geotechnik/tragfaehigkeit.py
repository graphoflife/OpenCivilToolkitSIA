"""
opencivil/geotechnik/tragfaehigkeit.py -- die Tragfähigkeitsfaktoren N_q und N_c.

VERANTWORTUNG:
N_q und N_c für einen Reibungswinkel phi, nach Kap. 9.2.6 in Lang, Huder,
Amann, Puzrin: Bodenmechanik und Grundbau, 8. Aufl. 2007::

    N_q = e^(pi tan phi) · tan²(45° + phi/2)
    N_c = (N_q - 1) / tan phi

Unter einem Fundament (:mod:`~opencivil.geotechnik.grundbruch`) und am Fuss
eines Pfahls (:mod:`~opencivil.pfahl.aussen`) dieselben Formeln -- darum in
einem Modul, das keinem der beiden gehört.

EINHEITEN:
SI-Basis; der Winkel in rad.
"""

from __future__ import annotations

import math
from typing import Tuple

from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert

#: Die Tragfähigkeitsfaktoren im Buch.
KAP_FAKTOREN = "Kap. 9.2.6"


def tragfaehigkeitsfaktoren(p: Protokoll, werte: Zwischenwerte, phi: Wert) -> Tuple[Wert, Wert]:
    """
    N_q und N_c für den Reibungswinkel ``phi`` (Kap. 9.2.6), in die
    Herleitung geschrieben -- unter einem Fundament und am Fuss eines Pfahls
    dieselben Formeln (:mod:`opencivil.pfahl.aussen`). ``phi`` grösser als null.
    """
    tan_phi = math.tan(phi.groesse.si)
    n_q = math.exp(math.pi * tan_phi) * math.tan(math.pi / 4 + phi.groesse.si / 2) ** 2
    N_q = werte.zahl("N_q", "N_q", n_q, "Tragfähigkeitsfaktor der seitlichen Auflast",
                     stellen=2)
    p.formel(N_q, r"e^{\pi \tan @phi} \cdot \tan^{2}\left(45^\circ + \frac{@phi}{2}\right)",
             {"phi": phi}, titel="Tragfähigkeitsfaktor der seitlichen Auflast",
             referenz=KAP_FAKTOREN, name="Tragfähigkeitsfaktor N_q")
    N_c = werte.zahl("N_c", "N_c", (n_q - 1.0) / tan_phi,
                     "Tragfähigkeitsfaktor der Kohäsion", stellen=2)
    p.formel(N_c, r"\frac{@N_q - 1}{\tan @phi}", {"N_q": N_q, "phi": phi},
             titel="Tragfähigkeitsfaktor der Kohäsion", referenz=KAP_FAKTOREN,
             name="Tragfähigkeitsfaktor N_c")
    return N_q, N_c
