import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from PIL import Image
import io

# Função para gerar o PDF com base nos dados inseridos pelo usuário
def generate_pdf(dados_edificacao, uploaded_image=None):
    pdf = FPDF()
    
    # Capa (Página 1)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Cálculo de Ações do Vento", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, "Conforme ABNT NBR 6123:2023", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(0, 10, "Cliente: Construtora ABC", ln=True)
    pdf.cell(0, 10, "Obra: Edifício Residencial", ln=True)
    pdf.cell(0, 10, "Localização: São Paulo, SP", ln=True)
    pdf.cell(0, 10, "Cód. do Projeto: 2025-001", ln=True)
    pdf.cell(0, 10, "Número do Documento: REL-001-2025", ln=True)
    pdf.cell(0, 10, "Revisão: 0", ln=True)
    pdf.cell(0, 10, "Data: 29/04/2025", ln=True)
    pdf.cell(0, 10, "Cálculo: João Silva", ln=True)
    pdf.cell(0, 10, "Aprovação: [A Definir]", ln=True)
    pdf.cell(0, 10, "Empresa: xAI Engenharia Ltda.", ln=True)
    pdf.cell(0, 10, "Contato: contato@xaiengenharia.com", ln=True)

    # Sumário (Página 2)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Sumário", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    sumario = [
        ("1", "Dados da Edificação", "2"),
        ("2", "Fator de Rajada (Fr)", "3"),
        ("3", "Parâmetros Meteorológicos", "3"),
        ("4", "Valores Mínimos do Fator Estatístico S3", "4"),
        ("5", "Cálculo do Fator S2 por Altura", "4"),
        ("6", "Velocidades e Pressões Características", "5"),
        ("7", "Parâmetros para Determinação do Fator S2", "5"),
        ("8", "Pressões de Vento na Direção X1", "6"),
        ("9", "Pressões de Vento na Direção X2", "6"),
        ("10", "Fator S2 Calculado", "7"),
        ("11", "Velocidade Característica (Vk)", "7"),
        ("12", "Pressão Dinâmica do Vento (q)", "7"),
        ("13", "Coeficientes de Pressão Externa (Ce)", "8"),
        ("14", "Zonas de Pressão Externa", "9"),
        ("15", "Coeficientes de Pressão Externa (Ce) Selecionados", "9"),
        ("16", "Coeficiente de Pressão Interno (Cpi)", "10"),
        ("17", "Pressão Efetiva (DP)", "10"),
        ("18", "Observações", "12"),
        ("19", "Legenda de Siglas", "12"),
    ]
    for secao, titulo, pagina in sumario:
        pdf.cell(0, 10, f"Seção {secao} - {titulo} - Página {pagina}", ln=True)

    # Metodologia de Cálculo (Fórmulas) - Nova Seção
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Metodologia de Cálculo", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Velocidade Característica do Vento (Vk):\nVk = V0 * S1 * S2 * S3")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Fator S2:\nS2 = bm * (z/10)^p * Fr")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Pressão Dinâmica do Vento (q):\nq = 0,613 * Vk^2 (N/m²)\nq = (0,613 * Vk^2) / 9,81 (kgf/m²)")
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Pressão Efetiva (DP):\nDP = (Ce - Cpi) * q")

    # Seção 1: Dados da Edificação (usando dados preenchidos pelo usuário)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "1. Dados da Edificação", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    for parametro, valor in dados_edificacao.items():
        pdf.cell(0, 10, f"{parametro}: {valor}", ln=True)

    # Seção 2: Fator de Rajada (Fr)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "2. Fator de Rajada (Fr)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Fr | Classes", ln=True)
    pdf.cell(0, 10, "   | A    | B    | C", ln=True)
    pdf.cell(0, 10, "1,00 | 0,98 | 0,95", ln=True)

    # Seção 3: Parâmetros Meteorológicos
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "3. Parâmetros Meteorológicos", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    params_meteorologicos = [
        ("Categoria | Zg (m) | Parâmetro | Classes", ""),
        ("", "", "         | A    | B    | C", ""),
        ("I   | 250    | bm       | 1,10 | 1,11 | 1,12", ""),
        ("    |        | p        | 0,06 | 0,065| 0,07", ""),
        ("II  | 300    | bm       | 1,00 | 1,00 | 1,00", ""),
        ("    |        | p        | 0,085| 0,09 | 0,10", ""),
        ("III | 350    | bm       | 0,94 | 0,94 | 0,93", ""),
        ("    |        | p        | 0,10 | 0,105| 0,115", ""),
        ("IV  | 420    | bm       | 0,86 | 0,85 | 0,84", ""),
        ("    |        | p        | 0,12 | 0,125| 0,135", ""),
        ("V   | 500    | bm       | 0,74 | 0,73 | 0,71", ""),
        ("    |        | p        | 0,15 | 0,16 | 0,175", ""),
    ]
    for linha in params_meteorologicos:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 4: Valores Mínimos do Fator Estatístico S3
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "4. Valores Mínimos do Fator Estatístico S3", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    valores_s3 = [
        ("Grupo | Descrição | S3 | Tp (anos)", ""),
        ("1 | Estruturas cuja ruína total ou parcial pode afetar a segurança ou possibilidade " +
         "de socorro a pessoas após uma tempestade destrutiva (hospitais, quartéis de bombeiros " +
         "e de forças de segurança, edifícios de centros de controle, torres de comunicação etc.). " +
         "Obras de infraestrutura crítica. Armazenamento de substâncias perigosas e/ou tóxicas " +
         "e/ou explosivas. Vedações das edificações do grupo 1 (telhas, vidros, painéis de vedação).", "1,11", "100"),
        ("2 | Estruturas cuja ruína representa substancial risco à vida humana, particularmente " +
         "pessoas em aglomerações, crianças e jovens, incluindo, mas não limitadamente a: " +
         "edificações com capacidade de aglomeração de mais de 300 pessoas em um mesmo ambiente, " +
         "como centros de convenções, ginásios, estádios etc.; creches com capacidade maior do que " +
         "150 pessoas; escolas com capacidade maior do que 250 pessoas. Vedações das edificações " +
         "do grupo 2 (telhas, vidros, painéis de vedação).", "1,06", "75"),
        ("3 | Edificações para residências, hotéis, comércio, indústrias. Estruturas ou elementos " +
         "estruturais desmontáveis com vistas a reutilização. Vedações das edificações do grupo 3 " +
         "(telhas, vidros, painéis de vedação).", "1,00", "50"),
        ("4 | Edificações não destinadas à ocupação humana (depósitos, silos) e sem circulação de " +
         "pessoas no entorno. Vedações das edificações do grupo 4 (telhas, vidros, painéis de vedação).", "0,95", "37"),
        ("5 | Edificações temporárias não reutilizáveis. Estruturas dos Grupos 1 a 4 durante a " +
         "construção (fator aplicável em um prazo máximo de 2 anos). Vedações das edificações do " +
         "grupo 5 (telhas, vidros, painéis de vedação).", "0,83", "15"),
    ]
    for grupo, descricao, s3, tp in valores_s3:
        pdf.multi_cell(0, 10, f"{grupo} | {descricao} | {s3} | {tp}")

    # Seção 5: Cálculo do Fator S2 por Altura
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "5. Cálculo do Fator S2 por Altura", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    fator_s2 = [
        ("z (m) | S2", ""),
        ("0,0  | 0,000000", ""),
        ("5,0  | 1,055191", ""),
        ("10,0 | 1,100000", ""),
        ("15,0 | 1,127089", ""),
        ("20,0 | 1,146712", ""),
        ("25,0 | 1,162168", ""),
        ("30,0 | 1,174952", ""),
        ("35,0 | 1,185869", ""),
        ("40,0 | 1,195408", ""),
        ("45,0 | 1,203886", ""),
        ("50,0 | 1,211521", ""),
        ("55,0 | 1,218469", ""),
        ("60,0 | 1,224847", ""),
        ("65,0 | 1,230743", ""),
        ("70,0 | 1,236228", ""),
        ("75,0 | 1,241356", ""),
    ]
    for linha in fator_s2:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 6: Velocidades e Pressões Características
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "6. Velocidades e Pressões Características", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    velocidades_pressoes = [
        ("z (m) | S1 | S2 | S3 | Vk (m/s) | q (kN/m²)", ""),
        ("0,0  | 1,00 | 0,00 | 1,11 | 0,00  | 0,000", ""),
        ("5,0  | 1,00 | 1,06 | 1,11 | 49,19 | 1,482", ""),
        ("10,0 | 1,00 | 1,10 | 1,11 | 51,28 | 1,611", ""),
        ("15,0 | 1,00 | 1,13 | 1,11 | 52,54 | 1,691", ""),
        ("20,0 | 1,00 | 1,15 | 1,11 | 53,46 | 1,750", ""),
        ("25,0 | 1,00 | 1,16 | 1,11 | 54,18 | 1,798", ""),
        ("30,0 | 1,00 | 1,17 | 1,11 | 54,78 | 1,838", ""),
        ("35,0 | 1,00 | 1,19 | 1,11 | 55,29 | 1,872", ""),
        ("40,0 | 1,00 | 1,20 | 1,11 | 55,73 | 1,902", ""),
        ("45,0 | 1,00 | 1,20 | 1,11 | 56,13 | 1,929", ""),
        ("50,0 | 1,00 | 1,21 | 1,11 | 56,48 | 1,954", ""),
        ("55,0 | 1,00 | 1,22 | 1,11 | 56,81 | 1,976", ""),
        ("60,0 | 1,00 | 1,22 | 1,11 | 57,10 | 1,997", ""),
        ("65,0 | 1,00 | 1,23 | 1,11 | 57,38 | 2,016", ""),
        ("70,0 | 1,00 | 1,24 | 1,11 | 57,63 | 2,034", ""),
        ("75,0 | 1,00 | 1,24 | 1,11 | 57,87 | 2,051", ""),
    ]
    for linha in velocidades_pressoes:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 7: Parâmetros para Determinação do Fator S2
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "7. Parâmetros para Determinação do Fator S2", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    params_s2 = [
        ("Direção do Vento | Fator de Rajada (Fr) | Coeficiente bm | Coeficiente p", ""),
        ("X1 | 0,95 | 0,93 | 0,10", ""),
        ("X2 | 0,95 | 0,93 | 0,10", ""),
    ]
    for linha in params_s2:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 8: Pressões de Vento na Direção X1
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "8. Pressões de Vento na Direção X1", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pressoes_x1 = [
        ("Altura z (m) | Fator S2 | S1 | S3 | Velocidade Vk (m/s) | Pressão q (kN/m²)", ""),
        ("5,0  | 1,06 | 1,00 | 1,11 | 49,19 | 1,482", ""),
        ("10,0 | 1,10 | 1,00 | 1,11 | 51,28 | 1,611", ""),
        ("15,0 | 1,13 | 1,00 | 1,11 | 52,54 | 1,691", ""),
        ("20,0 | 1,15 | 1,00 | 1,11 | 53,46 | 1,750", ""),
        ("25,0 | 1,16 | 1,00 | 1,11 | 54,18 | 1,798", ""),
    ]
    for linha in pressoes_x1:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 9: Pressões de Vento na Direção X2
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "9. Pressões de Vento na Direção X2", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pressoes_x2 = [
        ("Altura z (m) | Fator S2 | S1 | S3 | Velocidade Vk (m/s) | Pressão q (kN/m²)", ""),
        ("5,0  | 1,06 | 1,00 | 1,11 | 49,19 | 1,482", ""),
        ("10,0 | 1,10 | 1,00 | 1,11 | 51,28 | 1,611", ""),
        ("15,0 | 1,13 | 1,00 | 1,11 | 52,54 | 1,691", ""),
        ("20,0 | 1,15 | 1,00 | 1,11 | 53,46 | 1,750", ""),
        ("25,0 | 1,16 | 1,00 | 1,11 | 54,18 | 1,798", ""),
    ]
    for linha in pressoes_x2:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 10: Fator S2 Calculado
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "10. Fator S2 Calculado", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    fator_s2_calculado = [
        ("Parâmetro | Fechamento | Cobertura", ""),
        ("Altura z (m) | 13,00 | 13,80", ""),
        ("bm | 1,10 | 1,10", ""),
        ("p | 0,060 | 0,060", ""),
        ("Fr | 1,00 | 1,00", ""),
        ("S2 | 1,117453 | 1,121464", ""),
    ]
    for linha in fator_s2_calculado:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 11: Velocidade Característica (Vk)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "11. Velocidade Característica (Vk)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    velocidade_vk = [
        (" | Fechamento | Cob No ertura", ""),
        ("Vk (m/s) | 52,10 | 52,28", ""),
    ]
    for linha in velocidade_vk:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 12: Pressão Dinâmica do Vento (q)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "12. Pressão Dinâmica do Vento (q)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pressao_q = [
        (" | Fechamento | Cobertura", ""),
        ("q (N/m²) | 1662,30 | 1674,25", ""),
        ("q (kgf/m²) | 169,51 | 170,73", ""),
    ]
    for linha in pressao_q:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 13: Coeficientes de Pressão Externa (Ce)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "13. Coeficientes de Pressão Externa (Ce)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    coef_pressao_ce = [
        ("θ (°) | Valores de Ce para ângulo de incidência do vento α", ""),
        ("      | 90°       | 45°      | 0°        | -45°     | -90°", ""),
        ("      | HeI | LeJ | H  | L   | HeLa | HeLa | H  | L   | HeI | LeJ", ""),
        ("5     | -1,0| -0,5| -1,0| -0,9| -1,0 | -0,5 | -0,9| -1,0| -0,5| -1,0", ""),
        ("10    | -1,0| -0,5| -1,0| -0,8| -1,0 | -0,5 | -0,8| -1,0| -0,4| -1,0", ""),
        ("15    | -0,9| -0,5| -1,0| -0,7| -1,0 | -0,5 | -0,6| -1,0| -0,3| -1,0", ""),
        ("20 Bump | -0,8|     |     |     | -0,5 | -0,5 | -0,5| -1,0| -0,2| -1,0", ""),
        ("      | -0,7| -0,5| -1,0| -0,6| -0,8 | -0,5 | -0,3| -0,9| -0,1| -0,9", ""),
        ("30    | -0,5| -0,5| -1,0| -0,6| -0,8 | -0,5 | -0,1| -0,8| 0,0 | -0,6", ""),
        ("θ (°) | Ce médio", ""),
        ("      | H1  | H2  | L1  | L2  | H6", ""),
        ("5     | -2,0| -1,5| -2,0| -1,5| -2,0", ""),
        ("10    | -2,0| -1,5| -2,0| -1,5| -2,0", ""),
        ("15    | -1,8| -0,9| -1,8| -1,4| -2,0", ""),
        ("20    | -1,8| -0,8| -1,8| -1,4| -2,0", ""),
        ("25    | -1,8| -0,7| -0,9| -0,9| -2,0", ""),
        ("30    | -1,8| -0,5| -0,5| -0,5| -2,0", ""),
    ]
    for linha in coef_pressao_ce:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 14: Zonas de Pressão Externa
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "14. Zonas de Pressão Externa", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "H: Alta sucção (b/2 a partir da borda de barlavento); L: Baixa sucção (de b/2 até a/2); I, J: Zonas laterais.")

    # Seção 15: Coeficientes de Pressão Externa (Ce) Selecionados
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "15. Coeficientes de Pressão Externa (Ce) Selecionados", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    coef_pressao_ce_selecionados = [
        ("Direção do Vento | Fechamento | Cobertura", ""),
        ("0°/180° (Longitudinal) | -0,90,-0,46,-0,28,-0,42,0,70 | -0,90,-0,60,-0,33,0,70", ""),
        ("90°/270° (Transversal) | -0,90,-0,50,-0,54 | -0,93,-0,60,-0,54", ""),
    ]
    for linha in coef_pressao_ce_selecionados:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 16: Coeficiente de Pressão Interno (Cpi)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "16. Coeficiente de Pressão Interno (Cpi)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "Caso Selecionado (NBR 6123:2023 - Item 6.3.2.1): a", ln=True)
    pdf.cell(0, 10, "Descrição: a) Duas faces opostas igualmente permeáveis; as outras faces impermeáveis", ln=True)
    pdf.cell(0, 10, "Cpi: 0,20, -0,30", ln=True)

    # Seção 17: Pressão Efetiva (DP)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "17. Pressão Efetiva (DP)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "17.1. Vento a 0°/180° - Fechamento", ln=True)
    pressao_dp_1 = [
        ("Ce | Cpi | DP (kgf/m²)", ""),
        ("-0,90 | 0,20 | -186,46", ""),
        ("-0,90 | -0,30 | -101,70", ""),
        ("-0,46 | 0,20 | -112,30", ""),
        ("-0,46 | -0,30 | -27,54", ""),
        ("-0,28 | 0,20 | -81,70", ""),
        ("-0,28 | -0,30 | 3,05", ""),
        ("-0,42 | 0,20 | -105,94", ""),
        ("-0,42 | -0,30 | -21,19", ""),
        ("0,70 | 0,20 | 84,75", ""),
        ("0,70 | -0,30 | 169,51", ""),
    ]
    for linha in pressao_dp_1:
        pdf.cell(0, 10, linha[0], ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "17.2. Vento a 0°/180° - Cobertura", ln=True)
    pressao_dp_2 = [
        ("Ce | Cpi | DP (kgf/m²)", ""),
        ("-0,90 | 0,20 | -187,80", ""),
        ("-0,90 | -0,30 | -102,44", ""),
        ("-0,60 | 0,20 | -136,58", ""),
        ("-0,60 | -0,30 | -51,22", ""),
        ("-0,33 | 0,20 | -89,63", ""),
        ("-0,33 | -0,30 | -4,27", ""),
        ("0,70 | 0,20 | 85,36", ""),
        ("0,70 | -0,30 | 170,73", ""),
    ]
    for linha in pressao_dp_2:
        pdf.cell(0, 10, linha[0], ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "17.3. Vento a 90°/270° - Fechamento", ln=True)
    pressao_dp_3 = [
        ("Ce | Cpi | DP (kgf/m²)", ""),
        ("-0,90 | 0,20 | -186,46", ""),
        ("-0,90 | -0,30 | -101,70", ""),
        ("-0,50 | 0,20 | -118,66", ""),
        ("-0,50 | -0,30 | -33,90", ""),
        ("-0,54 | 0,20 | -125,01", ""),
        ("-0,54 | -0,30 | -40,26", ""),
    ]
    for linha in pressao_dp_3:
        pdf.cell(0, 10, linha[0], ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "17.4. Vento a 90°/270° - Cobertura", ln=True)
    pressao_dp_4 = [
        ("Ce | Cpi | DP (kgf/m²)", ""),
        ("-0,93 | 0,20 | -192,65", ""),
        ("-0,93 | -0,30 | -107,28", ""),
        ("-0,60 | 0,20 | -136,58", ""),
        ("-0,60 | -0,30 | -51,22", ""),
        ("-0,54 | 0,20 | -125,91", ""),
        ("-0,54 | -0,30 | -40,55", ""),
    ]
    for linha in pressao_dp_4:
        pdf.cell(0, 10, linha[0], ln=True)

    # Seção 18: Observações
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "18. Observações", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, "Os valores de DP são aplicáveis ao dimensionamento do sistema de vedação (fechamento e cobertura). Verificar a combinação mais crítica para cada elemento.\nCálculos realizados conforme ABNT NBR 6123:2023.")

    # Seção 19: Legenda de Siglas
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "19. Legenda de Siglas", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    legendas = [
        ("Sigla | Descrição", ""),
        ("z | Altura acima do terreno (m)", ""),
        ("V0 | Velocidade básica do vento (m/s)", ""),
        ("Vk | Velocidade característica do vento (m/s)", ""),
        ("q | Pressão dinâmica do vento (kN/m² ou kgf/m²)", ""),
        ("Ce | Coeficiente de forma externo", ""),
        ("Cpi | Coeficiente de pressão interna", ""),
        ("S1 | Fator topográfico", ""),
        ("S2 | Fator de rugosidade e dimensões da edificação", ""),
        ("S3 | Fator estatístico", ""),
        ("Fr | Fator de rajada", ""),
        ("bm | Fator meteorológico (NBR 6123:2023)", ""),
        ("p | Expoente meteorológico (NBR 6123:2023)", ""),
        ("DP | Pressão efetiva (kgf/m²)", ""),
    ]
    for linha in legendas:
        pdf.cell(0, 10, linha[0], ln=True)

    # Adicionar imagem, se fornecida
    if uploaded_image is not None:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Imagem Inserida pelo Usuário", ln=True)
        image = Image.open(uploaded_image)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        pdf.image(img_byte_arr, x=10, y=30, w=100)

    return pdf

# Interface do Streamlit
st.title("Relatório de Cálculo de Ações do Vento")
st.markdown("Preencha os dados abaixo para gerar o relatório.")

# Formulário para preenchimento dos dados da edificação
st.subheader("Dados da Edificação")
dados_edificacao = {}

dados_edificacao["Tipo de Cobertura"] = st.text_input("Tipo de Cobertura", value="Duas Águas")
dados_edificacao["Comprimento (a)"] = st.text_input("Comprimento (a)", value="48,00 m")
dados_edificacao["Largura (b)"] = st.text_input("Largura (b)", value="16,00 m")
dados_edificacao["Pé-Direito (h)"] = st.text_input("Pé-Direito (h)", value="10,90 m")
dados_edificacao["Inclinação da Cobertura"] = st.text_input("Inclinação da Cobertura", value="10,00 % (5,71°)")
dados_edificacao["Altura Média - Fechamento (z)"] = st.text_input("Altura Média - Fechamento (z)", value="13,00 m")
dados_edificacao["Altura Média - Cobertura (z)"] = st.text_input("Altura Média - Cobertura (z)", value="13,80 m")
dados_edificacao["Distância Entre Pórticos"] = st.text_input("Distância Entre Pórticos", value="5,00 m")
dados_edificacao["Velocidade Básica do Vento (V0)"] = st.text_input("Velocidade Básica do Vento (V0)", value="42,00 m/s")
dados_edificacao["Categoria de Rugosidade"] = st.text_input("Categoria de Rugosidade", value="I - I: Mar ou costa com poucos obstáculos")
dados_edificacao["Classe"] = st.text_input("Classe", value="A")
dados_edificacao["Fator Topográfico (S1)"] = st.text_input("Fator Topográfico (S1)", value="1,00")
dados_edificacao["Fator Estatístico (S3)"] = st.text_input("Fator Estatístico (S3)", value="1,11 (Tp: 100 anos)")

# Upload de Imagem
uploaded_image = st.file_uploader("Insira uma imagem para incluir no relatório (opcional):", type=["jpg", "jpeg", "png"])

# Botão para gerar o relatório
if st.button("Gerar Relatório"):
    # Exibir o relatório na interface
    st.markdown("## Relatório Gerado")

    # Capa
    st.markdown("""
    # Relatório de Cálculo de Ações do Vento
    **Conforme ABNT NBR 6123:2023**

    | **Cliente** | Construtora ABC |
    | **Obra** | Edifício Residencial |
    | **Localização** | São Paulo, SP |
    | **Cód. do Projeto** | 2025-001 |
    | **Número do Documento** | REL-001-2025 |
    | **Revisão** | 0 |
    | **Data** | 29/04/2025 |
    | **Cálculo** | João Silva |
    | **Aprovação** | [A Definir] |
    | **Empresa** | xAI Engenharia Ltda. |
    | **Contato** | contato@xaiengenharia.com |
    """)

    # Sumário
    st.markdown("""
    ## Sumário

    | Seção | Título | Página |
    |-------|--------|--------|
    | 1     | Dados da Edificação | 2 |
    | 2     | Fator de Rajada (Fr) | 3 |
    | 3     | Parâmetros Meteorológicos | 3 |
    | 4     | Valores Mínimos do Fator Estatístico S3 | 4 |
    | 5     | Cálculo do Fator S2 por Altura | 4 |
    | 6     | Velocidades e Pressões Características | 5 |
    | 7     | Parâmetros para Determinação do Fator S2 | 5 |
    | 8     | Pressões de Vento na Direção X1 | 6 |
    | 9     | Pressões de Vento na Direção X2 | 6 |
    | 10    | Fator S2 Calculado | 7 |
    | 11    | Velocidade Característica (Vk) | 7 |
    | 12    | Pressão Dinâmica do Vento (q) | 7 |
    | 13    | Coeficientes de Pressão Externa (Ce) | 8 |
    | 14    | Zonas de Pressão Externa | 9 |
    | 15    | Coeficientes de Pressão Externa (Ce) Selecionados | 9 |
    | 16    | Coeficiente de Pressão Interno (Cpi) | 10 |
    | 17    | Pressão Efetiva (DP) | 10 |
    | 18    | Observações | 12 |
    | 19    | Legenda de Siglas | 12 |
    """)

    # Metodologia de Cálculo (Fórmulas)
    st.markdown("""
    ## Metodologia de Cálculo
    **Velocidade Característica do Vento (Vk):**  
    \[
    Vk = V0 \cdot S1 \cdot S2 \cdot S3
    \]

    **Fator S2:**  
    \[
    S2 = bm \cdot \left(\frac{z}{10}\right)^p \cdot Fr
    \]

    **Pressão Dinâmica do Vento (q):**  
    \[
    q = 0,613 \cdot Vk^2 \quad (\text{N/m}^2)
    \]
    \[
    q = \frac{0,613 \cdot Vk^2}{9,81} \quad (\text{kgf/m}^2)
    \]

    **Pressão Efetiva (DP):**  
    \[
    DP = (Ce - Cpi) \cdot q
    \]
    """)

    # Seção 1: Dados da Edificação
    st.markdown("## 1. Dados da Edificação")
    data_edificacao = {
        "Parâmetro": dados_edificacao.keys(),
        "Valor": dados_edificacao.values()
    }
    st.table(data_edificacao)

    # Seção 2: Fator de Rajada (Fr)
    st.markdown("## 2. Fator de Rajada (Fr)")
    data_fr = {
        "Fr": ["", "1,00", "0,98", "0,95"],
        "Classes": ["", "A", "B", "C"]
    }
    st.table(data_fr)

    # Seção 3: Parâmetros Meteorológicos
    st.markdown("## 3. Parâmetros Meteorológicos")
    data_meteorologicos = {
        "Categoria": ["I", "", "II", "", "III", "", "IV", "", "V", ""],
        "Zg (m)": ["250", "", "300", "", "350", "", "420", "", "500", ""],
        "Parâmetro": ["bm", "p", "bm", "p", "bm", "p", "bm", "p", "bm", "p"],
        "A": ["1,10", "0,06", "1,00", "0,085", "0,94", "0,10", "0,86", "0,12", "0,74", "0,15"],
        "B": ["1,11", "0,065", "1,00", "0,09", "0,94", "0,105", "0,85", "0,125", "0,73", "0,16"],
        "C": ["1,12", "0,07", "1,00", "0,10", "0,93", "0,115", "0,84", "0,135", "0,71", "0,175"]
    }
    st.table(data_meteorologicos)

    # Seção 4: Valores Mínimos do Fator Estatístico S3
    st.markdown("## 4. Valores Mínimos do Fator Estatístico S3")
    data_s3 = {
        "Grupo": ["1", "2", "3", "4", "5"],
        "Descrição": [
            "Estruturas cuja ruína total ou parcial pode afetar a segurança ou possibilidade de socorro a pessoas após uma tempestade destrutiva (hospitais, quartéis de bombeiros e de forças de segurança, edifícios de centros de controle, torres de comunicação etc.). Obras de infraestrutura crítica. Armazenamento de substâncias perigosas e/ou tóxicas e/ou explosivas. Vedações das edificações do grupo 1 (telhas, vidros, painéis de vedação).",
            "Estruturas cuja ruína representa substancial risco à vida humana, particularmente pessoas em aglomerações, crianças e jovens, incluindo, mas não limitadamente a: edificações com capacidade de aglomeração de mais de 300 pessoas em um mesmo ambiente, como centros de convenções, ginásios, estádios etc.; creches com capacidade maior do que 150 pessoas; escolas com capacidade maior do que 250 pessoas. Vedações das edificações do grupo 2 (telhas, vidros, painéis de vedação).",
            "Edificações para residências, hotéis, comércio, indústrias. Estruturas ou elementos estruturais desmontáveis com vistas a reutilização. Vedações das edificações do grupo 3 (telhas, vidros, painéis de vedação).",
            "Edificações não destinadas à ocupação humana (depósitos, silos) e sem circulação de pessoas no entorno. Vedações das edificações do grupo 4 (telhas, vidros, painéis de vedação).",
            "Edificações temporárias não reutilizáveis. Estruturas dos Grupos 1 a 4 durante a construção (fator aplicável em um prazo máximo de 2 anos). Vedações das edificações do grupo 5 (telhas, vidros, painéis de vedação).",
        ],
        "S3": ["1,11", "1,06", "1,00", "0,95", "0,83"],
        "Tp (anos)": ["100", "75", "50", "37", "15"]
    }
    st.table(data_s3)

    # Seção 5: Cálculo do Fator S2 por Altura
    st.markdown("## 5. Cálculo do Fator S2 por Altura")
    data_s2_altura = {
        "z (m)": ["0,0", "5,0", "10,0", "15,0", "20,0", "25,0", "30,0", "35,0", "40,0", "45,0", "50,0", "55,0", "60,0", "65,0", "70,0", "75,0"],
        "S2": ["0,000000", "1,055191", "1,100000", "1,127089", "1,146712", "1,162168", "1,174952", "1,185869", "1,195408", "1,203886", "1,211521", "1,218469", "1,224847", "1,230743", "1,236228", "1,241356"]
    }
    st.table(data_s2_altura)

    # Seção 6: Velocidades e Pressões Características
    st.markdown("## 6. Velocidades e Pressões Características")
    data_velocidades = {
        "z (m)": ["0,0", "5,0", "10,0", "15,0", "20,0", "25,0", "30,0", "35,0", "40,0", "45,0", "50,0", "55,0", "60,0", "65,0", "70,0", "75,0"],
        "S1": ["1,00"] * 16,
        "S2": ["0,00", "1,06", "1,10", "1,13", "1,15", "1,16", "1,17", "1,19", "1,20", "1,20", "1,21", "1,22", "1,22", "1,23", "1,24", "1,24"],
        "S3": ["1,11"] * 16,
        "Vk (m/s)": ["0,00", "49,19", "51,28", "52,54", "53,46", "54,18", "54,78", "55,29", "55,73", "56,13", "56,48", "56,81", "57,10", "57,38", "57,63", "57,87"],
        "q (kN/m²)": ["0,000", "1,482", "1,611", "1,691", "1,750", "1,798", "1,838", "1,872", "1,902", "1,929", "1,954", "1,976", "1,997", "2,016", "2,034", "2,051"]
    }
    st.table(data_velocidades)

    # Gráfico de Velocidade x Altura
    df_velocidade = pd.DataFrame({
        "Altura (z) [m]": [float(z.replace(",", ".")) for z in data_velocidades["z (m)"]],
        "Velocidade Vk (m/s)": [float(vk.replace(",", ".")) for vk in data_velocidades["Vk (m/s)"]]
    })
    fig = px.line(df_velocidade, x="Altura (z) [m]", y="Velocidade Vk (m/s)", title="Velocidade Característica (Vk) em Função da Altura (z)")
    st.plotly_chart(fig)

    # Seção 7: Parâmetros para Determinação do Fator S2
    st.markdown("## 7. Parâmetros para Determinação do Fator S2")
    data_params_s2 = {
        "Direção do Vento": ["X1", "X2"],
        "Fator de Rajada (Fr)": ["0,95", "0,95"],
        "Coeficiente bm": ["0,93", "0,93"],
        "Coeficiente p": ["0,10", "0,10"]
    }
    st.table(data_params_s2)

    # Seção 8: Pressões de Vento na Direção X1
    st.markdown("## 8. Pressões de Vento na Direção X1")
    data_pressoes_x1 = {
        "Altura z (m)": ["5,0", "10,0", "15,0", "20,0", "25,0"],
        "Fator S2": ["1,06", "1,10", "1,13", "1,15", "1,16"],
        "S1": ["1,00"] * 5,
        "S3": ["1,11"] * 5,
        "Velocidade Vk (m/s)": ["49,19", "51,28", "52,54", "53,46", "54,18"],
        "Pressão q (kN/m²)": ["1,482", "1,611", "1,691", "1,750", "1,798"]
    }
    st.table(data_pressoes_x1)

    # Seção 9: Pressões de Vento na Direção X2
    st.markdown("## 9. Pressões de Vento na Direção X2")
    data_pressoes_x2 = {
        "Altura z (m)": ["5,0", "10,0", "15,0", "20,0", "25,0"],
        "Fator S2": ["1,06", "1,10", "1,13", "1,15", "1,16"],
        "S1": ["1,00"] * 5,
        "S3": ["1,11"] * 5,
        "Velocidade Vk (m/s)": ["49,19", "51,28", "52,54", "53,46", "54,18"],
        "Pressão q (kN/m²)": ["1,482", "1,611", "1,691", "1,750", "1,798"]
    }
    st.table(data_pressoes_x2)

    # Seção 10: Fator S2 Calculado
    st.markdown("## 10. Fator S2 Calculado")
    data_s2_calculado = {
        "Parâmetro": ["Altura z (m)", "bm", "p", "Fr", "S2"],
        "Fechamento": ["13,00", "1,10", "0,060", "1,00", "1,117453"],
        "Cobertura": ["13,80", "1,10", "0,060", "1,00", "1,121464"]
    }
    st.table(data_s2_calculado)

    # Seção 11: Velocidade Característica (Vk)
    st.markdown("## 11. Velocidade Característica (Vk)")
    data_vk = {
        "": ["Vk (m/s)"],
        "Fechamento": ["52,10"],
        "Cobertura": ["52,28"]
    }
    st.table(data_vk)

    # Seção 12: Pressão Dinâmica do Vento (q)
    st.markdown("## 12. Pressão Dinâmica do Vento (q)")
    data_q = {
        "": ["q (N/m²)", "q (kgf/m²)"],
        "Fechamento": ["1662,30", "169,51"],
        "Cobertura": ["1674,25", "170,73"]
    }
    st.table(data_q)

    # Seção 13: Coeficientes de Pressão Externa (Ce)
    st.markdown("## 13. Coeficientes de Pressão Externa (Ce)")
    data_ce = {
        "θ (°)": ["5", "10", "15", "20 Bump", "", "30", "", "θ (°)", "5", "10", "15", "20", "25", "30"],
        "90° HeI": ["-1,0", "-1,0", "-0,9", "-0,8", "-0,7", "-0,5", "", "", "", "", "", "", "", ""],
        "90° LeJ": ["-0,5", "-0,5", "-0,5", "", "-0,5", "-0,5", "", "", "", "", "", "", "", ""],
        "45° H": ["-1,0", "-1,0", "-1,0", "", "-1,0", "-1,0", "", "", "", "", "", "", "", ""],
        "45° L": ["-0,9", "-0,8", "-0,7", "", "-0,6", "-0,6", "", "", "", "", "", "", "", ""],
        "0° HeLa": ["-1,0", "-1,0", "-1,0", "-0,5", "-0,8", "-0,8", "", "", "", "", "", "", "", ""],
        "0° HeLa_2": ["-0,5", "-0,5", "-0,5", "-0,5", "-0,5", "-0,5", "", "", "", "", "", "", "", ""],
        "-45° H": ["-0,9", "-0,8", "-0,6", "-0,5", "-0,3", "-0,1", "", "", "", "", "", "", "", ""],
        "-45° L": ["-1,0", "-1,0", "-1,0", "-1,0", "-0,9", "-0,8", "", "", "", "", "", "", "", ""],
        "-90° HeI": ["-0,5", "-0,4", "-0,3", "-0,2", "-0,1", "0,0", "", "", "", "", "", "", "", ""],
        "-90° LeJ": ["-1,0", "-1,0", "-1,0", "-1,0", "-0,9", "-0,6", "", "", "", "", "", "", "", ""],
        "Ce médio H1": ["", "", "", "", "", "", "", "-2,0", "-2,0", "-1,8", "-1,8", "-1,8", "-1,8"],
        "Ce médio H2": ["", "", "", "", "", "", "", "-1,5", "-1,5", "-0,9", "-0,8", "-0,7", "-0,5"],
        "Ce médio L1": ["", "", "", "", "", "", "", "-2,0", "-2,0", "-1,8", "-1,8", "-0,9", "-0,5"],
        "Ce médio L2": ["", "", "", "", "", "", "", "-1,5", "-1,5", "-1,4", "-1,4", "-0,9", "-0,5"],
        "Ce médio H6": ["", "", "", "", "", "", "", "-2,0", "-2,0", "-2,0", "-2,0", "-2,0", "-2,0"]
    }
    st.table(data_ce)

    # Seção 14: Zonas de Pressão Externa
    st.markdown("## 14. Zonas de Pressão Externa")
    st.markdown("H: Alta sucção (b/2 a partir da borda de barlavento); L: Baixa sucção (de b/2 até a/2); I, J: Zonas laterais.")

    # Seção 15: Coeficientes de Pressão Externa (Ce) Selecionados
    st.markdown("## 15. Coeficientes de Pressão Externa (Ce) Selecionados")
    data_ce_selecionados = {
        "Direção do Vento": ["0°/180° (Longitudinal)", "90°/270° (Transversal)"],
        "Fechamento": ["-0,90,-0,46,-0,28,-0,42,0,70", "-0,90,-0,50,-0,54"],
        "Cobertura": ["-0,90,-0,60,-0,33,0,70", "-0,93,-0,60,-0,54"]
    }
    st.table(data_ce_selecionados)

    # Seção 16: Coeficiente de Pressão Interno (Cpi)
    st.markdown("## 16. Coeficiente de Pressão Interno (Cpi)")
    st.markdown("Caso Selecionado (NBR 6123:2023 - Item 6.3.2.1): a  \nDescrição: a) Duas faces opostas igualmente permeáveis; as outras faces impermeáveis  \nCpi: 0,20, -0,30")

    # Seção 17: Pressão Efetiva (DP)
    st.markdown("## 17. Pressão Efetiva (DP)")
    st.markdown("### 17.1. Vento a 0°/180° - Fechamento")
    data_dp_1 = {
        "Ce": ["-0,90", "-0,90", "-0,46", "-0,46", "-0,28", "-0,28", "-0,42", "-0,42", "0,70", "0,70"],
        "Cpi": ["0,20", "-0,30", "0,20", "-0,30", "0,20", "-0,30", "0,20", "-0,30", "0,20", "-0,30"],
        "DP (kgf/m²)": ["-186,46", "-101,70", "-112,30", "-27,54", "-81,70", "3,05", "-105,94", "-21,19", "84,75", "169,51"]
    }
    st.table(data_dp_1)

    st.markdown("### 17.2. Vento a 0°/180° - Cobertura")
    data_dp_2 = {
        "Ce": ["-0,90", "-0,90", "-0,60", "-0,60", "-0,33", "-0,33", "0,70", "0,70"],
        "Cpi": ["0,20", "-0,30", "0,20", "-0,30", "0,20", "-0,30", "0,20", "-0,30"],
        "DP (kgf/m²)": ["-187,80", "-102,44", "-136,58", "-51,22", "-89,63", "-4,27", "85,36", "170,73"]
    }
    st.table(data_dp_2)

    st.markdown("### 17.3. Vento a 90°/270° - Fechamento")
    data_dp_3 = {
        "Ce": ["-0,90", "-0,90", "-0,50", "-0,50", "-0,54", "-0,54"],
        "Cpi": ["0,20", "-0,30", "0,20", "-0,30", "0,20", "-0,30"],
        "DP (kgf/m²)": ["-186,46", "-101,70", "-118,66", "-33,90", "-125,01", "-40,26"]
    }
    st.table(data_dp_3)

    st.markdown("### 17.4. Vento a 90°/270° - Cobertura")
    data_dp_4 = {
        "Ce": ["-0,93", "-0,93", "-0,60", "-0,60", "-0,54", "-0,54"],
        "Cpi": ["0,20", "-0,30", "0,20", "-0,30", "0,20", "-0,30"],
        "DP (kgf/m²)": ["-192,65", "-107,28", "-136,58", "-51,22", "-125,91", "-40,55"]
    }
    st.table(data_dp_4)

    # Seção 18: Observações
    st.markdown("## 18. Observações")
    st.markdown("Os valores de DP são aplicáveis ao dimensionamento do sistema de vedação (fechamento e cobertura). Verificar a combinação mais crítica para cada elemento.  \nCálculos realizados conforme ABNT NBR 6123:2023.")

    # Seção 19: Legenda de Siglas
    st.markdown("## 19. Legenda de Siglas")
    data_legendas = {
        "Sigla": ["z", "V0", "Vk", "q", "Ce", "Cpi", "S1", "S2", "S3", "Fr", "bm", "p", "DP"],
        "Descrição": [
            "Altura acima do terreno (m)",
            "Velocidade básica do vento (m/s)",
            "Velocidade característica do vento (m/s)",
            "Pressão dinâmica do vento (kN/m² ou kgf/m²)",
            "Coeficiente de forma externo",
            "Coeficiente de pressão interna",
            "Fator topográfico",
            "Fator de rugosidade e dimensões da edificação",
            "Fator estatístico",
            "Fator de rajada",
            "Fator meteorológico (NBR 6123:2023)",
            "Expoente meteorológico (NBR 6123:2023)",
            "Pressão efetiva (kgf/m²)"
        ]
    }
    st.table(data_legendas)

    # Exibir imagem, se fornecida
    if uploaded_image is not None:
        st.markdown("## Imagem Inserida pelo Usuário")
        st.image(uploaded_image, caption="Imagem Inserida pelo Usuário", use_column_width=True)

    # Gerar e disponibilizar o PDF
    pdf = generate_pdf(dados_edificacao, uploaded_image)
    pdf_output = pdf.output(dest="S").encode("latin1")
    st.download_button("Baixar Relatório em PDF", pdf_output, file_name="relatorio_vento.pdf")
