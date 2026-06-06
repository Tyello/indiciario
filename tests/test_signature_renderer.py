from generator.signature_renderer import (
    HANDWRITING_MAX_CHARS,
    build_handwritten_note_svg,
    build_signature_svg,
    is_svg_like,
)


def _personagem(pid: str, nome: str, seed: str = "seed") -> dict:
    return {
        "id": pid,
        "nome": nome,
        "assinatura": {
            "estilo": "fluida",
            "pressao": "media",
            "legibilidade": "media",
            "inclinacao": "direita",
            "amplitude": "media",
            "ornamentacao": "sublinhado",
            "variacao": "media",
            "seed": seed,
        },
    }


def test_assinatura_deterministica_para_mesmo_personagem_seed() -> None:
    personagem = _personagem("01", "Iara Nunes", "iara-01")

    assert build_signature_svg(personagem) == build_signature_svg(personagem)


def test_assinatura_muda_entre_personagens() -> None:
    primeira = build_signature_svg(_personagem("01", "Iara Nunes", "iara-01"))
    segunda = build_signature_svg(_personagem("02", "Noemi Prado", "noemi-02"))

    assert primeira != segunda


def test_rubrica_difere_de_assinatura() -> None:
    personagem = _personagem("01", "Iara Nunes", "iara-01")

    assert build_signature_svg(personagem, modo="assinatura") != build_signature_svg(personagem, modo="rubrica")
    assert "signature-assinatura" in build_signature_svg(personagem, modo="assinatura")
    assert "signature-rubrica" in build_signature_svg(personagem, modo="rubrica")


def test_manuscrito_curto_gera_svg_valido_sem_fonte_decorativa() -> None:
    svg = build_handwritten_note_svg("conferir lacre azul", _personagem("01", "Iara Nunes"))

    assert is_svg_like(svg)
    assert "handwritten-note-svg" in svg
    assert "font-family" not in svg
    assert "<text" not in svg


def test_constante_limite_manuscrito() -> None:
    assert HANDWRITING_MAX_CHARS == 120
