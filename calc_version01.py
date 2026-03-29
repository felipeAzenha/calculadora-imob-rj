import streamlit as st
import plotly.express as px
import pandas as pd

# 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS
st.set_page_config(page_title="Calculadora Imobiliária RJ", page_icon="🏠", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eeeeee; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stSidebar"] { background-color: #f0f2f6; }
    .resumo-header { background-color: #4A4A4A; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .nota-info { background-color: #d1ecf1; color: #0c5460; padding: 10px; border-radius: 5px; border-left: 5px solid #bee5eb; font-size: 0.85em; margin-bottom: 15px; }
    .subtitulo-aviso { color: #666666; font-size: 0.9em; font-style: italic; margin-top: -15px; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)


# --- FUNÇÃO AUXILIAR DE FORMATAÇÃO PT-BR ---
def formar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- LÓGICA DE SINCRONIZAÇÃO (SESSION STATE) ---
if 'valor_imovel' not in st.session_state: st.session_state.valor_imovel = 550000.0
if 'perc_entrada' not in st.session_state: st.session_state.perc_entrada = 20.0
if 'valor_entrada' not in st.session_state: st.session_state.valor_entrada = st.session_state.valor_imovel * (
            st.session_state.perc_entrada / 100)
if 'itens_reforma' not in st.session_state: st.session_state.itens_reforma = []


def update_por_percentual():
    st.session_state.valor_entrada = st.session_state.valor_imovel * (st.session_state.perc_entrada / 100)


def update_por_valor():
    st.session_state.perc_entrada = (st.session_state.valor_entrada / st.session_state.valor_imovel) * 100


def adicionar_item():
    st.session_state.itens_reforma.append({"Descrição": "Novo Item", "Valor (R$)": 0.0})


def remover_item(index):
    st.session_state.itens_reforma.pop(index)


# 2. MENU LATERAL
with st.sidebar:
    st.header("⚙️ Configurações da Compra")
    st.session_state.valor_imovel = st.number_input("Valor do Imóvel (R$)", min_value=100000.0,
                                                    value=st.session_state.valor_imovel, step=10000.0,
                                                    on_change=update_por_percentual)
    valor_venal = st.number_input("Valor Venal / IPTU (R$ - Opcional)", min_value=0.0, value=0.0, step=10000.0)
    e_financiado = st.checkbox("Haverá Financiamento?", value=True)

    if e_financiado:
        st.slider("Percentual de Entrada (%)", 10.0, 99.0, key='perc_entrada', on_change=update_por_percentual)
        st.number_input("Valor da Entrada (R$)", min_value=st.session_state.valor_imovel * 0.1,
                        max_value=st.session_state.valor_imovel * 0.99, key='valor_entrada', on_change=update_por_valor)
        valor_financiado = st.session_state.valor_imovel - st.session_state.valor_entrada
        st.write(f"**Valor Financiado:** R$ {valor_financiado:,.2f}")
        valor_fgts = st.number_input("Valor do FGTS (R$)", min_value=0.0, value=st.session_state.get('fgts_val', 0.0))
        st.session_state['fgts_val'] = valor_fgts
        primeiro_imovel = st.checkbox("É o 1º Imóvel? (SFH/SFI)", value=False)
        entrada_liquida = st.session_state.valor_entrada - valor_fgts
    else:
        valor_financiado = 0.0
        entrada_liquida = st.session_state.valor_imovel
        valor_fgts = 0.0
        primeiro_imovel = False

    st.write("---")
    st.header("🛠️ Planejamento de Reforma")
    area_m2 = st.number_input("Área do Imóvel (m²)", min_value=1, value=70)
    st.button("➕ Adicionar Item de Reforma", on_click=adicionar_item)

    valor_total_obra = 0.0
    for i, item in enumerate(st.session_state.itens_reforma):
        col_desc, col_val, col_del = st.columns([3, 2, 0.5])
        with col_desc:
            st.session_state.itens_reforma[i]["Descrição"] = st.text_input(f"Item {i + 1}", value=item["Descrição"],
                                                                           key=f"desc_{i}")
        with col_val:
            st.session_state.itens_reforma[i]["Valor (R$)"] = st.number_input(f"R$ {i + 1}", min_value=0.0,
                                                                              value=item["Valor (R$)"], key=f"val_{i}")
        with col_del:
            st.button("🗑️", key=f"del_{i}", on_change=remover_item, args=(i,))
        valor_total_obra += st.session_state.itens_reforma[i]["Valor (R$)"]

# 3. LÓGICA DE CÁLCULO
base_calculo = max(st.session_state.valor_imovel, valor_venal)
itbi = base_calculo * 0.03
taxa_rgi = 0.007 * (0.5 if primeiro_imovel and e_financiado else 1.0)
custo_rgi = base_calculo * taxa_rgi
valor_escritura = 0.0 if e_financiado else (base_calculo * 0.006)
valor_banco = 3500.0 if e_financiado else 0.0
total_taxas = itbi + custo_rgi + valor_escritura + valor_banco
total_desembolso = entrada_liquida + total_taxas

# 4. DASHBOARD
st.title("🏠 Dashboard de Planejamento Imobiliário")
st.markdown(
    '<p class="subtitulo-aviso">Lembre-se que os cálculos são estimados em informações encontradas na internet, para informações precisas recomenda-se entrar em contato com seu banco e cartório da região.</p>',
    unsafe_allow_html=True)

resumo_tipo = "Imóvel Financiado" if e_financiado else "Compra à Vista"
st.markdown(
    f'<div class="resumo-header">VALOR DO IMÓVEL: R$ {st.session_state.valor_imovel:,.2f} | {resumo_tipo}</div>',
    unsafe_allow_html=True)

# ESTRUTURA DE CAPITAL
st.write("#### 💰 Estrutura de Capital")
c2_1, c2_2, c2_3 = st.columns(3)
with c2_1: st.metric("Entrada Líquida (Cash)", f"R$ {entrada_liquida:,.2f}")
with c2_2: st.metric("Valor Financiado", f"R$ {valor_financiado:,.2f}")
with c2_3: st.metric("FGTS Aplicado", f"R$ {valor_fgts:,.2f}")

# CUSTOS DE TRANSFERÊNCIA
st.write("#### 📑 Custos de Transferência")
if e_financiado: st.markdown(
    ' <div class="nota-info">ℹ️ <b>Nota:</b> Em compras financiadas, o contrato de financiamento bancário possui força de escritura pública (Lei 4.380/64).</div>',
    unsafe_allow_html=True)

c3_1, c3_2, c3_3, c3_4 = st.columns(4)
with c3_1: st.metric("ITBI (3%)", f"R$ {itbi:,.2f}")
with c3_2: st.metric("Registro (RGI)", f"R$ {custo_rgi:,.2f}")
with c3_3: st.metric("Escritura", f"R$ {valor_escritura:,.2f}")
with c3_4: st.metric("Taxas Bancárias", f"R$ {valor_banco:,.2f}")

st.success(f"### 💸 Valor necessário em mão para fechar contrato (+ FGTS se utilizável): R$ {total_desembolso:,.2f}")

# GRÁFICO COM MAPA DE CORES FIXO
st.write("---")
st.write("#### 📊 Composição dos Custos de Transferência")
df_custos = pd.DataFrame({
    'Custo': ['ITBI', 'Registro (RGI)', 'Taxas Extras'],
    'Valor': [itbi, custo_rgi, valor_escritura + valor_banco]
})
df_custos = df_custos[df_custos['Valor'] > 0]
mapa_cores = {'ITBI': '#4A4A4A', 'Registro (RGI)': '#0c5460', 'Taxas Extras': '#6c757d'}

fig = px.pie(df_custos, values='Valor', names='Custo', hole=.3,
             color='Custo', color_discrete_map=mapa_cores,
             title='Distribuição Percentual das Taxas')
st.plotly_chart(fig, use_container_width=True)

st.write("---")

# PLANEJAMENTO DE REFORMA
st.write("#### 🏗️ Planejamento de Reforma")
st.markdown(
    f'<div class="resumo-header" style="background-color: #6c757d;">VALOR TOTAL DA REFORMA: {formar_moeda(valor_total_obra)}</div>',
    unsafe_allow_html=True)

if st.session_state.itens_reforma:
    df_itens = pd.DataFrame(st.session_state.itens_reforma)
    df_itens['Relevância (%)'] = (df_itens['Valor (R$)'] / valor_total_obra * 100).round(
        2) if valor_total_obra > 0 else 0
    df_display = df_itens.copy()
    df_display['Valor (R$)'] = df_display['Valor (R$)'].apply(formar_moeda)
    df_display['Relevância (%)'] = df_display['Relevância (%)'].apply(lambda x: f"{x:.2f}%".replace(".", ","))
    st.table(df_display)

m1, m2 = st.columns(2)
with m1: st.metric("Valor Total / m²", formar_moeda(valor_total_obra / area_m2) if area_m2 > 0 else "R$ 0,00")
with m2: st.metric("Área Informada", f"{area_m2} m²")

st.write("---")
st.write("#### 📝 Observações Adicionais")
obs = st.text_area("Insira aqui anotações sobre o imóvel:",
                   placeholder="Ex: Estado de conservação, pontos de atenção na vistoria...")