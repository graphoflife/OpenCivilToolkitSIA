"""
opencivil/stahlprofile/tabelle.py -- welche Stahlprofile es gibt, mit ihren Massen.

VERANTWORTUNG:
Die Reihen der Walzprofile und Rohre und je Groesse ihre Masse in mm. Was
daraus gerechnet wird, sagt die Form der Reihe
(:mod:`opencivil.stahlprofile.formen`); gesucht wird ein Profil nach seinem
Namen (:func:`profil`).

QUELLE:
Die Tabelle des Benutzers, «Festigkeitsnachweise I-Standardprofile Stahl» vom
2019-04-15, Blatt «Querschnitte» -- dieselben Groessen in derselben Folge
(Benutzer, 2026-11-15). Was noch fehlt -- L, INP, T, HEAA und die
warmgefertigten Rechteckrohre --, steht im Notizbuch unter TODO.

NACH VORGABE, NICHT NACHGESCHLAGEN:
* RRK: die Radien aus der Wanddicke, wie in der Tabelle -- bis t = 6 mm
  r_o = 2t und r_i = t, bis 10 mm 2.5t und 1.5t, darueber 3t und 2t.
* UNP: bis h = 300 mm sind die Flansche um 8 % geneigt, und t_f gilt bei
  b/2; darueber 5 %, und t_f gilt in der Mitte des Flanschs, (b + t_w)/2.
  Damit trifft die Rechnung die Werte der Tabelle, die keine Formeln hat.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Tuple

from opencivil.stahlprofile.formen import (
    I_PROFIL, RECHTECKROHR_KALT, RUNDROHR, U_GENEIGT, U_PARALLEL,
)
from opencivil.stabwerk.querschnitte import Stabvorlage


@dataclass(frozen=True)
class Profil:
    """Eine Groesse einer Reihe: ihr Name und die Masse ihrer Form."""

    name: str
    reihe: str
    masse: Mapping[str, float]

    @property
    def form(self) -> Stabvorlage:
        return _REIHEN[self.reihe].form


@dataclass(frozen=True)
class Profilreihe:
    kurz: str
    """Wie die Reihe heisst und womit jeder ihrer Namen beginnt: «IPE»."""

    beschreibung: str
    form: Stabvorlage
    profile: Tuple[Profil, ...]


# ---------------------------------------------------------------------------
# Die Masse, Zeile fuer Zeile wie in der Tabelle
# ---------------------------------------------------------------------------

#: I-Profile: Name, h, b, t_w, t_f, r.
_I_PROFILE = """
IPE 80      80   46   3.8   5.2   5
IPE 100    100   55   4.1   5.7   7
IPE 120    120   64   4.4   6.3   7
IPE 140    140   73   4.7   6.9   7
IPE 160    160   82     5   7.4   9
IPE 180    180   91   5.3     8   9
IPE 200    200  100   5.6   8.5  12
IPE 220    220  110   5.9   9.2  12
IPE 240    240  120   6.2   9.8  15
IPE 270    270  135   6.6  10.2  15
IPE 300    300  150   7.1  10.7  15
IPE 330    330  160   7.5  11.5  18
IPE 360    360  170     8  12.7  18
IPE 400    400  180   8.6  13.5  21
IPE 450    450  190   9.4  14.6  21
IPE 500    500  200  10.2    16  21
IPE 550    550  210  11.1  17.2  24
IPE 600    600  220    12    19  24
HEA 100     96  100     5     8  12
HEA 120    114  120     5     8  12
HEA 140    133  140   5.5   8.5  12
HEA 160    152  160     6     9  15
HEA 180    171  180     6   9.5  15
HEA 200    190  200   6.5    10  18
HEA 220    210  220     7    11  18
HEA 240    230  240   7.5    12  21
HEA 260    250  260   7.5  12.5  24
HEA 280    270  280     8    13  24
HEA 300    290  300   8.5    14  27
HEA 320    310  300     9  15.5  27
HEA 340    330  300   9.5  16.5  27
HEA 360    350  300    10  17.5  27
HEA 400    390  300    11    19  27
HEA 450    440  300  11.5    21  27
HEA 500    490  300    12    23  27
HEA 550    540  300  12.5    24  27
HEA 600    590  300    13    25  27
HEA 650    640  300  13.5    26  27
HEA 700    690  300  14.5    27  27
HEA 800    790  300    15    28  30
HEA 900    890  300    16    30  30
HEA 1000   990  300  16.5    31  30
HEB 100    100  100     6    10  12
HEB 120    120  120   6.5    11  12
HEB 140    140  140     7    12  12
HEB 160    160  160     8    13  15
HEB 180    180  180   8.5    14  15
HEB 200    200  200     9    15  18
HEB 220    220  220   9.5    16  18
HEB 240    240  240    10    17  21
HEB 260    260  260    10  17.5  24
HEB 280    280  280  10.5    18  24
HEB 300    300  300    11    19  27
HEB 320    320  300  11.5  20.5  27
HEB 340    340  300    12  21.5  27
HEB 360    360  300  12.5  22.5  27
HEB 400    400  300  13.5    24  27
HEB 450    450  300    14    26  27
HEB 500    500  300  14.5    28  27
HEB 550    550  300    15    29  27
HEB 600    600  300  15.5    30  27
HEB 650    650  300    16    31  27
HEB 700    700  300    17    32  27
HEB 800    800  300  17.5    33  30
HEB 900    900  300  18.5    35  30
HEB 1000  1000  300    19    36  30
HEM 100    120  106    12    20  12
HEM 120    140  126  12.5    21  12
HEM 140    160  146    13    22  12
HEM 160    180  166    14    23  15
HEM 180    200  186  14.5    24  15
HEM 200    220  206    15    25  18
HEM 220    240  226  15.5    26  18
HEM 240    270  248    18    32  21
HEM 260    290  268    18  32.5  24
HEM 280    310  288  18.5    33  24
HEM 300    340  310    21    39  27
HEM 320    359  309    21    40  27
HEM 340    377  309    21    40  27
HEM 360    395  308    21    40  27
HEM 400    432  307    21    40  27
HEM 450    478  307    21    40  27
HEM 500    524  306    21    40  27
HEM 550    572  306    21    40  27
HEM 600    620  305    21    40  27
HEM 650    668  305    21    40  27
HEM 700    716  304    21    40  27
HEM 800    814  303    21    40  30
HEM 900    910  302    21    40  30
HEM 1000  1008  302    21    40  30
"""

#: UPE: Name, h, b, t_w, t_f, r.
_UPE = """
UPE 80    80   50     4     7  10
UPE 100  100   55   4.5   7.5  10
UPE 120  120   60     5     8  12
UPE 140  140   65     5     9  12
UPE 160  160   70   5.5   9.5  12
UPE 180  180   75   5.5  10.5  12
UPE 200  200   80     6    11  13
UPE 220  220   85   6.5    12  13
UPE 240  240   90     7  12.5  15
UPE 270  270   95   7.5  13.5  15
UPE 300  300  100   9.5    15  15
UPE 330  330  105    11    16  18
UPE 360  360  110    12    17  18
UPE 400  400  115  13.5    18  18
"""

#: UNP: Name, h, b, t_w, t_f, r_1, r_2.
_UNP = """
UNP 65    65   42   5.5   7.5   7.5     4
UNP 80    80   45     6     8     8     4
UNP 100  100   50     6   8.5   8.5   4.5
UNP 120  120   55     7     9     9   4.5
UNP 140  140   60     7    10    10     5
UNP 160  160   65   7.5  10.5  10.5   5.5
UNP 180  180   70     8    11    11   5.5
UNP 200  200   75   8.5  11.5  11.5     6
UNP 220  220   80     9  12.5  12.5   6.5
UNP 240  240   85   9.5    13    13   6.5
UNP 260  260   90    10    14    14     7
UNP 280  280   95    10    15    15   7.5
UNP 300  300  100    10    16    16     8
UNP 320  320  100    14  17.5  17.5  8.75
UNP 350  350  100    14    16    16     8
UNP 380  380  102  13.5    16    16     8
UNP 400  400  110    14    18    18     9
"""

#: RRK: h, b, t -- erst die quadratischen, dann die rechteckigen.
_RRK = """
 20   20     2
 25   25     2
 25   25   2.5
 25   25     3
 30   30     2
 30   30   2.5
 30   30     3
 40   40     2
 40   40   2.5
 40   40     3
 40   40     4
 50   50     2
 50   50   2.5
 50   50     3
 50   50     4
 50   50     5
 60   60     2
 60   60   2.5
 60   60     3
 60   60     4
 60   60     5
 60   60     6
 60   60   6.3
 70   70   2.5
 70   70     3
 70   70     4
 70   70     5
 70   70     6
 70   70   6.3
 80   80     3
 80   80     4
 80   80     5
 80   80     6
 80   80   6.3
 80   80     8
 90   90     3
 90   90     4
 90   90     5
 90   90     6
 90   90   6.3
 90   90     8
100  100     3
100  100     4
100  100     5
100  100     6
100  100   6.3
100  100     8
100  100    10
100  100    12
100  100  12.5
120  120     3
120  120     4
120  120     5
120  120     6
120  120   6.3
120  120     8
120  120    10
120  120    12
120  120  12.5
140  140     4
140  140     5
140  140     6
140  140   6.3
140  140     8
140  140    10
140  140    12
140  140  12.5
150  150     4
150  150     5
150  150     6
150  150   6.3
150  150     8
150  150    10
150  150    12
150  150  12.5
150  150    16
160  160     4
160  160     5
160  160     6
160  160   6.3
160  160     8
160  160    10
160  160    12
160  160  12.5
160  160    16
180  180     4
180  180     5
180  180     6
180  180   6.3
180  180     8
180  180    10
180  180    12
180  180  12.5
180  180    16
200  200     4
200  200     5
200  200     6
200  200   6.3
200  200     8
200  200    10
200  200    12
200  200  12.5
200  200    16
220  220     5
220  220     6
220  220   6.3
220  220     8
220  220    10
220  220    12
220  220  12.5
220  220    16
250  250     5
250  250     6
250  250   6.3
250  250     8
250  250    10
250  250    12
250  250  12.5
250  250    16
260  260     6
260  260   6.3
260  260     8
260  260    10
260  260    12
260  260  12.5
260  260    16
300  300     6
300  300   6.3
300  300     8
300  300    10
300  300    12
300  300  12.5
300  300    16
350  350     8
350  350    10
350  350    12
350  350  12.5
350  350    16
400  400    10
400  400    12
400  400  12.5
400  400    16
 40   20     2
 40   20   2.5
 40   20     3
 50   30     2
 50   30   2.5
 50   30     3
 50   30     4
 60   40     2
 60   40   2.5
 60   40     3
 60   40     4
 60   40     5
 70   50     2
 70   50   2.5
 70   50     3
 70   50     4
 70   50     5
 80   40     2
 80   40   2.5
 80   40     3
 80   40     4
 80   40     5
 80   60     2
 80   60   2.5
 80   60     3
 80   60     4
 80   60     5
 90   50     2
 90   50   2.5
 90   50     3
 90   50     4
 90   50     5
100   40   2.5
100   40     3
100   40     4
100   40     5
100   50   2.5
100   50     3
100   50     4
100   50     5
100   50     6
100   50   6.3
100   60   2.5
100   60     3
100   60     4
100   60     5
100   60     6
100   60   6.3
100   80   2.5
100   80     3
100   80     4
100   80     5
100   80     6
100   80   6.3
120   60   2.5
120   60     3
120   60     4
120   60     5
120   60     6
120   60   6.3
120   60     8
120   80     3
120   80     4
120   80     5
120   80     6
120   80   6.3
120   80     8
140   80     4
140   80     5
140   80     6
140   80   6.3
140   80     8
150  100     5
150  100     6
150  100   6.3
150  100     8
150  100    10
150  100    12
150  100  12.5
160   80     4
160   80     5
160   80     6
160   80   6.3
160   80     8
160   80    10
160   80    12
160   80  12.5
180  100     4
180  100     5
180  100     6
180  100   6.3
180  100     8
180  100    10
180  100    12
180  100  12.5
200  100     4
200  100     6
200  100   6.3
200  100     8
200  100    10
200  100    12
200  100  12.5
200  120     4
200  120     5
200  120     6
200  120   6.3
200  120     8
200  120    10
200  120    12
200  120  12.5
250  150     5
250  150     6
250  150   6.3
250  150     8
250  150    10
250  150    12
250  150  12.5
250  150    16
260  180     5
260  180     6
260  180   6.3
260  180     8
260  180    10
260  180    12
260  180  12.5
260  180    16
300  100     6
300  100   6.3
300  100     8
300  100    10
300  100    12
300  100  12.5
300  100    16
300  150     6
300  150   6.3
300  150     8
300  150    10
300  150    12
300  150  12.5
300  150    16
300  200     6
300  200   6.3
300  200     8
300  200    10
300  200    12
300  200  12.5
300  200    16
350  250     6
350  250   6.3
350  250     8
350  250    10
350  250    12
350  250  12.5
350  250    16
400  200     8
400  200    10
400  200    12
400  200  12.5
400  200    16
400  300     8
400  300    10
400  300    12
400  300  12.5
400  300    16
"""

#: ROR: D, t.
_ROR = """
 21.3   2.3
 21.3   2.6
 21.3   3.2
 26.9   2.3
 26.9   2.6
 26.9   3.2
 33.7   2.6
 33.7   3.2
 33.7     4
 42.4   2.6
 42.4   3.2
 42.4     4
 48.3   2.6
 48.3   3.2
 48.3     4
 48.3     5
 60.3   2.6
 60.3   3.2
 60.3     4
 60.3     5
 76.1   2.6
 76.1   3.2
 76.1     4
 76.1     5
 88.9   3.2
 88.9     4
 88.9     5
 88.9     6
 88.9   6.3
101.6   3.2
101.6     4
101.6     5
101.6     6
101.6   6.3
101.6     8
101.6    10
114.3   3.2
114.3     4
114.3     5
114.3     6
114.3   6.3
114.3     8
114.3    10
139.7     4
139.7     5
139.7     6
139.7   6.3
139.7     8
139.7    10
139.7    12
139.7  12.5
168.3     4
168.3     5
168.3     6
168.3   6.3
168.3     8
168.3    10
168.3    12
168.3  12.5
177.8     5
177.8     6
177.8   6.3
177.8     8
177.8    10
177.8    12
177.8  12.5
193.7     5
193.7     6
193.7   6.3
193.7   7.1
193.7     8
193.7    10
193.7    12
193.7  12.5
193.7    16
219.1     5
219.1     6
219.1   6.3
219.1     8
219.1    10
219.1    12
219.1  12.5
219.1    16
219.1    20
244.5     5
244.5     6
244.5   6.3
244.5     8
244.5    10
244.5    12
244.5  12.5
244.5    16
244.5    20
244.5    25
  273     5
  273     6
  273   6.3
  273     8
  273    10
  273    11
  273    12
  273  12.5
  273    16
  273    20
  273    25
323.9     5
323.9     6
323.9   6.3
323.9     8
323.9    10
323.9    12
323.9  12.5
323.9    16
323.9    20
323.9    25
355.6     6
355.6   6.3
355.6     8
355.6    10
355.6    12
355.6  12.5
355.6    16
355.6    20
355.6    25
406.4     6
406.4   6.3
406.4     8
406.4    10
406.4    12
406.4  12.5
406.4    16
406.4    20
406.4    25
406.4    30
406.4    40
  457     6
  457   6.3
  457     8
  457    10
  457    12
  457  12.5
  457    16
  457    20
  457    25
  457    30
  457    40
  508     6
  508   6.3
  508     8
  508    10
  508    12
  508  12.5
  508    16
  508    20
  508    25
  508    30
  508    40
  508    50
  610     6
  610   6.3
  610     8
  610    10
  610    12
  610  12.5
  610    16
  610    20
  610    25
  610    30
  610    40
  610    50
  660   7.1
  660  14.2
  711     6
  711   6.3
  711     8
  711    10
  711    12
  711  12.5
  711    16
  711    20
  711    25
  711    30
  711    40
  711    50
  711    60
  762     6
  762   6.3
  762     8
  762    10
  762    12
  762    16
  762    20
  762    25
  762    30
  762    40
  762    50
  813     8
  813    10
  813    12
  813  12.5
  813    16
  813    20
  813    25
  813    30
  914     8
  914    10
  914    12
  914  12.5
  914    16
  914    20
  914    25
  914    30
 1016     8
 1016    10
 1016    12
 1016  12.5
 1016    16
 1016    20
 1016    25
 1016    30
 1067    10
 1067    12
 1067  12.5
 1067    16
 1067    20
 1067    25
 1067    30
 1168    10
 1168    12
 1168  12.5
 1168    16
 1168    20
 1168    25
 1219    10
 1219    12
 1219  12.5
 1219    16
 1219    20
 1219    25
"""


def _zahlen(text: str) -> List[List[str]]:
    return [zeile.split() for zeile in text.strip().splitlines()]


def _z(text: str) -> str:
    """Eine Zahl, wie sie im Namen steht: 21.3, 400."""
    return f"{float(text):g}"


def _unp(h: float, b: float, t_w: float, t_f: float, r_1: float, r_2: float) -> Dict[str, float]:
    """Die Masse eines UNP -- Neigung p in % und die Stelle c von t_f nach der Hoehe."""
    p, c = (8.0, b / 2) if h <= 300.0 else (5.0, (b + t_w) / 2)
    return dict(h=h, b=b, t_w=t_w, t_f=t_f, r_1=r_1, r_2=r_2, p=p, c=c)


def _rrk(h: float, b: float, t: float) -> Dict[str, float]:
    """Die Masse eines RRK -- die Radien aus der Wanddicke."""
    r_o, r_i = (2.0 * t, t) if t <= 6.0 else (2.5 * t, 1.5 * t) if t <= 10.0 else (3.0 * t, 2.0 * t)
    return dict(h=h, b=b, t=t, r_o=r_o, r_i=r_i)


def _benannt(kurz: str, text: str, masse: Callable[..., Dict[str, float]]) -> Tuple[Profil, ...]:
    """Die Zeilen einer Reihe, deren Name vorne steht: «IPE 80  80  46 ...»."""
    return tuple(Profil(f"{z[0]} {z[1]}", kurz, masse(*map(float, z[2:])))
                 for z in _zahlen(text) if z[0] == kurz)


def _i(h: float, b: float, t_w: float, t_f: float, r: float) -> Dict[str, float]:
    return dict(h=h, b=b, t_w=t_w, t_f=t_f, r=r)


PROFILREIHEN: Tuple[Profilreihe, ...] = (
    Profilreihe("IPE", "I-Träger, schmale Flansche", I_PROFIL, _benannt("IPE", _I_PROFILE, _i)),
    Profilreihe("HEA", "Breitflanschträger, leichte Reihe", I_PROFIL, _benannt("HEA", _I_PROFILE, _i)),
    Profilreihe("HEB", "Breitflanschträger", I_PROFIL, _benannt("HEB", _I_PROFILE, _i)),
    Profilreihe("HEM", "Breitflanschträger, verstärkte Reihe", I_PROFIL, _benannt("HEM", _I_PROFILE, _i)),
    Profilreihe("UPE", "U-Profil mit parallelen Flanschen", U_PARALLEL, _benannt("UPE", _UPE, _i)),
    Profilreihe("UNP", "U-Profil mit geneigten Flanschen", U_GENEIGT, _benannt("UNP", _UNP, _unp)),
    Profilreihe("RRK", "Rechteckrohr, kaltgefertigt", RECHTECKROHR_KALT, tuple(
        Profil(f"RRK {_z(h)} x {_z(b)} x {_z(t)}", "RRK", _rrk(float(h), float(b), float(t)))
        for h, b, t in _zahlen(_RRK))),
    Profilreihe("ROR", "Rundrohr", RUNDROHR, tuple(
        Profil(f"ROR {_z(D)} x {_z(t)}", "ROR", dict(D=float(D), t=float(t)))
        for D, t in _zahlen(_ROR))),
)

#: Jedes Profil nach seinem Namen -- «HEB 300», «RRK 200 x 100 x 8».
PROFILE: Dict[str, Profil] = {p.name: p for r in PROFILREIHEN for p in r.profile}

_REIHEN: Dict[str, Profilreihe] = {r.kurz: r for r in PROFILREIHEN}


def reihe(kurz: str) -> Profilreihe:
    return _REIHEN[kurz]


def profil(name: str) -> Profil:
    """Das Profil dieses Namens -- ein unbekannter ist ein ``KeyError``, der es sagt."""
    try:
        return PROFILE[name]
    except KeyError:
        raise KeyError(f"Ein Profil «{name}» gibt es nicht.") from None
