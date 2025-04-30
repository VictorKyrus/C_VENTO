import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# Função para formatar números com vírgula (padrão brasileiro)
def format_with_comma(value):
    return f"{value:.2f}".replace(".", ",")

# Função para criar figura das zonas de pressão
def create_pressure_zones_image():
    fig, ax = plt.subplots(figsize=(8, 3), dpi=100)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    # Desenhar retângulo principal (planta da cobertura)
    ax.add_patch(plt.Rectangle((0, 0), 10, 4, fill=False, edgecolor='black', linewidth=1.5))
    # Linha divisória para zona H (b/2)
    ax.plot([5, 5], [0, 4], 'k--', linewidth=1, color='gray')
    # Linha divisória para zonas I/J
    ax.plot([8, 8], [0, 4], 'k--', linewidth=1, color='gray')
    # Rótulos das zonas com fundo branco e borda
    ax.text(2.5, 2, 'H', fontsize=14, ha='center', va='center', color='darkblue',
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax.text(6.5, 2, 'L', fontsize=14, ha='center', va='center', color='darkblue',
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax.text(9, 2, 'I/J', fontsize=14, ha='center', va='center', color='darkblue',
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel('Planta da Cobertura (Zonas de Pressão Externa)', fontsize=10, labelpad=10)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf

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

# Função para adicionar rodapé
def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    footer_text = "xAI Engenharia Ltda. | Relatório técnico – não substitui projeto executivo | Conforme NBR 6123:2023"
    canvas.drawCentredString(A4[0]/2, 1*cm, footer_text)
    canvas.drawString(A4[0] - 3*cm, 1*cm, f"Página {doc.page}")
    canvas.restoreState()

# Função para gerar o relatório PDF
def generate_pdf(data, results, project_info):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm, 
        topMargin=3*cm, 
        bottomMargin=2*cm,
        onLaterPages=add_footer
    )
    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(name='Title', fontName='Helvetica', fontSize=14, leading=16, alignment=1, spaceAfter=12, textTransform='uppercase', bold=True)
    heading_style = ParagraphStyle(name='Heading', fontName='Helvetica', fontSize=12, leading=14, spaceAfter=10, bold=True, textTransform='uppercase')
    body_style = ParagraphStyle(name='Body', fontName='Helvetica', fontSize=10, leading=12)
    table_title_style = ParagraphStyle(name='TableTitle', fontName='Helvetica', fontSize=9, leading=10, spaceAfter=6, bold=True)

    story = []

    # Sumário
    story.append(Paragraph("SUMÁRIO", heading_style))
    summary_data = [
        ["Seção", "Título", "Página"],
        ["1", "Dados da Edificação", "2"],
        ["2", "Fator de Rajada (Fr)", "3"],
        ["3", "Parâmetros Meteorológicos", "3"],
        ["4", "Valores Mínimos do Fator Estatístico S3", "4"],
        ["5", "Cálculo do Fator S2 por Altura", "4"],
        ["6", "Velocidades e Pressões Características", "5"],
        ["7", "Parâmetros para Determinação do Fator S2", "5"],
        ["8", "Pressões de Vento na Direção X1", "6"],
        ["9", "Pressões de Vento na Direção X2", "6"],
        ["10", "Fator S2 Calculado", "7"],
        ["11", "Velocidade Característica (Vk)", "7"],
        ["12", "Pressão Dinâmica do Vento (q)", "7"],
        ["13", "Coeficientes de Pressão Externa (Ce)", "8"],
        ["14", "Zonas de Pressão Externa", "9"],
        ["15", "Coeficientes de Pressão Externa (Ce) Selecionados", "9"],
        ["16", "Coeficiente de Pressão Interno (Cpi)", "10"],
        ["17", "Pressão Efetiva (DP)", "10"],
        ["18", "Observações", "12"],
        ["19", "Legenda de Siglas", "12"],
    ]
    summary_table = Table(summary_data, colWidths=[2*cm, 12*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 1*cm))
    story.append(PageBreak())

    # Página de Capa
    story.append(Paragraph("Relatório de Cálculo de Ações do Vento", title_style))
    story.append(Paragraph("Conforme ABNT NBR 6123:2023", body_style))
    story.append(Spacer(1, 2*cm))
    
    project_data = [
        ["Cliente", project_info.get("client", "[A Definir]")],
        ["Obra", project_info.get("project", "[A Definir]")],
        ["Localização", project_info.get("location", "[A Definir]")],
        ["Cód. do Projeto", "2025-001"],
        ["Número do Documento", "REL-001-2025"],
        ["Revisão", "0"],
        ["Data", "29/04/2025"],
        ["Cálculo", project_info.get("calculator", "[Seu Nome]")],
        ["Aprovação", "[A Definir]"],
        ["Empresa", "xAI Engenharia Ltda."],
        ["Contato", "contato@xaiengenharia.com"],
    ]
    project_table = Table(project_data, colWidths=[5*cm, 12*cm])
    project_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(project_table)
    story.append(Spacer(1, 10*cm))  # Espaço para rodapé
    story.append(PageBreak())

    # Seção 1: Dados da Edificação
    story.append(Paragraph("1. Dados da Edificação", heading_style))
    building_data = [
        ["Parâmetro", "Valor"],
        ["Tipo de Cobertura", data['roof_type']],
        ["Comprimento (a)", f"{data['length']:.2f} m".replace(".", ",")],
        ["Largura (b)", f"{data['width']:.2f} m".replace(".", ",")],
        ["Pé-Direito (h)", f"{data['height']:.2f} m".replace(".", ",")],
        ["Inclinação da Cobertura", f"{data['slope']:.2f}% ({np.arctan(data['slope']/100)*180/np.pi:.2f}°)".replace(".", ",")],
        ["Altura Média - Fechamento (z)", f"{data['z_fechamento']:.2f} m".replace(".", ",")],
        ["Altura Média - Cobertura (z)", f"{data['z_cobertura']:.2f} m".replace(".", ",")],
        ["Distância Entre Pórticos", f"{data['portico_distance']:.2f} m".replace(".", ",")],
        ["Velocidade Básica do Vento (V0)", f"{data['v0']:.2f} m/s".replace(".", ",")],
        ["Categoria de Rugosidade", f"{data['category']} - {data['category_description']}"],
        ["Classe", data['class']],
        ["Fator Topográfico (S1)", f"{data['s1']:.2f}".replace(".", ",")],
        ["Fator Estatístico (S3)", f"{data['s3']:.2f} (Tp: {data['s3_tp']} anos)".replace(".", ",")],
    ]
    story.append(Paragraph("Tabela 1 – Dados da Edificação", table_title_style))
    building_table = Table(building_data, colWidths=[8*cm, 9*cm])
    building_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(building_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 2: Tabela 2 - Fator de Rajada (Fr)
    story.append(Paragraph("2. Fator de Rajada (Fr)", heading_style))
    fr_table_data = [
        ["Fr", "Classes"],
        ["", "A", "B", "C"],
        ["", "1,00", "0,98", "0,95"],
    ]
    story.append(Paragraph("Tabela 2 – Fator de Rajada (Fr) – NBR 6123:2023", table_title_style))
    fr_table = Table(fr_table_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    fr_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,0), (0,1)),
        ('BACKGROUND', (0,0), (-1,1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(fr_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 3: Tabela 3 - Parâmetros Meteorológicos
    story.append(Paragraph("3. Parâmetros Meteorológicos", heading_style))
    meteo_table_data = [
        ["Categoria", "Zg (m)", "Parâmetro", "Classes"],
        ["", "", "", "A", "B", "C"],
        ["I", "250", "bm", "1,10", "1,11", "1,12"],
        ["", "", "p", "0,06", "0,065", "0,07"],
        ["II", "300", "bm", "1,00", "1,00", "1,00"],
        ["", "", "p", "0,085", "0,09", "0,10"],
        ["III", "350", "bm", "0,94", "0,94", "0,93"],
        ["", "", "p", "0,10", "0,105", "0,115"],
        ["IV", "420", "bm", "0,86", "0,85", "0,84"],
        ["", "", "p", "0,12", "0,125", "0,135"],
        ["V", "500", "bm", "0,74", "0,73", "0,71"],
        ["", "", "p", "0,15", "0,16", "0,175"],
    ]
    story.append(Paragraph("Tabela 3 – Parâmetros Meteorológicos – NBR 6123:2023", table_title_style))
    meteo_table = Table(meteo_table_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    meteo_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
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
        ('BACKGROUND', (0,0), (-1,1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(meteo_table)
    story.append(Spacer(1, 0.5*cm))

    # Estilo para os parágrafos dentro das células da coluna "Descrição"
    description_style = ParagraphStyle(
    name='DescriptionStyle',
    fontName='Helvetica',
    fontSize=8,
    leading=9,  # Espaçamento entre linhas
    alignment=0,  # 0 = esquerda
    spaceAfter=0,
    leftIndent=0
    )
    
    # Seção 4: Tabela 4 - Valores Mínimos do Fator Estatístico S3
    story.append(Paragraph("4. Valores Mínimos do Fator Estatístico S3", heading_style))
    s3_table_data = [
    ["Grupo", "Descrição", "S3", "Tp (anos)"],
    ["1", Paragraph("Estruturas cuja ruína total ou parcial pode afetar a segurança ou possibilidade de socorro a pessoas após uma tempestade destrutiva (hospitais, quartéis de bombeiros e de forças de segurança, edifícios de centros de controle, torres de comunicação etc.). Obras de infraestrutura rodoviária e ferroviária. Estruturas que abrigam substâncias inflamáveis, tóxicas e/ou explosivas. Vedações das edificações do grupo 1 (telhas, vidros, painéis de vedação).", description_style), "1,11", "100"],
    ["2", Paragraph("Estruturas cuja ruína representa substancial risco à vida humana, particularmente pessoas em aglomerações, crianças e jovens, incluindo, mas não limitadamente a: - edificações com capacidade de aglomeração de mais de 300 pessoas em um mesmo ambiente, como centros de convenções, ginásios, estádios etc.; - creches com capacidade maior do que 150 pessoas; - escolas com capacidade maior do que 250 pessoas. Vedações das edificações do grupo 2 (telhas, vidros, painéis de vedação).", description_style), "1,06", "75"],
    ["3", Paragraph("Edificações para residências, hotéis, comércio, indústrias. Estruturas ou elementos estruturais desmontáveis com vistas a reutilização. Vedações das edificações do grupo 3 (telhas, vidros, painéis de vedação).", description_style), "1,00", "50"],
    ["4", Paragraph("Edificações não destinadas à ocupação humana (depósitos, silos) e sem circulação de pessoas no entorno. Vedações das edificações do grupo 4 (telhas, vidros, painéis de vedação).", description_style), "0,95", "37"],
    ["5", Paragraph("Edificações temporárias não reutilizáveis. Estruturas dos Grupos 1 a 4 durante a construção (fator aplicável em um prazo máximo de 2 anos). Vedações das edificações do grupo 5 (telhas, vidros, painéis de vedação).", description_style), "0,83", "15"],
    ]
    story.append(Paragraph("Tabela 4 – Valores Mínimos do Fator S3 – NBR 6123:2023", table_title_style))
    s3_table = Table(s3_table_data, colWidths=[1.8*cm, 12*cm, 1.6*cm, 1.6*cm])
    s3_table.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
    ('FONTSIZE', (0,0), (-1,-1), 8),
    ('ALIGN', (0,0), (0,-1), 'CENTER'),
    ('ALIGN', (1,0), (1,-1), 'LEFT'),
    ('ALIGN', (2,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (0,-1), 'MIDDLE'),
    ('VALIGN', (1,0), (1,-1), 'TOP'),
    ('VALIGN', (2,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    ('BOX', (0,0), (-1,-1), 0.5, colors.black),
    ('LEFTPADDING', (0,0), (-1,-1), 10),
    ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(s3_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 5: Cálculo do Fator S2 por Altura
    story.append(Paragraph("5. Cálculo do Fator S2 por Altura", heading_style))
    s2_table_data = [["z (m)", "S2"]]
    for z, s2 in results['s2_by_height'].items():
        s2_table_data.append([f"{z:.1f}".replace(".", ","), f"{s2:.6f}".replace(".", ",")])
    story.append(Paragraph("Tabela 5 – Fator S2 por Altura", table_title_style))
    s2_table = Table(s2_table_data, colWidths=[4*cm, 13*cm])
    s2_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(s2_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 6: Tabela 6 - Velocidades e Pressões Características
    story.append(Paragraph("6. Velocidades e Pressões Características", heading_style))
    vk_q_table_data = [
        ["z (m)", "S1", "S2", "S3", "Vk (m/s)", "q (kN/m²)"],
    ]
    s1 = data['s1']
    s3 = data['s3']
    for z, s2 in results['s2_by_height'].items():
        vk = calculate_vk(data['v0'], s1, s2, s3)
        q_nm2, _ = calculate_q(vk)
        vk_q_table_data.append([
            f"{z:.1f}".replace(".", ","), 
            f"{s1:.2f}".replace(".", ","), 
            f"{s2:.2f}".replace(".", ","), 
            f"{s3:.2f}".replace(".", ","), 
            f"{vk:.2f}".replace(".", ","), 
            f"{q_nm2/1000:.3f}".replace(".", ",")
        ])
    story.append(Paragraph("Tabela 6 – Velocidades e Pressões Características – NBR 6123:2023", table_title_style))
    vk_q_table = Table(vk_q_table_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    vk_q_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(vk_q_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 7: Tabela 7 - Parâmetros para S2
    story.append(Paragraph("7. Parâmetros para Determinação do Fator S2", heading_style))
    s2_params_table_data = [
        ["Direção do Vento", "Fator de Rajada (Fr)", "Coeficiente bm", "Coeficiente p"],
        ["X1", "0,95", "0,93", "0,10"],
        ["X2", "0,95", "0,93", "0,10"],
    ]
    story.append(Paragraph("Tabela 7 – Parâmetros para Determinação do Fator S2 – NBR 6123:2023", table_title_style))
    s2_params_table = Table(s2_params_table_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    s2_params_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(s2_params_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 8: Tabela 8 - Pressões na Direção X1
    story.append(Paragraph("8. Pressões de Vento na Direção X1", heading_style))
    x1_table_data = [
        ["Altura z (m)", "Fator S2", "S1", "S3", "Velocidade Vk (m/s)", "Pressão q (kN/m²)"],
    ]
    for z in [5, 10, 15, 20, 25]:
        s2 = results['s2_by_height'][z]
        vk = calculate_vk(data['v0'], data['s1'], s2, data['s3'])
        q_nm2, _ = calculate_q(vk)
        x1_table_data.append([
            f"{z:.1f}".replace(".", ","), 
            f"{s2:.2f}".replace(".", ","), 
            f"{data['s1']:.2f}".replace(".", ","), 
            f"{data['s3']:.2f}".replace(".", ","), 
            f"{vk:.2f}".replace(".", ","), 
            f"{q_nm2/1000:.3f}".replace(".", ",")
        ])
    story.append(Paragraph("Tabela 8 – Pressões de Vento na Direção X1 – NBR 6123:2023", table_title_style))
    x1_table = Table(x1_table_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    x1_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(x1_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 9: Tabela 9 - Pressões na Direção X2
    story.append(Paragraph("9. Pressões de Vento na Direção X2", heading_style))
    x2_table_data = [
        ["Altura z (m)", "Fator S2", "S1", "S3", "Velocidade Vk (m/s)", "Pressão q (kN/m²)"],
    ]
    for z in [5, 10, 15, 20, 25]:
        s2 = results['s2_by_height'][z]
        vk = calculate_vk(data['v0'], data['s1'], s2, data['s3'])
        q_nm2, _ = calculate_q(vk)
        x2_table_data.append([
            f"{z:.1f}".replace(".", ","), 
            f"{s2:.2f}".replace(".", ","), 
            f"{data['s1']:.2f}".replace(".", ","), 
            f"{data['s3']:.2f}".replace(".", ","), 
            f"{vk:.2f}".replace(".", ","), 
            f"{q_nm2/1000:.3f}".replace(".", ",")
        ])
    story.append(Paragraph("Tabela 9 – Pressões de Vento na Direção X2 – NBR 6123:2023", table_title_style))
    x2_table = Table(x2_table_data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm, 3*cm, 3*cm])
    x2_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(x2_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 10: Fator S2 Calculado
    story.append(Paragraph("10. Fator S2 Calculado", heading_style))
    s2_data = [
        ["Parâmetro", "Fechamento", "Cobertura"],
        ["Altura z (m)", f"{data['z_fechamento']:.2f}".replace(".", ","), f"{data['z_cobertura']:.2f}".replace(".", ",")],
        ["bm", f"{data['bm']:.2f}".replace(".", ","), f"{data['bm']:.2f}".replace(".", ",")],
        ["p", f"{data['p']:.3f}".replace(".", ","), f"{data['p']:.3f}".replace(".", ",")],
        ["Fr", f"{data['fr']:.2f}".replace(".", ","), f"{data['fr']:.2f}".replace(".", ",")],
        ["S2", f"{results['s2_fechamento']:.6f}".replace(".", ","), f"{results['s2_cobertura']:.6f}".replace(".", ",")],
    ]
    story.append(Paragraph("Tabela 10 – Fator S2 Calculado", table_title_style))
    s2_table = Table(s2_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    s2_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(s2_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 11: Velocidade Característica (Vk)
    story.append(Paragraph("11. Velocidade Característica (Vk)", heading_style))
    vk_data = [
        ["", "Fechamento", "Cobertura"],
        ["Vk (m/s)", f"{results['vk_fechamento']:.2f}".replace(".", ","), f"{results['vk_cobertura']:.2f}".replace(".", ",")],
    ]
    story.append(Paragraph("Tabela 11 – Velocidade Característica (Vk)", table_title_style))
    vk_table = Table(vk_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    vk_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(vk_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 12: Pressão Dinâmica (q)
    story.append(Paragraph("12. Pressão Dinâmica do Vento (q)", heading_style))
    q_data = [
        ["", "Fechamento", "Cobertura"],
        ["q (N/m²)", f"{results['q_fechamento_nm2']:.2f}".replace(".", ","), f"{results['q_cobertura_nm2']:.2f}".replace(".", ",")],
        ["q (kgf/m²)", f"{results['q_fechamento_kgfm2']:.2f}".replace(".", ","), f"{results['q_cobertura_kgfm2']:.2f}".replace(".", ",")],
    ]
    story.append(Paragraph("Tabela 12 – Pressão Dinâmica do Vento (q)", table_title_style))
    q_table = Table(q_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    q_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(q_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 13: Tabela 13 - Coeficientes de Pressão Externa (Ce)
    story.append(Paragraph("13. Coeficientes de Pressão Externa (Ce)", heading_style))
    ce_table_data = [
        ["θ (°)", "Valores de Ce para ângulo de incidência do vento α"],
        ["", "90°", "", "45°", "", "0°", "", "-45°", "", "-90°", ""],
        ["", "H e I", "L e J", "H", "L", "H e L a", "H e L b", "H", "L", "H e I", "L e J"],
        ["5", "-1,0", "-0,5", "-1,0", "-0,9", "-1,0", "-0,5", "-0,9", "-1,0", "-0,5", "-1,0"],
        ["10", "-1,0", "-0,5", "-1,0", "-0,8", "-1,0", "-0,5", "-0,8", "-1,0", "-0,4", "-1,0"],
        ["15", "-0,9", "-0,5", "-1,0", "-0,7", "-1,0", "-0,5", "-0,6", "-1,0", "-0,3", "-1,0"],
        ["20 Bump", "-0,8", "-0,5", "-1,0", "-0,6", "-0,9", "-0,5", "-0,5", "-1,0", "-0,2", "-1,0"],
        ["25", "-0,7", "-0,5", "-1,0", "-0,6", "-0,8", "-0,5", "-0,3", "-0,9", "-0,1", "-0,9"],
        ["30", "-0,5", "-0,5", "-1,0", "-0,6", "-0,8", "-0,5", "-0,1", "-0,8", "0,0", "-0,6"],
        ["θ (°)", "Ce médio"],
        ["", "H 1", "H 2", "L 1", "L 2", "H 6"],
        ["5", "-2,0", "-1,5", "-2,0", "-1,5", "-2,0"],
        ["10", "-2,0", "-1,5", "-2,0", "-1,5", "-2,0"],
        ["15", "-1,8", "-0,9", "-1,8", "-1,4", "-2,0"],
        ["20", "-1,8", "-0,8", "-1,8", "-1,4", "-2,0"],
        ["25", "-1,8", "-0,7", "-0,9", "-0,9", "-2,0"],
        ["30", "-1,8", "-0,5", "-0,5", "-0,5", "-2,0"],
    ]
    story.append(Paragraph("Tabela 13 – Coeficientes de Pressão Externa (Ce) – NBR 6123:2023", table_title_style))
    ce_table = Table(ce_table_data, colWidths=[1.5*cm] + [1.5*cm]*10)
    ce_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,0), (0,1)),
        ('SPAN', (1,0), (10,0)),
        ('SPAN', (0,6), (0,7)),
        ('SPAN', (1,6), (5,6)),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('BACKGROUND', (0,1), (-1,1), colors.lightgrey),
        ('BACKGROUND', (0,6), (-1,6), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('WORDWRAP', (0,0), (-1,-1), 'CJK'),  # Permite quebra de linha automática
    ]))
    story.append(ce_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 14: Figura das Zonas de Pressão Externa
    story.append(Paragraph("14. Zonas de Pressão Externa", heading_style))
    story.append(Paragraph("Figura 1 – Zonas de Pressão Externa (H, L, I, J) – NBR 6123:2023", table_title_style))
    pressure_zones_img = create_pressure_zones_image()
    story.append(Image(pressure_zones_img, width=15*cm, height=5*cm))
    story.append(Paragraph("H: Alta sucção (b/2 a partir da borda de barlavento); L: Baixa sucção (de b/2 até a/2); I, J: Zonas laterais.", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 15: Coeficientes de Pressão Externa (Ce) Selecionados
    story.append(Paragraph("15. Coeficientes de Pressão Externa (Ce) Selecionados", heading_style))
    ce_selected_data = [
        ["Direção do Vento", "Fechamento", "Cobertura"],
        ["0°/180° (Longitudinal)", ", ".join(map(lambda x: format_with_comma(x), data['ce_fechamento_0'])), ", ".join(map(lambda x: format_with_comma(x), data['ce_cobertura_0']))],
        ["90°/270° (Transversal)", ", ".join(map(lambda x: format_with_comma(x), data['ce_fechamento_90'])), ", ".join(map(lambda x: format_with_comma(x), data['ce_cobertura_90']))],
    ]
    story.append(Paragraph("Tabela 14 – Coeficientes de Pressão Externa (Ce) Selecionados", table_title_style))
    ce_selected_table = Table(ce_selected_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    ce_selected_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('WORDWRAP', (0,0), (-1,-1), 'CJK'),  # Permite quebra de linha automática
    ]))
    story.append(ce_selected_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 16: Coeficiente de Pressão Interno (Cpi)
    story.append(Paragraph("16. Coeficiente de Pressão Interno (Cpi)", heading_style))
    story.append(Paragraph(f"Caso Selecionado (NBR 6123:2023 - Item 6.3.2.1): {data['cpi_case']}", body_style))
    story.append(Paragraph(f"Descrição: {data['cpi_case_description']}", body_style))
    story.append(Paragraph(f"Cpi: {', '.join(map(lambda x: format_with_comma(x), data['cpi']))}", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 17: Pressão Efetiva (DP)
    story.append(Paragraph("17. Pressão Efetiva (DP) = (Ce - Cpi) × q", heading_style))
    table_counter = 15
    for direction, dp_data in results['dp'].items():
        story.append(Paragraph(f"17.{table_counter - 14}. Vento a {direction}", heading_style))
        dp_table_data = [["Ce", "Cpi", "DP (kgf/m²)"]]
        for ce, cpi, dp in dp_data:
            dp_table_data.append([f"{ce:.2f}".replace(".", ","), f"{cpi:.2f}".replace(".", ","), f"{dp:.2f}".replace(".", ",")])
        story.append(Paragraph(f"Tabela {table_counter} – Pressão Efetiva (DP) para {direction}", table_title_style))
        dp_table = Table(dp_table_data, colWidths=[4*cm, 4*cm, 9*cm])
        dp_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.5, colors.black),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ]))
        story.append(dp_table)
        story.append(Spacer(1, 0.5*cm))
        table_counter += 1

    # Seção 18: Observações
    story.append(Paragraph("18. Observações", heading_style))
    observations = [
        "Os valores de DP são aplicáveis ao dimensionamento do sistema de vedação (fechamento e cobertura).",
        "Verificar a combinação mais crítica para cada elemento.",
        "Cálculos realizados conforme ABNT NBR 6123:2023.",
    ]
    for obs in observations:
        story.append(Paragraph(obs, body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 19: Legenda de Siglas
    story.append(Paragraph("19. Legenda de Siglas", heading_style))
    legend_data = [
        ["Sigla", "Descrição"],
        ["z", "Altura acima do terreno (m)"],
        ["V0", "Velocidade básica do vento (m/s)"],
        ["Vk", "Velocidade característica do vento (m/s)"],
        ["q", "Pressão dinâmica do vento (kN/m² ou kgf/m²)"],
        ["Ce", "Coeficiente de forma externo"],
        ["Cpi", "Coeficiente de pressão interna"],
        ["S1", "Fator topográfico"],
        ["S2", "Fator de rugosidade e dimensões da edificação"],
        ["S3", "Fator estatístico"],
        ["Fr", "Fator de rajada"],
        ["bm", "Fator meteorológico (NBR 6123:2023)"],
        ["p", "Expoente meteorológico (NBR 6123:2023)"],
        ["DP", "Pressão efetiva (kgf/m²)"],
    ]
    legend_table = Table(legend_data, colWidths=[3*cm, 14*cm])
    legend_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
    ]))
    story.append(legend_table)
    story.append(Spacer(1, 0.5*cm))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Interface Streamlit
st.title("Cálculo de Ações do Vento (NBR 6123:2023)")

# Entradas do usuário
st.header("Informações do Projeto")
project_info = {
    "client": st.text_input("Cliente", "Construtora ABC"),
    "project": st.text_input("Obra", "Edifício Residencial"),
    "location": st.text_input("Localização", "São Paulo, SP"),
    "calculator": st.text_input("Cálculo", "João Silva"),
}

st.header("Dados da Edificação")
roof_type = st.selectbox("Tipo de Cobertura", ["Uma Água", "Duas Águas"], index=1)
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
    "V": "V: Áreas com muitos obstáculos altos, como florestas densas ou centros urbanos muito desenvolvidos",
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
    "V": {"Zg": 500, "A": {"bm": 0.74, "p": 0.15}, "B": {"bm": 0.73, "p": 0.16}, "C": {"bm": 0.71, "p": 0.175}},
}
fr_data = {"A": 1.0, "B": 0.98, "C": 0.95}

bm = meteorological_data[category][class_]["bm"]
p = meteorological_data[category][class_]["p"]
fr = fr_data[class_]

st.header("Fatores S1, S2, S3")
s1 = st.selectbox("Fator Topográfico (S1)", [1.0, 0.9, 1.1], help="1,0: Terreno plano; 0,9: Depressão; 1,1: Elevação.")
s3_options = {
    1.11: "1,11 (Grupo 1: Estruturas críticas como hospitais, quartéis de bombeiros, torres de comunicação - Tp: 100 anos)",
    1.06: "1,06 (Grupo 2: Estruturas com aglomerações ou crianças, como ginásios e escolas - Tp: 75 anos)",
    1.00: "1,00 (Grupo 3: Residências, hotéis, comércio, indústrias - Tp: 50 anos)",
    0.95: "0,95 (Grupo 4: Depósitos, silos, sem circulação de pessoas - Tp: 37 anos)",
    0.83: "0,83 (Grupo 5: Edificações temporárias não reutilizáveis - Tp: 15 anos)",
}
s3 = st.selectbox("Fator Estatístico (S3)", list(s3_options.keys()), format_func=lambda x: s3_options[x], index=0)
s3_tp = {1.11: 100, 1.06: 75, 1.00: 50, 0.95: 37, 0.83: 15}[s3]
st.write(f"Parâmetros S2: bm = {format_with_comma(bm)}, p = {format_with_comma(p)}, Fr = {format_with_comma(fr)}")

# Cálculo de S2 por altura (de 0 a 75 m, a cada 5 m)
s2_by_height = {}
for z in np.arange(0, 75.1, 5):
    s2_by_height[z] = calculate_s2(z, bm, p, fr)

# Exibir tabela de S2 por altura na interface
st.subheader("Fator S2 por Altura")
s2_df = pd.DataFrame(list(s2_by_height.items()), columns=["Altura z (m)", "S2"])
s2_df["S2"] = s2_df["S2"].apply(format_with_comma)
st.dataframe(s2_df)

st.header("Coeficientes de Pressão")
st.subheader("Coeficiente de Pressão Interno (Cpi) - NBR 6123:2023 Item 6.3.2.1")
cpi_cases = {
    "a": "a) Duas faces opostas igualmente permeáveis; as outras faces impermeáveis",
    "b": "b) Quatro faces igualmente permeáveis",
    "c": "c) Abertura dominante em uma face; as outras faces de igual permeabilidade",
}
cpi_case = st.radio("Selecione o caso para Cpi:", list(cpi_cases.keys()), format_func=lambda x: cpi_cases[x])
cpi_case_description = cpi_cases[cpi_case]

if cpi_case == "a":
    st.write("- Vento perpendicular a uma face permeável: Cpi = +0,2")
    st.write("- Vento perpendicular a uma face impermeável: Cpi = -0,3")
    cpi = st.multiselect("Selecione os valores de Cpi:", [0.2, -0.3], default=[0.2, -0.3])
elif cpi_case == "b":
    st.write("- Cpi = -0,3 ou 0 (considerar o valor mais nocivo)")
    cpi = st.multiselect("Selecione os valores de Cpi:", [-0.3, 0.0], default=[-0.3, 0.0])
else:  # cpi_case == "c"
    st.write("O valor de Cpi depende da proporção entre a área de aberturas na face de barlavento e a área total de aberturas:")
    st.write("- 1: Cpi = +0,1")
    st.write("- 1,5: Cpi = +0,3")
    st.write("- 2: Cpi = +0,5")
    st.write("- 3: Cpi = +0,6")
    st.write("- 6 ou mais: Cpi = +0,8")
    cpi = st.multiselect("Selecione os valores de Cpi:", [0.1, 0.3, 0.5, 0.6, 0.8], default=[0.1, 0.3])

st.subheader("Coeficientes de Pressão Externa (Ce)")
st.write("Zonas de Pressão Externa (Figura 1 - NBR 6123:2023):")
pressure_zones_img = create_pressure_zones_image()
st.image(pressure_zones_img, caption="Zonas de Pressão Externa (H, L, I, J)")
ce_fechamento_0 = st.multiselect("Ce - Fechamento (0°/180°)", [-0.9, -0.4625, -0.2820, -0.425, 0.7], default=[-0.9, -0.4625, -0.2820, -0.425, 0.7])
ce_fechamento_90 = st.multiselect("Ce - Fechamento (90°/270°)", [-0.9, -0.5, -0.5375], default=[-0.9, -0.5, -0.5375])
ce_cobertura_0 = st.multiselect("Ce - Cobertura (0°/180°)", [-0.9, -0.6, -0.325, 0.7], default=[-0.9, -0.6, -0.325, 0.7])
ce_cobertura_90 = st.multiselect("Ce - Cobertura (90°/270°)", [-0.9284, -0.6, -0.5375], default=[-0.9284, -0.6, -0.5375])

# Cálculos
s2_fechamento = calculate_s2(z_fechamento, bm, p, fr)
s2_cobertura = calculate_s2(z_cobertura, bm, p, fr)
vk_fechamento = calculate_vk(v0, s1, s2_fechamento, s3)
vk_cobertura = calculate_vk(v0, s1, s2_cobertura, s3)
q_fechamento_nm2, q_fechamento_kgfm2 = calculate_q(vk_fechamento)
q_cobertura_nm2, q_cobertura_kgfm2 = calculate_q(vk_cobertura)

# Pressões efetivas
dp_results = {
    "0°/180° - Fechamento": [],
    "0°/180° - Cobertura": [],
    "90°/270° - Fechamento": [],
    "90°/270° - Cobertura": [],
}
for ce in ce_fechamento_0:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_fechamento_kgfm2)
        dp_results["0°/180° - Fechamento"].append((ce, cpi_val, dp))
for ce in ce_cobertura_0:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_cobertura_kgfm2)
        dp_results["0°/180° - Cobertura"].append((ce, cpi_val, dp))
for ce in ce_fechamento_90:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_fechamento_kgfm2)
        dp_results["90°/270° - Fechamento"].append((ce, cpi_val, dp))
for ce in ce_cobertura_90:
    for cpi_val in cpi:
        dp = calculate_dp(ce, cpi_val, q_cobertura_kgfm2)
        dp_results["90°/270° - Cobertura"].append((ce, cpi_val, dp))

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
    "dp": dp_results,
}

# Dados para o relatório
data = {
    "roof_type": roof_type,
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
    "s3_tp": s3_tp,
    "bm": bm,
    "p": p,
    "fr": fr,
    "cpi_case": cpi_case,
    "cpi_case_description": cpi_case_description,
    "cpi": cpi,
    "ce_fechamento_0": ce_fechamento_0,
    "ce_fechamento_90": ce_fechamento_90,
    "ce_cobertura_0": ce_cobertura_0,
    "ce_cobertura_90": ce_cobertura_90,
}

# Exibir resultados
st.header("Resultados")
st.subheader("Fator S2 Calculado")
st.write(f"Fechamento: {format_with_comma(s2_fechamento)}")
st.write(f"Cobertura: {format_with_comma(s2_cobertura)}")
st.subheader("Velocidade Característica (Vk)")
st.write(f"Fechamento: {format_with_comma(vk_fechamento)} m/s")
st.write(f"Cobertura: {format_with_comma(vk_cobertura)} m/s")
st.subheader("Pressão Dinâmica (q)")
st.write(f"Fechamento: {format_with_comma(q_fechamento_nm2)} N/m² ({format_with_comma(q_fechamento_kgfm2)} kgf/m²)")
st.write(f"Cobertura: {format_with_comma(q_cobertura_nm2)} N/m² ({format_with_comma(q_cobertura_kgfm2)} kgf/m²)")
st.subheader("Pressão Efetiva (DP)")
for direction, dp_data in dp_results.items():
    st.write(f"{direction}")
    dp_df = pd.DataFrame(dp_data, columns=["Ce", "Cpi", "DP (kgf/m²)"])
    dp_df["Ce"] = dp_df["Ce"].apply(format_with_comma)
    dp_df["Cpi"] = dp_df["Cpi"].apply(format_with_comma)
    dp_df["DP (kgf/m²)"] = dp_df["DP (kgf/m²)"].apply(format_with_comma)
    st.dataframe(dp_df)

# Botão para gerar e baixar o relatório
if st.button("Gerar Relatório PDF"):
    pdf_buffer = generate_pdf(data, results, project_info)
    st.download_button(
        label="Baixar Relatório PDF",
        data=pdf_buffer,
        file_name="relatorio_vento.pdf",
        mime="application/pdf",
        on_click="ignore",
        icon=":material/download:",
        type="primary"
    )
