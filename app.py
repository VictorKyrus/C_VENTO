import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

# Funções auxiliares
def format_with_comma(value, decimals=2):
    return f"{value:.{decimals}f}".replace('.', ',')

# Função para calcular S2
def calculate_s2(z, v0, category, class_):
    bm_dict = {"I": 1.0, "II": 0.9, "III": 0.8, "IV": 0.7, "V": 0.6}
    p_dict = {"I": 0.14, "II": 0.18, "III": 0.22, "IV": 0.28, "V": 0.35}
    fr_dict = {"A": 1.0, "B": 0.95, "C": 0.9}
    
    bm = bm_dict[category]
    p = p_dict[category]
    fr = fr_dict[class_]
    
    s2 = bm * (z / 10) ** p * fr if z > 0 else 0
    return s2, bm, p, fr

# Função para criar gráfico de velocidade do vento em função da altura
def create_velocity_height_graph(z_values, vk_values):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    ax.plot(vk_values, z_values, 'b-', label='Velocidade do Vento (Vk)')
    ax.set_xlabel('Velocidade do Vento (Vk) [m/s]', fontsize=10)
    ax.set_ylabel('Altura (z) [m]', fontsize=10)
    ax.set_title('Perfil de Velocidade do Vento em Função da Altura', fontsize=12, pad=15)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    return buf

# Função para adicionar cabeçalho e rodapé
def add_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(colors.darkblue)
    canvas.drawString(2*cm, A4[1] - 1.5*cm, "Memorial de Cálculo - Ações do Vento (NBR 6123:2023)")
    canvas.line(2*cm, A4[1] - 1.8*cm, A4[0] - 2*cm, A4[1] - 1.8*cm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    page_num = canvas.getPageNumber()
    footer_text = f"Página {page_num} | Data: {datetime.now().strftime('%d/%m/%Y')}"
    canvas.drawString(2*cm, 1*cm, footer_text)
    canvas.line(2*cm, 1.3*cm, A4[0] - 2*cm, 1.3*cm)
    canvas.restoreState()

# Função para gerar o PDF
def generate_pdf(data, results, project_info, uploaded_image=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=3*cm,
        bottomMargin=2*cm
    )
    story = []

    # Estilos
    heading_style = ParagraphStyle(
        name='Heading',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=12,
        leading=18
    )
    subheading_style = ParagraphStyle(
        name='Subheading',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.darkslategray,
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        name='Body',
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.black,
        spaceAfter=8
    )
    table_title_style = ParagraphStyle(
        name='TableTitle',
        fontName='Helvetica-Oblique',
        fontSize=10,
        textColor=colors.darkblue,
        spaceAfter=6
    )

    # Seção 1: Informações do Projeto
    story.append(Paragraph("1. Informações do Projeto", heading_style))
    project_data = [
        ["Cliente", project_info["client"]],
        ["Obra", project_info["project"]],
        ["Localização", project_info["location"]],
        ["Cálculo", project_info["calculator"]]
    ]
    project_table = Table(project_data, colWidths=[5*cm, 10*cm])
    project_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(project_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 2: Dados da Edificação
    story.append(Paragraph("2. Dados da Edificação", heading_style))
    building_data = [
        ["Comprimento (a)", f"{data['length']:.1f} m"],
        ["Largura (b)", f"{data['width']:.1f} m"],
        ["Pé-Direito", f"{data['height']:.1f} m"],
        ["Inclinação da Cobertura", f"{data['slope']:.1f}%"],
        ["Altura Média - Fechamento", f"{data['z_fechamento']:.1f} m"],
        ["Altura Média - Cobertura", f"{data['z_cobertura']:.1f} m"],
        ["Distância Entre Pórticos", f"{data['portico_distance']:.1f} m"],
        ["Tipo de Cobertura", data['roof_type']]
    ]
    building_table = Table(building_data, colWidths=[5*cm, 5*cm])
    building_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(building_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 3: Parâmetros Meteorológicos
    story.append(Paragraph("3. Parâmetros Meteorológicos", heading_style))
    meteo_data = [
        ["Velocidade Básica do Vento (V0)", f"{data['v0']:.1f} m/s"],
        ["Categoria de Rugosidade", f"{data['category']} - {data['category_description']}"],
        ["Classe", data['class_']]
    ]
    meteo_table = Table(meteo_data, colWidths=[5*cm, 10*cm])
    meteo_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(meteo_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 4: Fatores S1, S2, S3
    story.append(Paragraph("4. Fatores S1, S2, S3", heading_style))
    factors_data = [
        ["Fator Topográfico (S1)", f"{data['s1']}"],
        ["Fator S2 - Fechamento", format_with_comma(results['s2_fechamento'])],
        ["Fator S2 - Cobertura", format_with_comma(results['s2_cobertura'])],
        ["Fator Estatístico (S3)", f"{data['s3']} (Tp: {data['s3_tp']} anos)"],
        ["Parâmetro bm", format_with_comma(results['bm'])],
        ["Parâmetro p", format_with_comma(results['p'])],
        ["Parâmetro Fr", format_with_comma(results['fr'])]
    ]
    factors_table = Table(factors_data, colWidths=[5*cm, 5*cm])
    factors_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(factors_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 5: Velocidade Característica (Vk)
    story.append(Paragraph("5. Velocidade Característica (Vk)", heading_style))
    vk_data = [
        ["Fechamento", f"{format_with_comma(results['vk_fechamento'])} m/s"],
        ["Cobertura", f"{format_with_comma(results['vk_cobertura'])} m/s"]
    ]
    vk_table = Table(vk_data, colWidths=[5*cm, 5*cm])
    vk_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(vk_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 6: Velocidades e Pressões Características
    story.append(Paragraph("6. Velocidades e Pressões Características", heading_style))
    story.append(Paragraph("Tabela 1 – Velocidades e Pressões Características – NBR 6123:2023", table_title_style))
    
    z_values = np.arange(0, 76, 5)
    vp_data = [["z (m)", "S1", "S2", "S3", "Vk (m/s)", "q (kN/m²)"]]
    
    for z in z_values:
        s1 = data['s1']
        s2, _, _, _ = calculate_s2(z, data['v0'], data['category'], data['class_'])
        s3 = data['s3']
        vk = data['v0'] * s1 * s2 * s3
        q = 0.613 * vk**2 / 1000
        
        vp_data.append([
            format_with_comma(z, 1),
            format_with_comma(s1, 2),
            format_with_comma(s2, 2),
            format_with_comma(s3, 2),
            format_with_comma(vk, 2),
            format_with_comma(q, 3)
        ])
    
    vp_table = Table(vp_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    vp_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(vp_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 7: Pressão Dinâmica (q)
    story.append(Paragraph("7. Pressão Dinâmica (q)", heading_style))
    story.append(Paragraph("A pressão dinâmica é calculada pela fórmula: q = 0,613 * Vk²", body_style))
    q_data = [
        ["Fechamento", f"{format_with_comma(results['q_fechamento_nm2'])} N/m² ({format_with_comma(results['q_fechamento_kgfm2'])} kgf/m²)"],
        ["Cobertura", f"{format_with_comma(results['q_cobertura_nm2'])} N/m² ({format_with_comma(results['q_cobertura_kgfm2'])} kgf/m²)"]
    ]
    q_table = Table(q_data, colWidths=[5*cm, 10*cm])
    q_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(q_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 8: Coeficientes de Pressão Interna (Cpi)
    story.append(Paragraph("8. Coeficientes de Pressão Interna (Cpi)", heading_style))
    story.append(Paragraph(f"Caso Selecionado: {results['cpi_case_description']}", subheading_style))
    cpi_data = [[f"Cpi: {format_with_comma(val)}"] for val in results['cpi']]
    cpi_table = Table(cpi_data, colWidths=[5*cm])
    cpi_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
    ]))
    story.append(cpi_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 9: Pressão Efetiva (DP)
    story.append(Paragraph("9. Pressão Efetiva (DP)", heading_style))
    story.append(Paragraph("A pressão efetiva é calculada pela fórmula: DP = q * (Ce - Cpi)", body_style))
    for direction, dp_data in results['dp_results'].items():
        story.append(Paragraph(direction, subheading_style))
        dp_table_data = [["Ce", "Cpi", "DP (kgf/m²)"]] + dp_data
        dp_table = Table(dp_table_data, colWidths=[3*cm, 3*cm, 3*cm])
        dp_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
        ]))
        story.append(dp_table)
        story.append(Spacer(1, 0.3*cm))
    story.append(Spacer(1, 0.5*cm))

    # Seção 10: Metodologia de Cálculo
    story.append(Paragraph("10. Metodologia de Cálculo", heading_style))
    story.append(Paragraph("Velocidade Característica do Vento (Vk): Vk = V0 * S1 * S2 * S3", body_style))
    story.append(Paragraph("Fator S2: S2 = bm * (z/10)^p * Fr", body_style))
    story.append(Paragraph("Pressão Dinâmica do Vento (q): q = 0,613 * Vk^2 (N/m²); q = (0,613 * Vk^2) / 9,81 (kgf/m²)", body_style))
    story.append(Paragraph("Pressão Efetiva (DP): DP = (Ce - Cpi) * q", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 11: Perfil de Velocidade do Vento
    story.append(Paragraph("11. Perfil de Velocidade do Vento em Função da Altura", heading_style))
    z_values = np.linspace(0, max(data['z_fechamento'], data['z_cobertura']) * 1.5, 100)
    vk_values = [data['v0'] * data['s1'] * calculate_s2(z, data['v0'], data['category'], data['class_'])[0] * data['s3'] for z in z_values]
    velocity_img = create_velocity_height_graph(z_values, vk_values)
    story.append(Image(velocity_img, width=12*cm, height=8*cm))
    story.append(Spacer(1, 0.5*cm))

    # Seção 12: Imagem Inserida pelo Usuário
    if uploaded_image is not None:
        story.append(Paragraph("12. Imagem Inserida pelo Usuário", heading_style))
        image = PILImage.open(uploaded_image)
        img_buffer = BytesIO()
        image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        story.append(Image(img_buffer, width=12*cm, height=8*cm))
        story.append(Spacer(1, 0.5*cm))

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer

# Dados de cidades e velocidades de vento (agora com todos os estados brasileiros)
city_data = [
    # Acre (AC)
    {"municipio": "ACRELÂNDIA", "estado": "ACRE", "isopleta": "30 m/s"},
    {"municipio": "ASSIS BRASIL", "estado": "ACRE", "isopleta": "30 m/s"},
    {"municipio": "BRASILÉIA", "estado": "ACRE", "isopleta": "30 m/s"},
    {"municipio": "RIO BRANCO", "estado": "ACRE", "isopleta": "30 m/s"},
    # Alagoas (AL)
    {"municipio": "ÁGUA BRANCA", "estado": "ALAGOAS", "isopleta": "30 m/s"},
    {"municipio": "ARAPIRACA", "estado": "ALAGOAS", "isopleta": "30 m/s"},
    {"municipio": "MACEIÓ", "estado": "ALAGOAS", "isopleta": "30 m/s"},
    # Amapá (AP)
    {"municipio": "MACAPÁ", "estado": "AMAPÁ", "isopleta": "30 m/s"},
    {"municipio": "SANTANA", "estado": "AMAPÁ", "isopleta": "30 m/s"},
    {"municipio": "LARANJAL DO JARI", "estado": "AMAPÁ", "isopleta": "30 m/s"},
    # Amazonas (AM)
    {"municipio": "MANAUS", "estado": "AMAZONAS", "isopleta": "30 m/s"},
    {"municipio": "PARINTINS", "estado": "AMAZONAS", "isopleta": "30 m/s"},
    {"municipio": "ITACOATIARA", "estado": "AMAZONAS", "isopleta": "30 m/s"},
    # Bahia (BA)
    {"municipio": "SALVADOR", "estado": "BAHIA", "isopleta": "30 m/s"},
    {"municipio": "FEIRA DE SANTANA", "estado": "BAHIA", "isopleta": "30 m/s"},
    {"municipio": "VITÓRIA DA CONQUISTA", "estado": "BAHIA", "isopleta": "30 m/s"},
    # Ceará (CE)
    {"municipio": "FORTALEZA", "estado": "CEARÁ", "isopleta": "30 m/s"},
    {"municipio": "JUAZEIRO DO NORTE", "estado": "CEARÁ", "isopleta": "30 m/s"},
    {"municipio": "SOBRAL", "estado": "CEARÁ", "isopleta": "30 m/s"},
    # Distrito Federal (DF)
    {"municipio": "BRASÍLIA", "estado": "DISTRITO FEDERAL", "isopleta": "30 m/s"},
    {"municipio": "TAGUATINGA", "estado": "DISTRITO FEDERAL", "isopleta": "30 m/s"},
    {"municipio": "CEILÂNDIA", "estado": "DISTRITO FEDERAL", "isopleta": "30 m/s"},
    # Espírito Santo (ES)
    {"municipio": "VITÓRIA", "estado": "ESPÍRITO SANTO", "isopleta": "30 m/s"},
    {"municipio": "VILA VELHA", "estado": "ESPÍRITO SANTO", "isopleta": "30 m/s"},
    {"municipio": "SERRA", "estado": "ESPÍRITO SANTO", "isopleta": "30 m/s"},
    # Goiás (GO)
    {"municipio": "GOIÂNIA", "estado": "GOIÁS", "isopleta": "30 m/s"},
    {"municipio": "APARECIDA DE GOIÂNIA", "estado": "GOIÁS", "isopleta": "30 m/s"},
    {"municipio": "ANÁPOLIS", "estado": "GOIÁS", "isopleta": "30 m/s"},
    # Maranhão (MA)
    {"municipio": "SÃO LUÍS", "estado": "MARANHÃO", "isopleta": "30 m/s"},
    {"municipio": "IMPERATRIZ", "estado": "MARANHÃO", "isopleta": "30 m/s"},
    {"municipio": "CAXIAS", "estado": "MARANHÃO", "isopleta": "30 m/s"},
    # Mato Grosso (MT)
    {"municipio": "CUIABÁ", "estado": "MATO GROSSO", "isopleta": "30 m/s"},
    {"municipio": "VÁRZEA GRANDE", "estado": "MATO GROSSO", "isopleta": "30 m/s"},
    {"municipio": "RONDONÓPOLIS", "estado": "MATO GROSSO", "isopleta": "30 m/s"},
    # Mato Grosso do Sul (MS)
    {"municipio": "CAMPO GRANDE", "estado": "MATO GROSSO DO SUL", "isopleta": "30 m/s"},
    {"municipio": "DOURADOS", "estado": "MATO GROSSO DO SUL", "isopleta": "30 m/s"},
    {"municipio": "TRÊS LAGOAS", "estado": "MATO GROSSO DO SUL", "isopleta": "30 m/s"},
    # Minas Gerais (MG)
    {"municipio": "BELO HORIZONTE", "estado": "MINAS GERAIS", "isopleta": "30 m/s"},
    {"municipio": "UBERLÂNDIA", "estado": "MINAS GERAIS", "isopleta": "30 m/s"},
    {"municipio": "CONTAGEM", "estado": "MINAS GERAIS", "isopleta": "30 m/s"},
    # Pará (PA)
    {"municipio": "BELÉM", "estado": "PARÁ", "isopleta": "30 m/s"},
    {"municipio": "ANANINDEUA", "estado": "PARÁ", "isopleta": "30 m/s"},
    {"municipio": "SANTARÉM", "estado": "PARÁ", "isopleta": "30 m/s"},
    # Paraíba (PB)
    {"municipio": "JOÃO PESSOA", "estado": "PARAÍBA", "isopleta": "30 m/s"},
    {"municipio": "CAMPINA GRANDE", "estado": "PARAÍBA", "isopleta": "30 m/s"},
    {"municipio": "SANTA RITA", "estado": "PARAÍBA", "isopleta": "30 m/s"},
    # Paraná (PR)
    {"municipio": "CURITIBA", "estado": "PARANÁ", "isopleta": "30 m/s"},
    {"municipio": "LONDRINA", "estado": "PARANÁ", "isopleta": "30 m/s"},
    {"municipio": "MARINGÁ", "estado": "PARANÁ", "isopleta": "30 m/s"},
    # Pernambuco (PE)
    {"municipio": "RECIFE", "estado": "PERNAMBUCO", "isopleta": "30 m/s"},
    {"municipio": "JABOATÃO DOS GUARARAPES", "estado": "PERNAMBUCO", "isopleta": "30 m/s"},
    {"municipio": "OLINDA", "estado": "PERNAMBUCO", "isopleta": "30 m/s"},
    # Piauí (PI)
    {"municipio": "TERESINA", "estado": "PIAUÍ", "isopleta": "30 m/s"},
    {"municipio": "PARNAÍBA", "estado": "PIAUÍ", "isopleta": "30 m/s"},
    {"municipio": "PIRIPIRI", "estado": "PIAUÍ", "isopleta": "30 m/s"},
    # Rio de Janeiro (RJ)
    {"municipio": "RIO DE JANEIRO", "estado": "RIO DE JANEIRO", "isopleta": "30 m/s"},
    {"municipio": "NITERÓI", "estado": "RIO DE JANEIRO", "isopleta": "30 m/s"},
    {"municipio": "NOVA IGUAÇU", "estado": "RIO DE JANEIRO", "isopleta": "30 m/s"},
    # Rio Grande do Norte (RN)
    {"municipio": "NATAL", "estado": "RIO GRANDE DO NORTE", "isopleta": "30 m/s"},
    {"municipio": "MOSSORÓ", "estado": "RIO GRANDE DO NORTE", "isopleta": "30 m/s"},
    {"municipio": "PARNAMIRIM", "estado": "RIO GRANDE DO NORTE", "isopleta": "30 m/s"},
    # Rio Grande do Sul (RS)
    {"municipio": "PORTO ALEGRE", "estado": "RIO GRANDE DO SUL", "isopleta": "30 m/s"},
    {"municipio": "CAXIAS DO SUL", "estado": "RIO GRANDE DO SUL", "isopleta": "30 m/s"},
    {"municipio": "PELOTAS", "estado": "RIO GRANDE DO SUL", "isopleta": "30 m/s"},
    # Rondônia (RO)
    {"municipio": "PORTO VELHO", "estado": "RONDÔNIA", "isopleta": "30 m/s"},
    {"municipio": "JI-PARANÁ", "estado": "RONDÔNIA", "isopleta": "30 m/s"},
    {"municipio": "ARIQUEMES", "estado": "RONDÔNIA", "isopleta": "30 m/s"},
    # Roraima (RR)
    {"municipio": "BOA VISTA", "estado": "RORAIMA", "isopleta": "30 m/s"},
    {"municipio": "RORAINÓPOLIS", "estado": "RORAIMA", "isopleta": "30 m/s"},
    {"municipio": "CARACARAÍ", "estado": "RORAIMA", "isopleta": "30 m/s"},
    # Santa Catarina (SC)
    {"municipio": "FLORIANÓPOLIS", "estado": "SANTA CATARINA", "isopleta": "30 m/s"},
    {"municipio": "JOINVILLE", "estado": "SANTA CATARINA", "isopleta": "30 m/s"},
    {"municipio": "BLUMENAU", "estado": "SANTA CATARINA", "isopleta": "30 m/s"},
    # São Paulo (SP)
    {"municipio": "SÃO PAULO", "estado": "SÃO PAULO", "isopleta": "30 m/s"},
    {"municipio": "CAMPINAS", "estado": "SÃO PAULO", "isopleta": "30 m/s"},
    {"municipio": "SANTOS", "estado": "SÃO PAULO", "isopleta": "30 m/s"},
    # Sergipe (SE)
    {"municipio": "ARACAJU", "estado": "SERGIPE", "isopleta": "30 m/s"},
    {"municipio": "NOSSA SENHORA DO SOCORRO", "estado": "SERGIPE", "isopleta": "30 m/s"},
    {"municipio": "LAGARTO", "estado": "SERGIPE", "isopleta": "30 m/s"},
    # Tocantins (TO)
    {"municipio": "PALMAS", "estado": "TOCANTINS", "isopleta": "30 m/s"},
    {"municipio": "ARAGUAÍNA", "estado": "TOCANTINS", "isopleta": "30 m/s"},
    {"municipio": "GURUPI", "estado": "TOCANTINS", "isopleta": "30 m/s"}
]

# Interface do Streamlit
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    h1 {
        color: #003087;
        text-align: center;
        font-size: 28px;
        margin-bottom: 20px;
    }
    h2 {
        color: #333;
        font-size: 20px;
        margin-bottom: 15px;
    }
    .card {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .card-title {
        font-size: 18px;
        color: #003087;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stRadio > div,
    .stMultiSelect > div {
        border: 1px solid #d0d0d0;
        border-radius: 5px;
        padding: 8px;
        color: #333;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #003087;
    }
    .stButton > button {
        background-color: #d3d3d3;
        color: #000000;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #b0b0b0;
    }
    div, p, label, span, input, select {
        color: #333 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Cálculo de Ações do Vento (NBR 6123:2023)</h1>", unsafe_allow_html=True)

# Card 1: Informações do Projeto
st.markdown('<div class="card"><div class="card-title">Informações do Projeto</div>', unsafe_allow_html=True)
project_info = {
    "client": st.text_input("Cliente", "Construtora ABC"),
    "project": st.text_input("Obra", "Edifício Residencial"),
    "location": st.text_input("Localização", "São Paulo, SP"),
    "calculator": st.text_input("Cálculo", "João Silva"),
}
st.markdown('</div>', unsafe_allow_html=True)

# Card: Seleção de Cidade e Estado para Velocidade do Vento
st.markdown('<div class="card"><div class="card-title">Seleção de Localização para Velocidade do Vento</div>', unsafe_allow_html=True)
states = sorted(list(set(city["estado"] for city in city_data)))
state = st.selectbox("Selecione o Estado", [""] + states)
cities = sorted([city["municipio"] for city in city_data if city["estado"] == state]) if state else []
city = st.selectbox("Selecione a Cidade", [""] + cities)
wind_speed = next((float(city["isopleta"].split()[0]) for city in city_data if city["municipio"] == city and city["estado"] == state), 42.0)
st.write(f"Velocidade Básica do Vento (V0): {wind_speed} m/s")
st.markdown('</div>', unsafe_allow_html=True)

# Card 2: Dados da Edificação
st.markdown('<div class="card"><div class="card-title">Dados da Edificação</div>', unsafe_allow_html=True)
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
v0 = wind_speed
st.markdown('</div>', unsafe_allow_html=True)

# Card 3: Parâmetros Meteorológicos
st.markdown('<div class="card"><div class="card-title">Parâmetros Meteorológicos</div>', unsafe_allow_html=True)
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
st.markdown('</div>', unsafe_allow_html=True)

# Card 4: Fatores S1, S2, S3
st.markdown('<div class="card"><div class="card-title">Fatores S1, S2, S3</div>', unsafe_allow_html=True)
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

s2_fechamento, bm, p, fr = calculate_s2(z_fechamento, v0, category, class_)
s2_cobertura, _, _, _ = calculate_s2(z_cobertura, v0, category, class_)
st.write(f"Parâmetros S2: bm = {format_with_comma(bm)}, p = {format_with_comma(p)}, Fr = {format_with_comma(fr)}")
st.markdown('</div>', unsafe_allow_html=True)

# Card 5: Coeficientes de Pressão
st.markdown('<div class="card"><div class="card-title">Coeficientes de Pressão</div>', unsafe_allow_html=True)
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
else:
    st.write("O valor de Cpi depende da proporção entre a área de aberturas na face de barlavento e a área total de aberturas:")
    st.write("- 1: Cpi = +0,1")
    st.write("- 1,5: Cpi = +0,3")
    st.write("- 2: Cpi = +0,5")
    st.write("- 3: Cpi = +0,6")
    st.write("- 6 ou mais: Cpi = +0,8")
    cpi = st.multiselect("Selecione os valores de Cpi:", [0.1, 0.3, 0.5, 0.6, 0.8], default=[0.1, 0.3])

st.subheader("Pressões Externas nas Paredes e Cobertura")
st.write("Defina os coeficientes de pressão externa (Ce) para cada direção.")
ce_fechamento_0 = st.multiselect("Ce - Fechamento (0°/180°)", [-0.9, -0.4625, -0.2820, -0.425, 0.7], default=[-0.9, -0.4625, -0.2820, -0.425, 0.7])
ce_fechamento_90 = st.multiselect("Ce - Fechamento (90°/270°)", [-0.9, -0.5, -0.5375], default=[-0.9, -0.5, -0.5375])
ce_cobertura_0 = st.multiselect("Ce - Cobertura (0°/180°)", [-0.9, -0.6, -0.325, 0.7], default=[-0.9, -0.6, -0.325, 0.7])
ce_cobertura_90 = st.multiselect("Ce - Cobertura (90°/270°)", [-0.9284, -0.6, -0.5375], default=[-0.9284, -0.6, -0.5375])
st.markdown('</div>', unsafe_allow_html=True)

# Card 6: Resultados
st.markdown('<div class="card"><div class="card-title">Resultados</div>', unsafe_allow_html=True)

vk_fechamento = v0 * s1 * s2_fechamento * s3
vk_cobertura = v0 * s1 * s2_cobertura * s3

q_fechamento_nm2 = 0.613 * vk_fechamento**2
q_cobertura_nm2 = 0.613 * vk_cobertura**2
q_fechamento_kgfm2 = q_fechamento_nm2 / 9.81
q_cobertura_kgfm2 = q_cobertura_nm2 / 9.81

dp_results = {}
for direction, ce_values in [
    ("Fechamento (0°/180°)", ce_fechamento_0),
    ("Fechamento (90°/270°)", ce_fechamento_90),
    ("Cobertura (0°/180°)", ce_cobertura_0),
    ("Cobertura (90°/270°)", ce_cobertura_90)
]:
    q = q_fechamento_kgfm2 if "Fechamento" in direction else q_cobertura_kgfm2
    dp_data = []
    for ce in ce_values:
        for cp in cpi:
            dp = q * (ce - cp)
            dp_data.append([format_with_comma(ce), format_with_comma(cp), format_with_comma(dp)])
    dp_results[direction] = dp_data

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
    st.dataframe(dp_df)
st.markdown('</div>', unsafe_allow_html=True)

# Card: Upload de Imagem
st.markdown('<div class="card"><div class="card-title">Upload de Imagem (Opcional)</div>', unsafe_allow_html=True)
uploaded_image = st.file_uploader("Insira uma imagem para incluir no relatório:", type=["jpg", "jpeg", "png"])
if uploaded_image is not None:
    st.image(uploaded_image, caption="Imagem Inserida", use_column_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Dados para o PDF
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
    "class_": class_,
    "s1": s1,
    "s3": s3,
    "s3_tp": s3_tp,
}
results = {
    "s2_fechamento": s2_fechamento,
    "s2_cobertura": s2_cobertura,
    "vk_fechamento": vk_fechamento,
    "vk_cobertura": vk_cobertura,
    "q_fechamento_nm2": q_fechamento_nm2,
    "q_cobertura_nm2": q_cobertura_nm2,
    "q_fechamento_kgfm2": q_fechamento_kgfm2,
    "q_cobertura_kgfm2": q_cobertura_kgfm2,
    "cpi_case_description": cpi_case_description,
    "cpi": cpi,
    "ce_fechamento_0": ce_fechamento_0,
    "ce_fechamento_90": ce_fechamento_90,
    "ce_cobertura_0": ce_cobertura_0,
    "ce_cobertura_90": ce_cobertura_90,
    "dp_results": dp_results,
    "bm": bm,
    "p": p,
    "fr": fr
}

# Botão para gerar o relatório
st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
if st.button("Gerar Relatório PDF"):
    pdf_buffer = generate_pdf(data, results, project_info, uploaded_image)
    st.download_button(
        label="Baixar Relatório PDF",
        data=pdf_buffer,
        file_name="relatorio_vento.pdf",
        mime="application/pdf",
        on_click="ignore",
        icon=":material/download:",
        type="primary"
    )
st.markdown("</div>", unsafe_allow_html=True)
