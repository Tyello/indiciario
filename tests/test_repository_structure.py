from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_framework_core_files_exist():
    expected = [
        "00_README.md",
        "01_PRINCIPIOS_DO_MODELO.md",
        "02_ESTRUTURA_ENVELOPES.md",
        "03_TIPOS_DE_DOCUMENTOS.md",
        "04_DESIGN_DE_PISTAS.md",
        "05_CHECKLIST_SOLVABILIDADE.md",
        "06_TEMPLATE_NOVO_CASO.md",
        "07_PROMPT_GERADOR_DE_CASO.md",
        "08_MODELO_REFERENCIA.md",
        "09_TEMPLATE_GABARITO.md",
        "10_TEMPLATE_DICAS.md",
        "11_GUIA_DO_FACILITADOR.md",
        "12_GUIA_DE_PRODUCAO.md",
    ]
    missing = [name for name in expected if not (ROOT / "framework" / name).exists()]
    assert not missing, f"Arquivos de framework ausentes: {missing}"


def test_project_operational_files_exist():
    expected = [
        "AGENTS.md",
        ".gitignore",
        ".env.example",
        "generator/__init__.py",
        "generator/models.py",
        "generator/validator.py",
    ]
    missing = [path for path in expected if not (ROOT / path).exists()]
    assert not missing, f"Arquivos operacionais ausentes: {missing}"


def test_legacy_root_python_files_are_optional_compatibility_wrappers():
    """Arquivos legados na raiz são opcionais; se existirem, devem ser wrappers."""
    for filename in ["models.py", "validator.py"]:
        path = ROOT / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        assert "Compatibilidade temporária" in content
        assert "generator." in content


def test_framework_version_gap_is_visible_for_v6_migration():
    """Protege o diagnóstico atual: repo ainda está em estrutura V2, não V6 final."""
    assert (ROOT / "framework" / "06_TEMPLATE_NOVO_CASO.md").exists()
    assert not (ROOT / "framework" / "06_DESIGN_VISUAL_DOSSIE.md").exists()
    assert not (ROOT / "framework" / "14_GUIA_RENDERIZACAO_VISUAL.md").exists()
    assert not (ROOT / "framework" / "15_GUIA_EXECUCAO_AGENTE_IA.md").exists()


def test_html_templates_are_self_contained_when_present():
    """Templates ainda podem não existir; quando existirem, não devem depender de scripts remotos."""
    template_dir = ROOT / "templates"
    if not template_dir.exists():
        return

    html_files = list(template_dir.rglob("*.html"))
    for html_file in html_files:
        content = html_file.read_text(encoding="utf-8").lower()
        assert "<script src=" not in content, f"Template com script remoto obrigatório: {html_file}"
        assert "&nbsp;" not in content, f"Template contém entidade proibida &nbsp;: {html_file}"
