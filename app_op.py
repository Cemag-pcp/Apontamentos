import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from gspread_formatting import *
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import time
from PIL import Image
from datetime import date

# Connect to Google Sheets

scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)
sa = gspread.service_account('service_account.json')

# ======================================= #

#streamlit

# Título do app 

st.markdown("<h1 style='text-align: center; font-size:80px; color: black'>Gerenciador de OP</h1>", unsafe_allow_html=True)

with st.sidebar:
    image = Image.open('logo-cemagL.png')
    st.image(image, width=300)

# Contents of ~/my_app/streamlit_app.py

def page1():
    
    def create_op(df, n_op):
        
            # ======================================= #
        
            # Op extraída do pronest

            #df = pd.read_excel(r"G:\Meu Drive\AJUSTES PCP\OP15501.xls")

            df = df.dropna(how='all')
            
            tamanho_chapa = df[df.columns[16:17]][9:10]
            qt_chapa = df[df.columns[2:3]][9:10]
            
            nome_coluna_1 = df[df.columns[0]].name
            aproveitamento_df = df['Unnamed: 16'][4:5]
                    
            df = df[17:df.shape[0]-2]
            
            df = df[[nome_coluna_1,'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 27', 'Unnamed: 32', 'Unnamed: 35']]
            df = df.dropna(how='all')
            
            espessura_df = df[df.columns[2:3]][2:3]

            df = df[[nome_coluna_1,'Unnamed: 19', 'Unnamed: 27', 'Unnamed: 32', 'Unnamed: 35']]
            
            df = df[2:]
            
            # ======================================= #
            
            # criando planilha google sheet
            
            planilha = client.create("OP" + n_op)
            planilha.share('pcp@cemag.com.br', perm_type='user', role='writer')
            
            # Abra a planilha
            
            #n_op = '15500'
            
            planilha = client.open("OP" + n_op).sheet1
                    
            # quantidade de chapa
            
            planilha.update('B2', 'Qt. chapas')
            qt_chapa_list = qt_chapa.values.tolist()
            planilha.update('B3', qt_chapa_list[0][0])
            
            # tamanho da chapa
            
            planilha.update('C2', 'Ocupação da chapa')
            tamanho_chapa_list = tamanho_chapa.values.tolist()
            planilha.update('C3', tamanho_chapa_list[0][0])
            
            # aproveitamento
            
            planilha.update('D2', 'Aproveitamento')
            aproveitamento_list = aproveitamento_df.values.tolist()
            planilha.update('D3', aproveitamento_list[0])
            
            # espessura
            
            planilha.update('E2', 'Espessura')
            espessura_list = espessura_df.values.tolist()
            planilha.update('E3', espessura_list[0][0])
            
            # cabeçalho da tabela
            
            cabecalho_df = pd.DataFrame({'Peças':['Peças'], 'Quantidade':['Quantidade'], 
                                      'Tamanho chapa':['Tamanho chapa'],
                                      'Peso':['Peso'], 'Tempo':['Tempo']})
            cabecalho_list = cabecalho_df.values.tolist()
            planilha.update('A5', cabecalho_list)
            
            # colunas com nome, quantidade, tempo, peso, tamanho da peça
            
            lista = df.values.tolist()
            planilha.update('A6', lista)
            
            # Formatando células e tamanho de colunas
            
            planilha.format('A5:E5', {'textFormat': {'bold': True}, "horizontalAlignment":"CENTER"})
            planilha.format('B2:E2', {'textFormat': {'bold': True}, "horizontalAlignment":"CENTER"})
            planilha.format('A6:E', {"horizontalAlignment":"LEFT"})
            
            set_column_width(planilha, 'A', 500)
            set_column_width(planilha, 'C', 200)
            
            planilha.merge_cells('A1:A4')
            planilha.update('A1', 'Ordem de Produção - PLASMA')
            planilha.format('A1', {'textFormat': {'bold': True, "fontSize": 25},
                                   "horizontalAlignment":"CENTER", "verticalAlignment":"MIDDLE"})
        
    # =============================================================================
    #         url = 'https://drive.google.com/file/d/18o3wyOzID9Z-xooQ0KuNsONay-WzKgKo'
    #         
    #         picture = [f'=IMAGE("{url}",4,100,100)']
    #         planilha.insert_row(picture,1)
    #         planilha.insert_row(picture, 3, 'USER_ENTERED')
    # 
    # =============================================================================
            # Criando colunas na tabela para guardar no bando de dados
            
            df['espessura'] = espessura_list[0][0]
            df['aproveitamento'] = aproveitamento_list[0]
            df['tamanho da chapa'] = tamanho_chapa_list[0][0]
            df['qt. chapas'] = qt_chapa_list[0][0]
            df['op'] = n_op
            
            # reordenar colunas
            
            cols = df.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            df = df[cols]
            
            # Guardar no banco de dados
            
            name_sheet = 'Banco de dados OP'
            worksheet = 'Criadas'
            
            sh = sa.open(name_sheet)
            df_list = df.values.tolist()
            sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})

    st.markdown("<h2 style='text-align: center; font-size:50px; color: black'>Criar OP - Plasma</h2>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a XLS file", type="xls")
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        name_file = uploaded_file.name
        name_file = name_file[2:7]
        n_op = name_file
    
    if st.button('Gerar OP'):
        create_op(df, n_op)
    
    st.markdown("<h2 style='text-align: center; font-size:25px; color: black'>OP aberta!</h2>", unsafe_allow_html=True)

    

def page2():
    
    def finalizar_op(n_op):    
        
        name_sheet = 'Banco de dados OP'
        worksheet = 'Finalizadas'
        
        sh = sa.open(name_sheet)
        wks = sh.worksheet(worksheet)
    
        list1 = wks.get_all_records()
        table = pd.DataFrame(list1)
        table = table.drop_duplicates()
            
        table = table.query('op ==' + n_op)
        
        caract_op = table[['Aproveitamento','Tamanho da chapa','qt. chapa','Espessura']][0:1]
        
        caract_op = caract_op.reset_index(drop=True)
    
        gb = GridOptionsBuilder.from_dataframe(caract_op)
        gb.configure_column('Aproveitamento', editable=True)
        gb.configure_column('Tamanho da chapa', editable=True)
        gb.configure_column('qt. chapa', editable=True)
        gb.configure_column('Espessura', editable=True)
        grid_options = gb.build()
        grid_response = AgGrid(caract_op, gridOptions=grid_options, data_return_mode='AS_INPUT', update_model='MODEL_CHANGE\D')
    
        new_carac = grid_response['data']
                
        #st.dataframe(caract_op)
        
        table = table[['Peças', 'Quantidade']]
        
        #st.dataframe(table)
        
        gb = GridOptionsBuilder.from_dataframe(table)
        gb.configure_column('Quantidade', editable=True)
        grid_options = gb.build()
        grid_response = AgGrid(table, gridOptions=grid_options, data_return_mode='AS_INPUT', update_model='MODEL_CHANGE\D')
        
        table = grid_response['data']
        
        df2 = table
        
        if st.button('salvar'):
            
            df2['Aproveitamento'] = new_carac['Aproveitamento'][0]
            df2['Tamanho da chapa'] = new_carac['Tamanho da chapa'][0]
            df2['qt. chapa'] = new_carac['qt. chapa'][0]
            df2['Espessura'] = new_carac['Espessura'][0]
            df2['op'] = n_op
            df2['data finalização'] = date.today().strftime('%d/%m/%Y')
    
        # reordenando colunas
            
        
            df2 = df2[['op', 'Peças', 'Quantidade', 'Tamanho da chapa',
                       'qt. chapa','Aproveitamento', 'Espessura', 'data finalização']]    
                    
            # Guardar no banco de dados
        
            name_sheet = 'Banco de dados OP'
            worksheet = 'Finalizadas'
            
            sh = sa.open(name_sheet)
            
            df_list = df2.values.tolist()
            
            sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})
            
            st.markdown("<h2 style='text-align: center; font-size:25px; color: black'>OP FINALIZADA!!</h2>", unsafe_allow_html=True) 
    
    # Número da OP

    n_op = st.text_input("Número da op:")
        
    #if st.button('Consultar'):
    if n_op != '':
        finalizar_op(n_op) 
        
def page3():
    
    st.markdown("<h2 style='text-align: center; font-size:50px; color: black'>Apontar OP - Plasma</h2>", unsafe_allow_html=True)

page_names_to_funcs = {
    "Criar OP": page1,
    "Finalizar OP": page2,
    "Apontar OP": page3,
}

selected_page = st.sidebar.selectbox("Selecione a função", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]() 
