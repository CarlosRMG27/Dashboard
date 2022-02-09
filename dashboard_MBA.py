from calendar import month
import streamlit as st
import pandas as pd
import plotly.express as px

config = {'displayModeBar': False}

@st.cache
def load_data():
    df = pd.read_csv("data/kof_db_metrics_top_25.csv")
    df_lift = pd.read_csv("data/lift_por_cat.csv")
    #print(df.head())
    df.drop_duplicates(inplace=True)
    lista_productos = df["prod_A"].unique() 
    lista_canales = df["canal"].unique() 
    lista_gecs = df["gec"].unique() 
    lista_estados = df["estado"].unique() 
    return df, lista_productos, lista_canales, lista_gecs, lista_estados, df_lift
def filter_data(df,df2,n,canal,gec,estado):
    df = df[df["canal"]==canal]
    df = df[df["gec"]==gec] 
    df = df[df["estado"]==estado]
    df = df[df["rank_a"]<(n+1)]
    df = df[df["rank_b"]<(n+1)]
    df2 = df2[df2["canal"]==canal]
    df2 = df2[df2["gec"]==gec] 
    df2 = df2[df2["estado"]==estado]
    return df,df2

# ---------------------------------------------------------------------------- #
# ------------------------------- Configuración ------------------------------ #

#Page Config
st.set_page_config(page_title ="Market Basket Analysis",
                    initial_sidebar_state="expanded",
                    layout='wide',
                    page_icon="🛒")
                    
hide_streamlit_style = """<style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# ---------------------------------------------------------------------------- #
# ------------------------------- Elementos Top ------------------------------ #
#Logo
st.image("img/header.png",width=1710)
#col1, col2 = st.columns([8,1])
#with col2:
#    st.image("img/sintec_logo.png",width=180)
#Título
st.markdown('#')
st.title("🛒 Market Basket Analysis") 
#Introducción
with st.expander("Introducción",expanded =True):
        st.write('''Esta aplicación habilita la exploración de las relaciones entre los productos a partir de un **Market Basket Analysis**. A continuación se definen algunos conceptos relevantes:''')
        st.markdown("""
    1 📊 **Support**: Medida de la popularidad de uno o más productos. Se calcula dividiendo las transacciones que incluyen al producto entre el número total de transacciones.\n
    2 📈 **Confidence (A→B)**: Probabilidad de que el artículo B se compre también si se compra el artículo A. Se calcula dividiendo el número de transacciones en las que A y B se compran juntos entre el número total de transacciones en las que se compra A.\n
    3 ↗️ **Lift (A→B)**: Aumento de la proporción de venta de B cuando se vende A. Compara la frecuencia con la que se vende sólo A vs la frecuencia con la que se vende en conjunto con B.\n
    """)
st.markdown("***")



# ---------------------------------------------------------------------------- #
# ----------------------------- Cargar Dataframe ----------------------------- #


df_base, lista_productos, lista_canales, lista_gecs, lista_estados, df_lift = load_data()

col1, col2, col3, col4 = st.columns([2,2,2,2])

with col1:
    top_n = st.number_input(min_value=5, max_value=25, value=15, step=5,label="No. de SKUs")
with col2:
    select_c = st.selectbox(label="Canal",options=lista_canales)
with col3:
    select_g = st.selectbox(label="GEC",options=lista_gecs)
with col4:
    select_e = st.selectbox(label="Estado",options=lista_estados)


df_base, df_lift = filter_data(df_base,df_lift,top_n,select_c,select_g,select_e)

# ---------------------------------------------------------------------------- #
# --------------------------- Heatmap Combinaciones -------------------------- #
st.subheader("Vista por Categoría")
df_lift = df_lift[["cat_a", "cat_b","lift"]]
df_lift = df_lift[df_lift["cat_b"]!="LÁCTEOS"]
df_lift = df_lift[df_lift["cat_a"]!="LÁCTEOS"]
df_lift.rename({'cat_b':'Categoría (B)','cat_a':'Categoría (A)'}, axis=1, inplace=True)
df_lift = df_lift.pivot(index='Categoría (A)', columns='Categoría (B)').droplevel(0, axis=1)
plot = px.imshow(df_lift,height=700,width=700,title="Lift entre Categorías", color_continuous_scale="rdgy")
st.plotly_chart(plot)

# ---------------------------------------------------------------------------- #
# --------------------------- Heatmap Combinaciones -------------------------- #
st.subheader("Medidas por Combinación")
col1, _, col3= st.columns([5,1,5])
with col1:
    metrica = st.selectbox(label="Selecciona una métrica",options=["Lift","Confidence","Support"])
metrics_dict = dict({"Lift": 'lift', "Confidence": 'confidence', "Support":'support_a_b'})
df_heatmap = df_base[["prod_A", "prod_B",metrics_dict[metrica]]]
df_heatmap.rename({'prod_B':'Producto (B)','prod_A':'Producto (A)'}, axis=1, inplace=True)
df_heatmap = df_heatmap.pivot(index='Producto (A)', columns='Producto (B)').droplevel(0, axis=1)
with col1:
    plot = px.imshow(df_heatmap,height=700,width=700)
    st.plotly_chart(plot)
    
    top_3_combos = df_base.sort_values(by='lift',ascending=False).head(6).iloc[::2]
    st.text("Top 3 combinaciones con mayor impulso:")
    st.text("  1. "+top_3_combos.iloc[0]['prod_A']+", " +top_3_combos.iloc[0]['prod_B']+(" Lift: ")+"{:.1f}".format(top_3_combos.iloc[0]['lift']))
    st.text("  2. "+top_3_combos.iloc[1]['prod_A']+", " +top_3_combos.iloc[1]['prod_B']+(" Lift: ")+"{:.1f}".format(top_3_combos.iloc[1]['lift']))
    st.text("  3. "+top_3_combos.iloc[2]['prod_A']+", " +top_3_combos.iloc[2]['prod_B']+(" Lift: ")+"{:.1f}".format(top_3_combos.iloc[2]['lift']))

with col3:
    plot2 = px.scatter(df_base, x="support_a_b", y="confidence", color="lift",color_continuous_scale=px.colors.sequential.Viridis,
                 labels={
                     "support_a_b": "Support",
                     "confidence": "Confidence",
                     "lift": "Lift"
                 },hover_data={'prod_A':True,
                               'prod_B':True,
                               'support_a_b':':.2f',
                               'confidence':':.2f', 
                               'lift':':.2f'},height=750,width=750)
    st.plotly_chart(plot2,config=config)


# ---------------------------------------------------------------------------- #
# --------------------------- Tablas Producto Ancla -------------------------- #
st.markdown('#')
st.markdown("***")
st.markdown('#')
st.subheader("Vista por producto")


col1, col2= st.columns([3,6])
with col1:
    st.markdown('#')
    st.markdown('#')
    st.text("Venta (CU) por Producto ")
    venta_cat = df_base[["prod_A", "sales_a"]]
    venta_cat = venta_cat.drop_duplicates()
    venta_cat.rename({'prod_A':'Producto','sales_a':'Venta'}, axis=1, inplace=True)
    #st.dataframe(venta_cat.style.format(subset=["Venta"],formatter="{:,}"))
    venta_cat = venta_cat.sort_values(by='Venta')
    plot2_5 = px.bar(venta_cat, x='Venta', y='Producto',orientation='h',height=500,width=550)
    plot2_5.update_traces(marker_color='DarkBlue')
    plot2_5.update_layout(margin=dict(l=20, r=20, t=5, b=10))
    st.plotly_chart(plot2_5,config=config)

with col2:
    producto_ancla = st.selectbox(label="Selecciona un producto ancla (producto A)",options=lista_productos)
    st.text("Oportunidades de Impulso de Productos")
    impulso_venta = df_base[df_base["lift"]>=1]
    impulso_venta = impulso_venta[impulso_venta["prod_A"]==producto_ancla]
    impulso_venta.rename({'prod_B':'Producto (B)','sales_b':'Venta (B)','lift':'Lift','support_b':'Support (B)'}, axis=1, inplace=True)
    plot3 = px.scatter(impulso_venta, x="Lift", y="Venta (B)",color="Producto (B)",size="Support (B)",height=450,width=1000)

    plot3.add_shape(type="rect", x0=((impulso_venta["Lift"].max()-impulso_venta["Lift"].min())/2)+impulso_venta["Lift"].min(), y0=0, x1=round(impulso_venta["Lift"].max(), 1)+0.05, y1=30000000,
        line=dict(color="Crimson",
        width=2,
    ))
    plot3.update_layout(margin=dict(l=20, r=20, t=5, b=10))
    plot3.add_annotation(text="Tamaño: Support (B)",showarrow=False,yref='paper',y = -0.12,x=round(impulso_venta["Lift"].max(), 1),xanchor='right', yanchor='auto')
    st.plotly_chart(plot3,config=config)

    st.markdown('<p style="color:Crimson; font-size: 14px;">&emsp;&emsp;&emsp;&emsp;☐: Categorías con Lift elevado y baja venta</p>', unsafe_allow_html=True)


st.markdown('#')
st.markdown('#')
df_top_5 = df_base[(df_base["prod_A"]==producto_ancla) & (df_base["lift"]>0)]
df_top_5["metrica"] = df_top_5["lift"] * df_top_5["confidence"]
df_top_5 = df_top_5.sort_values(['metrica'], ascending=[True]).reset_index().head(5)
df_top_5 = df_top_5[["prod_B", "support_b","support_a_b","confidence","lift","sales_b"]]
df_top_5.rename({'prod_B':'Producto (B)','support_b':'Support (B)','support_a_b':'Support (A,B)','confidence':'Confidence','lift':'Lift','sales_b':'Venta CU (B)'}, axis=1, inplace=True)


st.text("Bottom 5 productos influenciados por "+producto_ancla)
#st.dataframe(df_top_5.style.format({'Lift': '{:.1f}','Confidence': '{:.1f}','Support (B)': '{:.1f}','Support (A,B)': '{:.1f}','Venta CU (B)': '{:,}'}))
#st.dataframe(df_top_5.style.format(subset=["Support (B)","Support (A,B)","Confidence","Lift"],formatter="{:.1f}"))

df_top_5 = df_top_5[["Producto (B)", "Confidence", "Lift", "Venta CU (B)"]]
df_top_5=df_top_5.melt(id_vars=['Producto (B)'], value_vars=["Confidence", "Lift", "Venta CU (B)"])

plot4 = px.bar(df_top_5, x='value', y='Producto (B)',orientation='h',height=500,width=1250, facet_col="variable",color="variable")
plot4.update_xaxes(matches=None)
plot4.update_yaxes(autorange="reversed")
st.plotly_chart(plot4,config=config)

#cd "OneDrive - SINTEC\POC Market Basket Analysis\dashboard_MBA_vkof - cortes"
#streamlit run dashboard_MBA.py



 