import json
from pathlib import Path

from generator import package_builder, renderer

BLUEPRINT_PATH = Path("examples/caso_canonico_iniciante.json")


def _blueprint() -> dict:
    return json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8"))


def _doc(codigo: str) -> dict:
    return next(doc for doc in _blueprint()["documentos"] if doc["codigo"] == codigo)


def test_assinaturas_visuais_tem_perfis_e_tracados_distintos() -> None:
    blueprint = _blueprint()
    dados = renderer.preparar_assinaturas_visuais(
        {
            "ASSINATURA_CURSIVA": "Inês Laranjeira",
            "ASSINATURA_GLIFO": "Vera Matos",
            "ASSINATURA_RESPONSAVEL": "Otávio Salles",
            "ASSINATURA_CONTRATANTE": "Marina Vale",
        },
        personagens=blueprint["personagens"],
    )

    assert "signature-perfil signature-assinatura estilo-formal" in dados["ASSINATURA_CURSIVA_VISUAL"]
    assert "signature-perfil signature-rubrica estilo-administrativa" in dados["ASSINATURA_GLIFO_VISUAL"]
    assert "signature-perfil signature-assinatura estilo-administrativa" in dados["ASSINATURA_RESPONSAVEL_VISUAL"]
    assert "signature-perfil signature-assinatura estilo-curta" in dados["ASSINATURA_CONTRATANTE_VISUAL"]
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


def test_assinatura_completa_e_rubrica_do_mesmo_personagem_sao_diferentes() -> None:
    blueprint = _blueprint()
    dados = renderer.preparar_assinaturas_visuais(
        {
            "ASSINATURA_RESPONSAVEL": "Vera Matos",
            "ASSINATURA_GLIFO": "Vera Matos",
        },
        personagens=blueprint["personagens"],
    )

    assert dados["ASSINATURA_RESPONSAVEL_VISUAL"] != dados["ASSINATURA_GLIFO_VISUAL"]
    assert "signature-assinatura" in dados["ASSINATURA_RESPONSAVEL_VISUAL"]
    assert "signature-rubrica" in dados["ASSINATURA_GLIFO_VISUAL"]


def test_override_svg_tem_prioridade_sobre_geracao_por_perfil(tmp_path: Path) -> None:
    asset = tmp_path / "manual.svg"
    conteudo_svg = '<svg xmlns="http://www.w3.org/2000/svg"><text>manual</text></svg>'
    asset.write_text(conteudo_svg, encoding="utf-8")
    personagens = [
        {
            "id": "P1",
            "nome": "Iara Nunes",
            "assinatura": {
                "estilo": "formal",
                "override_assinatura_svg": "manual.svg",
            },
        }
    ]

    dados = renderer.preparar_assinaturas_visuais(
        {
            "ASSINATURA_RESPONSAVEL": "qualquer texto",
            "ASSINATURA_RESPONSAVEL_PERSONAGEM_ID": "P1",
        },
        personagens=personagens,
        repo_root=tmp_path,
    )

    assert dados["ASSINATURA_RESPONSAVEL_VISUAL"] == conteudo_svg


def test_fallback_sem_perfil_continua_funcionando() -> None:
    dados = renderer.preparar_assinaturas_visuais({"ASSINATURA_RESPONSAVEL": "Nome Fictício"})

    assert "signature-svg signature-assinatura_comercial" in dados["ASSINATURA_RESPONSAVEL_VISUAL"]


def test_e1_documentos_usam_padrao_global_de_codigos() -> None:
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
        "SETOR-03",
        "SETOR-08",
    ]
    proibidos = ("Vitrine", "Guarita", "Administração", "Controle de fichas")
    assert not any(
        termo in registro["PORTA"]
        for registro in e105["REGISTROS"]
        for termo in proibidos
    )

    corpo_e106 = _doc("E1-06")["conteudo"]["CORPO_CARTA"]
    for codigo in [
        "BANC-REG-01",
        "ETQ-RM-17",
        "ETQ-PC-14",
        "OS-0147/2026",
        "TERM-ADM-03",
    ]:
        assert codigo in corpo_e106
    assert "SETOR-03</td>" not in corpo_e106
    assert "As divergências foram lacradas" not in corpo_e106
    assert "Divergências registradas para nova vistoria técnica." in corpo_e106


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


def test_e203_foi_removido_do_pacote_de_jogador() -> None:
    blueprint = _blueprint()
    codigos = {doc["codigo"] for doc in blueprint["documentos"]}

    assert "E2-03" not in codigos


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
    grupo_compras = next(doc for doc in chats if doc["codigo"] == "E2-08")
    assert (
        grupo_compras["conteudo"]["NOME_GRUPO"] == "Compras CAM — alinhamento interno"
    )
    assert "Conserva Sul" not in grupo_compras["conteudo"]["MEMBROS_LISTA"]
    assert {
        mensagem.get("NOME_REMETENTE")
        for mensagem in grupo_compras["conteudo"]["MENSAGENS"]
        if mensagem.get("NOME_REMETENTE")
    } <= {"Paula Monteiro", "Renato Azevedo", "Camila Rocha", "Nara Vidal"}

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
