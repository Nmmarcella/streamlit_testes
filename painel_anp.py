import zipfile
import pandas as pd
import streamlit as st
import os
from io import BytesIO
import plotly.express as px

# descompacta o arquivo ZIP
def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# título da aplicação
st.title('Upload de Arquivo ZIP')
uploaded_file = st.file_uploader("Escolha o arquivo ZIP", type=["zip"])

# se o arquivo for enviado
if uploaded_file is not None:
    extract_to = "extracted_files/"
    
    # cria a pasta de extração se não existir
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    # descompacta o arquivo ZIP
    unzip_file(uploaded_file, extract_to)
    
    csv_file = os.path.join(extract_to, "Lubrificante_Anexo_A.csv")  

    try:
        # carrega o arquivo CSV
        data = pd.read_csv(csv_file, sep=";", encoding="latin-1")
        st.write(data)
        
        # verifica se a coluna 'Ano' existe
        if 'Ano' not in data.columns:
            st.error("Coluna 'Ano' não encontrada no arquivo CSV.")
        else:
            st.success("Arquivo CSV carregado com sucesso.")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")

# se o arquivo foi carregado e contém a coluna 'Ano'
if 'data' in locals() and 'Ano' in data.columns:
    # título do painel dinâmico
    st.title("Painel Dinâmico - Vendas de Produtos Lubrificantes (ANP)")

    # filtros no painel lateral
    st.sidebar.header("Filtros")
    anos = st.sidebar.multiselect("Ano", sorted(data['Ano'].unique()))  # ajusta conforme necessário
    meses = st.sidebar.multiselect("Mês", sorted(data['Mês'].unique()))
    produtos = st.sidebar.multiselect("Produto", data['Descrição do Produto'].unique())
    ufs_origem = st.sidebar.multiselect("UF de Origem", data['UF de Origem'].unique())
    ufs_destino = st.sidebar.multiselect("UF do Destinatário", data['UF do Destinatário'].unique())

    # aplica os filtros
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

    # indicadores
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

    # gráficos de análise
    st.subheader("Gráficos de Análise")
    if not filtered_data.empty:
        # gráfico de barras por UF do Destinatário
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

        # gráfico de pizza por Região do Destinatário
        fig_pie = px.pie(
            filtered_data,
            names="Região do Destinatário",
            values="Volume(L)",
            title="Proporção por Região do Destinatário"
        )
        st.plotly_chart(fig_pie)

        # gráfico de linha da evolução do volume ao longo do tempo
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

    # dados filtrados
    st.subheader("Dados Filtrados")
    st.dataframe(filtered_data)

    # exportação dos dados filtrados
    if st.button("Exportar Dados Filtrados"):
        filtered_data.to_csv("dados_filtrados.csv", index=False)
        st.success("Dados exportados com sucesso!")
else:
    st.error("O arquivo CSV não foi carregado corretamente ou não contém a coluna 'Ano'.")
