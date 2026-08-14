from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import sympy as sp
from pydantic import BaseModel, Field
from enum import Enum


# ---------------------------------------------------------------------------
# Variable-Group Enum
# ---------------------------------------------------------------------------

class VarGroup(str, Enum):
    """Display group for a variable in the editor UI."""
    BASIS     = "basis"       # Direct user input
    BERECHNET = "berechnet"   # Computed / derived

    def __str__(self) -> str:  # ensure f-strings yield the value, not "VarGroup.BASIS"
        return self.value


# ---------------------------------------------------------------------------
# Variable-ID Enum
# ---------------------------------------------------------------------------

class VarId(str, Enum):
    """Canonical identifiers for all known engineering variables."""
    # ---- Concrete ----------------------------------------------------------
    F_CK      = "f_ck"
    GAMMA_C   = "gamma_c"
    F_CTM     = "f_ctm"
    EPS_C1D   = "eps_c1d"
    EPS_C2D   = "eps_c2d"
    TAU_CD    = "tau_cd"
    F_CM      = "f_cm"
    K_E       = "k_e"
    GAMMA_CE  = "gamma_cE"
    E_CM      = "E_cm"
    E_CD      = "E_cd"
    ETA_FC    = "eta_fc"
    F_CD      = "f_cd"
    K_SIGMA   = "k_sigma"
    # ---- Steel -------------------------------------------------------------
    F_YK      = "f_yk"
    F_YK_MINUS= "f_yk_minus"
    E_S       = "E_s"
    GAMMA_S   = "gamma_s"
    EPS_UK    = "eps_uk"
    EPS_UD    = "eps_ud"
    F_YD      = "f_yd"
    F_YD_MINUS= "f_yd_minus"
    # ---- Geometry (plate) --------------------------------------------------
    H         = "h"
    B         = "b"
    C_NOM_BOT = "c_nom_bottom"
    C_NOM_TOP = "c_nom_top"

    def __str__(self) -> str:  # ensure f-strings yield the value, not "VarId.F_CK"
        return self.value


# ---------------------------------------------------------------------------
# Unit Enum
# ---------------------------------------------------------------------------

class Unit(str, Enum):
    """
    All physical units used across the toolkit.

    Inherits ``str`` so instances can be passed anywhere a plain string unit
    is expected (format methods, LaTeX rendering, JSON serialisation).
    """
    NONE     = ""         # dimensionless
    MPA      = "MPa"
    KN       = "kN"
    KNM      = "kNm"
    KN_PER_M = "kN/m"
    KNM_PER_M= "kNm/m"
    MM       = "mm"
    MM2      = "mm^2"
    PERCENT  = r"\%"

    def __str__(self) -> str:  # ensure f-strings yield the value, not "Unit.MM"
        return self.value


# ---------------------------------------------------------------------------
# Direction / Location / Mode Enums
# ---------------------------------------------------------------------------

class Direction(str, Enum):
    """Reinforcement direction axis."""
    X = "x"
    Y = "y"

    def __str__(self) -> str:
        return self.value

    @property
    def label(self) -> str:
        return "Längs" if self == Direction.X else "Quer"


class Location(str, Enum):
    """Face of the plate cross-section."""
    BOT = "bot"
    TOP = "top"

    def __str__(self) -> str:
        return self.value

    @property
    def label(self) -> str:
        """Human-readable German label."""
        return "Oben" if self == Location.TOP else "Unten"

    @property
    def suffix(self) -> str:
        """LaTeX subscript suffix: prime for top, empty for bottom."""
        return "'" if self == Location.TOP else ""


class PosMode(str, Enum):
    """Layer positioning mode."""
    STANDARD = "standard"
    ZULAGE   = "zulage"

    def __str__(self) -> str:
        return self.value


class RebarType(str, Enum):
    """Rebar placement specification type."""
    SPACING = "spacing"
    COUNT   = "count"

    def __str__(self) -> str:
        return self.value


class MaterialType(str, Enum):
    """Material category."""
    CONCRETE = "concrete"
    STEEL    = "steel"

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Static Definition Types (Dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class EditorConfig:
    group: VarGroup
    step: float
    row: Optional[int] = None


@dataclass
class ReportExtraDef:
    id: str
    type: str
    title: str
    reference: str
    dependencies: List[str]
    diagram_type: Optional[str] = None
    latex: Optional[str] = None


# ---------------------------------------------------------------------------
# API / Data Types (Pydantic)
# ---------------------------------------------------------------------------

class ConcreteGrade(str, Enum):
    C12_15 = "C12/15"
    C16_20 = "C16/20"
    C20_25 = "C20/25"
    C25_30 = "C25/30"
    C30_37 = "C30/37"
    C35_45 = "C35/45"
    C40_50 = "C40/50"
    C45_55 = "C45/55"
    C50_60 = "C50/60"

class SteelGrade(str, Enum):
    B500A = "B500A"
    B500B = "B500B"
    B500C = "B500C"
    B700B = "B700B"
    STAHL_II = "Stahl II"

class ConcreteTemplate(BaseModel):
    fck: float
    fctm: float

class SteelTemplate(BaseModel):
    fyk: float
    fyk_minus: float
    eps_uk: float
    eps_ud: float

class Material(BaseModel):
    id: str
    type: MaterialType
    name: str = ""
    grade: Optional[str] = None
    index: Optional[str] = None
    is_default: Optional[bool] = False
    properties: Dict[str, Any] = Field(default_factory=dict)


class RebarDir(BaseModel):
    active: bool = False
    diam: float = 0
    type: RebarType = RebarType.SPACING
    spacing: float = 150
    count: float = 0


class Layer(BaseModel):
    main_dir: Direction = Direction.X
    pos_mode: PosMode = PosMode.STANDARD
    clear_dist: float = 0
    steel_id: str = ""
    x: RebarDir = Field(default_factory=RebarDir)
    y: RebarDir = Field(default_factory=RebarDir)
    
    # Computation fields
    # In Pydantic v2, fields starting with an underscore are considered private.
    # To allow them to be mutated and stored normally without strict validation, 
    # we can use extra="allow" and normal fields. But since they are needed in Python:
    model_config = {"extra": "allow"}


# ---------------------------------------------------------------------------
# Layer Stacking Result Types (Dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class LayerItem:
    """Single rebar item within a layer group."""
    layer: Layer
    idx: int
    diam: float
    rebar: RebarDir
    is_zulage: bool


@dataclass
class LayerGroup:
    """Group of coplanar rebar layers sharing one cover distance."""
    main_dir: Direction
    layers: List[LayerItem]
    max_diam: float
    clear_dist: float
    group_idx: int
    is_dummy: bool = False
    # For dummy groups only:
    dummy_layer: Optional[Layer] = None
    dummy_idx: int = -1


@dataclass
class ComputedLayer:
    """Result for one computed reinforcement layer."""
    layer: Layer
    main_dir: Direction
    bottom_edge_dist: float
    edge_dist_str: str
    group_idx: int
    global_num: int
    is_zulage: bool
    color: str = "#000000"
    subs: Dict[Direction, str] = field(default_factory=dict)  # subscript labels per direction


@dataclass
class StackingResult:
    """Return value of _calculate_layer_stacking."""
    computed_layers: List[ComputedLayer]
    total_groups: int


class ShearConfig(BaseModel):
    active: bool = False
    diam: float = 10
    spacing: float = 150
    legs: float = 2


class Plate(BaseModel):
    id: str
    name: str
    is_plate_1m: bool = True
    h_mm: float = 300
    b_mm: float = 1000
    concrete_id: Optional[str] = None
    D_max: float = 32
    cover_top: float = 25
    cover_bottom: float = 25
    optimal_einlegen_bottom: bool = True
    optimal_einlegen_top: bool = False
    shear: ShearConfig = Field(default_factory=ShearConfig)
    top_layers: List[Layer] = Field(default_factory=list)
    bottom_layers: List[Layer] = Field(default_factory=list)
