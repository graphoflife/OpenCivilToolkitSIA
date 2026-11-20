"""
Platten der Tests für den Plattenquerschnitt und den M-N-Nachweis: h = 300
mm, b = 1 m, C30/37, Lagen nach Wahl. Sie brauchen
tests/test_plattenquerschnitt.py und tests/test_nachweis_mn.py.
"""

from opencivil.core.einheiten import MM, Groesse
from opencivil.material.beton import beton
from opencivil.material.betonstahl import betonstahl
from opencivil.querschnitt.platte import (
    Bewehrungslage, Bewehrungsposten, Plattenquerschnitt, Richtung,
)


def posten(phi: float, s: float = 150.0) -> Bewehrungsposten:
    return Bewehrungsposten(durchmesser=Groesse(phi, MM), abstand=Groesse(s, MM))


def leer() -> Bewehrungsposten:
    return Bewehrungsposten()


def lage(nummer: int, richtung: Richtung, phi: float = 0.0, zulage: float = 0.0,
         s: float = 150.0) -> Bewehrungslage:
    return Bewehrungslage(
        nummer=nummer, richtung=richtung, stahl=betonstahl("B500B"),
        grund=posten(phi, s) if phi else leer(),
        zulage=posten(zulage, s) if zulage else leer(),
    )


def platte(lagen, **abweichungen) -> Plattenquerschnitt:
    """h = 300 mm, b = 1 m, C30/37."""
    vorgaben = dict(
        name="Decke", h=Groesse(300, MM), b=Groesse(1000, MM), beton=beton("C30/37"),
        lagen=lagen, ueberdeckung_unten=Groesse(30, MM), ueberdeckung_oben=Groesse(30, MM),
    )
    vorgaben.update(abweichungen)
    return Plattenquerschnitt(**vorgaben)


def einfache_platte() -> Plattenquerschnitt:
    """Nur die 1. Lage bewehrt: ⌀18@150 in x-Richtung."""
    return platte([
        lage(1, Richtung.X, phi=18.0),
        lage(2, Richtung.Y),
        lage(3, Richtung.Y),
        lage(4, Richtung.X),
    ])


def symmetrische_platte() -> Plattenquerschnitt:
    """1. und 4. Lage gleich, beide x -- ergibt eine punktsymmetrische Linie."""
    return platte([
        lage(1, Richtung.X, phi=16.0),
        lage(2, Richtung.Y),
        lage(3, Richtung.Y),
        lage(4, Richtung.X, phi=16.0),
    ])
