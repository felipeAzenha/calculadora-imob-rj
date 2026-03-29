import streamlit as st
import plotly.express as px
import pandas as pd


# 1. FUNÇÃO PARA INJETAR O GOOGLE ANALYTICS
def inject_ga(ga_id):
    ga_code = f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{ga_id}');
    </script>
    """
    st.markdown(ga_code, unsafe_allow_html=True)


# SEU ID DE MENSURAÇÃO CONFIGURADO
inject_ga("G-SCKRXZTH4G")

# 2. CONFIGURAÇÃO DA PÁGINA E ESTILOS
st.set_page_config(page_title="Calculadora Imobiliária RJ", page_icon="🏠", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eeeeee; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stSidebar"] { background-color: #f0f2f6; }
    .resumo-header { background-color: #4A4A4A; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .subtitulo-aviso { color: #666666; font-size: 0.9em; font-style: italic; margin-top: -15px; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)


# --- FUNÇÃO DE FORMATAÇÃO PT-BR ---
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


# 3. MENU LATERAL
with st.sidebar:
    st.header("⚙️ Configurações da Compra")
    st.session_state.valor_imovel = st.number_input("Valor do Imóvel (R$)", min_value=100000.0,
                                                    value=st.session_state.valor_imovel, step=10000.0,
                                                    on_change=update_por_percentual)
    valor_venal = st.number_input("Valor Venal / IPTU (R$)", min_value=0.0, value=0.0)
    e_financiado = st.checkbox("Haverá Financiamento?", value=True)

    if e_financiado:
        st.slider("Percentual de Entrada (%)", 10.0, 99.0, key='perc_entrada', on_change=update_por_percentual)
        st.number_input("Valor da Entrada (R$)", min_value=0.0, key='valor_entrada', on_change=update_por_valor)
        valor_financiado = st.session_state.valor_imovel - st.session_state.valor_entrada
        valor_fgts = st.number_input("Valor do FGTS (R$)", min_value=0.0, value=st.session_state.get('fgts_val', 0.0))
        st.session_state['fgts_val'] = valor_fgts
        primeiro_imovel = st.checkbox("É o 1º Imóvel?", value=False)
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
        with col_desc: st.session_state.itens_reforma[i]["Descrição"] = st.text_input(f"Item {i + 1}",
                                                                                      value=item["Descrição"],
                                                                                      key=f"d_{i}")
        with col_val: st.session_state.itens_reforma[i]["Valor (R$)"] = st.number_input(f"R$ {i + 1}", min_value=0.0,
                                                                                        value=item["Valor (R$)"],
                                                                                        key=f"v_{i}")
        with col_del: st.button("🗑️", key=f"del_{i}", on_click=remover_item, args=(i,))
        valor_total_obra += st.session_state.itens_reforma[i]["Valor (R$)"]

    # ESPAÇO DE RENTABILIZAÇÃO (BANNER DE PARCEIRO)
    st.write("---")
    st.markdown("""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e0e0e0; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h4 style="color: #2e7d32; margin-top: 0;">🛡️ Seguro e Vistoria</h4>
            <p style="font-size: 0.85em; color: #666; line-height: 1.4;">Não compre no escuro! Garanta a vistoria técnica e o seguro do seu novo lar no Rio.</p>
            <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
            <a href="https://www.google.com.br" target="_blank" 
               style="display: inline-block; background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 0.9em;">
               CONFERIR OFERTAS
            </a>
            <p style="font-size: 0.65em; color: #aaa; margin-top: 10px;">Parceria verificada Calculadora Imob</p>
        </div>
    """, unsafe_allow_html=True)

# 4. DASHBOARD PRINCIPAL
st.title("🏠 Dashboard de Planejamento Imobiliário")
st.markdown(
    '<p class="subtitulo-aviso">Estimativa baseada em dados públicos. Recomenda-se consultar seu banco e cartório local.</p>',
    unsafe_allow_html=True)

base_calc = max(st.session_state.valor_imovel, valor_venal)
itbi = base_calc * 0.03
taxa_rgi = 0.007 * (0.5 if primeiro_imovel and e_financiado else 1.0)
custo_rgi = base_calc * taxa_rgi
v_escritura = 0.0 if e_financiado else (base_calc * 0.006)
v_banco = 3500.0 if e_financiado else 0.0
total_taxas = itbi + custo_rgi + v_escritura + v_banco
total_desembolso = entrada_liquida + total_taxas

st.markdown(f'<div class="resumo-header">VALOR DO IMÓVEL: {formar_moeda(st.session_state.valor_imovel)}</div>',
            unsafe_allow_html=True)

# ESTRUTURA DE CAPITAL
st.write("#### 💰 Estrutura de Capital")
c1, c2, c3 = st.columns(3)
with c1: st.metric("Entrada (Cash)", formar_moeda(entrada_liquida))
with c2: st.metric("Valor Financiado", formar_moeda(valor_financiado))
with c3: st.metric("FGTS Aplicado", formar_moeda(valor_fgts))

# TAXAS COM GRÁFICO FIXO
st.write("---")
c_graf, c_met = st.columns([1.5, 1])

with c_graf:
    df_c = pd.DataFrame({'Custo': ['ITBI', 'RGI', 'Outros'], 'Valor': [itbi, custo_rgi, v_escritura + v_banco]})
    fig = px.pie(df_c, values='Valor', names='Custo', hole=.3, color='Custo',
                 color_discrete_map={'ITBI': '#4A4A4A', 'RGI': '#0c5460', 'Outros': '#6c757d'})
    st.plotly_chart(fig, use_container_width=True)

with c_met:
    st.metric("ITBI (3%)", formar_moeda(itbi))
    st.metric("Registro (RGI)", formar_moeda(custo_rgi))
    st.metric("Taxas Extras", formar_moeda(v_escritura + v_banco))

st.success(f"### 💸 Total necessário em mãos: {formar_moeda(total_desembolso)}")

# REFORMA
st.write("---")
st.write("#### 🏗️ Planejamento de Reforma")
st.markdown(
    f'<div class="resumo-header" style="background-color: #6c757d;">VALOR TOTAL DA REFORMA: {formar_moeda(valor_total_obra)}</div>',
    unsafe_allow_html=True)

if st.session_state.itens_reforma:
    df_it = pd.DataFrame(st.session_state.itens_reforma)
    df_it['%'] = (df_it['Valor (R$)'] / valor_total_obra * 100).round(2) if valor_total_obra > 0 else 0
    df_disp = df_it.copy()
    df_disp['Valor (R$)'] = df_disp['Valor (R$)'].apply(formar_moeda)
    df_disp['%'] = df_disp['%'].apply(lambda x: f"{x:.2f}%".replace(".", ","))
    st.table(df_disp)

st.metric("Custo estimado por m²", formar_moeda(valor_total_obra / area_m2) if area_m2 > 0 else "R$ 0,00")

# OBSERVAÇÕES
st.write("---")
st.write("#### 📝 Observações Adicionais")
st.text_area("Anotações da visita:", placeholder="Ex: Precisa trocar fiação, sol da manhã, etc...")