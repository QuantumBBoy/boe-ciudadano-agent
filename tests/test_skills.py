"""Las cuatro skills existen y tienen frontmatter válido."""

from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parents[1] / "src" / "boe_agent" / "skills"
ESPERADAS = {"traducir", "encontrar", "vigilancia", "orientar"}


def _frontmatter(md: str) -> dict:
    assert md.startswith("---"), "falta el frontmatter YAML"
    _, fm, _ = md.split("---", 2)
    out = {}
    for line in fm.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def test_existen_las_cuatro_skills():
    presentes = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
    assert ESPERADAS <= presentes


@pytest.mark.parametrize("nombre", sorted(ESPERADAS))
def test_skill_tiene_frontmatter_valido(nombre):
    skill_md = SKILLS_DIR / nombre / "SKILL.md"
    assert skill_md.exists(), f"falta {skill_md}"
    fm = _frontmatter(skill_md.read_text(encoding="utf-8"))
    assert fm.get("name") == nombre
    assert fm.get("description"), "la description es obligatoria (decide la relevancia)"
    assert len(fm["description"]) <= 1024
