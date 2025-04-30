import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64

# Tentar importar weasyprint, mas lidar com o erro no Streamlit Cloud
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception as e:
    WEASYPRINT_AVAILABLE = False
    st.warning("A exportação para PDF não está disponível neste ambiente (Streamlit Cloud). Use a exportação em HTML ou execute localmente para gerar PDFs.")

# Função para formatar números com vírgula (padrão brasileiro)
def format_with_comma(value):
    return f"{value:.2f}".replace(".", ",")

# Função para criar figura esquemática das zonas de pressão (H, L, I, J)
def create_pressure_zones_figure():
    fig, ax = plt.subplots(figsize=(6, 4))
    building = plt.Rectangle((0, 0), 6, 4, fill=False, edgecolor='black')
    ax.add_patch(building)
    ax.text(1, 3.5, 'H', fontsize=12, color='blue')  # Barlavento
    ax.text(5, 0.5, 'L', fontsize=12, color='blue')  # Sotavento
    ax.text(1, 0.5, 'I', fontsize=12, color='blue')  # Lateral esquerda
    ax.text(5, 3.5, 'J', fontsize=12, color='blue')  # Lateral direita
    ax.set_xlim(-1, 7)
    ax.set_ylim(-1, 5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Figura 1 - Zonas de Pressão Externa (H, L, I, J)", pad=20)
    plt.grid(False)
    return fig

# Função para converter imagem em base64 (para embutir no HTML)
def image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Entrada de dados para a capa
st.subheader("INFORMAÇÕES DO PROJETO")
project_code = st.text_input("Código do Projeto:", "PROJ-001")
doc_number = st.text_input("Número do Documento:", "DOC-2023-001")
revision = st.text_input("Revisão:", "Rev. 0")
author = st.text_input("Autor:", "João Silva")
company = st.text_input("Empresa:", "Engenharia XYZ")
contact = st.text_input("Contato:", "joao.silva@xyz.com")
client = st.text_input("Cliente:", "Construtora ABC")
project_name = st.text_input("Obra:", "Edifício Residencial")

# Sumário com hyperlinks
st.subheader("SUMÁRIO")
st.markdown("""
- [Capa](#capa)  
- [Parâmetros de Vento](#parâmetros-de-vento)  
- [Tabela 3 - Fator S2](#tabela-3---fator-s2)  
- [Tabela 7 - Coeficientes de Telhado](#tabela-7---coeficientes-de-telhado)  
- [Figura 1 - Zonas de Pressão](#figura-1---zonas-de-pressão)  
- [Legenda de Siglas](#legenda-de-siglas)  
- [Assinatura Técnica](#assinatura-técnica)  
""")

# Capa
st.markdown("<a id='capa'></a>", unsafe_allow_html=True)
st.title("RELATÓRIO DE VENTO - NBR 6123:2023")
st.markdown(f"""
**Código do Projeto:** {project_code}  
**Número do Documento:** {doc_number}  
**Revisão:** {revision}  
**Autor:** {author}  
**Empresa:** {company}  
**Contato:** {contact}  
**Cliente:** {client}  
**Obra:** {project_name}  
""")

# Parâmetros de Vento
st.markdown("<a id='parâmetros-de-vento'></a>", unsafe_allow_html=True)
st.subheader("1. PARÂMETROS DE VENTO")
table_data = {
    "Altura z (m)": [10, 20, 30],
    "Velocidade Vk (m/s)": [30.5, 32.1, 34.0],
    "Pressão q (kN/m²)": [0.568, 0.631, 0.708],
}
table_df = pd.DataFrame(table_data)
table_df["Velocidade Vk (m/s)"] = table_df["Velocidade Vk (m/s)"].apply(format_with_comma)
table_df["Pressão q (kN/m²)"] = table_df["Pressão q (kN/m²)"].apply(format_with_comma)
styled_table = table_df.style.set_properties(**{
    'text-align': 'center',
    'border': '1px solid #ddd',
    'padding': '10px',
}).set_table_styles([
    {'selector': 'th', 'props': [('background-color', '#d3d3d3'), ('padding', '10px')]},
    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f5f5f5')]}
])
st.dataframe(styled_table)

# Tabela 3 - Fator S2
st.markdown("<a id='tabela-3---fator-s2'></a>", unsafe_allow_html=True)
st.subheader("2. TABELA 3 - FATOR S2 (CATEGORIA II)")
s2_data = {
    "z (m)": [5, 10, 15],
    "S2 (t=3s)": [1.00, 1.00, 1.04],
    "S2 (t=60s)": [0.82, 0.82, 0.86],
}
s2_df = pd.DataFrame(s2_data)
s2_df["S2 (t=3s)"] = s2_df["S2 (t=3s)"].apply(format_with_comma)
s2_df["S2 (t=60s)"] = s2_df["S2 (t=60s)"].apply(format_with_comma)
styled_s2 = s2_df.style.set_properties(**{
    'text-align': 'center',
    'border': '1px solid #ddd',
    'padding': '10px',
}).set_table_styles([
    {'selector': 'th', 'props': [('background-color', '#d3d3d3'), ('padding', '10px')]},
    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f5f5f5')]}
])
st.dataframe(styled_s2)

# Tabela 7 - Coeficientes de Telhado
st.markdown("<a id='tabela-7---coeficientes-de-telhado'></a>", unsafe_allow_html=True)
st.subheader("3. TABELA 7 - COEFICIENTES PARA TELHADOS DE DUAS ÁGUAS")
table_7_data = {
    "Ângulo (graus)": [15, 30, 45],
    "Ce (Barlavento)": [-0.2, -0.4, -0.6],
    "Ce (Sotavento)": [-0.3, -0.5, -0.7],
}
table_7_df = pd.DataFrame(table_7_data)
table_7_df["Ce (Barlavento)"] = table_7_df["Ce (Barlavento)"].apply(format_with_comma)
table_7_df["Ce (Sotavento)"] = table_7_df["Ce (Sotavento)"].apply(format_with_comma)
styled_table_7 = table_7_df.style.set_properties(**{
    'text-align': 'center',
    'border': '1px solid #ddd',
    'padding': '10px',
}).set_table_styles([
    {'selector': 'th', 'props': [('background-color', '#d3d3d3'), ('padding', '10px')]},
    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f5f5f5')]}
])
st.dataframe(styled_table_7)

# Figura 1 - Zonas de Pressão Externa
st.markdown("<a id='figura-1---zonas-de-pressão'></a>", unsafe_allow_html=True)
st.subheader("4. FIGURA 1 - ZONAS DE PRESSÃO EXTERNA")
fig = create_pressure_zones_figure()
st.pyplot(fig)
fig.savefig("pressure_zones.png", bbox_inches='tight')

# Legenda de Siglas
st.markdown("<a id='legenda-de-siglas'></a>", unsafe_allow_html=True)
st.subheader("5. LEGENDA DE SIGLAS")
legend = {
    "z": "Altura acima do terreno (m)",
    "Vk": "Velocidade característica do vento (m/s)",
    "q": "Pressão dinâmica do vento (kN/m²)",
    "Ce": "Coeficiente de forma externo",
}
for sigla, description in legend.items():
    st.write(f"**{sigla}**: {description}")

# Assinatura Técnica
st.markdown("<a id='assinatura-técnica'></a>", unsafe_allow_html=True)
st.subheader("6. ASSINATURA TÉCNICA")
st.markdown("""
**Responsável Técnico:** _____________________________  
**CREA:** _____________________________  
**Data:** _____________________________  
""")

# Função para gerar HTML para exportação
def generate_html_report():
    # Converter a figura para base64
    pressure_zones_base64 = image_to_base64("pressure_zones.png")
    
    # Tabelas convertidas para HTML
    params_table_html = table_df.to_html(index=False, classes="params-table")
    s2_table_html = s2_df.to_html(index=False, classes="s2-table")
    table_7_html = table_7_df.to_html(index=False, classes="table-7")
    
    # HTML do relatório
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ text-align: center; text-transform: uppercase; }}
            h2 {{ color: #333; text-transform: uppercase; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: center; }}
            th {{ background-color: #d3d3d3; }}
            tr:nth-child(even) {{ background-color: #f5f5f5; }}
            img {{ width: 100%; max-width: 500px; display: block; margin: 20px auto; }}
            .footer {{ position: fixed; bottom: 0; width: 100%; text-align: center; font-size: 12px; }}
            @page {{ @bottom-center {{ content: "Relatório_Vento.pdf - Página " counter(page); }} }}
        </style>
    </head>
    <body>
        <h1>Relatório de Vento - NBR 6123:2023</h1>
        
        <h2>Capa</h2>
        <p><b>Código do Projeto:</b> {project_code}</p>
        <p><b>Número do Documento:</b> {doc_number}</p>
        <p><b>Revisão:</b> {revision}</p>
        <p><b>Autor:</b> {author}</p>
        <p><b>Empresa:</b> {company}</p>
        <p><b>Contato:</b> {contact}</p>
        <p><b>Cliente:</b> {client}</p>
        <p><b>Obra:</b> {project_name}</p>
        
        <h2>1. Parâmetros de Vento</h2>
        {params_table_html}
        
        <h2>2. Tabela 3 - Fator S2 (Categoria II)</h2>
        {s2_table_html}
        
        <h2>3. Tabela 7 - Coeficientes para Telhados de Duas Águas</h2>
        {table_7_html}
        
        <h2>4. Figura 1 - Zonas de Pressão Externa</h2>
        <img src="data:image/png;base64,{pressure_zones_base64}" alt="Zonas de Pressão">
        
        <h2>5. Legenda de Siglas</h2>
        <ul>
            <li><b>z:</b> Altura acima do terreno (m)</li>
            <li><b>Vk:</b> Velocidade característica do vento (m/s)</li>
            <li><b>q:</b> Pressão dinâmica do vento (kN/m²)</li>
            <li><b>Ce:</b> Coeficiente de forma externo</li>
        </ul>
        
        <h2>6. Assinatura Técnica</h2>
        <p><b>Responsável Técnico:</b> _____________________________</p>
        <p><b>CREA:</b> _____________________________</p>
        <p><b>Data:</b> _____________________________</p>
        
        <div class="footer"></div>
    </body>
    </html>
    """
    return html_content

# Exportação para HTML
st.subheader("Exportar Relatório")
if st.button("Exportar Relatório para HTML"):
    html_content = generate_html_report()
    st.download_button(
        label="Baixar HTML",
        data=html_content,
        file_name="Relatório_Vento.html",
        mime="text/html"
    )

# Exportação para PDF (se weasyprint estiver disponível)
if WEASYPRINT_AVAILABLE:
    if st.button("Exportar Relatório para PDF"):
        html_content = generate_html_report()
        HTML(string=html_content).write_pdf("Relatório_Vento.pdf")
        with open("Relatório_Vento.pdf", "rb") as file:
            st.download_button("Baixar PDF", file, file_name="Relatório_Vento.pdf")
else:
    st.info("Exportação para PDF não disponível. Execute o aplicativo localmente e instale as dependências necessárias (veja o README para instruções).")
