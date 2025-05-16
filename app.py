import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

# Dados fixos (extraídos da imagem)
dados = """
102,8 kgf/m²

-61,7 kgf/m²  
-61,0 kgf/m²  
-61,7 kgf/m²  

-16,1 kgf/m²  
-31,2 kgf/m²  
-16,1 kgf/m²  

1,8 kgf/m²  
-2,6 kgf/m²  
1,8 kgf/m²  

-12,9 kgf/m²
"""

# Criar uma imagem em branco (ajuste o tamanho conforme necessário)
largura = 400
altura = 300
cor_fundo = (255, 255, 255)  # Branco
imagem = Image.new("RGB", (largura, altura), cor_fundo)
draw = ImageDraw.Draw(imagem)

# Usar uma fonte padrão ou carregar uma fonte personalizada (opcional)
try:
    fonte = ImageFont.truetype("arial.ttf", 20)
except:
    fonte = ImageFont.load_default()  # Fonte básica se 'arial' não estiver disponível

# Posicionar o texto na imagem (coordenadas x, y)
draw.text((50, 30), dados.strip(), fill="black", font=fonte)

# Salvar a imagem temporariamente (opcional)
caminho_imagem = "imagem_gerada.png"
imagem.save(caminho_imagem)

# Exibir a imagem no Streamlit
st.image(caminho_imagem, caption="Imagem Gerada", use_column_width=True)

# Remover o arquivo temporário (opcional)
os.remove(caminho_imagem)
