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
        ["Categoria de Rugosidade", data['category']],
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

    # Seção 2: Fator S2
    story.append(Paragraph("2. Fator S2", heading_style))
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

    # Seção 3: Velocidade Característica (Vk)
    story.append(Paragraph("3. Velocidade Característica (Vk)", heading_style))
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

    # Seção 4: Pressão Dinâmica (q)
    story.append(Paragraph("4. Pressão Dinâmica do Vento (q)", heading_style))
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

    # Seção 5: Coeficientes de Pressão Externo (Ce)
    story.append(Paragraph("5. Coeficientes de Pressão Externo (Ce)", heading_style))
    ce_data = [
        ["Direção do Vento", "Fechamento", "Cobertura"],
        ["0º/180º (Longitudinal)", ", ".join(map(str, data['ce_fechamento_0'])), ", ".join(map(str, data['ce_cobertura_0']))],
        ["90º/270º (Transversal)", ", ".join(map(str, data['ce_fechamento_90'])), ", ".join(map(str, data['ce_cobertura_90']))]
    ]
    ce_table = Table(ce_data, colWidths=[6*cm, 5.5*cm, 5.5*cm])
    ce_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(ce_table)
    story.append(Spacer(1, 0.5*cm))

    # Seção 6: Coeficiente de Pressão Interno (Cpi)
    story.append(Paragraph("6. Coeficiente de Pressão Interno (Cpi)", heading_style))
    story.append(Paragraph(f"Cpi = {', '.join(map(str, data['cpi']))}", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Seção 7: Pressão Efetiva (DP)
    story.append(Paragraph("7. Pressão Efetiva (DP) = (Ce - Cpi) × q", heading_style))
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

    # Seção 8: Observações
    story.append(Paragraph("8. Observações", heading_style))
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
category = st.selectbox("Categoria de Rugosidade", ["I", "II", "III", "IV", "V"], help="I: Mar ou costa; II: Terrenos abertos; III: Subúrbios; IV: Centros urbanos; V: Áreas com muitos obstáculos altos.")
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

st.header("Coeficientes de Pressão")
cpi = st.multiselect("Coeficiente de Pressão Interno (Cpi)", [0.0, -0.3, 0.2], default=[0.0, -0.3], help="0.0 ou -0.3 para quatro faces permeáveis; +0.2 para faces opostas permeáveis.")
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
    "class": class_,
    "s1": s1,
    "s3": s3,
    "bm": bm,
    "p": p,
    "fr": fr,
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
st.subheader("Fator S2")
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
