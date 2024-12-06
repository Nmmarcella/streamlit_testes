import zipfile
import pandas as pd
import streamlit as st
import os
from io import BytesIO

# Função para criar um arquivo ZIP a partir de arquivos existentes
def create_zip_from_folder(folder_path):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder_name, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
    zip_buffer.seek(0)
    return zip_buffer

# Função para exibir a opção de download do arquivo ZIP Anexo_A
def download_zip():
    # Caminho para o arquivo Anexo_A.zip (o arquivo que você deseja que o usuário baixe)
    zip_file_path = 'Anexo_A.zip'
    
    # Verificar se o arquivo ZIP existe
    if os.path.exists(zip_file_path):
        with open(zip_file_path, 'rb') as f:
            st.download_button(
                label="Baixar arquivo ZIP Anexo_A",
                data=f,
                file_name="Anexo_A.zip",
                mime="application/zip"
            )
    else:
        st.error("Arquivo Anexo_A.zip não encontrado para download.")

# Função para descompactar o arquivo ZIP enviado
def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Título da aplicação
st.title('Download de Arquivo ZIP e Upload de Novo ZIP')

# Primeira parte: Download do arquivo ZIP Anexo_A
st.header("Baixar o arquivo ZIP Anexo_A")
download_zip()

# Segunda parte: Upload de um novo arquivo ZIP (Anexo_A.zip)
uploaded_file = st.file_uploader("Agora, faça o upload do arquivo ZIP Anexo_A", type=["zip"])

# Se o usuário fez o upload de um arquivo ZIP
if uploaded_file is not None:
    extract_to = "extracted_files/"
    
    # Cria a pasta de extração se não existir
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    
    # Descompacta o arquivo ZIP
    unzip_file(uploaded_file, extract_to)
    
    # Exibe uma mensagem de sucesso
    st.success("Arquivo ZIP carregado e extraído com sucesso!")

    # Exemplo de carregamento de um arquivo CSV extraído (se presente)
    csv_file = os.path.join(extract_to, "Lubrificante_Anexo_A.csv")
    if os.path.exists(csv_file):
        data = pd.read_csv(csv_file, sep=";", encoding="latin-1")
        st.write(data)
    else:
        st.warning("Nenhum arquivo CSV encontrado no ZIP extraído.")
