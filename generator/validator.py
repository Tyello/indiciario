"""
Validador de blueprint do Indiciário.

Mantém a interface pública descrita em AGENTS.md:
- BlueprintValidator(blueprint, strict=False).validar() -> ResultadoValidacao
- CLI: python -m generator.validator <arquivo.json> [--strict] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

try:  # Execução como pacote: python -m generator.validator
    from .models import (
        Blueprint,
        Envelope,
        Intensidade,
        ModoValidacao,
        PapelPersonagem,
        SaltoFinanceiro,
        TipoDocumento,
    )
except ImportError:  # Execução direta: python generator/validator.py
    from models import (  # type: ignore[no-redef]
        Blueprint,
        Envelope,
        Intensidade,
        ModoValidacao,
        PapelPersonagem,
        SaltoFinanceiro,
        TipoDocumento,
    )


class Severidade(str, Enum):
    CRITICO = "CRÍTICO"
    MODERADO = "MODERADO"
    AVISO = "AVISO"


class NivelRisco(str, Enum):
    BAIXO = "Baixo"
    MEDIO_BAIXO = "Médio-baixo"
    MEDIO = "Médio"
    MEDIO_ALTO = "Médio-alto"
    ALTO = "Alto"


@dataclass
class Erro:
    codigo: str
    severidade: Severidade
    mensagem: str
    detalhe: Optional[str] = None
    documento: Optional[str] = None


@dataclass
class ResultadoValidacao:
    erros: list[Erro] = field(default_factory=list)
    avisos: list[Erro] = field(default_factory=list)
    nivel_risco: NivelRisco = NivelRisco.BAIXO
    pode_gerar: bool = True
    resumo: str = ""

    @property
    def criticos(self) -> list[Erro]:
        return [e for e in self.erros if e.severidade == Severidade.CRITICO]

    @property
    def moderados(self) -> list[Erro]:
        return [e for e in self.erros if e.severidade == Severidade.MODERADO]

    def adicionar(self, erro: Erro) -> None:
        if erro.severidade == Severidade.AVISO:
            self.avisos.append(erro)
        else:
            self.erros.append(erro)


class BlueprintValidator:
    """Executa validações narrativas, estruturais e offline sobre um blueprint."""

    def __init__(self, blueprint: Blueprint, strict: bool = False):
        self.bp = blueprint
        self.strict = strict
        self.resultado = ResultadoValidacao()
        self._ids_personagens: set[str] = {p.id for p in blueprint.personagens}
        self._codigos_docs: set[str] = {d.codigo for d in blueprint.documentos}

    def validar(self) -> ResultadoValidacao:
        self._verificar_elenco()
        self._verificar_documentos()
        self._verificar_pilares()
        self._verificar_pistas()
        self._verificar_red_herrings()
        self._verificar_codigos()
        self._verificar_cadeia_financeira()
        self._verificar_linha_do_tempo()
        self._verificar_dicas()
        self._verificar_autossuficiencia()
        self._calcular_risco()
        self._gerar_resumo()
        return self.resultado

    def _verificar_elenco(self) -> None:
        papeis = {p.papel for p in self.bp.personagens}
        for papel in [
            PapelPersonagem.EXECUTOR,
            PapelPersonagem.PLANEJADOR,
            PapelPersonagem.BENEFICIARIO,
        ]:
            if papel not in papeis:
                self.resultado.adicionar(Erro(
                    codigo="ELENCO_001",
                    severidade=Severidade.CRITICO,
                    mensagem=f"Papel obrigatório ausente no elenco: {papel.value}",
                    detalhe="Todo caso precisa diferenciar executor, planejador e beneficiário.",
                ))

        for campo, valor_id in [
            ("executor_id", self.bp.executor_id),
            ("planejador_id", self.bp.planejador_id),
            ("beneficiario_id", self.bp.beneficiario_id),
        ]:
            if valor_id not in self._ids_personagens:
                self.resultado.adicionar(Erro(
                    codigo="ELENCO_002",
                    severidade=Severidade.CRITICO,
                    mensagem=f"ID '{valor_id}' em '{campo}' não existe no elenco.",
                ))

        if PapelPersonagem.NARRADOR not in papeis:
            self.resultado.adicionar(Erro(
                codigo="ELENCO_003",
                severidade=Severidade.MODERADO,
                mensagem="Nenhum personagem com papel 'narrador' definido.",
                detalhe="O primeiro e-mail deve vir de personagem com interesse próprio.",
            ))

        red_herrings = [p for p in self.bp.personagens if p.papel == PapelPersonagem.RED_HERRING]
        if len(red_herrings) < 2:
            self.resultado.adicionar(Erro(
                codigo="ELENCO_004",
                severidade=Severidade.MODERADO,
                mensagem=f"Apenas {len(red_herrings)} red herring(s). Mínimo recomendado: 2.",
            ))

        for personagem in self.bp.personagens:
            if not personagem.documento_ancoragem:
                self.resultado.adicionar(Erro(
                    codigo="ELENCO_005",
                    severidade=Severidade.MODERADO,
                    mensagem=f"Personagem '{personagem.nome}' sem documento de ancoragem.",
                ))
            for codigo in personagem.documento_ancoragem:
                if codigo not in self._codigos_docs:
                    self.resultado.adicionar(Erro(
                        codigo="ELENCO_006",
                        severidade=Severidade.CRITICO,
                        mensagem=f"Documento de ancoragem '{codigo}' não existe.",
                    ))

    def _verificar_documentos(self) -> None:
        docs_e1 = [d for d in self.bp.documentos if d.envelope == Envelope.E1]
        docs_e2 = [d for d in self.bp.documentos if d.envelope == Envelope.E2]
        if len(docs_e1) < 6:
            self.resultado.adicionar(Erro(
                "DOC_001", Severidade.MODERADO, f"Envelope 1 tem apenas {len(docs_e1)} documentos."
            ))
        if len(docs_e2) < 6:
            self.resultado.adicionar(Erro(
                "DOC_002", Severidade.MODERADO, f"Envelope 2 tem apenas {len(docs_e2)} documentos."
            ))

        tipos_e1 = {d.tipo for d in docs_e1}
        if TipoDocumento.PROTO not in tipos_e1:
            self.resultado.adicionar(Erro(
                "DOC_003", Severidade.CRITICO, "Envelope 1 não tem protocolo de investigação."
            ))
        if TipoDocumento.CRUZ not in tipos_e1:
            self.resultado.adicionar(Erro(
                "DOC_004", Severidade.MODERADO, "Folha de cruzamento ausente no Envelope 1."
            ))

        for doc in self.bp.documentos:
            for id_citado in doc.ids_citados:
                if not self._id_tem_correspondencia(id_citado):
                    self.resultado.adicionar(Erro(
                        "DOC_005",
                        Severidade.CRITICO,
                        f"ID '{id_citado}' citado em '{doc.codigo}' não existe na matriz.",
                        documento=doc.codigo,
                    ))
            for ref in doc.confirma + doc.confirmado_por:
                if ref not in self._codigos_docs:
                    self.resultado.adicionar(Erro(
                        "DOC_007",
                        Severidade.MODERADO,
                        f"Documento '{doc.codigo}' referencia '{ref}' que não existe.",
                        documento=doc.codigo,
                    ))

    def _id_tem_correspondencia(self, id_citado: str) -> bool:
        if id_citado in self._ids_personagens:
            return True
        return id_citado.isdigit() and len(id_citado) >= 5

    def _verificar_pilares(self) -> None:
        if len(self.bp.pilares_validacao) != 4:
            self.resultado.adicionar(Erro(
                "PILAR_001",
                Severidade.CRITICO,
                f"O Envelope 1 deve ter exatamente 4 pilares; encontrado: {len(self.bp.pilares_validacao)}.",
            ))
            return

        personagens = {p.personagem_id for p in self.bp.pilares_validacao}
        if len(personagens) > 1:
            self.resultado.adicionar(Erro(
                "PILAR_006",
                Severidade.MODERADO,
                f"Pilares apontam para IDs diferentes: {personagens}.",
            ))

        for pilar in self.bp.pilares_validacao:
            if pilar.documento_principal not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PILAR_002", Severidade.CRITICO, f"Documento principal inexistente: {pilar.documento_principal}."
                ))
            if pilar.confirmacao not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PILAR_003", Severidade.CRITICO, f"Confirmação inexistente: {pilar.confirmacao}."
                ))
            elif pilar.confirmacao == pilar.documento_principal:
                self.resultado.adicionar(Erro(
                    "PILAR_004", Severidade.CRITICO, "Pilar usa o mesmo documento como prova e confirmação."
                ))
            if pilar.personagem_id not in self._ids_personagens:
                self.resultado.adicionar(Erro(
                    "PILAR_005", Severidade.CRITICO, f"Personagem do pilar não existe: {pilar.personagem_id}."
                ))

    def _verificar_pistas(self) -> None:
        for pista in self.bp.matriz_pistas:
            if pista.documento not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PISTA_002", Severidade.CRITICO, f"Pista referencia documento inexistente: {pista.documento}."
                ))
            if pista.confirmacao not in self._codigos_docs:
                self.resultado.adicionar(Erro(
                    "PISTA_003", Severidade.CRITICO, f"Pista sem confirmação existente: {pista.confirmacao}."
                ))
            elif pista.confirmacao == pista.documento:
                self.resultado.adicionar(Erro(
                    "PISTA_004", Severidade.CRITICO, "Pista usa o mesmo documento como prova e confirmação."
                ))

    def _verificar_red_herrings(self) -> None:
        culpados = {self.bp.executor_id, self.bp.planejador_id, self.bp.beneficiario_id}
        for rh in self.bp.red_herrings:
            if rh.personagem_id not in self._ids_personagens:
                self.resultado.adicionar(Erro("RH_001", Severidade.CRITICO, "Red herring aponta para personagem inexistente."))
            if rh.documento_descarte not in self._codigos_docs:
                self.resultado.adicionar(Erro("RH_002", Severidade.CRITICO, "Red herring sem documento de descarte existente."))
            if rh.personagem_id in culpados:
                self.resultado.adicionar(Erro("RH_003", Severidade.CRITICO, "Culpado também foi marcado como red herring."))

    def _verificar_codigos(self) -> None:
        for codigo in self.bp.codigos:
            if codigo.documento not in self._codigos_docs:
                self.resultado.adicionar(Erro("COD_001", Severidade.CRITICO, f"Código em documento inexistente: {codigo.documento}."))
            if codigo.chave_em not in self._codigos_docs:
                self.resultado.adicionar(Erro("COD_002", Severidade.CRITICO, f"Chave de código inexistente: {codigo.chave_em}."))
            if codigo.criterio == "ids_personagens":
                for elemento in codigo.elementos:
                    if elemento not in self._ids_personagens:
                        self.resultado.adicionar(Erro("COD_003", Severidade.CRITICO, f"Elemento de código sem personagem: {elemento}."))
            if codigo.criterio == "misto":
                self.resultado.adicionar(Erro("COD_004", Severidade.MODERADO, "Código com critério misto exige pista documental clara."))

    def _verificar_cadeia_financeira(self) -> None:
        if not self.bp.cadeia_financeira:
            if "fraude" in self.bp.genero.lower() or "roubo" in self.bp.genero.lower():
                self.resultado.adicionar(Erro("FIN_001", Severidade.AVISO, "Caso de fraude/roubo sem cadeia financeira/logística."))
            return

        finais: list[SaltoFinanceiro] = [s for s in self.bp.cadeia_financeira if s.is_salto_final]
        if len(finais) != 1:
            self.resultado.adicionar(Erro("FIN_002", Severidade.CRITICO, "Cadeia deve ter exatamente um salto final marcado."))

        for salto in self.bp.cadeia_financeira:
            if salto.documento_prova not in self._codigos_docs:
                self.resultado.adicionar(Erro("FIN_004", Severidade.CRITICO, f"Salto sem documento existente: {salto.documento_prova}."))
            if salto.is_salto_final:
                if not salto.confirmacao_independente:
                    self.resultado.adicionar(Erro("FIN_005", Severidade.CRITICO, "Salto final sem confirmação independente."))
                elif salto.confirmacao_independente not in self._codigos_docs:
                    self.resultado.adicionar(Erro("FIN_006", Severidade.CRITICO, "Confirmação do salto final não existe."))
                elif salto.confirmacao_independente == salto.documento_prova:
                    self.resultado.adicionar(Erro("FIN_007", Severidade.CRITICO, "Salto final usa o mesmo documento como prova e confirmação."))

    def _verificar_linha_do_tempo(self) -> None:
        if not self.bp.intervalo_critico_inicio or not self.bp.intervalo_critico_fim:
            self.resultado.adicionar(Erro("LT_001", Severidade.CRITICO, "Intervalo crítico não definido."))
        for evento in self.bp.linha_tempo_real:
            if evento.documento_prova not in self._codigos_docs:
                self.resultado.adicionar(Erro("LT_002", Severidade.MODERADO, f"Evento referencia documento inexistente: {evento.documento_prova}."))
            if evento.confirmacao_independente and evento.confirmacao_independente not in self._codigos_docs:
                self.resultado.adicionar(Erro("LT_003", Severidade.MODERADO, f"Evento referencia confirmação inexistente: {evento.confirmacao_independente}."))

    def _verificar_dicas(self) -> None:
        if not any(d.intensidade == Intensidade.QUASE_GABARITO for d in self.bp.dicas):
            self.resultado.adicionar(Erro("DICA_001", Severidade.MODERADO, "Nenhuma dica de quase-gabarito definida."))
        dicas_e2 = [d for d in self.bp.dicas if d.envelope == Envelope.E2]
        if len(dicas_e2) < 2:
            self.resultado.adicionar(Erro("DICA_002", Severidade.MODERADO, "Envelope 2 tem menos de 2 dicas."))
        nomes = {p.nome.lower() for p in self.bp.personagens}
        for dica in self.bp.dicas:
            if dica.intensidade in [Intensidade.LEVE, Intensidade.MEDIA]:
                if any(nome in dica.texto.lower() for nome in nomes):
                    self.resultado.adicionar(Erro("DICA_003", Severidade.AVISO, f"Dica {dica.numero} pode revelar nome diretamente."))

    def _verificar_autossuficiencia(self) -> None:
        tem_log = any(d.tipo in [TipoDocumento.LOG_ACESSO, TipoDocumento.LOG_SISTEMA] for d in self.bp.documentos)
        tem_glossario = any(d.tipo == TipoDocumento.GLOSS for d in self.bp.documentos)
        if tem_log and not tem_glossario:
            self.resultado.adicionar(Erro("AUTO_001", Severidade.AVISO, "Caso tem logs técnicos mas nenhum glossário."))
        if self.bp.modo_validacao == ModoValidacao.OFFLINE_PURO:
            for doc in self.bp.documentos:
                texto = f"{doc.titulo} {doc.objetivo_narrativo}".lower()
                if "qr" in texto or "link" in texto or "url" in texto:
                    self.resultado.adicionar(Erro(
                        "AUTO_002",
                        Severidade.MODERADO,
                        f"Documento '{doc.codigo}' menciona QR/link/url em modo offline puro.",
                        documento=doc.codigo,
                    ))

    def _calcular_risco(self) -> None:
        criticos = len(self.resultado.criticos)
        moderados = len(self.resultado.moderados)
        if criticos > 0:
            self.resultado.nivel_risco = NivelRisco.ALTO
            self.resultado.pode_gerar = False
        elif moderados >= 4:
            self.resultado.nivel_risco = NivelRisco.MEDIO_ALTO
            self.resultado.pode_gerar = False
        elif moderados >= 2:
            self.resultado.nivel_risco = NivelRisco.MEDIO
            self.resultado.pode_gerar = not self.strict
        elif moderados == 1:
            self.resultado.nivel_risco = NivelRisco.MEDIO_BAIXO
            self.resultado.pode_gerar = True
        else:
            self.resultado.nivel_risco = NivelRisco.BAIXO
            self.resultado.pode_gerar = True

    def _gerar_resumo(self) -> None:
        linhas = [
            "=" * 60,
            f"VALIDAÇÃO DE BLUEPRINT — {self.bp.titulo}",
            "=" * 60,
            f"Risco: {self.resultado.nivel_risco.value}",
            f"Pode gerar: {'SIM' if self.resultado.pode_gerar else 'NÃO'}",
            f"Críticos: {len(self.resultado.criticos)}",
            f"Moderados: {len(self.resultado.moderados)}",
            f"Avisos: {len(self.resultado.avisos)}",
        ]
        for grupo, itens in [
            ("CRÍTICOS", self.resultado.criticos),
            ("MODERADOS", self.resultado.moderados),
            ("AVISOS", self.resultado.avisos),
        ]:
            if itens:
                linhas.append(f"\n{grupo}")
                for item in itens:
                    linhas.append(f"[{item.codigo}] {item.mensagem}")
                    if item.detalhe:
                        linhas.append(f"  - {item.detalhe}")
        self.resultado.resumo = "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida um blueprint de caso antes de gerar documentos.")
    parser.add_argument("arquivo", help="Caminho para o blueprint em JSON")
    parser.add_argument("--strict", action="store_true", help="Falha também em risco Médio")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    path = Path(args.arquivo)
    if not path.exists():
        print(f"Arquivo não encontrado: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        blueprint = Blueprint(**json.loads(path.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001 - CLI deve exibir erro de parse claro.
        print(f"Erro ao parsear blueprint: {exc}", file=sys.stderr)
        sys.exit(2)

    resultado = BlueprintValidator(blueprint, strict=args.strict).validar()
    if args.json:
        print(json.dumps({
            "nivel_risco": resultado.nivel_risco.value,
            "pode_gerar": resultado.pode_gerar,
            "criticos": [e.__dict__ for e in resultado.criticos],
            "moderados": [e.__dict__ for e in resultado.moderados],
            "avisos": [e.__dict__ for e in resultado.avisos],
        }, ensure_ascii=False, indent=2, default=str))
    else:
        print(resultado.resumo)

    sys.exit(0 if resultado.pode_gerar else 1)


if __name__ == "__main__":
    main()
