"""
opencivil -- Nachweise nach SIA 262, jede Zahl mit ihrer Herleitung.

Der Einstieg ohne Oberflaeche::

    from opencivil import Projekt

    p = Projekt("Decke über EG")
    p.beton("C30/37")
    p.stahl("B500B")
    q = p.platte("Decke", h=300, x=[18, 12], y=[12, 12])
    q.einwirkung("Feld", M_Ed=100)
    print(p.rechnen().zusammenfassung())

``Projekt`` wird erst beim Zugriff geladen: wer nur ``opencivil.core``
braucht, soll dafuer nicht alle Nachweise importieren.

RECHENWEG:
Ein :class:`~opencivil.projekt.Projekt` ist eine Beschreibung -- Baustoffe,
Platten, gezeichnete Querschnitte, Einwirkungen --, so wie die Oberflaeche
sie speichert. :meth:`Projekt.aufbauen` macht daraus einen
:class:`~opencivil.projekt.aufbau.Aufbau`: ein
:class:`~opencivil.core.rechenwerk.Rechenwerk` voller Berechnungen, je
Kennwert, je Lage, je Nachweis eine.

Gefragt wird rueckwaerts: :meth:`Rechenwerk.loese` verfolgt, was ein Ziel
braucht, und rechnet genau das. Jede Berechnung schreibt dabei ihre
Herleitung ins :class:`~opencivil.core.protokoll.Protokoll` -- Formel,
Zahlen, Ergebnis. Heraus kommt eine
:class:`~opencivil.core.rechenwerk.Loesung`: die Werte, die Urteile und das
Protokoll.

Daraus setzt :mod:`opencivil.bericht` den Bericht und :mod:`opencivil.web`
die Oberflaeche -- ohne selbst zu rechnen. Daneben zeigt
:mod:`opencivil.spannungsanalyse`, was ein Querschnitt tut, ohne ihn
nachzuweisen, und :mod:`opencivil.bewehrungssuche` sucht eine Bewehrung,
statt sie zu setzen. Das Notizbuch (:mod:`opencivil.notizbuch`) schreibt aus
alldem die Formelsammlung und diese Seiten.
"""


def __getattr__(name: str):
    if name == "Projekt":
        from opencivil.projekt import Projekt
        return Projekt
    raise AttributeError(f"module 'opencivil' has no attribute '{name}'")
