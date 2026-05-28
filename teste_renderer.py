# teste_render.py — rode na raiz do projeto
from pathlib import Path
from generator.renderer import renderizar_documento

renderizar_documento(
    template_nome="04_boletim.html",
    dados={
        "ORGAO_NOME": "Polícia Civil do Estado",
        "ORGAO_SUBTITULO": "Delegacia de Crimes Patrimoniais",
        "NUMERO_CASO": "402FH",
        "TIPO_DOCUMENTO": "BOLETIM DE INSPEÇÃO INICIAL",
        "TIPO_OCORRENCIA": "Furto qualificado",
        "DATA": "01/03/2026",
        "LOCALIZACAO": "São Paulo — SP",
        "HORA_OCORRENCIA": "16h40",
        "DESCRICAO_OCORRENCIA": "Foi registrada a subtração de obra de arte avaliada em R$ 3 milhões...",
        "NOME_RESPONSAVEL": "Bruno Rodrigues Souto",
        "ASSINATURA_RESPONSAVEL": "Bruno R. Souto",
        "ASSINATURA_GLIFO": "BRS",
        "DATA_HORA_ASSINATURA": "01/03/2026 18h24",
        "MOSTRAR_CARIMBO": True,
        "TEXTO_CARIMBO": "PRELIMINAR",
    },
    output_path=Path("output/teste_boletim.pdf"),
)
print("PDF gerado em output/teste_boletim.pdf")