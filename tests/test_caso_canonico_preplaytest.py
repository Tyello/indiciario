import json
from pathlib import Path

from generator import package_builder, renderer

BLUEPRINT_PATH = Path("examples/caso_canonico_intermediario.json")


def _blueprint() -> dict:
    return json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))


def _doc(codigo: str) -> dict:
    return next(doc for doc in _blueprint()["documentos"] if doc["codigo"] == codigo)


def test_assinaturas_visuais_tem_perfis_e_tracados_distintos() -> None:
    dados = renderer.preparar_assinaturas_visuais(
        {
            "ASSINATURA_CURSIVA": "Inês Laranjeira",
            "ASSINATURA_GLIFO": "Vera Matos",
            "ASSINATURA_RESPONSAVEL": "Otávio Salles",
            "ASSINATURA_CONTRATANTE": "Marina Vale",
        }
    )

    assert "signature-assinatura_formal" in dados["ASSINATURA_CURSIVA_VISUAL"]
    assert "signature-rubrica_curta" in dados["ASSINATURA_GLIFO_VISUAL"]
    assert "signature-assinatura_comercial" in dados["ASSINATURA_RESPONSAVEL_VISUAL"]
    assert (
        "signature-assinatura_administrativa" in dados["ASSINATURA_CONTRATANTE_VISUAL"]
    )
    assert (
        len(
            {
                dados["ASSINATURA_CURSIVA_VISUAL"],
                dados["ASSINATURA_GLIFO_VISUAL"],
                dados["ASSINATURA_RESPONSAVEL_VISUAL"],
                dados["ASSINATURA_CONTRATANTE_VISUAL"],
            }
        )
        == 4
    )


def test_e1_logs_usam_codigos_puros_nos_campos_operacionais() -> None:
    e104 = _doc("E1-04")["conteudo"]
    assert {registro["PORTA"] for registro in e104["REGISTROS"]} <= {
        "P-01",
        "P-02",
        "P-03",
        "P-04",
        "P-05",
        "P-06",
    }
    assert all("/" not in registro["PORTA"] for registro in e104["REGISTROS"])

    e105 = _doc("E1-05")["conteudo"]
    assert [registro["PORTA"] for registro in e105["REGISTROS"]] == [
        "SETOR-08",
        "SETOR-08",
        "SETOR-01",
        "SETOR-03",
        "TERM-ADM-03",
        "SETOR-08",
    ]
    proibidos = ("Vitrine", "Guarita", "Administração", "Controle de fichas")
    assert not any(
        termo in registro["PORTA"]
        for registro in e105["REGISTROS"]
        for termo in proibidos
    )

    corpo_e106 = _doc("E1-06")["conteudo"]["CORPO_CARTA"]
    for codigo in ["SETOR-03", "ETQ-RM-17", "ETQ-PC-14", "OS-0147/2026", "TERM-ADM-03"]:
        assert codigo in corpo_e106
    assert "Controle de fichas / bancada" not in corpo_e106
    assert "Reserva Técnica B / conferência" not in corpo_e106


def test_existe_documento_diegético_de_credenciais_para_pessoa_e_funcao() -> None:
    doc = _doc("E1-09")
    corpo = doc["conteudo"]["CORPO_CARTA"]

    assert doc["titulo"] == "Relação de credenciais funcionais"
    for esperado in [
        "USR-022</td><td>Marina Vale</td><td>Curadoria operacional",
        "USR-066</td><td>Lia Figueira</td><td>Registro de acervo",
        "USR-031</td><td>Tadeu Nobre</td><td>Supervisão noturna",
        "TERM-ADM-03</td><td>Otávio Salles</td><td>Terminal administrativo",
    ]:
        assert esperado in corpo


def test_e203_renderiza_quatro_empresas_com_peso_visual_equivalente() -> None:
    doc = _doc("E2-03")
    html = renderer.renderizar_html(
        Path("templates/08_orcamento.html").read_text(encoding="utf-8"),
        doc["conteudo"],
    )

    assert html.count('class="company-card"') == 4
    for empresa in [
        "Ateliê Pedra Clara",
        "Conserva Sul Restauro",
        "LogisArte Transportes",
        "Mirante Norte Consultoria",
    ]:
        assert empresa in html
    assert "ruído" not in html.lower()
    assert "suspeito" not in html.lower()
    assert "legítimo" not in html.lower()


def test_chats_sao_ambiguos_e_entram_no_envelope_e2_e_manifest(
    monkeypatch, tmp_path
) -> None:
    blueprint_data = _blueprint()
    chats = [
        doc
        for doc in blueprint_data["documentos"]
        if doc["codigo"] in {"E2-06", "E2-08"}
    ]

    assert {doc["codigo"] for doc in chats} == {"E2-06", "E2-08"}
    assert all(doc["envelope"] == "E2" and doc["tipo"] == "chat" for doc in chats)
    texto_chats = " ".join(
        mensagem["TEXTO_MENSAGEM"]
        for doc in chats
        for mensagem in doc["conteudo"]["MENSAGENS"]
    ).lower()
    assert "cruze" not in texto_chats
    assert "cruzamento documental" not in texto_chats
    assert "documento prova" not in texto_chats

    blueprint = package_builder.Blueprint(**blueprint_data)
    rendered_by_code = {
        doc.codigo: tmp_path / f"{doc.codigo}.pdf" for doc in blueprint.documentos
    }
    final_by_envelope = {
        "E1": tmp_path / "01_envelope_E1.pdf",
        "E2": tmp_path / "02_envelope_E2.pdf",
    }
    for path in rendered_by_code.values():
        path.write_text("pdf", encoding="utf-8")
    for path in final_by_envelope.values():
        path.write_text("pdf", encoding="utf-8")
    monkeypatch.setattr(package_builder, "count_pdf_pages", lambda _path: 1)

    manifest_docs = package_builder._build_documents_manifest(
        blueprint,
        rendered_by_code,
        final_by_envelope,
        tmp_path,
    )
    docs_por_codigo = {doc["codigo"]: doc for doc in manifest_docs}
    assert docs_por_codigo["E2-06"]["envelope"] == "E2"
    assert docs_por_codigo["E2-08"]["envelope"] == "E2"
