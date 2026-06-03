"""Renderização procedural controlada de mapas e cartões visuais."""

from __future__ import annotations

import re
from html import escape
from pathlib import Path

from .models import Blueprint, LocalVisual, MapaProcedural, PersonagemVisual
from .renderer import renderizar_documento


def _safe_id(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return slug.strip("_") or "sem_id"


def _safe_color(value: str) -> str:
    text = value.strip()
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", text):
        return text
    return "#4b5563"


def _short_label(value: str, limit: int = 28) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _personagem_nome(personagem: PersonagemVisual, blueprint: Blueprint) -> str:
    for item in blueprint.personagens:
        if item.id == personagem.personagem_id:
            return item.nome
    return personagem.personagem_id




def _build_mirante_floor_plan_svg(mapa: MapaProcedural) -> str:
    """Planta baixa arquitetônica do térreo da Casa de Acervo Mirante.

    Melhorias sobre a versão esquemática:
    - Paredes com hachura diagonal (pattern SVG)
    - Símbolos de porta com arco de abertura
    - Símbolos de janela (linhas paralelas na parede)
    - Câmeras de segurança com campo de visão e estado (ativa/bloqueada)
    - Reserva Técnica B e Doca de Serviço destacadas como áreas críticas
    - Trilha investigativa RM-17 indicada
    - Bloco de título arquitetônico no rodapé
    - Norte, escala gráfica e legenda cromática
    """
    del mapa  # planta dedicada ao caso canônico — layout fixo
    return """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 700"
     role="img" aria-label="Planta baixa arquitetônica — Casa de Acervo Mirante">
<desc>Planta baixa do térreo da Casa de Acervo Mirante com paredes hachureadas,
símbolos de porta e janela, câmeras de segurança e destaque das áreas críticas
(Reserva Técnica B e Doca de Serviço). Portas codificadas P-01 a P-09.</desc>

<defs>
  <pattern id="hatch" x="0" y="0" width="8" height="8"
           patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="8" stroke="#9CA3AF" stroke-width="1.5"/>
  </pattern>
  <pattern id="hatch-light" x="0" y="0" width="6" height="6"
           patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="#D1D5DB" stroke-width="1"/>
  </pattern>
  <pattern id="grid" x="0" y="0" width="40" height="40"
           patternUnits="userSpaceOnUse">
    <path d="M40 0H0V40" fill="none" stroke="#F3F4F6" stroke-width="0.8"/>
  </pattern>
  <style>
    text { font-family: \'Arial Narrow\', Arial, sans-serif; }
    .r-label { font-size:13px; font-weight:700; fill:#111827; text-anchor:middle;
               dominant-baseline:central; letter-spacing:0.8px; }
    .r-sub   { font-size:10px; fill:#6B7280; text-anchor:middle; dominant-baseline:central; }
    .r-code  { font-size:9px;  fill:#9CA3AF; text-anchor:middle; dominant-baseline:central; }
    .p-code  { font-size:9px;  font-weight:700; fill:#FFFFFF;
               text-anchor:middle; dominant-baseline:central; }
    .leg-title { font-size:12px; font-weight:700; fill:#111827; }
    .leg-text  { font-size:10.5px; fill:#374151; }
    .leg-note  { font-size:9px; fill:#9CA3AF; }
    .tb-title  { font-size:14px; font-weight:700; fill:#FFFFFF; letter-spacing:0.5px; }
    .tb-sub    { font-size:10px; fill:#D1D5DB; }
    .tb-ref    { font-size:9px; fill:#9CA3AF; letter-spacing:0.3px; }
    .dim       { font-size:9px; fill:#6B7280; text-anchor:middle; }
  </style>
</defs>

<!-- FUNDO -->
<rect x="0" y="0" width="1120" height="700" fill="#FAFAF8"/>
<rect x="20" y="20" width="1080" height="660" fill="url(#grid)"
      stroke="#E5E7EB" stroke-width="0.8"/>

<!-- LIMITE DO LOTE -->
<rect x="50" y="55" width="960" height="590"
      fill="none" stroke="#9CA3AF" stroke-width="1.2" stroke-dasharray="12 6"/>

<!-- PÁTIO EXTERNO -->
<rect x="62" y="195" width="145" height="215"
      fill="#F0FDF4" stroke="#6B7280" stroke-width="1" stroke-dasharray="6 4"/>
<text x="134" y="285" class="r-label" font-size="11">Pátio</text>
<text x="134" y="300" class="r-sub">externo</text>

<!-- FOOTPRINT DO EDIFÍCIO — paredes externas com hachura -->
<rect x="205" y="68" width="760" height="524"
      fill="url(#hatch)" stroke="#1F2937" stroke-width="14" stroke-linejoin="miter"/>
<rect x="212" y="75" width="746" height="510" fill="#FAFAF8"/>

<!-- PAREDES DIVISÓRIAS INTERNAS -->
<rect x="386" y="75"  width="10" height="185" fill="url(#hatch-light)" stroke="#374151" stroke-width="1.5"/>
<rect x="541" y="75"  width="10" height="185" fill="url(#hatch-light)" stroke="#374151" stroke-width="1.5"/>
<rect x="696" y="75"  width="10" height="510" fill="url(#hatch-light)" stroke="#374151" stroke-width="1.5"/>
<rect x="212" y="256" width="490" height="10" fill="url(#hatch-light)" stroke="#374151" stroke-width="1.5"/>
<rect x="212" y="356" width="490" height="10" fill="url(#hatch-light)" stroke="#374151" stroke-width="1.5"/>
<rect x="702" y="447" width="254" height="10" fill="url(#hatch-light)" stroke="#374151" stroke-width="1.5"/>

<!-- FUNDOS DAS SALAS -->
<rect x="214" y="77"  width="170" height="177" fill="#EFF6FF" opacity="0.9"/>
<rect x="392" y="77"  width="147" height="177" fill="#F9FAFB" opacity="0.9"/>
<rect x="547" y="77"  width="147" height="177" fill="#EFF6FF" opacity="0.9"/>
<rect x="706" y="77"  width="250" height="177" fill="#F5F3FF" opacity="0.9"/>
<rect x="214" y="268" width="480" height="86"  fill="#F0F9FF" opacity="0.9"/>
<!-- Doca — destaque crítico -->
<rect x="214" y="368" width="230" height="180" fill="#FFFBEB" opacity="0.95"/>
<rect x="214" y="368" width="230" height="180"
      fill="none" stroke="#D97706" stroke-width="2" stroke-dasharray="7 3" opacity="0.7"/>
<rect x="452" y="368" width="250" height="180" fill="#F9FAFB" opacity="0.9"/>
<!-- Reserva B — destaque crítico -->
<rect x="706" y="268" width="250" height="177" fill="#FEF2F2" opacity="0.95"/>
<rect x="706" y="268" width="250" height="177"
      fill="none" stroke="#DC2626" stroke-width="2.5" stroke-dasharray="8 4" opacity="0.7"/>
<rect x="706" y="459" width="250" height="127" fill="#F0FDF4" opacity="0.9"/>

<!-- JANELAS -->
<rect x="234" y="60"  width="90" height="18" fill="#FAFAF8"/>
<line x1="234" y1="63" x2="324" y2="63" stroke="#93C5FD" stroke-width="3"/>
<line x1="234" y1="69" x2="324" y2="69" stroke="#60A5FA" stroke-width="2"/>
<line x1="234" y1="75" x2="324" y2="75" stroke="#93C5FD" stroke-width="1.5"/>
<rect x="420" y="60"  width="90" height="18" fill="#FAFAF8"/>
<line x1="420" y1="63" x2="510" y2="63" stroke="#93C5FD" stroke-width="3"/>
<line x1="420" y1="69" x2="510" y2="69" stroke="#60A5FA" stroke-width="2"/>
<line x1="420" y1="75" x2="510" y2="75" stroke="#93C5FD" stroke-width="1.5"/>
<rect x="950" y="100" width="18" height="80"  fill="#FAFAF8"/>
<line x1="953" y1="100" x2="953" y2="180" stroke="#93C5FD" stroke-width="3"/>
<line x1="959" y1="100" x2="959" y2="180" stroke="#60A5FA" stroke-width="2"/>
<line x1="965" y1="100" x2="965" y2="180" stroke="#93C5FD" stroke-width="1.5"/>
<rect x="950" y="480" width="18" height="70"  fill="#FAFAF8"/>
<line x1="953" y1="480" x2="953" y2="550" stroke="#93C5FD" stroke-width="3"/>
<line x1="959" y1="480" x2="959" y2="550" stroke="#60A5FA" stroke-width="2"/>
<line x1="965" y1="480" x2="965" y2="550" stroke="#93C5FD" stroke-width="1.5"/>
<rect x="280" y="579" width="90" height="18"  fill="#FAFAF8"/>
<line x1="280" y1="581" x2="370" y2="581" stroke="#93C5FD" stroke-width="3"/>
<line x1="280" y1="587" x2="370" y2="587" stroke="#60A5FA" stroke-width="2"/>
<line x1="280" y1="593" x2="370" y2="593" stroke="#93C5FD" stroke-width="1.5"/>

<!-- PORTAS com arco de abertura -->
<!-- P-01 Guarita → Pátio -->
<rect x="198" y="210" width="20" height="55" fill="#FAFAF8"/>
<line x1="205" y1="210" x2="205" y2="265" stroke="#1F2937" stroke-width="2"/>
<path d="M205 210 a55 55 0 0 0 55 55"
      fill="none" stroke="#B45309" stroke-width="2" stroke-dasharray="5 3"/>
<circle cx="218" cy="238" r="10" fill="#374151"/>
<text x="218" y="241" class="p-code">P01</text>

<!-- P-02 Guarita → Corredor -->
<rect x="254" y="250" width="60" height="22" fill="#FAFAF8"/>
<line x1="254" y1="258" x2="314" y2="258" stroke="#1F2937" stroke-width="2"/>
<path d="M314 258 a60 60 0 0 0 -60 -60"
      fill="none" stroke="#B45309" stroke-width="2" stroke-dasharray="5 3"/>
<circle cx="284" cy="254" r="10" fill="#374151"/>
<text x="284" y="257" class="p-code">P02</text>

<!-- P-03 Admin → Corredor -->
<rect x="415" y="250" width="55" height="22" fill="#FAFAF8"/>
<line x1="415" y1="258" x2="470" y2="258" stroke="#1F2937" stroke-width="2"/>
<path d="M415 258 a55 55 0 0 1 55 -55"
      fill="none" stroke="#B45309" stroke-width="2" stroke-dasharray="5 3"/>
<circle cx="442" cy="254" r="10" fill="#374151"/>
<text x="442" y="257" class="p-code">P03</text>

<!-- P-04 Doca → Pátio (CRÍTICA) -->
<rect x="198" y="395" width="20" height="55" fill="#FAFAF8"/>
<line x1="205" y1="395" x2="205" y2="450" stroke="#DC2626" stroke-width="2.5"/>
<path d="M205 395 a55 55 0 0 0 55 55"
      fill="none" stroke="#DC2626" stroke-width="2.5" stroke-dasharray="5 3"/>
<circle cx="218" cy="423" r="10" fill="#B91C1C"/>
<text x="218" y="426" class="p-code">P04</text>

<!-- P-05 Doca → Depósito -->
<rect x="446" y="405" width="22" height="55" fill="#FAFAF8"/>
<line x1="452" y1="405" x2="452" y2="460" stroke="#1F2937" stroke-width="2"/>
<path d="M452 405 a55 55 0 0 1 55 55"
      fill="none" stroke="#B45309" stroke-width="2" stroke-dasharray="5 3"/>
<circle cx="452" cy="432" r="10" fill="#374151"/>
<text x="452" y="435" class="p-code">P05</text>

<!-- P-06 Corredor → Reserva B (CRÍTICA) -->
<rect x="690" y="308" width="22" height="55" fill="#FAFAF8"/>
<line x1="700" y1="308" x2="700" y2="363" stroke="#DC2626" stroke-width="3"/>
<path d="M700 308 a55 55 0 0 0 -55 55"
      fill="none" stroke="#DC2626" stroke-width="3" stroke-dasharray="6 3"/>
<circle cx="700" cy="335" r="12" fill="#DC2626"/>
<text x="700" y="338" class="p-code">P06</text>

<!-- P-07 Corredor → Reserva A -->
<rect x="690" y="163" width="22" height="55" fill="#FAFAF8"/>
<line x1="700" y1="163" x2="700" y2="218" stroke="#1F2937" stroke-width="2"/>
<path d="M700 163 a55 55 0 0 0 -55 55"
      fill="none" stroke="#B45309" stroke-width="2" stroke-dasharray="5 3"/>
<circle cx="700" cy="190" r="10" fill="#374151"/>
<text x="700" y="193" class="p-code">P07</text>

<!-- P-08 Sala Seg. → Corredor -->
<rect x="570" y="250" width="55" height="22" fill="#FAFAF8"/>
<line x1="570" y1="258" x2="625" y2="258" stroke="#1F2937" stroke-width="2"/>
<path d="M570 258 a55 55 0 0 1 55 -55"
      fill="none" stroke="#B45309" stroke-width="2" stroke-dasharray="5 3"/>
<circle cx="597" cy="254" r="10" fill="#374151"/>
<text x="597" y="257" class="p-code">P08</text>

<!-- P-09 Reserva B → Vitrine -->
<rect x="749" y="443" width="60" height="22" fill="#FAFAF8"/>
<line x1="749" y1="452" x2="809" y2="452" stroke="#1F2937" stroke-width="2"/>
<path d="M809 452 a60 60 0 0 0 -60 -60"
      fill="none" stroke="#B45309" stroke-width="2" stroke-dasharray="5 3"/>
<circle cx="779" cy="448" r="10" fill="#374151"/>
<text x="779" y="451" class="p-code">P09</text>

<!-- CÂMERAS -->
<g transform="translate(310 284)">
  <polygon points="0,-10 -8,5 8,5" fill="#1D4ED8" opacity="0.85"/>
  <path d="M-16 5 L0 -10 L16 5 Z" fill="none" stroke="#93C5FD"
        stroke-width="1" opacity="0.5"/>
  <circle cx="0" cy="5" r="3" fill="#1D4ED8"/>
  <text x="0" y="22" font-size="8" fill="#1D4ED8" text-anchor="middle"
        font-weight="700">CAM-01</text>
</g>
<g transform="translate(956 270)">
  <polygon points="0,-10 -8,5 8,5" fill="#DC2626" opacity="0.9"/>
  <path d="M-20 5 L0 -10 L20 5 Z" fill="none" stroke="#FCA5A5"
        stroke-width="1.5" opacity="0.6"/>
  <circle cx="0" cy="5" r="3" fill="#DC2626"/>
  <text x="0" y="22" font-size="8" fill="#DC2626" text-anchor="middle"
        font-weight="700">CAM-02</text>
</g>
<g transform="translate(333 460)">
  <polygon points="0,-10 -8,5 8,5" fill="#9CA3AF" opacity="0.7"/>
  <line x1="-12" y1="-12" x2="12" y2="12" stroke="#EF4444" stroke-width="2.5" opacity="0.9"/>
  <line x1="12" y1="-12" x2="-12" y2="12" stroke="#EF4444" stroke-width="2.5" opacity="0.9"/>
  <text x="0" y="22" font-size="8" fill="#9CA3AF" text-anchor="middle"
        font-weight="700">CAM-03</text>
  <text x="0" y="32" font-size="7" fill="#EF4444" text-anchor="middle">OFFLINE</text>
</g>
<g transform="translate(260 138)">
  <polygon points="0,-10 -8,5 8,5" fill="#1D4ED8" opacity="0.85"/>
  <path d="M-14 5 L0 -10 L14 5 Z" fill="none" stroke="#93C5FD"
        stroke-width="1" opacity="0.5"/>
  <circle cx="0" cy="5" r="3" fill="#1D4ED8"/>
  <text x="0" y="22" font-size="8" fill="#1D4ED8" text-anchor="middle"
        font-weight="700">CAM-04</text>
</g>

<!-- RÓTULOS DAS SALAS -->
<text x="299" y="152" class="r-label">Guarita</text>
<text x="299" y="167" class="r-sub">Controle externo</text>
<text x="299" y="180" class="r-code">USR-031 · P-01</text>

<text x="464" y="150" class="r-label">Administração</text>
<text x="464" y="165" class="r-sub">Terminal TERM-ADM-03</text>
<text x="464" y="178" class="r-code">Otávio Salles</text>

<text x="620" y="150" class="r-label" font-size="12">Sala de Segurança</text>
<text x="620" y="165" class="r-code">P-08</text>

<text x="831" y="142" class="r-label">Reserva Técnica A</text>
<text x="831" y="157" class="r-sub">Acervo embalado</text>
<text x="831" y="170" class="r-code">P-07</text>

<text x="454" y="300" class="r-label">Corredor Técnico</text>
<text x="454" y="315" class="r-sub">Circulação restrita</text>
<text x="454" y="328" class="r-code">P-02 · P-03 · P-08</text>

<text x="329" y="432" class="r-label" font-size="12.5" fill="#92400E">Doca de Serviço</text>
<text x="329" y="448" class="r-sub">Sensor OS 0147/2026</text>
<text x="329" y="462" class="r-code" fill="#B45309">EVENTO CRÍTICO · P-04</text>
<rect x="218" y="492" width="130" height="20" rx="3"
      fill="#FEF3C7" stroke="#D97706" stroke-width="1"/>
<text x="283" y="506" font-size="8.5" fill="#92400E" text-anchor="middle"
      font-weight="700">TAPUME 19h40–20h05</text>

<text x="577" y="442" class="r-label">Depósito</text>
<text x="577" y="457" class="r-sub">Materiais · P-05</text>

<text x="831" y="318" class="r-label" fill="#DC2626">Reserva Técnica B</text>
<text x="831" y="334" class="r-sub">Abertura 19h48 — USR-022</text>
<text x="831" y="348" class="r-code" fill="#DC2626">ÁREA CRÍTICA · P-06</text>
<line x1="831" y1="360" x2="831" y2="440"
      stroke="#DC2626" stroke-width="2" stroke-dasharray="4 3"/>
<polygon points="831,446 825,434 837,434" fill="#DC2626"/>

<text x="831" y="496" class="r-label">Vitrine</text>
<text x="831" y="510" class="r-sub">Área pública · P-09</text>

<!-- JANELA DE TEMPO CRÍTICO -->
<rect x="214" y="140" width="170" height="68" rx="4"
      fill="#F0F9FF" stroke="#38BDF8" stroke-width="1.2"/>
<text x="299" y="157" font-size="9.5" fill="#0369A1" text-anchor="middle"
      font-weight="700">JANELA CRÍTICA</text>
<text x="299" y="170" font-size="9" fill="#0C4A6E" text-anchor="middle">19h40 — 20h05</text>
<line x1="228" y1="177" x2="370" y2="177" stroke="#BAE6FD" stroke-width="1"/>
<text x="299" y="188" font-size="8.5" fill="#0369A1" text-anchor="middle">
  visão direta bloqueada</text>
<text x="299" y="200" font-size="8.5" fill="#0369A1" text-anchor="middle">
  CAM-03 offline</text>

<!-- TRILHA INVESTIGATIVA RM-17 -->
<path d="M706 340 L540 340 L540 311 L706 311"
      fill="none" stroke="#DC2626" stroke-width="2.5"
      stroke-dasharray="10 5" opacity="0.65"/>
<text x="623" y="302" font-size="9" fill="#B91C1C" text-anchor="middle"
      font-weight="700">saída RM-17 →</text>

<!-- NORTE -->
<g transform="translate(1048 82)">
  <circle cx="0" cy="0" r="28" fill="#FFFFFF" stroke="#374151" stroke-width="1.5"/>
  <line x1="0" y1="-20" x2="0" y2="20" stroke="#374151" stroke-width="1.5"/>
  <line x1="-20" y1="0" x2="20" y2="0" stroke="#374151" stroke-width="1.5"/>
  <polygon points="0,-20 -7,0 0,-4 7,0" fill="#1F2937"/>
  <polygon points="0,20 -7,0 0,4 7,0" fill="#F9FAFB" stroke="#374151" stroke-width="1"/>
  <text x="0" y="-25" font-size="11" font-weight="700" fill="#111827"
        text-anchor="middle">N</text>
</g>

<!-- ESCALA GRÁFICA -->
<g transform="translate(70 583)">
  <line x1="0" y1="0" x2="120" y2="0" stroke="#374151" stroke-width="2"/>
  <line x1="0"   y1="-5" x2="0"   y2="5" stroke="#374151" stroke-width="2"/>
  <line x1="60"  y1="-4" x2="60"  y2="4" stroke="#374151" stroke-width="1.5"/>
  <line x1="120" y1="-5" x2="120" y2="5" stroke="#374151" stroke-width="2"/>
  <text x="30" y="16" class="dim">5 m</text>
  <text x="90" y="16" class="dim">5 m</text>
  <text x="60" y="-9" class="dim">0</text>
  <text x="0" y="28" class="leg-note">Escala esquemática</text>
</g>

<!-- LEGENDA -->
<rect x="50" y="434" width="145" height="140" rx="6"
      fill="#FFFFFF" stroke="#D1D5DB" stroke-width="1"/>
<text x="122" y="452" class="leg-title" text-anchor="middle">Legenda</text>
<line x1="60" y1="456" x2="185" y2="456" stroke="#E5E7EB" stroke-width="1"/>
<rect x="62" y="463" width="14" height="10" fill="#EFF6FF" stroke="#374151" stroke-width="1"/>
<text x="83" y="472" class="leg-text">Controle de acesso</text>
<rect x="62" y="479" width="14" height="10" fill="#F5F3FF" stroke="#374151" stroke-width="1"/>
<text x="83" y="488" class="leg-text">Reservas de acervo</text>
<rect x="62" y="495" width="14" height="10" fill="#FFFBEB" stroke="#374151" stroke-width="1"/>
<text x="83" y="504" class="leg-text">Área de carga</text>
<rect x="62" y="511" width="14" height="10" fill="#F0FDF4" stroke="#374151" stroke-width="1"/>
<text x="83" y="520" class="leg-text">Área pública</text>
<circle cx="69" cy="534" r="5" fill="#DC2626"/>
<text x="83" y="538" class="leg-text" fill="#DC2626">Área crítica</text>
<polygon points="69,552 63,562 75,562" fill="#1D4ED8" opacity="0.85"/>
<text x="83" y="560" class="leg-text">Câmera ativa</text>
<line x1="62" y1="572" x2="76" y2="572" stroke="#9CA3AF" stroke-width="1.2" stroke-dasharray="4 3"/>
<text x="83" y="575" class="leg-note">Limite do lote</text>

<!-- BLOCO DE TÍTULO -->
<rect x="50" y="622" width="1020" height="58" fill="#1F2937" rx="4"/>
<text x="68" y="643" class="tb-title">CASA DE ACERVO MIRANTE</text>
<text x="68" y="657" class="tb-sub">Planta baixa operacional — térreo</text>
<text x="68" y="671" class="tb-ref">
  Ref. CAM-NIP-0826-17 · Uso exclusivo para apuração interna · Indiciários v1.0</text>
<line x1="440" y1="630" x2="440" y2="672" stroke="#374151" stroke-width="1"/>
<text x="460" y="643" class="tb-sub">Portas</text>
<text x="460" y="655" class="tb-ref">P-01 Guarita  P-04 Doca  P-06 Reserva B</text>
<text x="460" y="666" class="tb-ref">P-03 Admin    P-05 Depósito  P-09 Vitrine</text>
<line x1="718" y1="630" x2="718" y2="672" stroke="#374151" stroke-width="1"/>
<text x="736" y="643" class="tb-sub">Câmeras</text>
<text x="736" y="655" class="tb-ref">CAM-01 Corredor  CAM-02 Reserva B  CAM-04 Guarita</text>
<text x="736" y="666" class="tb-ref" fill="#EF4444">
  CAM-03 Doca — OFFLINE na janela 19h40-20h05</text>
<line x1="950" y1="630" x2="950" y2="672" stroke="#374151" stroke-width="1"/>
<text x="966" y="645" class="tb-sub">Versão</text>
<text x="966" y="658" class="tb-ref">18/08/2026</text>
<text x="966" y="669" class="tb-ref">v1.0</text>
</svg>"""

def build_map_svg(mapa: MapaProcedural) -> str:
    """Monta SVG local para uma planta esquemática simples de um andar."""
    if mapa.id == "casa_acervo_mirante_andar_1":
        return _build_mirante_floor_plan_svg(mapa)

    largura = max(mapa.largura, 1)
    altura = max(mapa.altura, 1)
    centers = {
        area.id: (area.x + area.w / 2, area.y + area.h / 2)
        for area in mapa.areas
        if area.id
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura:g} {altura:g}" role="img" aria-label="{escape(mapa.titulo)}">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc" stroke="#111827" stroke-width="2"/>',
        '<text x="28" y="36" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#111827">Planta esquemática</text>',
    ]

    for conexao in mapa.conexoes:
        origem = centers.get(conexao.origem)
        destino = centers.get(conexao.destino)
        if not origem or not destino:
            continue
        parts.append(
            f'<line x1="{origem[0]:g}" y1="{origem[1]:g}" x2="{destino[0]:g}" y2="{destino[1]:g}" '
            'stroke="#bfdbfe" stroke-width="18" stroke-linecap="round"/>'
        )
        parts.append(
            f'<line x1="{origem[0]:g}" y1="{origem[1]:g}" x2="{destino[0]:g}" y2="{destino[1]:g}" '
            'stroke="#1d4ed8" stroke-width="3" stroke-linecap="round" stroke-dasharray="9 7"/>'
        )

    palette = {
        "controle_acesso": "#dbeafe",
        "circulacao": "#e0f2fe",
        "carga": "#fef3c7",
        "reserva": "#ede9fe",
        "exposicao": "#dcfce7",
        "administrativo": "#fce7f3",
    }
    for area in mapa.areas:
        fill = palette.get(area.tipo, "#ffffff") if area.acessivel else "#e5e7eb"
        stroke_dash = "" if area.acessivel else ' stroke-dasharray="8 5"'
        parts.append(
            f'<rect x="{area.x:g}" y="{area.y:g}" width="{area.w:g}" height="{area.h:g}" rx="12" '
            f'fill="{fill}" stroke="#334155" stroke-width="2.5"{stroke_dash}/>'
        )
        label = escape(_short_label(area.nome, 20))
        text_x = area.x + area.w / 2
        text_y = area.y + area.h / 2 - (8 if area.observacao else 0)
        parts.append(
            f'<text x="{text_x:g}" y="{text_y:g}" text-anchor="middle" font-family="Arial, sans-serif" '
            f'font-size="16" font-weight="700" fill="#111827">{label}</text>'
        )
        if area.observacao:
            parts.append(
                f'<text x="{text_x:g}" y="{text_y + 22:g}" text-anchor="middle" font-family="Arial, sans-serif" '
                f'font-size="11" fill="#475569">{escape(_short_label(area.observacao, 24))}</text>'
            )

    marker_items: list[str] = []
    for index, marcador in enumerate(mapa.marcadores, start=1):
        label = escape(_short_label(marcador.label, 24))
        marker_items.append(f"{index}. {label}")
        parts.append(
            f'<circle cx="{marcador.x:g}" cy="{marcador.y:g}" r="15" fill="#111827"/>'
        )
        parts.append(
            f'<text x="{marcador.x:g}" y="{marcador.y + 5:g}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#ffffff">{index}</text>'
        )

    legend_items = marker_items or [
        f"{item.simbolo}: {_short_label(item.descricao, 28)}" for item in mapa.legenda
    ]
    if legend_items:
        legend_width = 300
        legend_height = 34 + 22 * len(legend_items)
        x = max(12, largura - legend_width - 24)
        y = 24
        parts.append(f'<g transform="translate({x:g} {y:g})">')
        parts.append(
            f'<rect x="0" y="0" width="{legend_width}" height="{legend_height}" rx="10" '
            'fill="#ffffff" fill-opacity="0.96" stroke="#94a3b8"/>'
        )
        parts.append(
            '<text x="16" y="22" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#111827">Marcadores</text>'
        )
        for index, item in enumerate(legend_items):
            line_y = 46 + index * 22
            parts.append(
                f'<text x="16" y="{line_y}" font-family="Arial, sans-serif" font-size="12" fill="#111827">'
                f"{escape(_short_label(item, 36))}</text>"
            )
        parts.append("</g>")

    parts.append("</svg>")
    return "".join(parts)


def build_character_card_svg(personagem: PersonagemVisual, blueprint: Blueprint) -> str:
    """Monta SVG local para um cartão visual de personagem."""
    nome = escape(_personagem_nome(personagem, blueprint))
    cor = _safe_color(personagem.cor)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 560" role="img">',
        '<rect x="0" y="0" width="420" height="560" rx="18" fill="#ffffff" stroke="#111827" stroke-width="3"/>',
        f'<rect x="0" y="0" width="420" height="96" rx="18" fill="{cor}"/>',
        f'<text x="32" y="58" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#ffffff">{nome}</text>',
        f'<circle cx="210" cy="230" r="86" fill="{cor}" opacity="0.15" stroke="{cor}" stroke-width="4"/>',
        f'<text x="210" y="244" text-anchor="middle" font-family="Arial, sans-serif" font-size="64" fill="{cor}">{escape(personagem.icone)}</text>',
        f'<text x="210" y="344" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#374151">{escape(personagem.silhueta)}</text>',
    ]
    for index, detalhe in enumerate(personagem.detalhes[:6]):
        y = 392 + index * 26
        parts.append(
            f'<text x="44" y="{y}" font-family="Arial, sans-serif" font-size="15" fill="#111827">• {escape(detalhe)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def build_location_card_svg(local: LocalVisual) -> str:
    """Monta SVG local para um cartão/placa visual de local."""
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 300" role="img">',
        '<rect x="0" y="0" width="420" height="300" rx="16" fill="#ffffff" stroke="#111827" stroke-width="3"/>',
        '<rect x="0" y="0" width="420" height="72" rx="16" fill="#1f2937"/>',
        f'<text x="28" y="46" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#ffffff">{escape(local.nome)}</text>',
        f'<text x="34" y="136" font-family="Arial, sans-serif" font-size="52" fill="#111827">{escape(local.icone)}</text>',
        f'<text x="104" y="118" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#111827">{escape(local.tipo)}</text>',
        f'<foreignObject x="104" y="132" width="280" height="100"><div xmlns="http://www.w3.org/1999/xhtml" '
        f'style="font-family:Arial,sans-serif;font-size:14px;color:#374151;line-height:1.35">{escape(local.descricao)}</div></foreignObject>',
    ]
    if local.documentos_relacionados:
        docs = ", ".join(local.documentos_relacionados)
        parts.append(
            f'<text x="28" y="260" font-family="Arial, sans-serif" font-size="13" fill="#111827">Documentos: {escape(docs)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def visual_document_code(kind: str, identifier: str) -> str:
    prefixes = {"map": "VP-MAPA", "character": "VP-PERSONAGEM", "location": "VP-LOCAL"}
    return f"{prefixes[kind]}-{identifier}"


def visual_document_path(kind: str, identifier: str, output_dir: Path) -> Path:
    names = {
        "map": "visual_map",
        "character": "visual_personagem",
        "location": "visual_local",
    }
    return output_dir / f"{names[kind]}_{_safe_id(identifier)}.pdf"


def build_visual_documents(
    blueprint: Blueprint,
    output_dir: Path,
    strict: bool = True,
    html_debug_dir: Path | None = None,
) -> dict[str, list[Path]]:
    """Renderiza PDFs visuais e agrupa por envelope/fase para o pacote final."""
    visual = blueprint.visual_procedural
    grupos: dict[str, list[Path]] = {}
    if visual is None:
        return grupos

    output_dir.mkdir(parents=True, exist_ok=True)
    for mapa in visual.mapas:
        svg = build_map_svg(mapa)
        output_path = visual_document_path("map", mapa.id, output_dir)
        dados = {
            "TITULO": mapa.titulo,
            "SUBTITULO": f"Mapa procedural — {mapa.fase}",
            "SVG": svg,
        }
        render_kwargs = {"strict": strict, "landscape": True}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = (
                html_debug_dir / f"{output_path.stem}.html"
            )
        caminho = renderizar_documento(
            "visual_map.html", dados, output_path, **render_kwargs
        )
        grupos.setdefault(mapa.fase or "E1", []).append(caminho)

    for personagem in visual.personagens:
        svg = build_character_card_svg(personagem, blueprint)
        output_path = visual_document_path(
            "character", personagem.personagem_id, output_dir
        )
        nome = _personagem_nome(personagem, blueprint)
        dados = {"TITULO": f"Cartão de personagem — {nome}", "SVG": svg}
        render_kwargs = {"strict": strict}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = (
                html_debug_dir / f"{output_path.stem}.html"
            )
        caminho = renderizar_documento(
            "visual_character_card.html", dados, output_path, **render_kwargs
        )
        grupos.setdefault("E1", []).append(caminho)

    for local in visual.locais:
        svg = build_location_card_svg(local)
        output_path = visual_document_path("location", local.id, output_dir)
        dados = {"TITULO": f"Cartão de local — {local.nome}", "SVG": svg}
        render_kwargs = {"strict": strict}
        if html_debug_dir is not None:
            render_kwargs["html_debug_path"] = (
                html_debug_dir / f"{output_path.stem}.html"
            )
        caminho = renderizar_documento(
            "visual_location_card.html", dados, output_path, **render_kwargs
        )
        grupos.setdefault("E1", []).append(caminho)

    return grupos
