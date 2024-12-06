import zipfile
import pandas as pd
import streamlit as st
import os
from io import BytesIO

#descompact zip
def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

#upload
st.title('Upload de Arquivo ZIP')
uploaded_file = st.file_uploader("Escolha o arquivo ZIP", type=["zip"])

if uploaded_file is not None:
    #way
    extract_to = "extracted_files/"

    
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    #descompact
    unzip_file(uploaded_file, extract_to)
    
    
    csv_file = os.path.join(extract_to, "Lubrificante_Anexo_A.csv")  
    

    csv_file = os.path.join(extract_to, "Lubrificante_Anexo_A.csv")  

    try:
        data = pd.read_csv(csv_file, sep=";", encoding="latin-1")
        st.write(data)
        
        # Verifique se a coluna 'Ano' existe
        if 'Ano' not in data.columns:
            st.error("Coluna 'Ano' não encontrada no arquivo CSV.")
        else:
            st.success("Arquivo CSV carregado com sucesso.")
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")

if 'data' in locals() and 'Ano' in data.columns:
    st.title("Painel Dinâmico - Vendas de Produtos Lubrificantes (ANP)")


#filters
st.sidebar.header("Filtros")
anos = st.sidebar.multiselect("Ano", sorted(data['Ano'].unique()))  # Ajuste conforme necessário
meses = st.sidebar.multiselect("Mês", sorted(data['Mês'].unique()))
produtos = st.sidebar.multiselect("Produto", data['Descrição do Produto'].unique())
ufs_origem = st.sidebar.multiselect("UF de Origem", data['UF de Origem'].unique())
ufs_destino = st.sidebar.multiselect("UF do Destinatário", data['UF do Destinatário'].unique())

#aplicando filters
filtered_data = data

#verific o filter
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

#kpis
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

#graphs
st.subheader("Gráficos de Análise")
if not filtered_data.empty:
    #volume por uf
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

    
    fig_pie = px.pie(
        filtered_data,
        names="Região do Destinatário",
        values="Volume(L)",
        title="Proporção por Região do Destinatário"
    )
    st.plotly_chart(fig_pie)

    
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


st.subheader("Dados Filtrados")
st.dataframe(filtered_data)


if st.button("Exportar Dados Filtrados"):
    filtered_data.to_csv("dados_filtrados.csv", index=False)
    st.success("Dados exportados com sucesso!")
