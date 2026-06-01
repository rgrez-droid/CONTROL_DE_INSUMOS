import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from pathlib import Path

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="ANÁLISIS DE INSUMOS CTO MULCHÉN",
    page_icon="📊",
    layout="wide"
)

ARCHIVO_EXCEL = "Control_Insumos.xlsx"
HOJA_DATOS = "Fact_Solped_PBI"

LOGO_SUPERIOR = "logo1.png"
SELLO_AGUA = "logoredondo.png"

TIPO_FIJO = "Gasto"

PRESUPUESTO_MENSUAL = 3728742
PRESUPUESTO_ANUAL = PRESUPUESTO_MENSUAL * 12

GASTO_ANUAL_ROPA_TRABAJO = 9000000
GASTO_MENSUAL_ROPA_TRABAJO = GASTO_ANUAL_ROPA_TRABAJO / 12


# ============================================================
# FUNCIONES GENERALES
# ============================================================

def imagen_base64(ruta):
    ruta = Path(ruta)
    if ruta.exists():
        with open(ruta, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return None


def formato_clp(valor):
    try:
        monto = "{:,.0f}".format(float(valor)).replace(",", ".")
        return f"CLP $ {monto}"
    except:
        return "CLP $ 0"


def formato_clp_html(valor):
    try:
        monto = "{:,.0f}".format(float(valor)).replace(",", ".")
        return (
            f'<span class="monto-clp">'
            f'<span class="moneda-clp">CLP &#36;</span>'
            f'<span class="numero-clp">{monto}</span>'
            f'</span>'
        )
    except:
        return (
            f'<span class="monto-clp">'
            f'<span class="moneda-clp">CLP &#36;</span>'
            f'<span class="numero-clp">0</span>'
            f'</span>'
        )


def formato_porcentaje(valor):
    try:
        return f"{valor:.1%}".replace(".", ",")
    except:
        return "0,0%"


def cargar_datos():
    try:
        df = pd.read_excel(ARCHIVO_EXCEL, sheet_name=HOJA_DATOS)
    except Exception as e:
        st.error(f"No se pudo cargar el archivo Excel: {e}")
        st.stop()

    columnas_requeridas = ["Año", "Mes", "Fecha_Mes", "Área", "Monto_CLP", "Tipo"]
    faltantes = [col for col in columnas_requeridas if col not in df.columns]

    if faltantes:
        st.error(f"Faltan columnas en la hoja '{HOJA_DATOS}': {faltantes}")
        st.stop()

    df["Fecha_Mes"] = pd.to_datetime(df["Fecha_Mes"], errors="coerce")
    df["Monto_CLP"] = pd.to_numeric(df["Monto_CLP"], errors="coerce").fillna(0)
    df = df.dropna(subset=["Año", "Mes", "Área", "Tipo"])

    return df


def ordenar_meses(lista_meses):
    orden = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Setiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12,
    }

    return sorted(lista_meses, key=lambda x: orden.get(str(x), 99))


def aplicar_formato_eje_clp(fig, df_valores, columna="Monto_CLP", titulo_eje="Monto CLP"):
    if df_valores.empty:
        return fig

    maximo = df_valores[columna].abs().max()
    minimo = df_valores[columna].min()

    if maximo <= 0:
        tickvals = [0]
    else:
        tickvals = [
            -maximo if minimo < 0 else 0,
            0,
            maximo * 0.25,
            maximo * 0.50,
            maximo * 0.75,
            maximo
        ]

    tickvals = sorted(list(set(tickvals)))
    ticktext = [formato_clp(v) for v in tickvals]

    fig.update_yaxes(
        title_text=titulo_eje,
        tickmode="array",
        tickvals=tickvals,
        ticktext=ticktext,
        showgrid=True,
        exponentformat="none",
        separatethousands=False
    )

    return fig


def tarjeta_metrica(titulo, valor, subtitulo=None, clase_extra=""):
    subtitulo_html = ""
    if subtitulo:
        subtitulo_html = f'<div class="metric-subtitle">{subtitulo}</div>'

    st.markdown(
        f"""
        <div class="metric-card {clase_extra}">
            <div class="metric-title">{titulo}</div>
            <div class="metric-value">{valor}</div>
            {subtitulo_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def evaluar_estado_presupuestario(uso_presupuesto):
    if uso_presupuesto <= 0.85:
        return "Dentro de presupuesto", "estado-ok", "Controlado"
    elif uso_presupuesto <= 1:
        return "Alerta presupuestaria", "estado-alerta", "Requiere seguimiento"
    else:
        return "Sobreconsumo", "estado-critico", "Requiere acción correctiva"


# ============================================================
# DISEÑO VISUAL / SELLO DE AGUA
# ============================================================

sello_b64 = imagen_base64(SELLO_AGUA)

sello_css = ""
if sello_b64:
    sello_css = f"""
    .stApp::before {{
        content: "";
        position: fixed;
        top: 17%;
        left: 50%;
        transform: translateX(-50%);
        width: 760px;
        height: 760px;
        background-image: url("data:image/png;base64,{sello_b64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        opacity: 0.095;
        z-index: 0;
        pointer-events: none;
    }}
    """
else:
    sello_css = ""


st.markdown(
    f"""
    <style>
    {sello_css}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        position: relative;
        z-index: 1;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #f1f5f9;
    }}

    h1 {{
        color: #0f172a;
        font-weight: 850;
        letter-spacing: 0.4px;
    }}

    h2, h3 {{
        color: #0f172a;
        font-weight: 800;
    }}

    .texto-intro {{
        font-size: 17px;
        line-height: 1.5;
        color: #334155;
        max-width: 980px;
    }}

    .logo-box {{
        padding-top: 70px;
    }}

    .metric-card {{
        background: rgba(255,255,255,0.97);
        padding: 18px;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0px 5px 18px rgba(15, 23, 42, 0.08);
        min-height: 112px;
        margin-bottom: 14px;
    }}

    .metric-title {{
        font-size: 14px;
        font-weight: 700;
        color: #475569;
        margin-bottom: 8px;
    }}

    .metric-value {{
        font-size: 27px;
        font-weight: 850;
        color: #0f172a;
        line-height: 1.15;
        word-break: normal;
    }}

    .metric-subtitle {{
        margin-top: 8px;
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
    }}

    .monto-clp {{
        display: inline-flex;
        flex-direction: row;
        align-items: baseline;
        gap: 7px;
        white-space: nowrap;
    }}

    .moneda-clp {{
        display: inline-block;
        font-weight: 850;
    }}

    .numero-clp {{
        display: inline-block;
        font-weight: 850;
    }}

    .estado-ok {{
        border-left: 7px solid #16a34a;
    }}

    .estado-alerta {{
        border-left: 7px solid #f59e0b;
    }}

    .estado-critico {{
        border-left: 7px solid #dc2626;
    }}

    .filtro-fijo {{
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        font-size: 15px;
        color: #0f172a;
        font-weight: 650;
        margin-bottom: 12px;
    }}

    .nota-presupuesto {{
        background: rgba(248,250,252,0.95);
        border-left: 5px solid #0f172a;
        padding: 16px 20px;
        border-radius: 12px;
        color: #334155;
        font-size: 15px;
        margin-bottom: 18px;
        line-height: 1.65;
    }}

    .resumen-ejecutivo {{
        background: linear-gradient(135deg, rgba(248,250,252,0.96) 0%, rgba(238,242,255,0.96) 100%);
        border: 1px solid #dbeafe;
        border-left: 6px solid #1d4ed8;
        padding: 18px 22px;
        border-radius: 16px;
        color: #1e293b;
        font-size: 16px;
        line-height: 1.65;
        margin-bottom: 24px;
        box-shadow: 0px 5px 16px rgba(15, 23, 42, 0.06);
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CARGA DE DATOS
# ============================================================

df = cargar_datos()

if TIPO_FIJO in df["Tipo"].unique():
    df = df[df["Tipo"] == TIPO_FIJO].copy()


# ============================================================
# GASTO ROPA DE TRABAJO CARGADO AL ÁREA EPP
# ============================================================

df["Detalle"] = "Gasto registrado Excel"

meses_base = (
    df[["Año", "Mes", "Fecha_Mes"]]
    .drop_duplicates()
    .copy()
)

df_ropa = meses_base.copy()
df_ropa["Área"] = "EPP"
df_ropa["Tipo"] = TIPO_FIJO
df_ropa["Monto_CLP"] = GASTO_MENSUAL_ROPA_TRABAJO
df_ropa["Detalle"] = "Ropa de trabajo"

df = pd.concat([df, df_ropa], ignore_index=True)


# ============================================================
# ENCABEZADO PRINCIPAL
# ============================================================

col_titulo, col_logo = st.columns([5, 1])

with col_titulo:
    st.title("ANÁLISIS DE INSUMOS CTO MULCHÉN")

    st.markdown(
        """
        <div class="texto-intro">
            Herramienta de análisis ejecutivo orientada al seguimiento y control mensual de los insumos
            asociados al contrato, incorporando el gasto de ropa de trabajo dentro del área EPP,
            sin modificar el presupuesto oficial asignado.
        </div>
        """,
        unsafe_allow_html=True
    )

with col_logo:
    st.markdown('<div class="logo-box">', unsafe_allow_html=True)

    if Path(LOGO_SUPERIOR).exists():
        st.image(LOGO_SUPERIOR, use_container_width=True)
    else:
        st.info("Agregar logo1.png")

    st.markdown('</div>', unsafe_allow_html=True)

st.divider()


# ============================================================
# FILTROS
# ============================================================

st.sidebar.header("Filtros de análisis")

anios = sorted(df["Año"].dropna().unique())
meses = ordenar_meses(df["Mes"].dropna().unique())
areas = sorted(df["Área"].dropna().unique())
detalles = sorted(df["Detalle"].dropna().unique())

filtro_anio = st.sidebar.multiselect(
    "Año",
    options=anios,
    default=anios
)

filtro_mes = st.sidebar.multiselect(
    "Mes",
    options=meses,
    default=meses
)

filtro_area = st.sidebar.multiselect(
    "Área",
    options=areas,
    default=areas
)

filtro_detalle = st.sidebar.multiselect(
    "Detalle",
    options=detalles,
    default=detalles
)

st.sidebar.markdown("Concepto / Ítem")
st.sidebar.markdown(
    f"""
    <div class="filtro-fijo">
        {TIPO_FIJO}
    </div>
    """,
    unsafe_allow_html=True
)

df_filtrado = df[
    (df["Año"].isin(filtro_anio)) &
    (df["Mes"].isin(filtro_mes)) &
    (df["Área"].isin(filtro_area)) &
    (df["Detalle"].isin(filtro_detalle))
].copy()

if df_filtrado.empty:
    st.warning("No existen datos para los filtros seleccionados.")
    st.stop()


# ============================================================
# CÁLCULOS PRINCIPALES
# ============================================================

total_gasto = df_filtrado["Monto_CLP"].sum()

gasto_mensual = (
    df_filtrado
    .groupby(["Año", "Mes", "Fecha_Mes"], as_index=False)["Monto_CLP"]
    .sum()
    .sort_values("Fecha_Mes")
)

promedio_mensual = gasto_mensual["Monto_CLP"].mean()

gasto_area = (
    df_filtrado
    .groupby("Área", as_index=False)["Monto_CLP"]
    .sum()
    .sort_values("Monto_CLP", ascending=False)
)

area_mayor_gasto = gasto_area.iloc[0]["Área"]
monto_area_mayor = gasto_area.iloc[0]["Monto_CLP"]

gasto_ropa_periodo = df_filtrado[df_filtrado["Detalle"] == "Ropa de trabajo"]["Monto_CLP"].sum()
gasto_excel_periodo = df_filtrado[df_filtrado["Detalle"] == "Gasto registrado Excel"]["Monto_CLP"].sum()

gasto_epp_total = df_filtrado[df_filtrado["Área"] == "EPP"]["Monto_CLP"].sum()
gasto_epp_excel = df_filtrado[
    (df_filtrado["Área"] == "EPP") &
    (df_filtrado["Detalle"] == "Gasto registrado Excel")
]["Monto_CLP"].sum()
gasto_epp_ropa = df_filtrado[
    (df_filtrado["Área"] == "EPP") &
    (df_filtrado["Detalle"] == "Ropa de trabajo")
]["Monto_CLP"].sum()

participacion_epp = gasto_epp_total / total_gasto if total_gasto > 0 else 0


# ============================================================
# PRESUPUESTO Y AHORRO
# ============================================================

gasto_mensual_ahorro = gasto_mensual.copy()

gasto_mensual_ahorro["Presupuesto_Mensual"] = PRESUPUESTO_MENSUAL

gasto_mensual_ahorro["Ahorro_Mensual"] = (
    gasto_mensual_ahorro["Presupuesto_Mensual"] - gasto_mensual_ahorro["Monto_CLP"]
)

gasto_mensual_ahorro["Desviacion_Mensual"] = (
    gasto_mensual_ahorro["Monto_CLP"] - gasto_mensual_ahorro["Presupuesto_Mensual"]
)

gasto_mensual_ahorro["Estado"] = gasto_mensual_ahorro["Ahorro_Mensual"].apply(
    lambda x: "Ahorro" if x >= 0 else "Sobreconsumo"
)

cantidad_meses = len(gasto_mensual_ahorro)

presupuesto_periodo = PRESUPUESTO_MENSUAL * cantidad_meses
gasto_periodo = gasto_mensual_ahorro["Monto_CLP"].sum()
ahorro_periodo = presupuesto_periodo - gasto_periodo

ahorro_promedio_mensual = PRESUPUESTO_MENSUAL - promedio_mensual
proyeccion_ahorro_anual = ahorro_promedio_mensual * 12

porcentaje_uso_presupuesto = (
    gasto_periodo / presupuesto_periodo if presupuesto_periodo > 0 else 0
)

porcentaje_ahorro_presupuestario = (
    ahorro_periodo / presupuesto_periodo if presupuesto_periodo > 0 else 0
)

estado_presupuesto, clase_estado, subtitulo_estado = evaluar_estado_presupuestario(
    porcentaje_uso_presupuesto
)


# ============================================================
# RESUMEN EJECUTIVO
# ============================================================

st.subheader("Resumen ejecutivo")

st.markdown(
    f"""
    <div class="resumen-ejecutivo">
        Durante el periodo seleccionado, el gasto total considerado alcanzó
        <b>{formato_clp_html(total_gasto)}</b>, frente a un presupuesto oficial de
        <b>{formato_clp_html(presupuesto_periodo)}</b>. Esto representa un uso presupuestario de
        <b>{formato_porcentaje(porcentaje_uso_presupuesto)}</b> y un ahorro presupuestario de
        <b>{formato_porcentaje(porcentaje_ahorro_presupuestario)}</b>.
        El área con mayor incidencia fue <b>{area_mayor_gasto}</b>, con un monto de
        <b>{formato_clp_html(monto_area_mayor)}</b>. La ropa de trabajo fue incorporada como gasto dentro del área
        <b>EPP</b>, sin modificar el presupuesto oficial asignado.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INDICADORES PRINCIPALES
# ============================================================

st.subheader("Indicadores principales")

col0, col1, col2, col3 = st.columns(4)

with col0:
    tarjeta_metrica("Estado presupuestario", estado_presupuesto, subtitulo_estado, clase_estado)

with col1:
    tarjeta_metrica("Gasto total considerado", formato_clp_html(total_gasto))

with col2:
    tarjeta_metrica("Gasto promedio mensual", formato_clp_html(promedio_mensual))

with col3:
    tarjeta_metrica("Uso del presupuesto", formato_porcentaje(porcentaje_uso_presupuesto))


col4, col5, col6, col7 = st.columns(4)

with col4:
    tarjeta_metrica("Área mayor gasto", area_mayor_gasto)

with col5:
    tarjeta_metrica("Monto área mayor", formato_clp_html(monto_area_mayor))

with col6:
    tarjeta_metrica("Ahorro acumulado periodo", formato_clp_html(ahorro_periodo))

with col7:
    tarjeta_metrica("Ahorro presupuestario", formato_porcentaje(porcentaje_ahorro_presupuestario))


col8, col9, col10, col11 = st.columns(4)

with col8:
    tarjeta_metrica("Gasto registrado Excel", formato_clp_html(gasto_excel_periodo))

with col9:
    tarjeta_metrica("Gasto ropa trabajo EPP", formato_clp_html(gasto_ropa_periodo))

with col10:
    tarjeta_metrica("Presupuesto mensual oficial", formato_clp_html(PRESUPUESTO_MENSUAL))

with col11:
    tarjeta_metrica("Presupuesto anual oficial", formato_clp_html(PRESUPUESTO_ANUAL))


# ============================================================
# ANÁLISIS PRESUPUESTARIO
# ============================================================

st.subheader("Análisis presupuestario")

st.markdown(
    f"""
    <div class="nota-presupuesto">
        El presupuesto mensual oficial se mantiene en <b>{formato_clp_html(PRESUPUESTO_MENSUAL)}</b>.
        La ropa de trabajo se incorpora como gasto dentro del área <b>EPP</b>, por un monto mensual de
        <b>{formato_clp_html(GASTO_MENSUAL_ROPA_TRABAJO)}</b>, equivalente a
        <b>{formato_clp_html(GASTO_ANUAL_ROPA_TRABAJO)}</b> anual. Este gasto no aumenta el presupuesto,
        solamente se suma al gasto real considerado.
    </div>
    """,
    unsafe_allow_html=True
)

col_a1, col_a2, col_a3, col_a4 = st.columns(4)

with col_a1:
    tarjeta_metrica("Presupuesto periodo filtrado", formato_clp_html(presupuesto_periodo))

with col_a2:
    tarjeta_metrica("Gasto acumulado periodo", formato_clp_html(gasto_periodo))

with col_a3:
    tarjeta_metrica("Ahorro promedio mensual", formato_clp_html(ahorro_promedio_mensual))

with col_a4:
    tarjeta_metrica("Proyección ahorro anual", formato_clp_html(proyeccion_ahorro_anual))


# ============================================================
# ANÁLISIS EPP
# ============================================================

st.subheader("Análisis específico del área EPP")

col_epp1, col_epp2, col_epp3, col_epp4 = st.columns(4)

with col_epp1:
    tarjeta_metrica("Gasto total EPP", formato_clp_html(gasto_epp_total))

with col_epp2:
    tarjeta_metrica("EPP registrado Excel", formato_clp_html(gasto_epp_excel))

with col_epp3:
    tarjeta_metrica("Ropa trabajo cargada a EPP", formato_clp_html(gasto_epp_ropa))

with col_epp4:
    tarjeta_metrica("Participación EPP", formato_porcentaje(participacion_epp))


# ============================================================
# RANKING DE ÁREAS
# ============================================================

st.subheader("Ranking de áreas con mayor gasto")

ranking_area = gasto_area.copy()
ranking_area["Ranking"] = range(1, len(ranking_area) + 1)
ranking_area["Monto"] = ranking_area["Monto_CLP"].apply(formato_clp)
ranking_area["Participación"] = ranking_area["Monto_CLP"].apply(
    lambda x: formato_porcentaje(x / total_gasto) if total_gasto > 0 else "0,0%"
)

st.dataframe(
    ranking_area[["Ranking", "Área", "Monto", "Participación"]],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# PROMEDIOS POR ÁREA
# ============================================================

st.subheader("Promedios por área")

promedio_area_base = (
    df_filtrado
    .groupby(["Año", "Mes", "Fecha_Mes", "Área"], as_index=False)["Monto_CLP"]
    .sum()
)

promedio_area = (
    promedio_area_base
    .groupby("Área", as_index=False)
    .agg(
        Gasto_Total=("Monto_CLP", "sum"),
        Promedio_Mensual=("Monto_CLP", "mean"),
        Meses_Con_Registro=("Monto_CLP", "count")
    )
    .sort_values("Gasto_Total", ascending=False)
)

promedio_area_mostrar = promedio_area.copy()
promedio_area_mostrar["Gasto_Total"] = promedio_area_mostrar["Gasto_Total"].apply(formato_clp)
promedio_area_mostrar["Promedio_Mensual"] = promedio_area_mostrar["Promedio_Mensual"].apply(formato_clp)

st.dataframe(
    promedio_area_mostrar,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# EVOLUCIÓN MENSUAL CON LÍNEA DE PRESUPUESTO
# ============================================================

st.subheader("Evolución mensual del gasto en insumos")

gasto_mensual["Monto_Texto"] = gasto_mensual["Monto_CLP"].apply(formato_clp)

fig_linea = go.Figure()

fig_linea.add_trace(
    go.Scatter(
        x=gasto_mensual["Fecha_Mes"],
        y=gasto_mensual["Monto_CLP"],
        mode="lines+markers",
        name="Gasto considerado",
        line=dict(width=4),
        marker=dict(size=9),
        customdata=gasto_mensual["Monto_Texto"],
        hovertemplate="<b>Mes:</b> %{x|%m-%Y}<br><b>Gasto:</b> %{customdata}<extra></extra>"
    )
)

fig_linea.add_trace(
    go.Scatter(
        x=gasto_mensual["Fecha_Mes"],
        y=[PRESUPUESTO_MENSUAL] * len(gasto_mensual),
        mode="lines",
        name="Presupuesto oficial mensual",
        line=dict(width=3, dash="dash"),
        hovertemplate=f"<b>Presupuesto mensual:</b> {formato_clp(PRESUPUESTO_MENSUAL)}<extra></extra>"
    )
)

fig_linea.update_layout(
    title="Evolución mensual del gasto considerado versus presupuesto oficial",
    height=450,
    title_font_size=20,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
    xaxis_title="Mes",
    legend_title_text=""
)

fig_linea = aplicar_formato_eje_clp(fig_linea, gasto_mensual, "Monto_CLP", "Monto CLP")

st.plotly_chart(fig_linea, use_container_width=True)


# ============================================================
# COMPARATIVO PRESUPUESTO VS GASTO
# ============================================================

st.subheader("Comparativo mensual: presupuesto versus gasto considerado")

comparativo = gasto_mensual_ahorro.copy()
comparativo["Mes_Año"] = comparativo["Fecha_Mes"].dt.strftime("%m-%Y")

comparativo_largo = comparativo.melt(
    id_vars=["Mes_Año", "Fecha_Mes"],
    value_vars=["Presupuesto_Mensual", "Monto_CLP"],
    var_name="Indicador",
    value_name="Monto"
)

comparativo_largo["Indicador"] = comparativo_largo["Indicador"].replace({
    "Presupuesto_Mensual": "Presupuesto oficial",
    "Monto_CLP": "Gasto considerado"
})

comparativo_largo["Monto_Texto"] = comparativo_largo["Monto"].apply(formato_clp)

fig_comparativo = px.bar(
    comparativo_largo,
    x="Mes_Año",
    y="Monto",
    color="Indicador",
    barmode="group",
    title="Presupuesto oficial versus gasto considerado",
    text="Monto_Texto",
    labels={
        "Mes_Año": "Mes",
        "Monto": "Monto CLP",
        "Indicador": "Indicador"
    },
    custom_data=["Monto_Texto"]
)

fig_comparativo.update_traces(
    textposition="outside",
    hovertemplate="<b>Mes:</b> %{x}<br><b>Monto:</b> %{customdata[0]}<extra></extra>"
)

fig_comparativo.update_layout(
    height=470,
    title_font_size=20,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Mes",
    legend_title_text=""
)

fig_comparativo = aplicar_formato_eje_clp(fig_comparativo, comparativo_largo, "Monto", "Monto CLP")

st.plotly_chart(fig_comparativo, use_container_width=True)


# ============================================================
# AHORRO / SOBRECONSUMO MENSUAL Y DESVIACIÓN
# ============================================================

st.subheader("Ahorro, sobreconsumo y desviación mensual")

gasto_mensual_ahorro["Ahorro_Texto"] = gasto_mensual_ahorro["Ahorro_Mensual"].apply(formato_clp)
gasto_mensual_ahorro["Desviacion_Texto"] = gasto_mensual_ahorro["Desviacion_Mensual"].apply(formato_clp)
gasto_mensual_ahorro["Mes_Año"] = gasto_mensual_ahorro["Fecha_Mes"].dt.strftime("%m-%Y")

fig_ahorro = px.bar(
    gasto_mensual_ahorro,
    x="Mes_Año",
    y="Ahorro_Mensual",
    color="Estado",
    title="Resultado mensual frente al presupuesto oficial",
    text="Ahorro_Texto",
    labels={
        "Mes_Año": "Mes",
        "Ahorro_Mensual": "Ahorro / Sobreconsumo CLP",
        "Estado": "Estado"
    },
    custom_data=["Ahorro_Texto", "Estado"]
)

fig_ahorro.update_traces(
    textposition="outside",
    hovertemplate="<b>Mes:</b> %{x}<br><b>Estado:</b> %{customdata[1]}<br><b>Resultado:</b> %{customdata[0]}<extra></extra>"
)

fig_ahorro.update_layout(
    height=470,
    title_font_size=20,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Mes",
    legend_title_text=""
)

fig_ahorro = aplicar_formato_eje_clp(
    fig_ahorro,
    gasto_mensual_ahorro,
    "Ahorro_Mensual",
    "Ahorro / Sobreconsumo CLP"
)

st.plotly_chart(fig_ahorro, use_container_width=True)


# ============================================================
# GASTO EXCEL VS ROPA DE TRABAJO
# ============================================================

st.subheader("Composición del gasto considerado")

composicion = pd.DataFrame({
    "Origen del gasto": ["Gasto registrado Excel", "Ropa de trabajo cargada a EPP"],
    "Monto_CLP": [gasto_excel_periodo, gasto_ropa_periodo]
})

composicion["Monto_Texto"] = composicion["Monto_CLP"].apply(formato_clp)

fig_composicion = px.pie(
    composicion,
    names="Origen del gasto",
    values="Monto_CLP",
    title="Distribución gasto registrado Excel vs ropa de trabajo",
    hole=0.45,
    custom_data=["Monto_Texto"]
)

fig_composicion.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>Origen:</b> %{label}<br><b>Monto:</b> %{customdata[0]}<br><b>Participación:</b> %{percent}<extra></extra>"
)

fig_composicion.update_layout(
    height=470,
    title_font_size=20,
    paper_bgcolor="rgba(0,0,0,0)"
)

st.plotly_chart(fig_composicion, use_container_width=True)


# ============================================================
# GRÁFICOS POR ÁREA
# ============================================================

st.subheader("Análisis por área")

col_g1, col_g2 = st.columns(2)

with col_g1:
    gasto_area["Monto_Texto"] = gasto_area["Monto_CLP"].apply(formato_clp)

    fig_barra_area = px.bar(
        gasto_area,
        x="Área",
        y="Monto_CLP",
        title="Gasto total por área",
        text="Monto_Texto",
        labels={
            "Área": "Área",
            "Monto_CLP": "Monto CLP"
        },
        custom_data=["Monto_Texto"]
    )

    fig_barra_area.update_traces(
        textposition="outside",
        hovertemplate="<b>Área:</b> %{x}<br><b>Monto:</b> %{customdata[0]}<extra></extra>"
    )

    fig_barra_area.update_layout(
        height=460,
        title_font_size=20,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_tickangle=-35
    )

    fig_barra_area = aplicar_formato_eje_clp(fig_barra_area, gasto_area, "Monto_CLP", "Monto CLP")

    st.plotly_chart(fig_barra_area, use_container_width=True)

with col_g2:
    fig_torta_area = px.pie(
        gasto_area,
        names="Área",
        values="Monto_CLP",
        title="Distribución porcentual por área",
        hole=0.45,
        custom_data=["Monto_Texto"]
    )

    fig_torta_area.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>Área:</b> %{label}<br><b>Monto:</b> %{customdata[0]}<br><b>Participación:</b> %{percent}<extra></extra>"
    )

    fig_torta_area.update_layout(
        height=460,
        title_font_size=20,
        paper_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig_torta_area, use_container_width=True)


# ============================================================
# DETALLE MENSUAL DE PRESUPUESTO Y AHORRO
# ============================================================

st.subheader("Detalle mensual de presupuesto, ahorro y desviación")

tabla_ahorro = gasto_mensual_ahorro.copy()

tabla_ahorro["Presupuesto Oficial"] = tabla_ahorro["Presupuesto_Mensual"].apply(formato_clp)
tabla_ahorro["Gasto Considerado"] = tabla_ahorro["Monto_CLP"].apply(formato_clp)
tabla_ahorro["Ahorro / Sobreconsumo"] = tabla_ahorro["Ahorro_Mensual"].apply(formato_clp)
tabla_ahorro["Desviación"] = tabla_ahorro["Desviacion_Mensual"].apply(formato_clp)

st.dataframe(
    tabla_ahorro[[
        "Año",
        "Mes",
        "Presupuesto Oficial",
        "Gasto Considerado",
        "Ahorro / Sobreconsumo",
        "Desviación",
        "Estado"
    ]],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# TABLA CONSOLIDADA
# ============================================================

st.subheader("Tabla consolidada de insumos")

tabla_resumen = (
    df_filtrado
    .groupby(["Año", "Mes", "Área", "Tipo", "Detalle"], as_index=False)["Monto_CLP"]
    .sum()
    .sort_values(["Año", "Mes", "Área", "Detalle"])
)

tabla_resumen_mostrar = tabla_resumen.copy()
tabla_resumen_mostrar["Monto"] = tabla_resumen_mostrar["Monto_CLP"].apply(formato_clp)

st.dataframe(
    tabla_resumen_mostrar[["Año", "Mes", "Área", "Tipo", "Detalle", "Monto"]],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DESCARGA
# ============================================================

csv = tabla_resumen.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Descargar resumen en CSV",
    data=csv,
    file_name="resumen_insumos_cto_mulchen.csv",
    mime="text/csv"
)
