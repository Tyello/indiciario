"""Geração procedural offline de assinaturas, rubricas e manuscritos curtos.

O módulo não depende de fontes externas, imagens ou APIs: todos os artefatos são
SVG inline determinísticos a partir de caso/personagem/seed/perfil visual.
"""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from html import escape
from random import Random
from typing import Any

SVG_NS = "http://www.w3.org/2000/svg"
HANDWRITING_MAX_CHARS = 120

STYLE_CHOICES = ("fluida", "angular", "compacta", "formal", "tremida", "apressada", "ornamental", "minimalista")
PRESSURE_CHOICES = ("leve", "media", "forte")
LEGIBILITY_CHOICES = ("baixa", "media", "alta")
SLANT_CHOICES = ("esquerda", "neutra", "direita")
AMPLITUDE_CHOICES = ("curta", "media", "longa")
ORNAMENT_CHOICES = ("nenhuma", "sublinhado", "laco", "inicial_destacada", "corte_horizontal")
VARIATION_CHOICES = ("baixa", "media", "alta")

LEGACY_STYLE_MAP = {
    "administrativa": "formal",
    "comercial": "fluida",
    "curta": "compacta",
    "rubrica": "minimalista",
    "leve": "fluida",
}
LEGACY_ORNAMENT_MAP = {"baixo": "nenhuma", "medio": "sublinhado", "alto": "laco"}
LEGACY_SLANT_MAP = {"reta": "neutra"}
LEGACY_FLUIDITY_STYLE = {"baixa": "angular", "media": "formal", "alta": "fluida"}


def _get(obj: Any, field: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(field, default)
    return getattr(obj, field, default)


def _value(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(getattr(value, "value", value))


def _slug(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(ch for ch in norm if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_") or "sem_nome"


def _stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def _rng(*parts: object) -> Random:
    return Random(_stable_int("|".join(str(part) for part in parts)))


def _profile(personagem: Any) -> dict[str, str]:
    perfil = _get(personagem, "assinatura_visual") or _get(personagem, "assinatura") or {}
    nome = _value(_get(personagem, "nome"), "Pessoa sem nome")
    pid = _value(_get(personagem, "id"), _slug(nome))
    base_seed = _value(_get(perfil, "seed"), f"{pid}:{nome}")
    chooser = _rng("profile", base_seed)

    estilo = _value(_get(perfil, "estilo"), "")
    if estilo in LEGACY_STYLE_MAP:
        estilo = LEGACY_STYLE_MAP[estilo]
    if not estilo:
        fluidez = _value(_get(perfil, "fluidez"), "")
        estilo = LEGACY_FLUIDITY_STYLE.get(fluidez) or STYLE_CHOICES[chooser.randrange(len(STYLE_CHOICES))]
    if estilo not in STYLE_CHOICES:
        estilo = "formal"

    pressao = _value(_get(perfil, "pressao"), "") or PRESSURE_CHOICES[chooser.randrange(len(PRESSURE_CHOICES))]
    legibilidade = _value(_get(perfil, "legibilidade"), "") or LEGIBILITY_CHOICES[chooser.randrange(len(LEGIBILITY_CHOICES))]
    inclinacao = _value(_get(perfil, "inclinacao"), "")
    inclinacao = LEGACY_SLANT_MAP.get(inclinacao, inclinacao) or SLANT_CHOICES[chooser.randrange(len(SLANT_CHOICES))]
    amplitude = _value(_get(perfil, "amplitude"), "") or ("curta" if estilo in {"compacta", "minimalista"} else "longa" if estilo == "ornamental" else "media")
    ornamentacao = _value(_get(perfil, "ornamentacao"), "")
    if not ornamentacao:
        ornamentacao = LEGACY_ORNAMENT_MAP.get(_value(_get(perfil, "ornamento"), ""), "")
    if not ornamentacao:
        ornamentacao = ORNAMENT_CHOICES[chooser.randrange(len(ORNAMENT_CHOICES))]
    variacao = _value(_get(perfil, "variacao"), "")
    if variacao.isdigit():
        n = int(variacao)
        variacao = "baixa" if n <= 3 else "media" if n <= 8 else "alta"
    if variacao not in VARIATION_CHOICES:
        variacao = VARIATION_CHOICES[chooser.randrange(len(VARIATION_CHOICES))]

    return {
        "nome": nome,
        "id": pid,
        "estilo": estilo,
        "pressao": pressao if pressao in PRESSURE_CHOICES else "media",
        "legibilidade": legibilidade if legibilidade in LEGIBILITY_CHOICES else "media",
        "inclinacao": inclinacao if inclinacao in SLANT_CHOICES else "neutra",
        "amplitude": amplitude if amplitude in AMPLITUDE_CHOICES else "media",
        "ornamentacao": ornamentacao if ornamentacao in ORNAMENT_CHOICES else "nenhuma",
        "variacao": variacao,
        "seed": base_seed,
        "classe_estilo": _value(_get(perfil, "estilo"), estilo) or estilo,
    }


def _pressure_width(pressure: str, mode: str) -> float:
    base = {"leve": 0.9, "media": 1.25, "forte": 1.65}.get(pressure, 1.25)
    return base - (0.15 if mode == "rubrica" else 0.0)


def _slant_degrees(slant: str, rng: Random, variation: str) -> float:
    base = {"esquerda": -7.0, "neutra": 0.0, "direita": 8.0}.get(slant, 0.0)
    spread = {"baixa": 1.5, "media": 3.5, "alta": 6.0}.get(variation, 3.0)
    return base + rng.uniform(-spread, spread)


def _initials(name: str) -> str:
    parts = [p for p in re.split(r"\s+", name.replace(".", " ").strip()) if p]
    return "".join(part[0] for part in parts[:3]).upper() or "?"


def _signature_points(width: int, height: int, profile: dict[str, str], mode: str) -> list[tuple[float, float]]:
    rng = _rng("points", profile["seed"], profile["id"], mode, profile["estilo"])
    count = 5 if mode == "rubrica" else {"curta": 7, "media": 10, "longa": 13}[profile["amplitude"]]
    if profile["estilo"] == "minimalista":
        count = max(4, count - 3)
    if profile["estilo"] == "ornamental" and mode == "assinatura":
        count += 3
    margin = 12 if mode == "rubrica" else 16
    usable = width - 2 * margin
    baseline = height * (0.58 if mode == "assinatura" else 0.55)
    amp = {"baixa": 5, "media": 9, "alta": 14}[profile["variacao"]]
    if profile["estilo"] in {"tremida", "apressada"}:
        amp += 5
    if profile["estilo"] == "formal":
        amp = max(4, amp - 4)
    points = []
    for i in range(count):
        x = margin + (usable * i / (count - 1))
        wave = math.sin(i * 1.28 + rng.random()) * amp
        jitter = rng.uniform(-amp * 0.55, amp * 0.55)
        y = baseline + wave + jitter
        if profile["estilo"] == "angular":
            y += (-1) ** i * amp * 0.85
        points.append((round(x, 2), round(max(8, min(height - 10, y)), 2)))
    return points


def _path_from_points(points: list[tuple[float, float]], style: str, rng: Random) -> str:
    if not points:
        return ""
    d = [f"M {points[0][0]:g} {points[0][1]:g}"]
    if style in {"angular", "tremida", "minimalista"}:
        for x, y in points[1:]:
            d.append(f"L {x:g} {y:g}")
        return " ".join(d)
    for idx in range(1, len(points)):
        x0, y0 = points[idx - 1]
        x1, y1 = points[idx]
        dx = (x1 - x0) / 2
        c1 = (x0 + dx * rng.uniform(0.55, 0.95), y0 + rng.uniform(-8, 8))
        c2 = (x1 - dx * rng.uniform(0.55, 0.95), y1 + rng.uniform(-8, 8))
        d.append(f"C {c1[0]:g} {c1[1]:g}, {c2[0]:g} {c2[1]:g}, {x1:g} {y1:g}")
    return " ".join(d)


def _letter_gestures(profile: dict[str, str], mode: str, width: int, height: int) -> list[str]:
    if profile["legibilidade"] == "baixa" and mode == "rubrica":
        return []
    rng = _rng("letters", profile["seed"], profile["nome"], mode)
    initials = _initials(profile["nome"])
    count = 1 if mode == "rubrica" else {"baixa": 1, "media": min(2, len(initials)), "alta": min(3, len(initials))}[profile["legibilidade"]]
    paths: list[str] = []
    x = 18 if mode == "assinatura" else 14
    base = height * 0.56
    for idx, _char in enumerate(initials[:count]):
        h = rng.uniform(18, 30) if mode == "assinatura" else rng.uniform(14, 22)
        w = rng.uniform(8, 16)
        if idx == 0 and profile["ornamentacao"] == "inicial_destacada":
            h *= 1.25
            w *= 1.15
        top = base - h
        left = x + idx * (w + 9)
        if profile["estilo"] == "angular":
            d = f"M {left:g} {base:g} L {left + w * .45:g} {top:g} L {left + w:g} {base - rng.uniform(3, 9):g} M {left + w*.25:g} {base-h*.45:g} L {left+w*.85:g} {base-h*.55:g}"
        else:
            d = f"M {left:g} {base:g} C {left-3:g} {top+h*.25:g}, {left+w*.2:g} {top:g}, {left+w*.55:g} {top+2:g} C {left+w*1.25:g} {top+5:g}, {left+w*.8:g} {base-3:g}, {left+w*1.15:g} {base-rng.uniform(2, 8):g}"
        paths.append(d)
    return paths


def _ornament_paths(profile: dict[str, str], mode: str, width: int, height: int) -> list[str]:
    rng = _rng("orn", profile["seed"], mode, profile["ornamentacao"])
    base = height * (0.76 if mode == "assinatura" else 0.72)
    paths: list[str] = []
    ornament = profile["ornamentacao"]
    if ornament == "sublinhado" or (mode == "rubrica" and ornament == "nenhuma"):
        paths.append(f"M 18 {base:g} C {width*.25:g} {base+rng.uniform(4, 8):g}, {width*.62:g} {base+rng.uniform(-4, 3):g}, {width-18:g} {base+rng.uniform(2, 7):g}")
    elif ornament == "laco":
        paths.append(f"M {width*.18:g} {base:g} c 18 -18, 36 -18, 28 0 c -7 13, -25 10, -18 -4 C {width*.42:g} {base+7:g}, {width*.7:g} {base-2:g}, {width-18:g} {base+4:g}")
    elif ornament == "corte_horizontal":
        y = height * 0.5
        paths.append(f"M 10 {y:g} L {width-12:g} {y+rng.uniform(-3, 3):g}")
    return paths


def _svg(paths: list[tuple[str, float, float]], width: int, height: int, cls: str, label: str, rotate: float, scale_y: float = 1.0) -> str:
    body = []
    for d, stroke_width, opacity in paths:
        body.append(
            f'<path d="{escape(d, quote=True)}" fill="none" stroke="#111" stroke-width="{stroke_width:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round" opacity="{opacity:.2f}"/>'
        )
    return (
        f'<svg class="signature-svg {cls}" xmlns="{SVG_NS}" viewBox="0 0 {width} {height}" '
        f'aria-label="{escape(label)}" role="img">'
        f'<g transform="rotate({rotate:.2f} {width/2:g} {height/2:g}) scale(1 {scale_y:.3f})">'
        f'{"".join(body)}</g></svg>'
    )


def build_signature_svg(personagem: Any, modo: str = "assinatura") -> str:
    """Retorna SVG inline para assinatura completa ou rubrica de um personagem."""
    mode = "rubrica" if modo == "rubrica" else "assinatura"
    profile = _profile(personagem)
    rng = _rng("signature", profile["seed"], profile["nome"], mode)
    width = 142 if mode == "rubrica" else {"curta": 196, "media": 238, "longa": 282}[profile["amplitude"]]
    height = 46 if mode == "rubrica" else 66
    if profile["estilo"] == "compacta":
        width = int(width * 0.82)
    if profile["estilo"] == "ornamental" and mode == "assinatura":
        width += 24
        height += 8
    points = _signature_points(width, height, profile, mode)
    main = _path_from_points(points, profile["estilo"], rng)
    stroke = _pressure_width(profile["pressao"], mode)
    paths: list[tuple[str, float, float]] = [(main, stroke, 0.86)]
    for d in _letter_gestures(profile, mode, width, height):
        paths.append((d, max(0.8, stroke - 0.1), 0.76))
    for d in _ornament_paths(profile, mode, width, height):
        paths.append((d, max(0.65, stroke - 0.35), 0.58))
    if mode == "rubrica":
        # Rubrica recebe um gesto final próprio para nunca ser só assinatura reduzida.
        y = height * 0.48 + rng.uniform(-4, 4)
        paths.append((f"M {width-38:g} {y:g} q 13 {-14+rng.uniform(-3,3):g} 27 {0+rng.uniform(-3,3):g} q -8 8 -18 15", max(0.7, stroke - 0.2), 0.72))
    cls = (
        f"signature-perfil signature-{mode} estilo-{profile['classe_estilo']} "
        f"estilo-p3-{profile['estilo']} pressao-{profile['pressao']} legibilidade-{profile['legibilidade']} "
        f"inclinacao-{profile['inclinacao']} amplitude-{profile['amplitude']} ornamentacao-{profile['ornamentacao']} variacao-{profile['variacao']}"
    )
    rotate = _slant_degrees(profile["inclinacao"], rng, profile["variacao"])
    scale_y = 0.96 + rng.uniform(-0.035, 0.04)
    return _svg(paths, width, height, cls, f"{mode} manuscrita {profile['nome']}", rotate, scale_y)


def build_handwritten_note_svg(texto: str, personagem: Any, largura_maxima: int = 320) -> str:
    """Retorna SVG inline para anotação manuscrita curta (até 120 caracteres)."""
    clean = " ".join(str(texto or "").strip().split())
    profile = _profile(personagem)
    rng = _rng("hand", profile["seed"], profile["nome"], clean, largura_maxima)
    visible = clean[:HANDWRITING_MAX_CHARS]
    width = max(120, min(int(largura_maxima), 36 + len(visible) * 6))
    height = 34 + max(0, math.ceil(len(visible) / 42) - 1) * 18
    stroke = max(0.55, _pressure_width(profile["pressao"], "rubrica") - 0.25)
    paths: list[tuple[str, float, float]] = []
    x = 12.0
    y = 20.0
    max_x = width - 16
    for index, ch in enumerate(visible):
        if ch == " ":
            x += rng.uniform(4.5, 7.0)
            continue
        if x > max_x - 8:
            x = 12 + rng.uniform(-1, 4)
            y += 17 + rng.uniform(-2, 2)
        h = rng.uniform(4.0, 10.0)
        w = rng.uniform(2.5, 5.5)
        base = y + rng.uniform(-2.0, 2.2)
        if profile["estilo"] == "angular":
            d = f"M {x:g} {base:g} l {w*.45:g} {-h:g} l {w*.65:g} {h+rng.uniform(-2,2):g}"
        elif ch in ".,;:!?'\"":
            d = f"M {x:g} {base:g} q {w*.5:g} {-h*.45:g} {w:g} 0"
        else:
            d = f"M {x:g} {base:g} c {w*.25:g} {-h:g}, {w*.9:g} {-h:g}, {w:g} {-1:g} c {w*.35:g} {h*.55:g}, {w*.8:g} {h*.35:g}, {w*1.25:g} {-0.8:g}"
        paths.append((d, stroke + rng.uniform(-0.08, 0.1), 0.82))
        x += w + rng.uniform(2.0, 4.4)
        if index % 9 == 0:
            paths.append((f"M {max(10, x-7):g} {base+2.8:g} l {rng.uniform(4, 9):g} {rng.uniform(-1.2, 1.2):g}", max(0.45, stroke - 0.28), 0.32))
    cls = f"handwritten-note-svg estilo-p3-{profile['estilo']} pressao-{profile['pressao']} personagem-{_slug(profile['id'])}"
    rotate = rng.uniform(-2.4, 2.4)
    return _svg(paths, width, height, cls, f"anotação manuscrita {profile['nome']}", rotate)


def is_svg_like(value: str) -> bool:
    return bool(re.search(r"<svg\b", value or "", flags=re.IGNORECASE) and re.search(r"</svg>", value or "", flags=re.IGNORECASE))
