import zipfile
import pandas as pd
import streamlit as st
import os
from io import BytesIO
import plotly.express as px
import time

# Função para exibir a opção de download do arquivo ZIP Anexo_A do GitHub
def download_zip_from_github():
    github_url = "https://github.com/Nmmarcella/streamlit_testes/blob/main/Lubrificante_Anexo_A.zip?raw=true"
    st.markdown(f"[Baixar arquivo ZIP Anexo_A](<{github_url}>)")

# Função para descompactar o arquivo ZIP enviado
def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        progress_bar = st.progress(0)  # Inicializa a barra de progresso
        total_files = len(file_list)
        
        for i, file in enumerate(file_list):
            zip_ref.extract(file, extract_to)
            progress_bar.progress((i + 1) / total_files)  # Atualiza a barra de progresso
            time.sleep(0.1)  # Pequena pausa para garantir feedback visual

# Função otimizada para carregar os dados CSV
@st.cache_data
def load_data(csv_file):
    try:
        data = pd.read_csv(csv_file, sep=";", encoding="latin-1", low_memory=False)
        return data
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

# Título da aplicação
st.title('Download de Arquivo ZIP e Upload de Novo ZIP')

# Primeira parte: Download do arquivo ZIP Anexo_A do GitHub
st.header("Baixar o arquivo ZIP Anexo_A")
download_zip_from_github()

# Segunda parte: Upload de um novo arquivo ZIP (Anexo_A.zip)
st.header("Agora, faça o upload do arquivo ZIP Anexo_A")

uploaded_file = st.file_uploader("Escolha o arquivo ZIP", type=["zip"])

# Se o usuário fez o upload de um arquivo ZIP
if uploaded_file is not None:
    extract_to = "extracted_files/"
    
    # Cria a pasta de extração se não existir
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    
    st.info("Extraindo o arquivo ZIP...")  # Feedback ao usuário
    
    # Descompacta o arquivo ZIP com barra de progresso
    unzip_file(uploaded_file, extract_to)
    
    st.success("Arquivo ZIP carregado e extraído com sucesso!")

    # Caminho do arquivo CSV extraído
    csv_file = os.path.join(extract_to, "Lubrificante_Anexo_A.csv")
    
    if os.path.exists(csv_file):
        # Carregar e exibir os dados do CSV
        st.info("Carregando os dados do arquivo CSV...")  # Feedback ao usuário
        data = load_data(csv_file)
        
        if data is not None:
            st.write(data.head())  # Exibe os primeiros registros
            
            # Filtros de dados
            st.sidebar.header("Filtros")
            anos = st.sidebar.multiselect("Ano", sorted(data['Ano'].unique()))
            meses = st.sidebar.multiselect("Mês", sorted(data['Mês'].unique()))
            produtos = st.sidebar.multiselect("Produto", data['Descrição do Produto'].unique())
            ufs_origem = st.sidebar.multiselect("UF de Origem", data['UF de Origem'].unique())
            ufs_destino = st.sidebar.multiselect("UF do Destinatário", data['UF do Destinatário'].unique())

            # Aplicando filtros
            filtered_data = data

            if anos:
                filtered_data = filtered_data[filtered_data['Ano'].isin(anos)]
            if meses:
                filtered_data = filtered_data[filtered_data['Mês'].isin(meses)]
            if produtos:
                filtered_data = filtered_data[filtered_data['Descrição do Produto'].isin(produtos)]
            if ufs_origem:
                filtered_data = filtered_data[filtered_data['UF de Origem'].isin(ufs_origem)]
            if ufs_destino:
                filtered_data = filtered_data[filtered_data['UF do Destinatário'].isin(ufs_destino)]

            # Indicadores
            st.subheader("Indicadores")
            if not filtered_data.empty:
                total_volume = filtered_data['Volume(L)'].sum()
                st.metric("Volume Total", f"{total_volume:,.2f} litros")
                
                produto_mais_vendido = (
                    filtered_data.groupby("Descrição do Produto")['Volume(L)'].sum().idxmax()
                )
                st.metric("Produto Mais Vendido", produto_mais_vendido)
            else:
                st.warning("Nenhum dado encontrado para os filtros selecionados.")

            # Gráficos de Análise
            st.subheader("Gráficos de Análise")
            if not filtered_data.empty:
                # Gráfico de Volume por UF do Destinatário
                fig_bar = px.bar(
                    filtered_data,
                    x="UF do Destinatário",
                    y="Volume(L)",
                    color="Ano",
                    title="Volume por UF do Destinatário",
                    labels={"Volume(L)": "Volume (L)"},
                    text="Volume(L)"
                )
                st.plotly_chart(fig_bar)

                # Gráfico de Proporção por Região do Destinatário
                fig_pie = px.pie(
                    filtered_data,
                    names="Região do Destinatário",
                    values="Volume(L)",
                    title="Proporção por Região do Destinatário"
                )
                st.plotly_chart(fig_pie)
            else:
                st.warning("Nenhum dado encontrado para gráficos.")

            # Dados Filtrados
            st.subheader("Dados Filtrados")
            st.dataframe(filtered_data)
        else:
            st.warning("Não foi possível carregar os dados do arquivo CSV.")
    else:
        st.warning("Nenhum arquivo CSV encontrado no ZIP extraído.")
