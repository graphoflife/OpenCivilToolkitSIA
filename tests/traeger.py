"""
Der Einfeldträger der Tests für Balkensysteme -- 6 m, Rechteck 300 × 600
mm, 10 kN/m. Ihn brauchen tests/test_balkensystem.py und
tests/test_balkensystem_querschnitte.py.
"""

from opencivil.projekt import Projekt


def traeger(**masse) -> Projekt:
    """Ein Einfeldträger von 6 m mit 10 kN/m -- max M = 45 kNm."""
    p = Projekt(name="Träger")
    p.beton("C30/37")
    p.stahl("B500B")
    s = p.balkensystem("Träger")
    q = s.querschnitt("R", "rechteck", **(masse or {"b": 300.0, "h": 600.0}))
    linie = s.linie((0, 0), (6, 0), querschnitt=q, material=s.beton("b1"))
    s.lager_an((0, 0), "gelenkig")
    s.lager_an((6, 0), "verschieblich")
    s.stablast(s.lastfall("G"), linie, wert=10.0)
    return p
