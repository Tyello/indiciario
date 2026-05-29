"""
tests/test_conteudo.py — Testes de validação do campo conteudo

Execute: pytest tests/test_conteudo.py -v
"""

from generator.models import Blueprint
from generator.validator import BlueprintValidator

# ─── Fixture base ─────────────────────────────────────────────────────────────


def blueprint_minimo(documentos: list[dict]) -> Blueprint:
    """Retorna um blueprint válido mínimo com os documentos fornecidos."""
    base = {
        "titulo": "Teste",
        "subtitulo": "Sub",
        "genero": "teste",
        "tom": "policial",
        "modo_validacao": "offline_puro",
        "dificuldade": "medio",
        "tempo_estimado_min": 60,
        "numero_jogadores": "4",
        "formato_envelopes": 2,
        "premissa": "Premissa de teste.",
        "verdade_real": "Verdade interna.",
        "executor_id": "09",
        "planejador_id": "09",
        "beneficiario_id": "09",
        "motivacao": "Motivo.",
        "metodo_ocultacao": "Método.",
        "erro_que_permite_descobrir": "Erro.",
        "cadeia_causal": ["1", "2", "3"],
        "personagens": [
            {
                "id": "09",
                "nome": "A",
                "funcao": "f",
                "papel": "executor",
                "suspeita_aparente": "s",
                "verdade": "v",
                "documento_ancoragem": [],
            },
            {
                "id": "14",
                "nome": "B",
                "funcao": "f",
                "papel": "red_herring",
                "suspeita_aparente": "s",
                "verdade": "v",
                "documento_ancoragem": [],
            },
            {
                "id": "22",
                "nome": "C",
                "funcao": "f",
                "papel": "narrador",
                "suspeita_aparente": "s",
                "verdade": "v",
                "documento_ancoragem": [],
            },
            {
                "id": "31",
                "nome": "D",
                "funcao": "f",
                "papel": "testemunha",
                "suspeita_aparente": "s",
                "verdade": "v",
                "documento_ancoragem": [],
            },
        ],
        "linha_tempo_real": [
            {
                "data_hora": "10h",
                "evento": "e1",
                "documento_prova": documentos[0]["codigo"],
            },
            {
                "data_hora": "11h",
                "evento": "e2",
                "documento_prova": documentos[0]["codigo"],
            },
            {
                "data_hora": "12h",
                "evento": "e3",
                "documento_prova": documentos[0]["codigo"],
            },
        ],
        "pilares_validacao": [
            {
                "nome": "p1",
                "documento_principal": documentos[0]["codigo"],
                "confirmacao": (
                    documentos[1]["codigo"]
                    if len(documentos) > 1
                    else documentos[0]["codigo"]
                ),
                "personagem_id": "09",
            },
            {
                "nome": "p2",
                "documento_principal": documentos[0]["codigo"],
                "confirmacao": documentos[0]["codigo"],
                "personagem_id": "09",
            },
            {
                "nome": "p3",
                "documento_principal": documentos[0]["codigo"],
                "confirmacao": documentos[0]["codigo"],
                "personagem_id": "09",
            },
            {
                "nome": "p4",
                "documento_principal": documentos[0]["codigo"],
                "confirmacao": documentos[0]["codigo"],
                "personagem_id": "09",
            },
        ],
        "intervalo_critico_inicio": "10h",
        "intervalo_critico_fim": "12h",
        "documentos": documentos,
        "matriz_pistas": [
            {
                "descricao": "p",
                "documento": documentos[0]["codigo"],
                "o_que_sugere": "s",
                "o_que_prova": "p",
                "confirmacao": documentos[0]["codigo"],
                "risco_ambiguidade": "baixo",
                "emocao_esperada": "surpresa",
            },
            {
                "descricao": "p2",
                "documento": documentos[0]["codigo"],
                "o_que_sugere": "s",
                "o_que_prova": "p",
                "confirmacao": documentos[0]["codigo"],
                "risco_ambiguidade": "baixo",
                "emocao_esperada": "surpresa",
            },
            {
                "descricao": "p3",
                "documento": documentos[0]["codigo"],
                "o_que_sugere": "s",
                "o_que_prova": "p",
                "confirmacao": documentos[0]["codigo"],
                "risco_ambiguidade": "baixo",
                "emocao_esperada": "surpresa",
            },
        ],
        "red_herrings": [
            {
                "personagem_id": "14",
                "motivo_aparente": "m",
                "como_descartar": "c",
                "documento_descarte": documentos[0]["codigo"],
                "categoria": "motivo_sem_oportunidade",
            },
            {
                "personagem_id": "31",
                "motivo_aparente": "m",
                "como_descartar": "c",
                "documento_descarte": documentos[0]["codigo"],
                "categoria": "motivo_sem_oportunidade",
            },
        ],
        "dicas": [
            {
                "numero": i,
                "intensidade": "leve",
                "envelope": "E1",
                "condicao_uso": "c",
                "texto": "t",
                "o_que_desbloqueia": "d",
            }
            for i in range(1, 8)
        ],
        "versao": "0.1",
    }
    return Blueprint(**base)


def doc_base(codigo="E1-01", tipo="email_narrador", conteudo=None):
    return {
        "codigo": codigo,
        "titulo": "Doc teste",
        "envelope": "E1",
        "tipo": tipo,
        "emocao_esperada": "urgencia",
        "objetivo_narrativo": "teste",
        "conteudo": conteudo or {},
    }


CONTEUDO_EMAIL_VALIDO = {
    "REMETENTE_NOME": "João Silva",
    "REMETENTE_EMAIL": "joao@ficticio.com",
    "DESTINATARIO_EMAIL": "detetive@indiciarios.com",
    "DESTINATARIO_LABEL": "Investigação",
    "DATA_HORA": "01 de março de 2026 às 17:05",
    "ASSUNTO": "Urgente",
    "AVATAR_INICIAL": "J",
    "AVATAR_COR": "#1A2E4A",
    "CORPO_EMAIL": "<p>Texto do e-mail.</p>",
    "NOTA_RODAPE": "CONFIDENCIAL",
}

CONTEUDO_BOLETIM_VALIDO = {
    "ORGAO_NOME": "POLÍCIA CIVIL",
    "ORGAO_SUBTITULO": "Delegacia 5ª",
    "NUMERO_CASO": "001",
    "TIPO_DOCUMENTO": "BOLETIM DE INSPEÇÃO INICIAL",
    "TIPO_OCORRENCIA": "Furto",
    "DATA": "01/03/2026",
    "LOCALIZACAO": "SP",
    "HORA_OCORRENCIA": "16h40",
    "DESCRICAO_OCORRENCIA": "<p>Descrição.</p>",
    "NOME_RESPONSAVEL": "Dr. Silva",
    "ASSINATURA_RESPONSAVEL": "Dr. Silva",
    "ASSINATURA_GLIFO": "DS",
    "DATA_HORA_ASSINATURA": "01/03/2026 18h00",
}

CONTEUDO_LOG_VALIDO = {
    "NOME_SISTEMA": "CONTROLE DE ACESSOS",
    "SUBTITULO_SISTEMA": "Exportação auditada",
    "COR_SISTEMA": "#1A2E4A",
    "COR_SISTEMA_DARK": "#0d1a2e",
    "DATA_EXPORTACAO": "01/03/2026",
    "HORA_EXPORTACAO": "17:04",
    "OPERADOR_EXPORT": "SISTEMA",
    "HASH_REGISTRO": "a3f9c1",
    "PERIODO_INICIO": "01/03/2026 09:50",
    "PERIODO_FIM": "01/03/2026 17:04",
    "LOCALIZACAO_SISTEMA": "Sala N3",
    "TOTAL_REGISTROS": "2",
    "COLUNA_NOME": True,
    "COLUNA_TERMINAL": False,
    "COLUNA_METODO": False,
    "COLUNA_OBS": False,
    "TOTAL_USUARIOS": "2",
    "TOTAL_ENTRADAS": "2",
    "TOTAL_NEGADOS": "0",
    "TOTAL_ANOMALIAS": "0",
    "REGISTROS": [
        {
            "CLASSE_LINHA": "",
            "DATA": "01/03/2026",
            "HORA": "09:58:02",
            "PORTA": "1A",
            "ID_USUARIO": "09",
            "NOME_USUARIO": "João",
            "TIPO_EVENTO": "in",
            "EVENTO": "ENTRADA",
        },
    ],
}


# ─── Testes ───────────────────────────────────────────────────────────────────


class TestConteudoAusente:
    def test_conteudo_vazio_gera_critico(self):
        docs = [
            doc_base("E1-01", "email_narrador", {}),
            doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        codigos = [e.codigo for e in r.criticos]
        assert "CONT_001" in codigos

    def test_conteudo_ausente_gera_critico(self):
        doc = doc_base("E1-01", "email_narrador")
        doc.pop("conteudo", None)
        # Pydantic usa default_factory=dict, então conteudo={} — mesmo caso
        docs = [doc, doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO)]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        codigos = [e.codigo for e in r.criticos]
        assert "CONT_001" in codigos


class TestChavesObrigatorias:
    def test_email_completo_sem_erro_cont(self):
        docs = [
            doc_base("E1-01", "email_narrador", CONTEUDO_EMAIL_VALIDO),
            doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        cont_erros = [e for e in r.criticos if e.codigo.startswith("CONT_")]
        assert cont_erros == []

    def test_email_faltando_assunto(self):
        conteudo = {k: v for k, v in CONTEUDO_EMAIL_VALIDO.items() if k != "ASSUNTO"}
        docs = [
            doc_base("E1-01", "email_narrador", conteudo),
            doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        assert any(
            e.codigo == "CONT_003" and "E1-01" in (e.documento or "")
            for e in r.criticos
        )

    def test_boletim_completo_sem_erro_cont(self):
        docs = [
            doc_base("E1-01", "boletim", CONTEUDO_BOLETIM_VALIDO),
            doc_base("E1-02", "boletim", CONTEUDO_BOLETIM_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        cont_erros = [e for e in r.criticos if e.codigo.startswith("CONT_")]
        assert cont_erros == []

    def test_log_completo_sem_erro_cont(self):
        docs = [
            doc_base("E1-01", "log_acesso", CONTEUDO_LOG_VALIDO),
            doc_base("E1-02", "log_acesso", CONTEUDO_LOG_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        cont_erros = [e for e in r.criticos if e.codigo.startswith("CONT_")]
        assert cont_erros == []


class TestListasObrigatorias:
    def test_registros_vazio_gera_critico(self):
        conteudo = {**CONTEUDO_LOG_VALIDO, "REGISTROS": []}
        docs = [
            doc_base("E1-01", "log_acesso", conteudo),
            doc_base("E1-02", "log_acesso", CONTEUDO_LOG_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        assert any(e.codigo == "CONT_004" for e in r.criticos)

    def test_mensagens_vazio_gera_critico(self):
        conteudo = {
            "HORA_TELA": "16:57",
            "CONTADOR_NAOVISTOS": "5",
            "NOME_GRUPO": "Grupo",
            "MEMBROS_LISTA": "A, B",
            "DATA_CONVERSA": "01 mar",
            "MENSAGENS": [],
        }
        docs = [
            doc_base("E1-01", "chat", conteudo),
            doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        assert any(e.codigo == "CONT_004" for e in r.criticos)


class TestCorpoHTML:
    def test_corpo_sem_tag_p_gera_aviso(self):
        conteudo = {**CONTEUDO_EMAIL_VALIDO, "CORPO_EMAIL": "Texto simples sem p."}
        docs = [
            doc_base("E1-01", "email_narrador", conteudo),
            doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        assert any(e.codigo == "CONT_005" for e in r.avisos)

    def test_corpo_com_tag_p_sem_aviso(self):
        docs = [
            doc_base("E1-01", "email_narrador", CONTEUDO_EMAIL_VALIDO),
            doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        assert not any(e.codigo == "CONT_005" for e in r.avisos)


class TestTipoSemSchema:
    def test_tipo_outro_gera_aviso_nao_critico(self):
        conteudo = {"QUALQUER_CHAVE": "valor"}
        docs = [
            doc_base("E1-01", "outro", conteudo),
            doc_base("E1-02", "email_narrador", CONTEUDO_EMAIL_VALIDO),
        ]
        bp = blueprint_minimo(docs)
        r = BlueprintValidator(bp).validar()
        assert any(e.codigo == "CONT_002" for e in r.avisos)
        assert not any(e.codigo == "CONT_002" for e in r.criticos)
