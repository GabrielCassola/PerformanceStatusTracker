import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("📊 Dashboard de Adesão de Avaliações")


# =========================
# FUNÇÕES
# =========================
def carregar_dados(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file, sep=";")
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()

    df["Status"] = (
        df["Status"]
        .astype(str)
        .str.strip()
        .str.capitalize()
    )
    return df


def aplicar_filtros(df):
    st.sidebar.header("🔎 Filtros")

    def filtro(col, label):
        return st.sidebar.multiselect(
            label,
            sorted(df[col].dropna().unique())
        )

    nomes_filtros = {
        "Nome do Avaliador": "Avaliador",
        "Gestor do Avaliador": "Gestor",
        "Área do Avaliador": "Área",
        "Cargo do Avaliador": "Cargo",
        "Senioridade do Avaliador": "Senioridade"
    }

    filtros = {
        col: filtro(col, label)
        for col, label in nomes_filtros.items()
    }

    mostrar_pendentes = st.sidebar.toggle("Mostrar apenas pendentes")

    df_f = df.copy()

    for col, val in filtros.items():
        if val:
            df_f = df_f[df_f[col].isin(val)]

    if mostrar_pendentes:
        df_f = df_f[df_f["Status"] != "Finalizado"]

    st.sidebar.markdown("---")

    if len(df_f) != len(df):
        st.sidebar.caption(f"Exibindo {len(df_f):,} de {len(df):,} registros")
    else:
        st.sidebar.caption(f"{len(df)} registros totais")

    return df_f


def calcular_kpis(df_f):
    total_av = len(df_f)
    total_pessoas = df_f["Chave do Avaliado"].nunique()
    concluidas = (df_f["Status"] == "Finalizado").sum()
    pendentes = total_av - concluidas
    adesao = concluidas / total_av if total_av else 0

    return total_av, total_pessoas, concluidas, pendentes, adesao


def render_kpis(total_av, total_pessoas, pendentes, adesao):
    st.subheader("📌 Principais indicadores")

    cols = st.columns(4, gap="large")

    cols[0].metric("Avaliadores", total_pessoas)
    cols[1].metric("Avaliações", total_av)
    cols[2].metric("Adesão", f"{adesao:.1%}")
    cols[3].metric("Pendências", pendentes)


def render_grafico(df_f):
    st.subheader("📋 Adesão por grupo avaliativo")

    status_group = (
        df_f.groupby(["Grupo Avaliativo do Avaliado", "Status"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["Pendente", "Finalizado"], fill_value=0)
    )

    status_pct = status_group.div(status_group.sum(axis=1), axis=0)

    for col in ["Pendente", "Finalizado"]:
        if col not in status_pct.columns:
            status_pct[col] = 0

    fig = go.Figure()

    fig.add_bar(
        x=status_pct.index,
        y=status_pct["Pendente"],
        name="Pendente",
        text=[f"{v:.0%}" for v in status_pct["Pendente"]],
        customdata=status_group["Pendente"],
        marker_color="red",
        hovertemplate="Total: %{customdata}<br>Percentual: %{y:.0%}<extra></extra>"
    )

    fig.add_bar(
        x=status_pct.index,
        y=status_pct["Finalizado"],
        name="Finalizado",
        marker_color="green",
        text=[f"{v:.0%}" for v in status_pct["Finalizado"]],
        textposition="inside",
        customdata=status_group["Finalizado"],
        hovertemplate="Total: %{customdata}<br>Percentual: %{y:.0%}<extra></extra>"
    )

    fig.update_layout(
        barmode="stack",
        yaxis=dict(tickformat=".0%")
    )

    st.plotly_chart(fig, use_container_width=True)


def gerar_resumo(df_f):
    df_f["Concluido"] = df_f["Status"] == "Finalizado"

    resumo = (
        df_f.groupby("Nome do Avaliador")
        .agg(
            Total=("Status", "count"),
            Concluidas=("Concluido", "sum"),
            Gestor=("Gestor do Avaliador", "first"),
            Área=("Área do Avaliador", "first"),
            Cargo=("Cargo do Avaliador", "first"),
            Senioridade=("Senioridade do Avaliador", "first")
        )
    )

    resumo["Pendentes"] = resumo["Total"] - resumo["Concluidas"]
    resumo["% concluído"] = (resumo["Concluidas"] / resumo["Total"]).fillna(0)

    resumo = resumo.sort_values("% concluído")

    resumo_display = resumo.copy()
    resumo_display["% concluído"] = resumo_display["% concluído"].map(lambda x: f"{x:.1%}")

    ordem_colunas = [
    "Nome do Avaliador",
    "Gestor",
    "Área",
    "Cargo",
    "Senioridade",
    "Total",
    "Concluidas",
    "Pendentes",
    "% concluído"
]

    resumo_display = resumo_display.reset_index()
    resumo_display = resumo_display[ordem_colunas]

    return resumo, resumo_display


def render_tabela(resumo_display):
    st.subheader("👥 Progresso por avaliador")

    event = st.dataframe(
        resumo_display,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    return event


def render_detalhamento(event, resumo_display, df_f):
    st.subheader("🔎 Detalhamento das avaliações")

    if event.selection.rows:
        idx = event.selection.rows[0]
        linha = resumo_display.iloc[idx]
        avaliador = linha["Nome do Avaliador"]

        df_av = df_f[df_f["Nome do Avaliador"] == avaliador]

        total = len(df_av)
        concl = (df_av["Status"] == "Finalizado").sum()
        pend = total - concl
        perc = concl / total if total else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total", total)
        c2.metric("Pendentes", pend)
        c3.metric("Conclusão", f"{perc:.1%}")

        pendencias = df_av[df_av["Status"] != "Finalizado"]

        st.write("### Pendências")

        if pendencias.empty:
            st.success("Nenhuma pendência")
        else:
            st.dataframe(
                pendencias[[
                    "Nome do Avaliado",
                    "Grupo Avaliativo do Avaliado",
                    "Status"
                ]],
                use_container_width=True
            )
    else:
        st.info("Selecione um avaliador na tabela acima")


def exportar_excel(df_f, resumo, total_pessoas, total_av, adesao, pendentes):
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:

        kpis = pd.DataFrame({
            "Métrica": ["Avaliadores", "Avaliações", "Adesão", "Pendências"],
            "Valor": [
                total_pessoas,
                total_av,
                f"{adesao:.2%}",
                pendentes
            ]
        })
        kpis.to_excel(writer, index=False, sheet_name="Resumo Executivo")

        resumo.reset_index().to_excel(writer, index=False, sheet_name="Resumo Avaliador")

        df_f[df_f["Status"] != "Finalizado"].to_excel(writer, index=False, sheet_name="Pendencias")

        df_f.to_excel(writer, index=False, sheet_name="Base de Dados")

    buffer.seek(0)

    st.download_button(
        label="⬇️ Exportar relatório completo",
        data=buffer,
        file_name="Relatorio_Adesao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


# =========================
# UI - Upload
# =========================

with st.expander("ℹ️ Sobre o dashboard"):
    st.markdown("""
    Este dashboard é uma ferramenta para acompanhar e analisar a adesão da AVD em tempo real, permitindo uma visão clara do andamento das avaliações e apoiando a tomada de decisão ao longo do processo.

    Com ele, é possível:
    - Verificar a adesão por grupo avaliativo
    - Acompanhar avaliações detalhadas por pessoa
    - Exportar todo o conteúdo do dashboard para análises adicionais

    Utilize os filtros disponíveis à esquerda para refinar as informações exibidas e facilitar sua análise.

    Para visualizar os resultados das avaliações:
    1. Acesse a rodada desejada
    2. Vá até a aba "Resultado"
    """)

with st.expander("ℹ️ Como exportar os dados"):
    st.markdown("""
    1. Acesse a rodada que deseja analisar
    2. Vá até a aba "Avaliação"     
    3. Clique no botão "Exportações"
    4. Selecione a opção "Exportar status por avaliador-avaliado"
    """)

file = st.file_uploader( "Faça upload do arquivo 'evaluations_by_pair' exportado da plataforma (CSV ou Excel)",type=["csv", "xlsx"])


# =========================
# EXECUÇÃO
# =========================
if file:

    df = carregar_dados(file)
    df_f = aplicar_filtros(df)

    total_av, total_pessoas, concluidas, pendentes, adesao = calcular_kpis(df_f)

    render_kpis(total_av, total_pessoas, pendentes, adesao)
    render_grafico(df_f)

    resumo, resumo_display = gerar_resumo(df_f)

    event = render_tabela(resumo_display)

    render_detalhamento(event, resumo_display, df_f)

    exportar_excel(df_f, resumo, total_pessoas, total_av, adesao, pendentes)

else:
    st.info("Faça upload de um arquivo para iniciar.")