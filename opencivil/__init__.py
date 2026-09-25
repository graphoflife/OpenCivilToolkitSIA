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
"""


def __getattr__(name: str):
    if name == "Projekt":
        from opencivil.projekt import Projekt
        return Projekt
    raise AttributeError(f"module 'opencivil' has no attribute '{name}'")
