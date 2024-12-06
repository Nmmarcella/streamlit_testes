import zipfile
import pandas as pd
import streamlit as st
import os
from io import BytesIO

# Função para exibir a opção de download do arquivo ZIP Anexo_A
def download_zip():
    # Caminho para o arquivo Anexo_A.zip (o arquivo que você deseja que o usuário baixe)
    zip_file_path = 'Anexo_A.zip'  # Aqui você deve garantir que esse arquivo esteja no mesmo diretório do script

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

# Função para carregar os dados CSV após extração do ZIP
def load_data(csv_file):
    try:
        # Carregar o CSV extraído do ZIP
        data = pd.read_csv(csv_file, sep=";", encoding="latin-1")
        return data
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

# Título da aplicação
st.title('Download de Arquivo ZIP e Upload de Novo ZIP')

# Primeira parte: Download do arquivo ZIP Anexo_A
st.header("Baixar o arquivo ZIP Anexo_A")
download_zip()

# Segunda parte: Upload de um novo arquivo ZIP (Anexo_A.zip)
st.header("Agora, faça o upload do arquivo ZIP Anexo_A")

uploaded_file = st.file_uploader("Escolha o arquivo ZIP", type=["zip"])

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

    # Caminho do arquivo CSV extraído
    csv_file = os.path.join(extract_to, "Lubrificante_Anexo_A.csv")
    
    if os.path.exists(csv_file):
        # Carregar e exibir os dados do CSV
        data = load_data(csv_file)
        
        if data is not None:
            st.write(data)
            
            # Filtros de dados
            st.sidebar.header("Filtros")
            anos = st.sidebar.multiselect("Ano", sorted(data['Ano'].unique()))  # Ajuste conforme necessário
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
                import plotly.express as px

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

                # Gráfico de Evolução do Volume ao Longo do Tempo
                fig_line = px.line(
                    filtered_data.groupby(['Ano', 'Mês'])['Volume(L)'].sum().reset_index(),
                    x="Mês",
                    y="Volume(L)",
                    color="Ano",
                    title="Evolução do Volume ao Longo do Tempo",
                    labels={"Volume(L)": "Volume (L)", "Mês": "Mês"}
                )
                st.plotly_chart(fig_line)
            else:
                st.warning("Nenhum dado encontrado para gráficos.")

            # Dados Filtrados
            st.subheader("Dados Filtrados")
            st.dataframe(filtered_data)

            # Exportar Dados Filtrados
            if st.button("Exportar Dados Filtrados"):
                filtered_data.to_csv("dados_filtrados.csv", index=False)
                st.success("Dados exportados com sucesso!")
        else:
            st.warning("Não foi possível carregar os dados do arquivo CSV.")
    else:
        st.warning("Nenhum arquivo CSV encontrado no ZIP extraído.")
