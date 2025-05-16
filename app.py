import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# Dados da segunda imagem (com ajustes para padrão kgf/m²)
dados_originais = """
102.8 kgf/ml  
-61.7 kgf/ml  
-61.0 kgf/ml  
-61.7 kgf/ml  
-16,1 kgf/ml  
-31.2 kgf/ml  
-16,1 kgf/ml  

1,8 kgf/ml  
-2,6 kgf/ml  
1,8 kgf/ml  
-12,9 kgf/ml
"""

# Padronização: substitui vírgula por ponto e corrige a unidade
dados_padronizados = dados_originais.replace(",", ".").replace("kgf/ml", "kgf/m²")

# Divide os dados em blocos conforme a primeira imagem
bloco1 = dados_padronizados.split("\n")[1]  # "102.8 kgf/m²"
bloco2 = "\n".join(dados_padronizados.split("\n")[2:5])  # Valores -61.X
bloco3 = "\n".join(dados_padronizados.split("\n")[5:8])  # Valores -16.X e -31.2
bloco4 = "\n".join(dados_padronizados.split("\n")[9:12])  # Valores 1.8 e -2.6
bloco5 = dados_padronizados.split("\n")[12]  # "-12.9 kgf/m²"

# Texto final formatado (igual ao layout da primeira imagem)
texto_final = f"""
{bloco1}

{bloco2}

{bloco3}

{bloco4}

{bloco5}
"""

# Configurações da imagem
largura, altura = 400, 400
cor_fundo = (255, 255, 255)  # Branco
cor_texto = (0, 0, 0)  # Preto

# Criar imagem
imagem = Image.new("RGB", (largura, altura), cor_fundo)
draw = ImageDraw.Draw(imagem)

# Usar fonte monoespaçada para alinhamento consistente
try:
    fonte = ImageFont.truetype("arial.ttf", 20)
except:
    fonte = ImageFont.load_default()

# Centralizar o texto na imagem
draw.text((50, 50), texto_final.strip(), fill=cor_texto, font=fonte, spacing=10)

# Exibir no Streamlit
st.image(imagem, caption="Imagem Gerada (Layout Original)", use_column_width=False)
