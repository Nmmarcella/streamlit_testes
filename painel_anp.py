import streamlit as st
import pandas as pd
import plotly.express as px

#func para carregar dados
@st.cache_data
def load_data():
    #caminho
    file_path = r"C:\Users\marce\painel-dinamico-dado-lubrificante\Lubrificante_Anexo_A.csv"
    data = pd.read_csv(file_path, sep=";", encoding="latin-1")
    return data

#carregando dados
data = load_data()

#titulo
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