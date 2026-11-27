"""
opencivil/projekt/beispiele_verbund.py -- die Querschnitte im Verbund des Pruefprojekts.

VERANTWORTUNG:
Die Querschnittsanalysen nach SIA 264:2014, die «Jeder Nachweis»
(:func:`opencivil.projekt.beispiele.jeder_nachweis`) einmal laut fuehrt:
zwei Verbundtraeger, einer mit Kopfbolzenduebeln, zwei Verbundstuetzen
und zwei Blechverbunddecken. Sie zeigen auf die Materialien des
Pruefprojekts: ``b1`` C30/37, ``s1`` B500B, ``st1`` S355, ``st2`` S460 und
``pb1`` SE 350 G. Bis 2026-11-27 standen sie in
:mod:`opencivil.projekt.beispiele`, die sonst ueber tausend Zeilen bekommen
haette.
"""

from __future__ import annotations

from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.querschnitt.vorlagen import kreispunkte
from opencivil.verbund.blechdecke import Belastung, Feld
from opencivil.verbund.duebel import Verduebelung


def traeger(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Ein HEA 300 aus S460 unter einer Platte 1500 × 120 mm aus C30/37, Beton
    auch zwischen den Flanschen, Betonstahl B500B in der Platte, zweiachsig
    (SIA 264:2014). Der Kammerbeton hebt die gedrückten Flansche nach
    Tabelle 3 in die Klasse 2 und den Steg nach 5.2.1.3; S460 mindert mit β.

    Im Feld plastisch und schief, die Nulllinie im Profil; an der Stütze
    negativ, der Betonstahl gezogen, mit einer Querkraft über der Hälfte von
    V_Rd, die dem Steg nimmt, und mit Torsion, die nur ein Hinweis ist; mit
    viel Druck reicht die Druckzone über 0.4 h, wo Figur 1 endet; reiner Zug,
    reiner Druck und eine Druckkraft jenseits des Widerstands.
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Verbundträger")
    a.polygon([(-150, 0), (150, 0), (150, 290), (750, 290), (750, 410), (-750, 410),
               (-750, 290), (-150, 290)], material="b1")
    a.profil(0, 145, "HEA 300", stahl="st2")
    a.stablinie([-700, 370], [700, 370], art="teilung", durchmesser=12, teilung=150,
                stahl="s1")
    a.lastfall("Feld", M_y_Ed=600.0, M_z_Ed=40.0, V_z_Ed=150.0)
    a.lastfall("Stütze", M_y_Ed=-300.0, V_z_Ed=500.0, T_Ed=2.0)
    a.lastfall("Druck mit Biegung", N_Ed=-4000.0, M_y_Ed=300.0)
    a.lastfall("Zug", N_Ed=1000.0)
    a.lastfall("Druck", N_Ed=-5000.0)
    a.lastfall("Zu viel Druck", N_Ed=-20000.0, M_y_Ed=10.0)
    return a


def traeger_mit_duebeln(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Ein IPE 400 aus S355 unter einer Platte 2000 × 150 mm aus C30/37 mit
    Betonstahl B500B, einachsig, mit Kopfbolzendübeln ⌀19 × 125 mm (SIA
    264:2014, 6.1). Im Feld teilverdübelt, (29) gehalten -- mit zu wenig
    Dübeln nicht; an der Stütze verlangt das negative Moment volle
    Verdübelung; ohne Zahl der Dübel und ohne L_e grau; L_e über 25 m
    verlangt volle Verdübelung; ohne Moment prüft er die Dübel nicht. Als
    Verbundstütze kennt ihn Tabelle 7 nicht: sein Stabilitätsfall steht grau.

    Dazu der Schubfluss: ein Schnitt längs der Oberkante des Profils trennt
    die Platte ab -- v ist, was die Dübel je Meter tragen --, ein zweiter in
    der Platte trennt nichts ab; im Feld, an der Stütze und mit einem Moment
    jenseits des Widerstands, das keinen hat.
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Verbundträger mit Dübeln")
    a.einachsig = True
    a.polygon([(-1000, 400), (1000, 400), (1000, 550), (-1000, 550)], material="b1")
    a.profil(0, 200, "IPE 400", stahl="st1")
    a.stablinie([-950, 510], [950, 510], art="teilung", durchmesser=10, teilung=300,
                stahl="s1")
    a.verduebelung = Verduebelung.KOPFBOLZEN
    a.duebel_h = 125.0
    a.lastfall("Feld", M_y_Ed=500.0, V_z_Ed=100.0, duebelzahl=25, L_e=12.0)
    a.lastfall("Feld, zu wenig Dübel", M_y_Ed=500.0, duebelzahl=15, L_e=12.0)
    a.lastfall("Stütze", M_y_Ed=-300.0, V_z_Ed=200.0, duebelzahl=12)
    a.lastfall("Ohne Zahl", M_y_Ed=400.0)
    a.lastfall("Ohne L_e", M_y_Ed=400.0, duebelzahl=30)
    a.lastfall("Weit gespannt", M_y_Ed=400.0, duebelzahl=40, L_e=30.0)
    a.lastfall("Zug", N_Ed=500.0, duebelzahl=10)
    a.stabilitaetsfall("Als Stütze", N_Ed=-1000.0, L_K_y=4.0, L_K_z=4.0, L=4.0)
    a.schnitt([-90, 400], [90, 400], seite="links")
    a.schnitt([-950, 450], [-950, 500], seite="links")
    a.schubflussfall("Feld", V_z_Ed=300.0, M_y_Ed=500.0)
    a.schubflussfall("Stütze", V_z_Ed=200.0, M_y_Ed=-300.0)
    a.schubflussfall("Zu viel", V_z_Ed=100.0, M_y_Ed=5000.0)
    return a


def stuetze(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Ein HEB 300 aus S355, ganz einbetoniert in 500 × 500 mm aus C30/37, mit
    vier ⌀20 aus B500B in den Ecken, zweiachsig, Kriechzahl 2 (SIA 264:2014,
    5.3). Einachsig gebogen um y, zweiachsig, zentrisch, um y gehalten und
    ohne Druck; grau, wo die Knicklänge die Stütze überragt und wo λ̄ über 2
    liegt; ausgeknickt, wo N_Ed N_cr,eff erreicht.
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Verbundstütze")
    a.polygon([(-250, -250), (250, -250), (250, 250), (-250, 250)], material="b1")
    a.profil(0, 0, "HEB 300", stahl="st1")
    for y, z in ((200, 200), (-200, 200), (200, -200), (-200, -200)):
        a.stab(y, z, durchmesser=20, stahl="s1")
    a.stuetze_kriechzahl = 2.0
    stuetze = dict(L_K_y=6.0, L_K_z=6.0, L=6.0, staendig=60.0)
    a.stabilitaetsfall("Einachsig", N_Ed=-6000.0, M_y_Ed=200.0, **stuetze)
    a.stabilitaetsfall("Zweiachsig", N_Ed=-4000.0, M_y_Ed=150.0, psi_y=0.5, M_z_Ed=60.0,
                       **stuetze)
    a.stabilitaetsfall("Zentrisch", N_Ed=-5000.0, **{**stuetze, "L_K_z": 4.0})
    a.stabilitaetsfall("Um y gehalten", N_Ed=-5000.0, M_y_Ed=100.0, **{**stuetze, "L_K_y": 0.0})
    a.stabilitaetsfall("Ohne Druck", M_y_Ed=100.0, **stuetze)
    a.stabilitaetsfall("Knicklänge zu lang", N_Ed=-3000.0, M_y_Ed=100.0,
                       **{**stuetze, "L_K_y": 8.0})
    a.stabilitaetsfall("Zu schlank", N_Ed=-500.0, L_K_y=30.0, L_K_z=30.0, L=30.0)
    a.stabilitaetsfall("Knickt aus", N_Ed=-9000.0, M_y_Ed=100.0, L_K_y=12.0, L_K_z=1.0, L=12.0)
    return a


def rohr(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Ein ROR 219.1 x 8 aus S355, mit C30/37 gefüllt und vier ⌀16 aus B500B,
    einachsig (SIA 264:2014, 5.3): der Beton mit 1.0 statt 0.85 (5.3.2.5),
    ρ_s unter 3 % und darum Kurve a, ohne Kriechen.
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Gefülltes Rohr")
    a.einachsig = True
    a.polygon(kreispunkte((0.0, 0.0), 101.55), material="b1")
    a.profil(0, 0, "ROR 219.1 x 8", stahl="st1")
    for y, z in ((60, 0), (-60, 0), (0, 60), (0, -60)):
        a.stab(y, z, durchmesser=16, stahl="s1")
    a.stabilitaetsfall("Druck und Biegung", N_Ed=-1500.0, M_y_Ed=30.0, psi_y=0.0, L_K_y=3.5,
                       L_K_z=3.5, L=3.5, staendig=70.0)
    return a


def blechdecke(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Eine Blechverbunddecke nach Vorgabe -- fuenf offene Rippen aus SE 350 G
    unter 140 mm C30/37, ohne Betonstahl --, das Endfeld einer durchlaufenden
    Decke unter gleichmaessiger Last (SIA 264:2014, 5.4). Im Feld Biegung,
    Querkraft und Laengsschub, mit L/d_p ueber 26; an der Stuetze traegt
    nichts Zug -- das Blech zaehlt dort nicht --, der Widerstand ist null;
    Druck mit kleinem Moment und reiner Zug, bei dem das Blech zaehlt.
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Blechverbunddecke")
    a.blechdecke(0, 0, beton="b1", blech="pb1")
    a.blech_m, a.blech_k, a.blech_L = 150.0, 0.1, 3.0
    a.blech_feld = Feld.ENDFELD
    a.lastfall("Feld", M_y_Ed=30.0, V_z_Ed=20.0)
    a.lastfall("Stütze ohne Bewehrung", M_y_Ed=-10.0, V_z_Ed=-25.0)
    a.lastfall("Druck", N_Ed=-500.0, M_y_Ed=5.0)
    a.lastfall("Zug", N_Ed=150.0)
    return a


def hinterschnittene_blechdecke(kennung: str) -> QuerschnittsanalyseEintrag:
    """
    Eine Decke von 200 mm auf hinterschnittenen Rippen, oben ⌀10 @ 150 aus
    B500B, ein Innenfeld unter zwei Einzellasten (SIA 264:2014, 5.4): ``b_0``
    ist dann ``b_o``, die Schublaenge der Abstand ``a``, und ``d_p`` liegt
    ueber 150 mm -- fuer die Querkraft gaelte SIA 262, das sagt ihr Urteil
    mit einem Hinweis. An der Stuetze traegt der
    Betonstahl; ein Fall mit ``M_z`` sagt, dass die Decke nur in einer
    Richtung traegt.
    """
    a = QuerschnittsanalyseEintrag(kennung=kennung, name="Hinterschnittene Blechdecke")
    a.blechdecke(0, 0, beton="b1", blech="pb1", h=200.0, b_o=70.0, b_u=120.0)
    a.stablinie([20, 170], [980, 170], art="teilung", durchmesser=10, teilung=150, stahl="s1")
    a.blech_m, a.blech_k, a.blech_L = 180.0, 0.05, 3.6
    a.blech_feld, a.blech_last, a.blech_a = Feld.INNENFELD, Belastung.EINZELLASTEN, 0.9
    a.lastfall("Stütze", M_y_Ed=-15.0, V_z_Ed=30.0)
    a.lastfall("Feld", M_y_Ed=25.0, V_z_Ed=20.0)
    a.lastfall("Schief", M_y_Ed=10.0, M_z_Ed=3.0)
    return a
