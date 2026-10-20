import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="RADLA-Carne - Simulador Logístico e Ambiental",
    page_icon="🥩",
    layout="wide"
)

# Título Principal
st.title("🥩 RADLA-Carne")
st.subheader("Referencial de Avaliação do Desempenho Logístico e Ambiental da Cadeia da Carne Bovina")
st.markdown("---")

# Barra Lateral - Parâmetros de Entrada
st.sidebar.header("⚙️ Parâmetros da Simulação")

st.sidebar.subheader("1. Rota e Origem-Destino")
origem = st.sidebar.selectbox("Estado/Região de Origem", ["Mato Grosso (MT) - Cuiabá", "Mato Grosso do Sul (MS) - Campo Grande", "Goiás (GO) - Goiânia", "Pará (PA) - Redenção"])
destino = st.sidebar.selectbox("Porto de Escoamento / Destino", ["Porto de Santos (SP) - Rota Tradicional", "Porto de Paranaguá (PR) - Rota Sul", "Porto de Miritituba (PA) - Corredor Arco Norte"])

st.sidebar.subheader("2. Características da Frota e Carga")
distancia_km = st.sidebar.slider("Distância Percorrida (km)", min_value=800, max_value=3500, value=2200, step=50)
peso_carga_ton = st.sidebar.number_input("Carga Útil / Carcaça (Toneladas)", min_value=10.0, max_value=30.0, value=24.0, step=0.5)
tipo_veiculo = st.sidebar.selectbox("Configuração do Veículo", ["Carreta 6x2 (3 eixos)", "Bitrem 7 eixos", "Rodotrem 9 eixos"])

st.sidebar.subheader("3. Matriz Energética (Biodiesel)")
teor_biodiesel = st.sidebar.slider("Percentual de Mistura de Biodiesel (%)", min_value=10, max_value=30, value=14, step=1)
condicao_via = st.sidebar.selectbox("Condição Predominante da Via", ["Pavimentada / Boa", "Mista (Trechos com pavimento irregular)", "Não Pavimentada / Crítica (Ex: Arco Norte)"])

consumo_base = {"Carreta 6x2 (3 eixos)": 0.45, "Bitrem 7 eixos": 0.58, "Rodotrem 9 eixos": 0.72}[tipo_veiculo]
fator_via = {"Pavimentada / Boa": 1.0, "Mista (Trechos com pavimento irregular)": 1.15, "Não Pavimentada / Crítica (Ex: Arco Norte)": 1.30}[condicao_via]

consumo_total_litros = distancia_km * consumo_base * fator_via
fator_emissao_co2 = (2.68 * (1 - (teor_biodiesel / 100) * 0.75)) 
emissoes_totais_kg = consumo_total_litros * fator_emissao_co2
emissoes_por_t_km = emissoes_totais_kg / (peso_carga_ton * distancia_km) * 1000

custo_km_base = {"Carreta 6x2 (3 eixos)": 6.50, "Bitrem 7 eixos": 8.20, "Rodotrem 9 eixos": 10.50}[tipo_veiculo]
custo_total_frete = distancia_km * custo_km_base * (1.1 if "Não Pavimentada" in condicao_via else 1.0)
custo_por_tonelada = custo_total_frete / peso_carga_ton

vel_media = {"Pavimentada / Boa": 65, "Mista (Trechos com pavimento irregular)": 50, "Não Pavimentada / Crítica (Ex: Arco Norte)": 35}[condicao_via]
tempo_viagem_horas = distancia_km / vel_media

pontuacao_custo = max(0, 100 - (custo_por_tonelada / 150) * 100)
pontuacao_ambiental = max(0, 100 - (emissoes_por_t_km / 150) * 100)
pontuacao_operacional = max(0, 100 - (tempo_viagem_horas / 70) * 100)
indice_sintetico = (pontuacao_custo * 0.4) + (pontuacao_ambiental * 0.4) + (pontuacao_operacional * 0.2)

st.markdown("### 📊 Painel de Desempenho Logístico e Ambiental")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Custo Total do Frete", value=f"R$ {custo_total_frete:,.2f}", delta=f"R$ {custo_por_tonelada:.2f} / t")
with col2:
    st.metric(label="Emissões Totais de CO2e", value=f"{emissoes_totais_kg:,.1f} kg", delta=f"{emissoes_por_t_km:.1f} g/t·km")
with col3:
    st.metric(label="Tempo Estimado (Lead Time)", value=f"{tempo_viagem_horas:.1f} horas", delta=f"{tempo_viagem_horas/24:.1f} dias")
with col4:
    st.metric(label="Índice Sintético (ISSE)", value=f"{indice_sintetico:.1f} / 100", delta="Eficiência Geral")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💰 Dimensão Econômica", "🌿 Dimensão Ambiental", "🛣️ Infraestrutura e Rota"])

with tab1:
    st.markdown("#### Detalhamento de Custos e Eficiência Financeira")
    st.write(f"- **Custo por Quilômetro:** R$ {custo_km_base:.2f} / km")
    st.write(f"- **Impacto na Carga:** R$ {custo_por_tonelada:.2f} por tonelada de carne exportada.")
    st.info("💡 *Nota gerencial:* A rota selecionada reflete os custos médios das tabelas de referência de frete para o escoamento de carne bovina.")

with tab2:
    st.markdown("#### Balanço de Emissões e Impacto do Biodiesel")
    st.write(f"- **Consumo Estimado de Combustível:** {consumo_total_litros:,.1f} litros")
    st.write(f"- **Teor de Mistura considerado:** B{teor_biodiesel}")
    st.write(f"- **Intensidade de Carbono:** {emissoes_por_t_km:.2f} gramas de CO2e por tonelada-quilômetro.")
    st.success(f"🌱 A introdução da mistura obrigatória de {teor_biodiesel}% de biodiesel mitiga parcialmente a pegada fóssil da operação logística.")

with tab3:
    st.markdown("#### Análise de Corredores e Gargalos Logísticos")
    st.write(f"- **Origem:** {origem}")
    st.write(f"- **Destino:** {destino}")
    st.write(f"- **Condição Viária Atribuída:** {condicao_via}")
    st.warning("⚠️ *Ponto Crítico Identificado:* Trechos com pavimentação deficiente aumentam o consumo de combustível em até 30% e elevam o tempo de trânsito, afetando diretamente a integridade da cadeia fria.")

st.markdown("---")
st.caption("🚀 **RADLA-Carne v1.0** — Desenvolvido como Produto Técnico-Aplicado para o Mestrado Profissional em Administração (FCAV/UNESP). Base metodológica integrando dados públicos e literatura científica setorial.")
