import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image # Image já está aqui
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
import matplotlib.pyplot as plt
from PIL import Image as PILImage
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader # Certifique-se que está importado
from datetime import datetime
import math

# Funções auxiliares
def format_with_comma(value, decimals=2):
    return f"{value:.{decimals}f}".replace('.', ',')

# Função para calcular S2
def calculate_s2(z, v0, category, class_):
    bm_dict = {"I": 1.0, "II": 1.0, "III": 0.8, "IV": 0.7, "V": 0.6}
    p_dict = {"I": 0.14, "II": 0.10, "III": 0.22, "IV": 0.28, "V": 0.35}
    fr_dict = {"A": 1.0, "B": 0.95, "C": 0.9}

    bm = bm_dict[category]
    p = p_dict[category]
    fr = fr_dict[class_]

    s2 = bm * (z / 10) ** p * fr if z > 0 else 0
    return s2, bm, p, fr

# Função para criar gráfico de velocidade do vento em função da altura
def create_velocity_height_graph(z_values, vk_values):
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300) # MODIFICADO: dpi para 300
    ax.plot(vk_values, z_values, 'b-', label='Velocidade do Vento (Vk)')
    ax.set_xlabel('Velocidade do Vento (Vk) [m/s]', fontsize=10)
    ax.set_ylabel('Altura (z) [m]', fontsize=10)
    ax.set_title('Perfil de Velocidade do Vento em Função da Altura', fontsize=12, pad=15)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) # MODIFICADO: dpi para 300 (redundante se já no subplots, mas garante)
    plt.close(fig) # Fechar a figura para liberar memória
    buf.seek(0)
    return buf

# Função para criar diagrama de pressão do vento
def create_wind_pressure_diagram(data, results):
    # Ajustar figsize e fontsize para melhor clareza com DPI maior
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300) # MODIFICADO: dpi para 300 e figsize ajustado

    pressures = {
        'top': 72.0,
        'roof_front_left': -92.6, 'roof_front_center': -92.2, 'roof_front_right': -92.6,
        'roof_mid_left': -47.6, 'roof_mid_center': -62.5, 'roof_mid_right': -47.6,
        'base_front_left': -29.0, 'base_center': -33.8, 'base_front_right': -29.0,
        'base_bottom': -43.7
    }
    # Valores de exemplo para dp_results, substitua pelos seus valores reais se necessário
    # Isso é apenas para que a função possa ser chamada independentemente para teste se results não estiver completo
    # Na sua aplicação, 'results' virá preenchido
    example_dp_results = {
        "Fechamento (0°/180°)": [
            ["0.7", "0.2", format_with_comma(data.get('q_fechamento_kgfm2', 50) * (0.7 - 0.2))], # Exemplo de cálculo
            ["-0.9", "0.2", format_with_comma(data.get('q_fechamento_kgfm2', 50) * (-0.9 - 0.2))]
        ]
    }
    current_dp_results = results.get('dp_results', example_dp_results)


    l1 = data['length']
    l2 = data['width']
    h_total_fechamento = data['z_fechamento'] # Altura total do fechamento
    
    # Extraindo pressões para a fachada (simplificado - ajuste conforme sua lógica de DP)
    # Idealmente, você pegaria os DPs calculados de 'results['dp_results']'
    # Para este exemplo, vou usar valores fixos ou um placeholder
    # Isso precisará de uma lógica mais robusta para mapear os DPs corretos para as zonas do diagrama
    
    # Tentativa de pegar valores de DP relevantes (EXEMPLO - PRECISA DE AJUSTE FINO)
    # Esta é uma simplificação, você precisará de uma lógica para escolher os DPs corretos para visualizar
    dp_values_facade = {}
    if "Fechamento (0°/180°)" in current_dp_results:
        dps = [float(row[2].replace(',','.')) for row in current_dp_results["Fechamento (0°/180°)"]]
        if dps:
            dp_values_facade['zona_superior'] = max(dps)  # Exemplo: usar o DP máximo
            dp_values_facade['zona_media'] = sorted(dps)[len(dps)//2] if len(dps) > 1 else dps[0] # Exemplo: usar mediano
            dp_values_facade['zona_inferior'] = min(dps) # Exemplo: usar o DP mínimo

    # Desenho da fachada
    ax.add_patch(plt.Rectangle((0, 0), l2, h_total_fechamento, fill=True, facecolor='lightgray', edgecolor='black', linewidth=1))

    # Zonas e Rótulos (Exemplo de subdivisão - ajuste conforme a necessidade)
    # Zona Superior (e.g., terço superior)
    ax.text(l2/2, h_total_fechamento * 0.83, f"{dp_values_facade.get('zona_superior', pressures['top']):.1f} kgf/m²", ha='center', va='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.5, pad=0.2))
    # Zona Média (e.g., terço médio)
    ax.text(l2/2, h_total_fechamento * 0.5, f"{dp_values_facade.get('zona_media', pressures['roof_mid_center']):.1f} kgf/m²", ha='center', va='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.5, pad=0.2))
    # Zona Inferior (e.g., terço inferior)
    ax.text(l2/2, h_total_fechamento * 0.17, f"{dp_values_facade.get('zona_inferior', pressures['base_center']):.1f} kgf/m²", ha='center', va='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.5, pad=0.2))

    # Linhas divisórias (opcional)
    ax.plot([0, l2], [h_total_fechamento * 2/3, h_total_fechamento * 2/3], 'k--', linewidth=0.5)
    ax.plot([0, l2], [h_total_fechamento * 1/3, h_total_fechamento * 1/3], 'k--', linewidth=0.5)
    
    ax.set_xlim(-0.1*l2, 1.1*l2)
    ax.set_ylim(-0.1*h_total_fechamento, 1.1*h_total_fechamento) # Ajustar Y limit para cobrir a altura do fechamento
    ax.set_xlabel(f'Largura ({l2:.1f}m)', fontsize=10)
    ax.set_ylabel(f'Altura ({h_total_fechamento:.1f}m)', fontsize=10)
    ax.set_title('Diagrama de Pressão do Vento (0°/180°)\nValores de DP (kgf/m²)', fontsize=12, pad=15)
    ax.grid(False)
    ax.set_aspect('equal', adjustable='box') # Tenta manter proporção, pode precisar de ajuste no figsize

    plt.tight_layout(pad=1.5) # Adiciona um pouco de padding
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300) # MODIFICADO: dpi para 300
    plt.close(fig) # Fechar a figura para liberar memória
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
    footer_text = f"Página {page_num} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas.drawString(2*cm, 1*cm, footer_text)
    canvas.line(2*cm, 1.3*cm, A4[0] - 2*cm, 1.3*cm)
    canvas.restoreState()

# Função para gerar o PDF
def generate_pdf(data, results, project_info, wind_forces, uploaded_image_file=None): # Renomeado para evitar conflito
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

    # Estilos (mantidos como no seu código original)
    heading_style = ParagraphStyle(name='Heading', fontName='Helvetica-Bold', fontSize=16, textColor=colors.darkblue, spaceAfter=12, leading=18)
    subheading_style = ParagraphStyle(name='Subheading', fontName='Helvetica-Bold', fontSize=12, textColor=colors.darkslategray, spaceAfter=10)
    body_style = ParagraphStyle(name='Body', fontName='Helvetica', fontSize=10, textColor=colors.black, spaceAfter=8)
    table_title_style = ParagraphStyle(name='TableTitle', fontName='Helvetica-Oblique', fontSize=10, textColor=colors.darkblue, spaceAfter=6)

    # Largura útil da página para as imagens
    page_content_width = A4[0] - doc.leftMargin - doc.rightMargin - 0.5*cm # Pequena margem de segurança

    # ... (Todas as seções do seu PDF de 1 a 11 permanecem iguais) ...
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
        ["Comprimento (\( l_1 \))", f"{data['length']:.1f} m"],
        ["Largura (\( l_2 \))", f"{data['width']:.1f} m"],
        ["Pé-Direito", f"{data['height']:.1f} m"],
        ["Inclinação da Cobertura", f"{data['slope']:.1f}%"],
        ["Altura Média - Fechamento (\( h \))", f"{data['z_fechamento']:.1f} m"],
        ["Altura Média - Cobertura", f"{data['z_cobertura']:.1f} m"],
        ["Distância Entre Pórticos", f"{data['portico_distance']:.1f} m"],
        ["Tipo de Cobertura", data['roof_type']]
    ]
    building_table = Table(building_data, colWidths=[5*cm, 5*cm]) # Ajustar colWidths se necessário
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
        ["V0 (m/s)", f"{data['v0']:.1f} m/s"],
        ["Categoria de Rugosidade", f"{data['category']}"],
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
    factors_table = Table(factors_data, colWidths=[5*cm, 5*cm]) # Ajustar colWidths
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
    vk_table = Table(vk_data, colWidths=[5*cm, 5*cm]) # Ajustar colWidths
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

    for z_val in z_values: # Renomeado para evitar conflito com nome de variável anterior
        s1_val = data['s1'] # Renomeado
        s2_val, _, _, _ = calculate_s2(z_val, data['v0'], data['category'], data['class_']) # Renomeado
        s3_val = data['s3'] # Renomeado
        vk_val = data['v0'] * s1_val * s2_val * s3_val # Renomeado
        q_val = 0.613 * vk_val**2 / 1000 # Renomeado

        vp_data.append([
            format_with_comma(z_val, 1),
            format_with_comma(s1_val, 2),
            format_with_comma(s2_val, 2),
            format_with_comma(s3_val, 2),
            format_with_comma(vk_val, 2),
            format_with_comma(q_val, 3)
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
    cpi_data_list = [[f"Cpi: {format_with_comma(val)}"] for val in results['cpi']] # Renomeado
    cpi_table = Table(cpi_data_list, colWidths=[5*cm]) # Usar lista renomeada
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
    for direction, dp_data_list in results['dp_results'].items(): # Renomeado
        story.append(Paragraph(direction, subheading_style))
        dp_table_data = [["Ce", "Cpi", "DP (kgf/m²)"]] + dp_data_list # Usar lista renomeada
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

    # Seção 10: Forças de Vento na Cobertura de Duas Águas
    if data['roof_type'] == "Duas Águas":
        story.append(Paragraph("10. Forças de Vento na Cobertura de Duas Águas", heading_style))
        story.append(Paragraph("As forças são calculadas pela fórmula: F = DP * A, onde A é a área de cada água.", body_style))
        for direction, force_data_list in wind_forces.items(): # Renomeado
            story.append(Paragraph(direction, subheading_style))
            force_table_data = [["Ce", "Cpi", "DP (kgf/m²)", "Área (m²)", "F (kgf)"]] + force_data_list # Usar lista renomeada
            force_table = Table(force_table_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
            force_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
            ]))
            story.append(force_table)
            story.append(Spacer(1, 0.3*cm))
        story.append(Spacer(1, 0.5*cm))

    # Seção 11: Metodologia de Cálculo
    story.append(Paragraph("11. Metodologia de Cálculo", heading_style))
    story.append(Paragraph("Velocidade Característica do Vento (Vk): Vk = V0 * S1 * S2 * S3", body_style))
    story.append(Paragraph("Fator S2: S2 = bm * (z/10)^p * Fr", body_style))
    story.append(Paragraph("Pressão Dinâmica do Vento (q): q = 0,613 * Vk^2 (N/m²); q = (0,613 * Vk^2) / 9,81 (kgf/m²)", body_style))
    story.append(Paragraph("Pressão Efetiva (DP): DP = (Ce - Cpi) * q", body_style))
    if data['roof_type'] == "Duas Águas":
        story.append(Paragraph("Força do Vento (F): F = DP * A", body_style))
    story.append(Spacer(1, 0.5*cm))


    # MODIFICADO: Seção 12 - Perfil de Velocidade do Vento
    story.append(Paragraph("12. Perfil de Velocidade do Vento em Função da Altura", heading_style))
    z_plot_values = np.linspace(0, max(data['z_fechamento'], data['z_cobertura']) * 1.5, 100) # Renomeado
    vk_plot_values = [data['v0'] * data['s1'] * calculate_s2(z_val, data['v0'], data['category'], data['class_'])[0] * data['s3'] for z_val in z_plot_values] # Renomeado
    
    velocity_img_buffer = create_velocity_height_graph(z_plot_values, vk_plot_values)
    img_reader_velocity = ImageReader(velocity_img_buffer)
    iw_vel, ih_vel = img_reader_velocity.getSize()
    aspect_ratio_vel = ih_vel / float(iw_vel)
    
    img_width_pdf_vel = min(12*cm, page_content_width) # Usar uma largura definida ou a largura da página
    img_height_pdf_vel = img_width_pdf_vel * aspect_ratio_vel
    
    story.append(Image(velocity_img_buffer, width=img_width_pdf_vel, height=img_height_pdf_vel))
    story.append(Spacer(1, 0.5*cm))

    # MODIFICADO: Seção 13 - Imagem Inserida pelo Usuário
    if uploaded_image_file is not None:
        story.append(Paragraph("13. Imagem Inserida pelo Usuário", heading_style))
        
        # Usar o BytesIO diretamente se for o caso, ou abrir se for um caminho de arquivo
        # No seu app.py, uploaded_image é um objeto UploadedFile do Streamlit
        pil_img_uploaded = PILImage.open(uploaded_image_file)
        
        img_buffer_uploaded = BytesIO()
        # Tentar salvar no formato original, ou PNG como fallback
        img_format = pil_img_uploaded.format if pil_img_uploaded.format in ['PNG', 'JPEG', 'JPG'] else 'PNG'
        pil_img_uploaded.save(img_buffer_uploaded, format=img_format)
        img_buffer_uploaded.seek(0)
        
        img_reader_uploaded = ImageReader(img_buffer_uploaded)
        iw_up, ih_up = img_reader_uploaded.getSize()
        aspect_ratio_up = ih_up / float(iw_up)
        
        img_width_pdf_up = min(15*cm, page_content_width) # Largura máxima de 15cm ou largura da página
        img_height_pdf_up = img_width_pdf_up * aspect_ratio_up
        
        story.append(Image(img_buffer_uploaded, width=img_width_pdf_up, height=img_height_pdf_up))
        story.append(Spacer(1, 0.5*cm))

    # Seção 14: Força de Atrito Longitudinal (0° / 180°) - Mantido como no seu código original
    story.append(Paragraph("14. Força de Atrito Longitudinal (0° / 180°)", heading_style))
    story.append(Paragraph("Conforme NBR 6123:2023, a força de atrito longitudinal (\( F' \)) é calculada quando \( l_2 / h > 4 \) ou \( l_2 / l_1 > 4 \).", body_style))
    
    l1_fric = data['length']  # Usar variáveis locais para clareza
    l2_fric = data['width']
    h_fric = data['z_fechamento']
    Cfr = 0.04
    q_cob_fric = results['q_cobertura_kgfm2']
    q_fec_fric = results['q_fechamento_kgfm2']
    
    l2_h_ratio_fric = l2_fric / h_fric if h_fric > 0 else float('inf') # Evitar divisão por zero
    l2_l1_ratio_fric = l2_fric / l1_fric if l1_fric > 0 else float('inf') # Evitar divisão por zero
    condition_met_fric = l2_h_ratio_fric > 4 or l2_l1_ratio_fric > 4
    
    F_prime_val, F_cob_val, F_fec_val = "Não Aplicável", "Não Aplicável", "Não Aplicável" # Renomeado

    if condition_met_fric:
        if h_fric <= l1_fric:
            F_cob_val = Cfr * q_cob_fric * l1_fric * (l2_fric - 4 * h_fric) if (l2_fric - 4 * h_fric) > 0 else 0
            F_fec_val = Cfr * q_fec_fric * 2 * h_fric * (l2_fric - 4 * h_fric) if (l2_fric - 4 * h_fric) > 0 else 0
            F_prime_val = F_cob_val + F_fec_val
            story.append(Paragraph("Condição: \( h \leq l_1 \)", body_style))
            # ... (fórmulas)
        else: # h_fric > l1_fric
            F_cob_val = Cfr * q_cob_fric * l1_fric * (l2_fric - 4 * h_fric) if (l2_fric - 4 * h_fric) > 0 else 0 # Esta fórmula parece ser a mesma, revisar NBR se l2-4l1 é aplicável a F_cob também
            F_fec_val = Cfr * q_fec_fric * 2 * h_fric * (l2_fric - 4 * l1_fric) if (l2_fric - 4 * l1_fric) > 0 else 0
            F_prime_val = F_cob_val + F_fec_val
            story.append(Paragraph("Condição: \( h > l_1 \)", body_style))
            # ... (fórmulas)
    else:
        story.append(Paragraph("Condição não atendida: \( l_2 / h \leq 4 \) e \( l_2 / l_1 \leq 4 \). Portanto, os cálculos de \( F' \), \( F'_{cob} \) e \( F'_{fec} \) não são aplicáveis.", body_style))
    
    friction_data = [
        ["Parâmetro", "Valor"],
        ["\( l_1 \)", f"{format_with_comma(l1_fric)} m"],
        ["\( l_2 \)", f"{format_with_comma(l2_fric)} m"],
        ["\( h \)", f"{format_with_comma(h_fric)} m"],
        ["\( l_2 / h \)", f"{format_with_comma(l2_h_ratio_fric)}"],
        ["\( l_2 / l_1 \)", f"{format_with_comma(l2_l1_ratio_fric)}"],
        ["\( C_{fr} \)", f"{format_with_comma(Cfr)}"],
        ["\( q_{cob} \)", f"{format_with_comma(q_cob_fric)} kgf/m²"],
        ["\( q_{fec} \)", f"{format_with_comma(q_fec_fric)} kgf/m²"],
        ["\( F'_{cob} \)", f"{format_with_comma(F_cob_val)} kgf" if isinstance(F_cob_val, (int, float)) else F_cob_val],
        ["\( F'_{fec} \)", f"{format_with_comma(F_fec_val)} kgf" if isinstance(F_fec_val, (int, float)) else F_fec_val],
        ["\( F' \)", f"{format_with_comma(F_prime_val)} kgf" if isinstance(F_prime_val, (int, float)) else F_prime_val],
    ]
    
    friction_table = Table(friction_data, colWidths=[5*cm, 5*cm]) # Ajustar colWidths
    friction_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(friction_table)
    story.append(Spacer(1, 0.5*cm))


    # MODIFICADO: Seção 15 - Diagrama de Pressão do Vento
    story.append(Paragraph("15. Diagrama de Pressão do Vento (0°/180°)", heading_style))
    story.append(Paragraph("Ilustração das pressões efetivas do vento (DP) aplicadas na fachada da edificação:", body_style))
    
    pressure_img_buffer = create_wind_pressure_diagram(data, results) # Já retorna buffer com DPI 300
    img_reader_pressure = ImageReader(pressure_img_buffer)
    iw_press, ih_press = img_reader_pressure.getSize()
    aspect_ratio_press = ih_press / float(iw_press)
    
    img_width_pdf_press = min(15*cm, page_content_width) # Usar uma largura definida ou a largura da página
    img_height_pdf_press = img_width_pdf_press * aspect_ratio_press
    
    story.append(Image(pressure_img_buffer, width=img_width_pdf_press, height=img_height_pdf_press))
    story.append(Spacer(1, 0.5*cm))

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer

# Lista fixa de estados brasileiros (mantida)
brazilian_states = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal",
    "Espírito Santo", "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul",
    "Minas Gerais", "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
    "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima", "Santa Catarina",
    "São Paulo", "Sergipe", "Tocantins"
]

# Interface do Streamlit (mantida como no seu código original)
st.markdown("""
    <style>
    .stApp { /* ... styles ... */ }
    /* ... (seu CSS existente) ... */
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Cálculo de Ações do Vento (NBR 6123:2023)</h1>", unsafe_allow_html=True)

# Card 1: Informações do Projeto (mantido)
st.markdown('<div class="card"><div class="card-title">Informações do Projeto</div>', unsafe_allow_html=True)
project_info = {
    "client": st.text_input("Cliente", "Construtora ABC"),
    "project": st.text_input("Obra", "Edifício Residencial"),
    "location": st.text_input("Localização", "São Paulo, SP"),
    "calculator": st.text_input("Cálculo", "João Silva"),
}
st.markdown('</div>', unsafe_allow_html=True)


# Card: Seleção de Localização para Velocidade do Vento (mantido)
st.markdown('<div class="card"><div class="card-title">Seleção de Localização para Velocidade do Vento</div>', unsafe_allow_html=True)
state = st.selectbox("Selecione o Estado", [""] + brazilian_states)
city = st.text_input("Cidade", "São Paulo") # Removido value fixo para permitir entrada do usuário
v0 = st.number_input("V0 (m/s)", min_value=0.0, value=42.0, format="%.1f")
st.write(f"Velocidade Básica do Vento (V0): {v0} m/s")
st.markdown('</div>', unsafe_allow_html=True)


# Card 2: Dados da Edificação (mantido)
st.markdown('<div class="card"><div class="card-title">Dados da Edificação</div>', unsafe_allow_html=True)
roof_type = st.selectbox("Tipo de Cobertura", ["Uma Água", "Duas Águas"], index=1)
col1, col2 = st.columns(2)
with col1:
    length = st.number_input("Comprimento (\( l_1 \)) (m)", min_value=0.0, value=48.0, format="%.1f")
    width = st.number_input("Largura (\( l_2 \)) (m)", min_value=0.0, value=16.0, format="%.1f")
    height = st.number_input("Pé-Direito (m)", min_value=0.0, value=10.9, format="%.1f")
with col2:
    slope = st.number_input("Inclinação da Cobertura (%)", min_value=0.0, value=10.0, format="%.1f")
    z_fechamento = st.number_input("Altura Média - Fechamento (\( h \)) (m)", min_value=0.0, value=13.0, format="%.1f")
    z_cobertura = st.number_input("Altura Média - Cobertura (m)", min_value=0.0, value=13.8, format="%.1f")
portico_distance = st.number_input("Distância Entre Pórticos (m)", min_value=0.0, value=5.0, format="%.1f")
st.markdown('</div>', unsafe_allow_html=True)


# Card 3: Parâmetros Meteorológicos (mantido)
st.markdown('<div class="card"><div class="card-title">Parâmetros Meteorológicos</div>', unsafe_allow_html=True)
category_options = {
    "I": "I: Mar ou costa com poucos obstáculos",
    "II": "II: Terrenos abertos, em nível ou aproximadamente em nível, com poucos obstáculos isolados, tais como árvores e edificações baixas",
    "III": "III: Subúrbios ou áreas industriais com edificações de altura média",
    "IV": "IV: Centros urbanos com edificações altas e densas",
    "V": "V: Áreas com muitos obstáculos altos, como florestas densas ou centros urbanos muito desenvolvidos",
}
category = st.selectbox("Categoria de Rugosidade", list(category_options.keys()), format_func=lambda x: category_options[x])
category_description = category_options[category] # Definido aqui
class_ = st.selectbox("Classe", ["A", "B", "C"], help="A: Dimensão frontal ≤ 20 m; B: 20 m < Dimensão ≤ 50 m; C: Dimensão > 50 m.")
st.markdown('</div>', unsafe_allow_html=True)


# Card 4: Fatores S1, S2, S3 (mantido)
st.markdown('<div class="card"><div class="card-title">Fatores S1, S2, S3</div>', unsafe_allow_html=True)
s1 = st.selectbox("Fator Topográfico (S1)", [1.0, 0.9, 1.1], index=0, format_func=lambda x: f"{x:.1f}", help="1,0: Terreno plano; 0,9: Depressão; 1,1: Elevação.")
s3_options = {
    1.11: "1,11 (Grupo 1: Estruturas críticas como hospitais, quartéis de bombeiros, torres de comunicação - Tp: 100 anos)",
    1.06: "1,06 (Grupo 2: Estruturas com aglomerações ou crianças, como ginásios e escolas - Tp: 75 anos)",
    1.00: "1,00 (Grupo 3: Residências, hotéis, comércio, indústrias - Tp: 50 anos)",
    0.95: "0,95 (Grupo 4: Depósitos, silos, sem circulação de pessoas - Tp: 37 anos)",
    0.83: "0,83 (Grupo 5: Edificações temporárias não reutilizáveis - Tp: 15 anos)",
}
s3 = st.selectbox("Fator Estatístico (S3)", list(s3_options.keys()), format_func=lambda x: s3_options[x], index=2) # Default para 1.00
s3_tp = {1.11: 100, 1.06: 75, 1.00: 50, 0.95: 37, 0.83: 15}[s3]

s2_fechamento, bm, p, fr = calculate_s2(z_fechamento, v0, category, class_)
s2_cobertura, _, _, _ = calculate_s2(z_cobertura, v0, category, class_)
st.write(f"Parâmetros S2: bm = {format_with_comma(bm)}, p = {format_with_comma(p)}, Fr = {format_with_comma(fr)}")
st.markdown('</div>', unsafe_allow_html=True)


# Card 5: Coeficientes de Pressão (mantido)
st.markdown('<div class="card"><div class="card-title">Coeficientes de Pressão</div>', unsafe_allow_html=True)
st.subheader("Coeficiente de Pressão Interno (Cpi) - NBR 6123:2023 Item 6.3.2.1")
cpi_cases = {
    "a": "a) Duas faces opostas igualmente permeáveis; as outras faces impermeáveis",
    "b": "b) Quatro faces igualmente permeáveis",
    "c": "c) Abertura dominante em uma face; as outras faces de igual permeabilidade",
}
cpi_case_key = st.radio("Selecione o caso para Cpi:", list(cpi_cases.keys()), index=0, key="cpi_case_key") # Renomeado
cpi_case_description = cpi_cases[cpi_case_key]

cpi_values = [] # Renomeado
if cpi_case_key == "a":
    st.write("- Vento perpendicular a uma face permeável: Cpi = +0,2")
    st.write("- Vento perpendicular a uma face impermeável: Cpi = -0,3")
    cpi_values = st.multiselect("Selecione os valores de Cpi:", [0.2, -0.3], default=[0.2, -0.3])
elif cpi_case_key == "b":
    st.write("- Cpi = -0,3 ou 0 (considerar o valor mais nocivo)")
    cpi_values = st.multiselect("Selecione os valores de Cpi:", [-0.3, 0.0], default=[-0.3, 0.0])
else: # cpi_case_key == "c"
    st.write("O valor de Cpi depende da proporção entre a área de aberturas na face de barlavento e a área total de aberturas:")
    # ... (descrições para caso c)
    cpi_values = st.multiselect("Selecione os valores de Cpi:", [0.1, 0.3, 0.5, 0.6, 0.8], default=[0.1, 0.3])

st.subheader("Pressões Externas nas Paredes e Cobertura")
st.write("Defina os coeficientes de pressão externa (Ce) para cada direção.")
ce_fechamento_0 = st.multiselect("Ce - Fechamento (0°/180°)", [-0.9, -0.4625, -0.2820, -0.425, 0.7], default=[-0.9, -0.4625, -0.2820, -0.425, 0.7])
ce_fechamento_90 = st.multiselect("Ce - Fechamento (90°/270°)", [-0.9, -0.5, -0.5375], default=[-0.9, -0.5, -0.5375])
ce_cobertura_0 = st.multiselect("Ce - Cobertura (0°/180°)", [-0.9, -0.6, -0.325, 0.7], default=[-0.9, -0.6, -0.325, 0.7])
ce_cobertura_90 = st.multiselect("Ce - Cobertura (90°/270°)", [-0.9284, -0.6, -0.5375], default=[-0.9284, -0.6, -0.5375])
st.markdown('</div>', unsafe_allow_html=True)


# Card 6: Resultados (lógica de cálculo mantida, apenas nomes de variáveis Cpi atualizados)
st.markdown('<div class="card"><div class="card-title">Resultados</div>', unsafe_allow_html=True)

vk_fechamento = v0 * s1 * s2_fechamento * s3
vk_cobertura = v0 * s1 * s2_cobertura * s3

q_fechamento_nm2 = 0.613 * vk_fechamento**2
q_cobertura_nm2 = 0.613 * vk_cobertura**2
q_fechamento_kgfm2 = q_fechamento_nm2 / 9.81
q_cobertura_kgfm2 = q_cobertura_nm2 / 9.81

dp_results = {}
wind_forces = {}

# Certifique-se que cpi_values (anteriormente cpi) está definido antes deste bloco
if not cpi_values: # Adiciona um valor padrão se estiver vazio para evitar erros
    st.warning("Nenhum valor de Cpi selecionado. Usando [0.0] como padrão para cálculos de DP e Força.")
    cpi_values_for_calc = [0.0]
else:
    cpi_values_for_calc = cpi_values


if roof_type == "Duas Águas":
    theta = math.atan(slope / 100)
    tan_theta = math.tan(theta)
    
    cpb, cps = -0.9, -0.6 # Default
    if 0 <= tan_theta <= 0.07:  cpb, cps = 1.4 - 3.5 * tan_theta, -0.4
    elif 0.07 < tan_theta <= 0.4: cpb, cps = -1.4 + 3.5 * tan_theta, -0.4
    
    width_inclined = (width / 2) / math.cos(theta) if math.cos(theta) != 0 else (width / 2)
    area_per_water = length * width_inclined

    for direction_key, ce_vals in [ # Renomeado
        ("Cobertura (0°/180°)", [cpb, cps]),
        ("Cobertura (90°/270°)", [cpb, cps]) # Considerar diferentes Ce para 90 graus se aplicável pela norma
    ]:
        q_eff = q_cobertura_kgfm2 # Renomeado
        dp_data_list_forces = [] # Renomeado
        force_data_list_forces = [] # Renomeado
        for i, ce_val in enumerate(ce_vals): # Renomeado
            for cp_val in cpi_values_for_calc: # Usar a lista de Cpi
                dp_val = q_eff * (ce_val - cp_val) # Renomeado
                force_val = dp_val * area_per_water # Renomeado
                dp_data_list_forces.append([format_with_comma(ce_val), format_with_comma(cp_val), format_with_comma(dp_val)])
                force_data_list_forces.append([
                    format_with_comma(ce_val), format_with_comma(cp_val), format_with_comma(dp_val),
                    format_with_comma(area_per_water, 2), format_with_comma(force_val, 2)
                ])
        dp_results[direction_key] = dp_data_list_forces
        wind_forces[direction_key] = force_data_list_forces


for direction_key, ce_vals_fech in [ # Renomeado
    ("Fechamento (0°/180°)", ce_fechamento_0),
    ("Fechamento (90°/270°)", ce_fechamento_90),
]:
    q_eff_fech = q_fechamento_kgfm2 # Renomeado
    dp_data_list_fech = [] # Renomeado
    for ce_val_f in ce_vals_fech: # Renomeado
        for cp_val_f in cpi_values_for_calc: # Usar a lista de Cpi
            dp_val_f = q_eff_fech * (ce_val_f - cp_val_f) # Renomeado
            dp_data_list_fech.append([format_with_comma(ce_val_f), format_with_comma(cp_val_f), format_with_comma(dp_val_f)])
    dp_results[direction_key] = dp_data_list_fech


st.subheader("Fator S2 Calculado")
st.write(f"Fechamento: {format_with_comma(s2_fechamento)}")
st.write(f"Cobertura: {format_with_comma(s2_cobertura)}")
# ... (restante da exibição de resultados mantida) ...
st.subheader("Velocidade Característica (Vk)")
st.write(f"Fechamento: {format_with_comma(vk_fechamento)} m/s")
st.write(f"Cobertura: {format_with_comma(vk_cobertura)} m/s")
st.subheader("Pressão Dinâmica (q)")
st.write(f"Fechamento: {format_with_comma(q_fechamento_nm2)} N/m² ({format_with_comma(q_fechamento_kgfm2)} kgf/m²)")
st.write(f"Cobertura: {format_with_comma(q_cobertura_nm2)} N/m² ({format_with_comma(q_cobertura_kgfm2)} kgf/m²)")
st.subheader("Pressão Efetiva (DP)")
for direction_disp, dp_data_disp in dp_results.items(): # Renomeado
    st.write(f"{direction_disp}")
    dp_df = pd.DataFrame(dp_data_disp, columns=["Ce", "Cpi", "DP (kgf/m²)"])
    st.dataframe(dp_df)

if roof_type == "Duas Águas":
    st.subheader("Forças de Vento na Cobertura de Duas Águas")
    if area_per_water is not None : # Checar se area_per_water foi calculada
      st.write(f"Área de cada água: {format_with_comma(area_per_water, 2)} m²")
    for direction_disp_f, force_data_disp in wind_forces.items(): # Renomeado
        st.write(f"{direction_disp_f}")
        force_df = pd.DataFrame(force_data_disp, columns=["Ce", "Cpi", "DP (kgf/m²)", "Área (m²)", "F (kgf)"])
        st.dataframe(force_df)

st.markdown('</div>', unsafe_allow_html=True)


# Card: Upload de Imagem (mantido, o nome da variável passada para generate_pdf foi ajustado)
st.markdown('<div class="card"><div class="card-title">Upload de Imagem (Opcional)</div>', unsafe_allow_html=True)
uploaded_image_streamlit = st.file_uploader("Insira uma imagem para incluir no relatório:", type=["jpg", "jpeg", "png"])
if uploaded_image_streamlit is not None:
    st.image(uploaded_image_streamlit, caption="Imagem Inserida", use_column_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# Dados para o PDF (ajustado para usar cpi_values)
input_data_pdf = { # Renomeado
    "roof_type": roof_type, "length": length, "width": width, "height": height, "slope": slope,
    "z_fechamento": z_fechamento, "z_cobertura": z_cobertura, "portico_distance": portico_distance,
    "v0": v0, "category": category, "category_description": category_description,
    "class_": class_, "s1": s1, "s3": s3, "s3_tp": s3_tp,
}
results_pdf = { # Renomeado
    "s2_fechamento": s2_fechamento, "s2_cobertura": s2_cobertura,
    "vk_fechamento": vk_fechamento, "vk_cobertura": vk_cobertura,
    "q_fechamento_nm2": q_fechamento_nm2, "q_cobertura_nm2": q_cobertura_nm2,
    "q_fechamento_kgfm2": q_fechamento_kgfm2, "q_cobertura_kgfm2": q_cobertura_kgfm2,
    "cpi_case_description": cpi_case_description, "cpi": cpi_values_for_calc, # Usar a lista de Cpi correta
    "ce_fechamento_0": ce_fechamento_0, "ce_fechamento_90": ce_fechamento_90,
    "ce_cobertura_0": ce_cobertura_0, "ce_cobertura_90": ce_cobertura_90,
    "dp_results": dp_results, "bm": bm, "p": p, "fr": fr
}

# Botão para gerar o relatório (passando a variável correta para a imagem)
st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
if st.button("Gerar Relatório PDF"):
    # Passar uploaded_image_streamlit para a função generate_pdf
    pdf_buffer = generate_pdf(input_data_pdf, results_pdf, project_info, wind_forces, uploaded_image_streamlit)
    st.download_button(
        label="Baixar Relatório PDF",
        data=pdf_buffer,
        file_name="relatorio_vento.pdf",
        mime="application/pdf",
        # on_click="ignore", # Removido pois pode não ser necessário ou causar problemas
        icon=":material/download:", # Streamlit pode não suportar ícones assim, testar
        type="primary"
    )
st.markdown("</div>", unsafe_allow_html=True)import streamlit as st
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
import math

# Funções auxiliares
def format_with_comma(value, decimals=2):
    return f"{value:.{decimals}f}".replace('.', ',')

# Função para calcular S2
def calculate_s2(z, v0, category, class_):
    bm_dict = {"I": 1.0, "II": 1.0, "III": 0.8, "IV": 0.7, "V": 0.6}
    p_dict = {"I": 0.14, "II": 0.10, "III": 0.22, "IV": 0.28, "V": 0.35}
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

# Função para criar diagrama de pressão do vento
def create_wind_pressure_diagram(data, results):
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    
    # Valores de exemplo baseados na imagem fornecida
    pressures = {
        'top': 72.0,  # Cobertura
        'roof_front_left': -92.6, 'roof_front_center': -92.2, 'roof_front_right': -92.6,
        'roof_mid_left': -47.6, 'roof_mid_center': -62.5, 'roof_mid_right': -47.6,
        'base_front_left': -29.0, 'base_center': -33.8, 'base_front_right': -29.0,
        'base_bottom': -43.7
    }
    
    # Dimensões aproximadas (baseado nos dados do usuário)
    l1 = data['length']  # Comprimento
    l2 = data['width']   # Largura
    h = data['z_fechamento']  # Altura Média - Fechamento
    
    # Criar o retângulo da fachada
    ax.add_patch(plt.Rectangle((0, 0), l2, h, fill=True, facecolor='lightgray', edgecolor='black', linewidth=1))
    
    # Dividir em zonas e adicionar rótulos de pressão
    # Cobertura
    ax.text(l2/2, h, f"{pressures['top']} kgf/m²", ha='center', va='bottom', fontsize=10)
    
    # Telhado (dividido em 3 partes horizontais)
    roof_height = h * 0.3  # Aproximadamente 30% da altura para o telhado
    ax.add_patch(plt.Rectangle((0, h), l2, roof_height, fill=True, facecolor='lightgray', hatch='//', edgecolor='black'))
    ax.text(l2*0.25, h + roof_height/2, f"{pressures['roof_front_left']} kgf/m²", ha='center', va='center', fontsize=10)
    ax.text(l2*0.5, h + roof_height/2, f"{pressures['roof_front_center']} kgf/m²", ha='center', va='center', fontsize=10)
    ax.text(l2*0.75, h + roof_height/2, f"{pressures['roof_front_right']} kgf/m²", ha='center', va='center', fontsize=10)
    
    # Meio da fachada (dividido em 3 partes horizontais)
    mid_height = h * 0.4  # Aproximadamente 40% da altura para o meio
    ax.add_patch(plt.Rectangle((0, h + roof_height), l2, mid_height, fill=True, facecolor='lightgray', hatch='//', edgecolor='black'))
    ax.text(l2*0.25, h + roof_height + mid_height/2, f"{pressures['roof_mid_left']} kgf/m²", ha='center', va='center', fontsize=10)
    ax.text(l2*0.5, h + roof_height + mid_height/2, f"{pressures['roof_mid_center']} kgf/m²", ha='center', va='center', fontsize=10)
    ax.text(l2*0.75, h + roof_height + mid_height/2, f"{pressures['roof_mid_right']} kgf/m²", ha='center', va='center', fontsize=10)
    
    # Base da fachada (dividido em 3 partes horizontais)
    base_height = h * 0.3  # Aproximadamente 30% da altura para a base
    ax.add_patch(plt.Rectangle((0, h + roof_height + mid_height), l2, base_height, fill=True, facecolor='lightgray', hatch='//', edgecolor='black'))
    ax.text(l2*0.25, h + roof_height + mid_height + base_height/2, f"{pressures['base_front_left']} kgf/m²", ha='center', va='center', fontsize=10)
    ax.text(l2*0.5, h + roof_height + mid_height + base_height/2, f"{pressures['base_center']} kgf/m²", ha='center', va='center', fontsize=10)
    ax.text(l2*0.75, h + roof_height + mid_height + base_height/2, f"{pressures['base_front_right']} kgf/m²", ha='center', va='center', fontsize=10)
    
    # Base inferior
    ax.add_patch(plt.Rectangle((0, 0), l2, 0.1*h, fill=True, facecolor='lightgray', hatch='//', edgecolor='black'))
    ax.text(l2/2, 0.05*h, f"{pressures['base_bottom']} kgf/m²", ha='center', va='center', fontsize=10)
    
    # Ajustes de visualização
    ax.set_xlim(-0.1*l2, 1.1*l2)
    ax.set_ylim(-0.1*h, 1.5*h)
    ax.set_xlabel('Largura (m)')
    ax.set_ylabel('Altura (m)')
    ax.set_title('Diagrama de Pressão do Vento (0°/180°)', fontsize=12, pad=15)
    ax.grid(False)
    ax.axis('off')
    
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
    footer_text = f"Página {page_num} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    canvas.drawString(2*cm, 1*cm, footer_text)
    canvas.line(2*cm, 1.3*cm, A4[0] - 2*cm, 1.3*cm)
    canvas.restoreState()

# Função para gerar o PDF
def generate_pdf(data, results, project_info, wind_forces, uploaded_image=None):
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

    # Seção 2: Dados da Edificação (restaurada conforme a imagem)
    story.append(Paragraph("2. Dados da Edificação", heading_style))
    building_data = [
        ["Descrição", "Valor"],
        ["Tipo de Cobertura", data['roof_type']],
        ["Comprimento (\( l_1 \))", f"{data['length']:.1f} m"],
        ["Largura (\( l_2 \))", f"{data['width']:.1f} m"],
        ["Pé Direito", f"{data['height']:.1f} m"],
        ["Inclinação da Cobertura", f"{data['slope']:.1f}%"],
        ["Altura Média - Fechamento (\( h \))", f"{data['z_fechamento']:.1f} m"],
        ["Altura Média - Cobertura", f"{data['z_cobertura']:.1f} m"],
    ]
    building_table = Table(building_data, colWidths=[5*cm, 5*cm])
    building_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(building_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 3: Parâmetros Meteorológicos
    story.append(Paragraph("3. Parâmetros Meteorológicos", heading_style))
    meteo_data = [
        ["V0 (m/s)", f"{data['v0']:.1f} m/s"],
        ["Categoria de Rugosidade", f"{data['category']}"],
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

    # Seção 10: Forças de Vento na Cobertura de Duas Águas
    if data['roof_type'] == "Duas Águas":
        story.append(Paragraph("10. Forças de Vento na Cobertura de Duas Águas", heading_style))
        story.append(Paragraph("As forças são calculadas pela fórmula: F = DP * A, onde A é a área de cada água.", body_style))
        for direction, force_data in wind_forces.items():
            story.append(Paragraph(direction, subheading_style))
            force_table_data = [["Ce", "Cpi", "DP (kgf/m²)", "Área (m²)", "F (kgf)"]] + force_data
            force_table = Table(force_table_data, colWidths=[2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
            force_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
            ]))
            story.append(force_table)
            story.append(Spacer(1, 0.3*cm))
        story.append(Spacer(1, 0.5*cm))

    # Seção 11: Metodologia de Cálculo
    story.append(Paragraph("11. Metodologia de Cálculo", heading_style))
    story.append(Paragraph("Velocidade Característica do Vento (Vk): Vk = V0 * S1 * S2 * S3", body_style))
    story.append(Paragraph("Fator S2: S2 = bm * (z/10)^p * Fr", body_style))
    story.append(Paragraph("Pressão Dinâmica do Vento (q): q = 0,613 * Vk^2 (N/m²); q = (0,613 * Vk^2) / 9,81 (kgf/m²)", body_style))
    story.append(Paragraph("Pressão Efetiva (DP): DP = (Ce - Cpi) * q", body_style))
    if data['roof_type'] == "Duas Águas":
        story.append(Paragraph("Força do Vento (F): F = DP * A", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 12: Perfil de Velocidade do Vento
    story.append(Paragraph("12. Perfil de Velocidade do Vento em Função da Altura", heading_style))
    z_values = np.linspace(0, max(data['z_fechamento'], data['z_cobertura']) * 1.5, 100)
    vk_values = [data['v0'] * data['s1'] * calculate_s2(z, data['v0'], data['category'], data['class_'])[0] * data['s3'] for z in z_values]
    velocity_img = create_velocity_height_graph(z_values, vk_values)
    story.append(Image(velocity_img, width=12*cm, height=8*cm))
    story.append(Spacer(1, 0.5*cm))

    # Seção 13: Imagem Inserida pelo Usuário
    if uploaded_image is not None:
        story.append(Paragraph("13. Imagem Inserida pelo Usuário", heading_style))
        image = PILImage.open(uploaded_image)
        img_buffer = BytesIO()
        image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        story.append(Image(img_buffer, width=12*cm, height=8*cm))
        story.append(Spacer(1, 0.5*cm))

    # Seção 14: Força de Atrito Longitudinal (0° / 180°) - Ajustada
    story.append(Paragraph("14. Força de Atrito Longitudinal (0° / 180°)", heading_style))
    story.append(Paragraph("Esta seção verifica a força de atrito longitudinal conforme a NBR 6123:2023. Primeiro, é necessário verificar se a relação entre as dimensões da edificação atende a uma condição específica para que o cálculo seja aplicável.", body_style))
    
    # Usar valores do usuário
    l1 = data['length']  # Comprimento
    l2 = data['width']   # Largura
    h = data['z_fechamento']  # Altura Média - Fechamento
    Cfr = 0.04  # Valor fixo conforme NBR 6123
    q_cob = results['q_cobertura_kgfm2']  # Pressão dinâmica da cobertura
    q_fec = results['q_fechamento_kgfm2']  # Pressão dinâmica do fechamento
    
    # Verificação da condição
    l2_h_ratio = l2 / h
    l2_l1_ratio = l2 / l1
    condition_met = l2_h_ratio > 4 or l2_l1_ratio > 4
    
    # Explicação da verificação
    story.append(Paragraph("Verificação: Calculamos as relações \( l_2 / h \) e \( l_2 / l_1 \). Se \( l_2 / h > 4 \) ou \( l_2 / l_1 > 4 \), o cálculo da força de atrito longitudinal (F') deve ser realizado. Caso contrário, o cálculo não é aplicável.", body_style))
    
    if condition_met:
        story.append(Paragraph("A condição foi atendida (\( l_2 / h > 4 \) ou \( l_2 / l_1 > 4 \)). Vamos calcular a força de atrito longitudinal (F'), que é composta por duas partes: F' cob (relativa à cobertura) e F' fec (relativa ao fechamento).", body_style))
        
        if h <= l1:
            story.append(Paragraph("Condição adicional: Como \( h \leq l_1 \), usamos as seguintes fórmulas:", body_style))
            story.append(Paragraph("F' cob = \( C_{fr} \cdot q_{cob} \cdot l_1 \cdot (l_2 - 4h) \)", body_style))
            story.append(Paragraph("F' fec = \( C_{fr} \cdot q_{fec} \cdot 2h \cdot (l_2 - 4h) \)", body_style))
            F_cob = Cfr * q_cob * l1 * (l2 - 4 * h)
            F_fec = Cfr * q_fec * 2 * h * (l2 - 4 * h)
            F_prime = F_cob + F_fec
        else:
            story.append(Paragraph("Condição adicional: Como \( h > l_1 \), usamos as seguintes fórmulas:", body_style))
            story.append(Paragraph("F' cob = \( C_{fr} \cdot q_{cob} \cdot l_1 \cdot (l_2 - 4h) \)", body_style))
            story.append(Paragraph("F' fec = \( C_{fr} \cdot q_{fec} \cdot 2h \cdot (l_2 - 4l_1) \)", body_style))
            F_cob = Cfr * q_cob * l1 * (l2 - 4 * h)
            F_fec = Cfr * q_fec * 2 * h * (l2 - 4 * l1)
            F_prime = F_cob + F_fec
        
        story.append(Paragraph("A força total F' é a soma de F' cob e F' fec: F' = F' cob + F' fec.", body_style))
    else:
        F_prime = "Não Aplicável"
        F_cob = "Não Aplicável"
        F_fec = "Não Aplicável"
        story.append(Paragraph("A condição não foi atendida (\( l_2 / h \leq 4 \) e \( l_2 / l_1 \leq 4 \)). Portanto, o cálculo da força de atrito longitudinal (F') não é necessário.", body_style))
    
    # Dados para a tabela
    friction_data = [
        ["Parâmetro", "Valor"],
        ["\( l_1 \)", f"{format_with_comma(l1)} m"],
        ["\( l_2 \)", f"{format_with_comma(l2)} m"],
        ["\( h \)", f"{format_with_comma(h)} m"],
        ["\( l_2 / h \)", f"{format_with_comma(l2_h_ratio)}"],
        ["\( l_2 / l_1 \)", f"{format_with_comma(l2_l1_ratio)}"],
        ["Cfr", f"{format_with_comma(Cfr)}"],
        ["q cob", f"{format_with_comma(q_cob)} kgf/m²"],
        ["q fec", f"{format_with_comma(q_fec)} kgf/m²"],
        ["F' cob", f"{format_with_comma(F_cob)} kgf" if F_cob != "Não Aplicável" else F_cob],
        ["F' fec", f"{format_with_comma(F_fec)} kgf" if F_fec != "Não Aplicável" else F_fec],
        ["F'", f"{format_with_comma(F_prime)} kgf" if F_prime != "Não Aplicável" else F_prime],
    ]
    
    friction_table = Table(friction_data, colWidths=[5*cm, 5*cm])
    friction_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(friction_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 15: Diagrama de Pressão do Vento
    story.append(Paragraph("15. Diagrama de Pressão do Vento (0°/180°)", heading_style))
    story.append(Paragraph("Ilustração das pressões efetivas do vento aplicadas na fachada da edificação:", body_style))
    pressure_img = create_wind_pressure_diagram(data, results)
    story.append(Image(pressure_img, width=12*cm, height=9*cm))
    story.append(Spacer(1, 0.5*cm))

    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer

# Lista fixa de estados brasileiros
brazilian_states = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal",
    "Espírito Santo", "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul",
    "Minas Gerais", "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
    "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", "Roraima", "Santa Catarina",
    "São Paulo", "Sergipe", "Tocantins"
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

# Card: Seleção de Localização para Velocidade do Vento
st.markdown('<div class="card"><div class="card-title">Seleção de Localização para Velocidade do Vento</div>', unsafe_allow_html=True)
state = st.selectbox("Selecione o Estado", [""] + brazilian_states)
city = st.text_input("Cidade", "São Paulo")
v0 = st.number_input("V0 (m/s)", min_value=0.0, value=42.0)
st.write(f"Velocidade Básica do Vento (V0): {v0} m/s")
st.markdown('</div>', unsafe_allow_html=True)

# Card 2: Dados da Edificação
st.markdown('<div class="card"><div class="card-title">Dados da Edificação</div>', unsafe_allow_html=True)
roof_type = st.selectbox("Tipo de Cobertura", ["Uma Água", "Duas Águas"], index=1)
col1, col2 = st.columns(2)
with col1:
    length = st.number_input("Comprimento (\( l_1 \)) (m)", min_value=0.0, value=48.0)
    width = st.number_input("Largura (\( l_2 \)) (m)", min_value=0.0, value=16.0)
    height = st.number_input("Pé-Direito (m)", min_value=0.0, value=10.9)
with col2:
    slope = st.number_input("Inclinação da Cobertura (%)", min_value=0.0, value=10.0)
    z_fechamento = st.number_input("Altura Média - Fechamento (\( h \)) (m)", min_value=0.0, value=13.0)
    z_cobertura = st.number_input("Altura Média - Cobertura (m)", min_value=0.0, value=13.8)
portico_distance = st.number_input("Distância Entre Pórticos (m)", min_value=0.0, value=5.0)
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
wind_forces = {}
if roof_type == "Duas Águas":
    # Calcular o ângulo de inclinação (theta) a partir do percentual de inclinação
    theta = math.atan(slope / 100)  # slope em % convertido para radianos
    tan_theta = math.tan(theta)
    
    # Calcular coeficientes Ce para barlavento (CPb) e sotavento (CPs) conforme NBR 6123:2023 Tabela 25
    if 0 <= tan_theta <= 0.07:
        cpb = 1.4 - 3.5 * tan_theta
        cps = -0.4
    elif 0.07 < tan_theta <= 0.4:
        cpb = -1.4 + 3.5 * tan_theta
        cps = -0.4
    else:
        cpb = -0.9  # Valor padrão para ângulos fora da faixa (sucção máxima)
        cps = -0.6  # Valor padrão para sotavento
    
    # Calcular a área de cada água
    width_inclined = (width / 2) / math.cos(theta)  # Largura inclinada de cada água
    area_per_water = length * width_inclined  # Área de cada água (barlavento e sotavento)

    for direction, ce_values in [
        ("Cobertura (0°/180°)", [cpb, cps]),  # Usando CPb e CPs para barlavento e sotavento
        ("Cobertura (90°/270°)", [cpb, cps])  # Mesmos coeficientes para perpendicular
    ]:
        q = q_cobertura_kgfm2  # Pressão dinâmica em kgf/m²
        dp_data = []
        force_data = []
        for i, ce in enumerate(ce_values):
            for cp in cpi:
                dp = q * (ce - cp)  # DP em kgf/m²
                force = dp * area_per_water if i == 0 else dp * area_per_water  # Força para barlavento e sotavento
                dp_data.append([format_with_comma(ce), format_with_comma(cp), format_with_comma(dp)])
                force_data.append([
                    format_with_comma(ce),
                    format_with_comma(cp),
                    format_with_comma(dp),
                    format_with_comma(area_per_water, 2),
                    format_with_comma(force, 2)
                ])
        dp_results[direction] = dp_data
        wind_forces[direction] = force_data

# Adicionar as pressões efetivas para o fechamento (que não têm forças calculadas aqui)
for direction, ce_values in [
    ("Fechamento (0°/180°)", ce_fechamento_0),
    ("Fechamento (90°/270°)", ce_fechamento_90),
]:
    q = q_fechamento_kgfm2
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

# Exibir as forças de vento na cobertura de duas águas
if roof_type == "Duas Águas":
    st.subheader("Forças de Vento na Cobertura de Duas Águas")
    st.write(f"Área de cada água: {format_with_comma(area_per_water, 2)} m²")
    for direction, force_data in wind_forces.items():
        st.write(f"{direction}")
        force_df = pd.DataFrame(force_data, columns=["Ce", "Cpi", "DP (kgf/m²)", "Área (m²)", "F (kgf)"])
        st.dataframe(force_df)

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
    pdf_buffer = generate_pdf(data, results, project_info, wind_forces, uploaded_image)
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
