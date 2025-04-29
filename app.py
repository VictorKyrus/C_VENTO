import streamlit as st
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO

# Função para calcular S2
def calculate_s2(z, bm, p, fr):
    return bm * fr * (z / 10) ** p

# Função para calcular Vk
def calculate_vk(v0, s1, s2, s3):
    return v0 * s1 * s2 * s3

# Função para calcular q
def calculate_q(vk, rho=1.225):
    q_nm2 = 0.5 * rho * vk ** 2  # N/m²
    q_kgfm2 = q_nm2 / 9.80665  # kgf/m²
    return q_nm2, q_kgfm2

# Função para calcular DP
def calculate_dp(ce, cpi, q):
    return (ce - cpi) * q

# Função para gerar o relatório PDF
def generate_pdf(data, results, project_info):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Estilo personalizado
    title_style = ParagraphStyle(name='Title', fontSize=14, leading=16, alignment=1, spaceAfter=12)
    heading_style = ParagraphStyle(name='Heading', fontSize=12, leading=14, spaceAfter=10)
    body_style = ParagraphStyle(name='Body', fontSize=10, leading=12)

    # Cabeçalho
    story.append(Paragraph("Relatório de Cálculo de Ações do Vento (NBR 6123:2023)", title_style))
    story.append(Spacer(1, 0.5*cm))
    project_data = [
        ["Cliente", project_info.get("client", "[A Definir]")],
        ["Obra", project_info.get("project", "[A Definir]")],
        ["Localização", project_info.get("location", "[A Definir]")],
        ["Data", "29/04/2025"],
        ["Cálculo", project_info.get("calculator", "[Seu Nome]")],
        ["Aprovação", "[A Definir]"],
        ["Revisão", "0"]
    ]
    project_table = Table(project_data, colWidths=[5*cm, 12*cm])
    project_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(project_table)
    story.append(Spacer(1, 1*cm))

    # Seção 1: Dados da Edificação
    story.append(Paragraph("1. Dados da Edificação", heading_style))
    building_data = [
        ["Comprimento (a)", f"{data['length']:.2f} m"],
        ["Largura (b)", f"{data['width']:.2f} m"],
        ["Pé-Direito (h)", f"{data['height']:.2f} m"],
        ["Inclinação da Cobertura", f"{data['slope']:.2f}% ({np.arctan(data['slope']/100)*180/np.pi:.2f}°)"],
        ["Altura Média - Fechamento (Z)", f"{data['z_fechamento']:.2f} m"],
        ["Altura Média - Cobertura (Z)", f"{data['z_cobertura']:.2f} m"],
        ["Distância Entre Pórticos", f"{data['portico_distance']:.2f} m"],
        ["Velocidade Básica do Vento (V0)", f"{data['v0']:.2f} m/s"],
        ["Categoria de Rugosidade", f"{data['category']} - {data['category_description']}"],
        ["Classe", data['class']],
        ["Fator Topográfico (S1)", f"{data['s1']:.2f}"],
        ["Fator Estatístico (S3)", f"{data['s3']:.2f}"]
    ]
    building_table = Table(building_data, colWidths=[8*cm, 9*cm])
    building_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(building_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 2: Tabela 1 - Fator de Rajada (Fr)
    story.append(Paragraph("2. Fator de Rajada (Fr) - Tabela 1 (NBR 6123:2023)", heading_style))
    fr_table_data = [
        ["Fr", "Classes"],
        ["", "A", "B", "C"],
        ["", "1", "0.98", "0.95"]
    ]
    fr_table = Table(fr_table_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    fr_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,0), (0,1)),
        ('BACKGROUND', (0,0), (-1,1), colors.lightgrey)
    ]))
    story.append(fr_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 3: Tabela 2 - Parâmetros Meteorológicos
    story.append(Paragraph("3. Parâmetros Meteorológicos - Tabela 2 (NBR 6123:2023)", heading_style))
    meteo_table_data = [
        ["Categoria", "Zg (m)", "Parâmetro", "Classes"],
        ["", "", "", "A", "B", "C"],
        ["I", "250", "bm", "1.10", "1.11", "1.12"],
        ["", "", "p", "0.06", "0.065", "0.07"],
        ["II", "300", "bm", "1.00", "1.00", "1.00"],
        ["", "", "p", "0.085", "0.09", "0.10"],
        ["III", "350", "bm", "0.94", "0.94", "0.93"],
        ["", "", "p", "0.10", "0.105", "0.115"],
        ["IV", "420", "bm", "0.86", "0.85", "0.84"],
        ["", "", "p", "0.12", "0.125", "0.135"],
        ["V", "500", "bm", "0.74", "0.73", "0.71"],
        ["", "", "p", "0.15", "0.16", "0.175"]
    ]
    meteo_table = Table(meteo_table_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    meteo_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,0), (0,1)),
        ('SPAN', (1,0), (1,1)),
        ('SPAN', (2,0), (2,1)),
        ('SPAN', (0,2), (0,3)),
        ('SPAN', (0,4), (0,5)),
        ('SPAN', (0,6), (0,7)),
        ('SPAN', (0,8), (0,9)),
        ('SPAN', (0,10), (0,11)),
        ('BACKGROUND', (0,0), (-1,1), colors.lightgrey)
    ]))
    story.append(meteo_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 4: Cálculo do Fator S2 por Altura
    story.append(Paragraph("4. Cálculo do Fator S2 por Altura", heading_style))
    s2_table_data = [["z (m)", "S2"]]
    for z, s2 in results['s2_by_height'].items():
        s2_table_data.append([f"{z:.1f}", f"{s2:.6f}"])
    s2_table = Table(s2_table_data, colWidths=[4*cm, 13*cm])
    s2_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(s2_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 5: Tabela 3 - Velocidades e Pressões Características
    story.append(Paragraph("5. Velocidades e Pressões Características - Tabela 3 (NBR 6123:2023)", heading_style))
    vk_q_table_data = [
        ["z (m)", "S1", "S2", "S3", "Vk (m/s)", "q (kN/m²)"],
        ["0", "1", "0.92", "", "38.64", "0.915"],
        ["5", "1", "0.92", "", "38.64", "0.915"],
        ["10", "1", "0.98", "", "41.16", "1.039"],
        ["15", "1", "1.02", "", "42.84", "1.125"],
        ["20", "1", "1.04", "", "43.68", "1.17"],
        ["25", "1", "1.06", "", "44.52", "1.215"],
        ["30", "1", "1.08", "", "45.36", "1.261"],
        ["35", "1", "1.1", "", "46.20", "1.308"],
        ["40", "1", "1.11", "", "46.62", "1.332"],
        ["45", "1", "1.12", "", "47.04", "1.356"],
        ["50", "1", "1.13", "", "47.46", "1.381"],
        ["55", "1", "1.14", "", "47.88", "1.405"],
        ["60", "1", "1.15", "", "48.30", "1.43"],
        ["65", "1", "1.16", "", "48.72", "1.455"],
        ["70", "1", "1.17", "", "49.14", "1.48"],
        ["75", "1", "1.17", "", "49.14", "1.48"]
    ]
    vk_q_table = Table(vk_q_table_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    vk_q_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(vk_q_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 6: Tabela 4 - Parâmetros para S2
    story.append(Paragraph("6. Parâmetros para Determinação do Fator S2 - Tabela 4 (NBR 6123:2023)", heading_style))
    s2_params_table_data = [
        ["Direção do Vento", "Fator de Rajada (Fr)", "Coeficiente bm", "Coeficiente p"],
        ["X1", "0.95", "0.93", "0.10"],
        ["X2", "0.95", "0.93", "0.10"]
    ]
    s2_params_table = Table(s2_params_table_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    s2_params_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(s2_params_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 7: Tabela 5 - Pressões na Direção X1
    story.append(Paragraph("7. Pressões de Vento na Direção X1 - Tabela 5 (NBR 6123:2023)", heading_style))
    x1_table_data = [
        ["Altura z (m)", "Velocidade V0 (m/s)", "Fator S1", "Fator S2", "Fator S3", "Velocidade Vk (m/s)", "Pressão q (kN/m²)"],
        ["5", "42", "", "0.82", "", "34.44", "0.727"],
        ["10", "42", "", "0.88", "", "36.96", "0.837"],
        ["15", "42", "", "0.92", "", "38.64", "0.915"],
        ["20", "42", "", "0.95", "", "39.9", "0.976"],
        ["25", "42", "", "0.97", "", "40.74", "1.017"]
    ]
    x1_table = Table(x1_table_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    x1_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(x1_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 8: Tabela 6 - Pressões na Direção X2
    story.append(Paragraph("8. Pressões de Vento na Direção X2 - Tabela 6 (NBR 6123:2023)", heading_style))
    x2_table_data = [
        ["Altura z (m)", "Velocidade V0 (m/s)", "Fator S1", "Fator S2", "Fator S3", "Velocidade Vk (m/s)", "Pressão q (kN/m²)"],
        ["5", "42", "", "0.82", "", "34.44", "0.727"],
        ["10", "42", "", "0.88", "", "36.96", "0.837"],
        ["15", "42", "", "0.92", "", "38.64", "0.915"],
        ["20", "42", "", "0.95", "", "39.9", "0.976"],
        ["25", "42", "", "0.97", "", "40.74", "1.017"]
    ]
    x2_table = Table(x2_table_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    x2_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(x2_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 9: Fator S2 Calculado
    story.append(Paragraph("9. Fator S2 Calculado", heading_style))
    s2_data = [
        ["Parâmetro", "Fechamento", "Cobertura"],
        ["Altura (z)", f"{data['z_fechamento']:.2f} m", f"{data['z_cobertura']:.2f} m"],
        ["bm", f"{data['bm']:.2f}", f"{data['bm']:.2f}"],
        ["p", f"{data['p']:.3f}", f"{data['p']:.3f}"],
        ["Fr", f"{data['fr']:.2f}", f"{data['fr']:.2f}"],
        ["S2", f"{results['s2_fechamento']:.6f}", f"{results['s2_cobertura']:.6f}"]
    ]
    s2_table = Table(s2_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    s2_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(s2_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 10: Velocidade Característica (Vk)
    story.append(Paragraph("10. Velocidade Característica (Vk)", heading_style))
    vk_data = [
        ["", "Fechamento", "Cobertura"],
        ["Vk", f"{results['vk_fechamento']:.2f} m/s", f"{results['vk_cobertura']:.2f} m/s"]
    ]
    vk_table = Table(vk_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    vk_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(vk_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 11: Pressão Dinâmica (q)
    story.append(Paragraph("11. Pressão Dinâmica do Vento (q)", heading_style))
    q_data = [
        ["", "Fechamento", "Cobertura"],
        ["q (N/m²)", f"{results['q_fechamento_nm2']:.2f}", f"{results['q_cobertura_nm2']:.2f}"],
        ["q (kgf/m²)", f"{results['q_fechamento_kgfm2']:.2f}", f"{results['q_cobertura_kgfm2']:.2f}"]
    ]
    q_table = Table(q_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    q_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(q_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 12: Coeficientes de Pressão Externo (Ce) - Tabela 7
    story.append(Paragraph("12. Coeficientes de Pressão Externa (Ce) - Tabela 7 (NBR 6123:2023)", heading_style))
    ce_table_data = [
        ["θ", "Valores de Ce para ângulo de incidência do vento α"],
        ["", "90°", "", "45°", "", "0°", "", "-45°", "", "-90°", ""],
        ["", "H e I", "L e J", "H", "L", "H e Lᵃ", "H e Lᵇ", "H", "L", "H e I", "L e J"],
        ["5°", "-1.0", "-0.5", "-1.0", "-0.9", "-1.0", "-0.5", "-0.9", "-1.0", "-0.5", "-1.0"],
        ["10°", "-1.0", "-0.5", "-1.0", "-0.8", "-1.0", "-0.5", "-0.8", "-1.0", "-0.4", "-1.0"],
        ["15°", "-0.9", "-0.5", "-1.0", "-0.7", "-1.0", "-0.5", "-0.6", "-1.0", "-0.3", "-1.0"],
        ["20°", "-0.8", "-0.5", "-1.0", "-0.6", "-0.9", "-0.5", "-0.5", "-1.0", "-0.2", "-1.0"],
        ["25°", "-0.7", "-0.5", "-1.0", "-0.6", "-0.8", "-0.5", "-0.3", "-0.9", "-0.1", "-0.9"],
        ["30°", "-0.5", "-0.5", "-1.0", "-0.6", "-0.8", "-0.5", "-0.1", "-0.8", "0", "-0.6"],
        ["θ", "Ce médio"],
        ["", "H₁", "H₂", "L₁", "L₂", "H₆"],
        ["5°", "-2.0", "-1.5", "-2.0", "-1.5", "-2.0"],
        ["10°", "-2.0", "-1.5", "-2.0", "-1.5", "-2.0"],
        ["15°", "-1.8", "-0.9", "-1.8", "-1.4", "-2.0"],
        ["20°", "-1.8", "-0.8", "-1.8", "-1.4", "-2.0"],
        ["25°", "-1.8", "-0.7", "-0.9", "-0.9", "-2.0"],
        ["30°", "-1.8", "-0.5", "-0.5", "-0.5", "-2.0"]
    ]
    ce_table = Table(ce_table_data, colWidths=[1.5*cm] + [1.5*cm]*10)
    ce_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,0), (0,1)),
        ('SPAN', (1,0), (10,0)),
        ('SPAN', (0,6), (0,7)),
        ('SPAN', (1,6), (5,6)),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('BACKGROUND', (0,1), (-1,1), colors.lightgrey),
        ('BACKGROUND', (0,6), (-1,6), colors.lightgrey)
    ]))
    story.append(ce_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 13: Desenho das Zonas de Pressão Externa (Figura 6 - NBR 6123:2023)
    story.append(Paragraph("13. Descrição das Zonas de Pressão Externa (Figura 6 - NBR 6123:2023)", heading_style))
    drawing_description = [
        "A cobertura de 1 água é dividida em zonas para aplicação dos coeficientes de pressão externa (Ce):",
        "- H: Zona de alta sucção no topo da cobertura (b/2 a partir da borda de barlavento).",
        "- L: Zona de baixa sucção no restante da cobertura (de b/2 até a/2).",
        "- I e J: Zonas laterais para ângulos de incidência específicos.",
        "Representação simplificada (vista em planta):",
        "  _________________________",
        " |        H        |       |",
        " |-----------------|   I   |",
        " |        L        |       |",
        " |_________________|_______|",
        "Nota: H e L variam com o ângulo de incidência do vento (α). I e J aplicáveis para quadrantes específicos."
    ]
    for line in drawing_description:
        story.append(Paragraph(line, body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 14: Coeficientes de Pressão Externa (Ce) Selecionados
    story.append(Paragraph("14. Coeficientes de Pressão Externa (Ce) Selecionados", heading_style))
    ce_selected_data = [
        ["Direção do Vento", "Fechamento", "Cobertura"],
        ["0º/180º (Longitudinal)", ", ".join(map(str, data['ce_fechamento_0'])), ", ".join(map(str, data['ce_cobertura_0']))],
        ["90º/270º (Transversal)", ", ".join(map(str, data['ce_fechamento_90'])), ", ".join(map(str, data['ce_cobertura_90']))]
    ]
    ce_selected_table = Table(ce_selected_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    ce_selected_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(ce_selected_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 15: Coeficiente de Pressão Interno (Cpi)
    story.append(Paragraph("15. Coeficiente de Pressão Interno (Cpi)", heading_style))
    story.append(Paragraph(f"Caso Selecionado (NBR 6123:2023 - Item 6.3.2.1): {data['cpi_case']}", body_style))
    story.append(Paragraph(f"Descrição: {data['cpi_case_description']}", body_style))
    story.append(Paragraph(f"Cpi = {', '.join(map(str, data['cpi']))}", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 16: Pressão Efetiva (DP)
    story.append(Paragraph("16. Pressão Efetiva (DP) = (Ce - Cpi) × q", heading_style))
    for direction, dp_data in results['dp'].items():
        story.append(Paragraph(f"Vento a {direction}", heading_style))
        dp_table_data = [["Ce", "Cpi", "DP (kgf/m²)"]]
        for ce, cpi, dp in dp_data:
            dp_table_data.append([f"{ce:.2f}", f"{cpi:.2f}", f"{dp:.2f}"])
        dp_table = Table(dp_table_data, colWidths=[4*cm, 4*cm, 9*cm])
        dp_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
        ]))
        story.append(dp_table)
        story.append(Spacer(1, 0.5*cm))

    # Seção 17: Observações
    story.append(Paragraph("17. Observações", heading_style))
    observations = [
        "Os valores de DP são aplicáveis ao dimensionamento do sistema de vedação (fechamento e cobertura).",
        "Verificar a combinação mais crítica para cada elemento.",
        "Cálculos realizados conforme ABNT NBR 6123:2023."
    ]
    for obs in observations:
        story.append(Paragraph(obs, body_style))
    story.append(Spacer(1, 0.5*cm))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Interface Streamlit
st.title("Cálculo de Ações do Vento (NBR 6123:2023)")

# Entradas do usuário
st.header("Dados da Edificação")
col1, col2 = st.columns(2)
with col1:
    length = st.number_input("Comprimento (m)", min_value=0.0, value=48.0)
    width = st.number_input("Largura (m)", min_value=0.0, value=16.0)
    height = st.number_input("Pé-Direito (m)", min_value=0.0, value=10.9)
with col2:
    slope = st.number_input("Inclinação da Cobertura (%)", min_value=0.0, value=10.0)
    z_fechamento = st.number_input("Altura Média - Fechamento (m)", min_value=0.0, value=13.0)
    z_cobertura = st.number_input("Altura Média - Cobertura (m)", min_value=0.0, value=13.8)
portico_distance = st.number_input("Distância Entre Pórticos (m)", min_value=0.0, value=5.0)
v0 = st.number_input("Velocidade Básica do Vento (V0) (m/s)", min_value=0.0, value=42.0)

st.header("Parâmetros Meteorológicos")
category_options = {
    "I": "I: Mar ou costa com poucos obstáculos",
    "II": "II: Terrenos abertos, em nível ou aproximadamente em nível, com poucos obstáculos isolados, tais como árvores e edificações baixas",
    "III": "III: Subúrbios ou áreas industriais com edificações de altura média",
    "IV": "IV: Centros urbanos com edificações altas e densas",
    "V": "V: Áreas com muitos obstáculos altos, como florestas densas ou centros urbanos muito desenvolvidos"
}
category = st.selectbox("Categoria de Rugosidade", list(category_options.keys()), format_func=lambda x: category_options[x])
category_description = category_options[category]
class_ = st.selectbox("Classe", ["A", "B", "C"], help="A: Dimensão frontal ≤ 20 m; B: 20 m < Dimensão ≤ 50 m; C: Dimensão > 50 m.")

# Dados meteorológicos baseados na norma
meteorological_data = {
    "I": {"Zg": 250, "A": {"bm": 1.10, "p": 0.06}, "B": {"bm": 1.11, "p": 0.065}, "C": {"bm": 1.12, "p": 0.07}},
    "II": {"Zg": 300, "A": {"bm": 1.00, "p": 0.085}, "B": {"bm": 1.00, "p": 0.09}, "C": {"bm": 1.00, "p": 0.10}},
    "III": {"Zg": 350, "A": {"bm": 0.94, "p": 0.10}, "B": {"bm": 0.94, "p": 0.105}, "C": {"bm": 0.93, "p": 0.115}},
    "IV": {"Zg": 420, "A": {"bm": 0.86, "p": 0.12}, "B": {"bm": 0.85, "p": 0.125}, "C": {"bm": 0.84, "p": 0.135}},
    "V": {"Zg": 500, "A": {"bm": 0.74, "p": 0.15}, "B": {"bm": 0.73, "p": 0.16}, "C": {"bm": 0.71, "p": 0.175}}
}
fr_data = {"A": 1.0, "B": 0.98, "C": 0.95}

bm = meteorological_data[category][class_]["bm"]
p = meteorological_data[category][class_]["p"]
fr = fr_data[class_]

st.header("Fatores S1, S2, S3")
s1 = st.selectbox("Fator Topográfico (S1)", [1.0, 0.9, 1.1], help="1.0: Terreno plano; 0.9: Depressão; 1.1: Elevação.")
s3 = st.selectbox("Fator Estatístico (S3)", [1.0, 1.11], help="1.0: Edificações residenciais/industriais (Tp=50 anos); 1.11: Estruturas com maior risco.")
st.write(f"Parâmetros S2: bm = {bm:.2f}, p = {p:.3f}, Fr = {fr:.2f}")

# Cálculo de S2 por altura (de 0 a 75 m, a cada 5 m)
s2_by_height = {}
for z in np.arange(0, 75.1, 5):
    s2_by_height[z] = calculate_s2(z, bm, p, fr)

# Exibir tabela de S2 por altura na interface
st.subheader("Fator S2 por Altura")
s2_df = pd.DataFrame(list(s2_by_height.items()), columns=["Altura z (m)", "S2"])
st.dataframe(s2_df)

st.header("Coeficientes de Pressão")
st.subheader("Coeficiente de Pressão Interno (Cpi) - NBR 6123:2023 Item 6.3.2.1")
cpi_cases = {
    "a": "a) Duas faces opostas igualmente permeáveis; as outras faces impermeáveis",
    "b": "b) Quatro faces igualmente permeáveis",
    "c": "c) Abertura dominante em uma face; as outras faces de igual permeabilidade"
}
cpi_case = st.radio("Selecione o caso para Cpi:", list(cpi_cases.keys()), format_func=lambda x: cpi_cases[x])
cpi_case_description = cpi_cases[cpi_case]

if cpi_case == "a":
    st.write("- Vento perpendicular a uma face permeável: Cpi = +0.2")
    st.write("- Vento perpendicular a uma face impermeável: Cpi = -0.3")
    cpi = st.multiselect("Selecione os valores de Cpi:", [0.2, -0.3], default=[0.2, -0.3])
elif cpi_case == "b":
    st.write("- Cpi = -0.3 ou 0 (considerar o valor mais nocivo)")
    cpi = st.multiselect("Selecione os valores de Cpi:", [-0.3, 0.0], default=[-0.3, 0.0])
else:  # cpi_case == "c"
    st.write("O valor de Cpi depende da proporção entre a área de aberturas na face de barlavento e a área total de aberturas:")
    st.write("- 1: Cpi = +0.1")
    st.write("- 1.5: Cpi = +0.3")
    st.write("- 2: Cpi = +0.5")
    st.write("- 3: Cpi = +0.6")
    st.write("- 6 ou mais: Cpi = +0.8")
    cpi = st.multiselect("Selecione os valores de Cpi:", [0.1, 0.3, 0.5, 0.6, 0.8], default=[0.1, 0.3])

st.subheader("Coeficientes de Pressão Externa (Ce)")
st.write("Zonas de Pressão Externa (Figura 6 - NBR 6123:2023):")
st.text("""
  _________________________
 |        H        |       |
 |-----------------|   I   |
 |        L        |       |
 |_________________|_______|
H: Alta sucção (b/2 a partir da borda de barlavento)
L: Baixa sucção (de b/2 até a/2)
I, J: Zonas laterais
""")
ce_fechamento_0 = st.multiselect("Ce - Fechamento (0º/180º)", [-0.9, -0.4625, -0.2820, -0.425, 0.7], default=[-0.9, -0.4625, -0.2820, -0.425, 0.7])
ce_fechamento_90 = st.multiselect("Ce - Fechamento (90º/270º)", [-0.9, -0.5, -0.5375], default=[-0.9, -0.5, -0.5375])
ce_cobertura_0 = st.multiselect("Ce - Cobertura (0º/180º)", [-0.9, -0.6, -0.325, 0.7], default=[-0.9, -0.6, -0.325, 0.7])
ce_cobertura_90 = st.multiselect("Ce - Cobertura (90º/270º)", [-0.9284, -0.6, -0.5375], default=[-0.9284, -0.6, -0.5375])

# Cálculos
s2_fechamento = calculate_s2(z_fechamento, bm, p, fr)
s2_cobertura = calculate_s2(z_cobertura, bm, p, fr)
vk_fechamento = calculate_vk(v0, s1, s2_fechamento, s3)
vk_cobertura = calculate_vk(v0, s1, s2_cobertura, s3)
q_fechamento_nm2, q_fechamento_kgfm2 = calculate_q(vk_fechamento)
q_cobertura_nm2, q_cobertura_kgfm2 = calculate_q(vk_cobertura)

# Pressões efetivas
dp_results = {
    "0º/180º - Fechamento": [],
    "0º/180º - Cobertura": [],
    "90º/270º - Fechamento": [],
    "90º/270º - Cobertura": []
}
for ce in ce_fechamento_0:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_fechamento_kgfm2)
        dp_results["0º/180º - Fechamento"].append((ce, cpi_val, dp))
for ce in ce_cobertura_0:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_cobertura_kgfm2)
        dp_results["0º/180º - Cobertura"].append((ce, cpi_val, dp))
for ce in ce_fechamento_90:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_fechamento_kgfm2)
        dp_results["90º/270º - Fechamento"].append((ce, cpi_val, dp))
for ce in ce_cobertura_90:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_cobertura_kgfm2)
        dp_results["90º/270º - Cobertura"].append((ce, cpi_val, dp))

# Resultados
results = {
    "s2_by_height": s2_by_height,
    "s2_fechamento": s2_fechamento,
    "s2_cobertura": s2_cobertura,
    "vk_fechamento": vk_fechamento,
    "vk_cobertura": vk_cobertura,
    "q_fechamento_nm2": q_fechamento_nm2,
    "q_fechamento_kgfm2": q_fechamento_kgfm2,
    "q_cobertura_nm2": q_cobertura_nm2,
    "q_cobertura_kgfm2": q_cobertura_kgfm2,
    "dp": dp_results
}

# Dados para o relatório
data = {
    "length": length,
    "width": width,
    "height": height,
    "slope": slope,
    "z_fechamento": z_fechamento,
    "z_cobertura": z_cobertura,
    "portico_distance": portico_distance,
    "v0": v0,
    "category": category,
    "category_description": category_description,
    "class": class_,
    "s1": s1,
    "s3": s3,
    "bm": bm,
    "p": p,
    "fr": fr,
    "cpi_case": cpi_case,
    "cpi_case_description": cpi_case_description,
    "cpi": cpi,
    "ce_fechamento_0": ce_fechamento_0,
    "ce_fechamento_90": ce_fechamento_90,
    "ce_cobertura_0": ce_cobertura_0,
    "ce_cobertura_90": ce_cobertura_90
}
project_info = {
    "client": st.text_input("Cliente", "[A Definir]"),
    "project": st.text_input("Obra", "[A Definir]"),
    "location": st.text_input("Localização", "[A Definir]"),
    "calculator": st.text_input("Cálculo", "[Seu Nome]")
}

# Exibir resultados
st.header("Resultados")
st.subheader("Fator S2 Calculado")
st.write(f"Fechamento: {s2_fechamento:.6f}")
st.write(f"Cobertura: {s2_cobertura:.6f}")
st.subheader("Velocidade Característica (Vk)")
st.write(f"Fechamento: {vk_fechamento:.2f} m/s")
st.write(f"Cobertura: {vk_cobertura:.2f} m/s")
st.subheader("Pressão Dinâmica (q)")
st.write(f"Fechamento: {q_fechamento_nm2:.2f} N/m² ({q_fechamento_kgfm2:.2f} kgf/m²)")
st.write(f"Cobertura: {q_cobertura_nm2:.2f} N/m² ({q_cobertura_kgfm2:.2f} kgf/m²)")
st.subheader("Pressão Efetiva (DP)")
for direction, dp_data in dp_results.items():
    st.write(f"{direction}")
    dp_df = pd.DataFrame(dp_data, columns=["Ce", "Cpi", "DP (kgf/m²)"])
    st.dataframe(dp_df)

# Botão para gerar e baixar o relatório
if st.button("Gerar Relatório PDF"):
    pdf_buffer = generate_pdf(data, results, project_info)
    st.download_button(
        label="Baixar Relatório PDF",
        data=pdf_buffer,
        file_name="relatorio_vento.pdf",
        mime="application/pdf"
    )
