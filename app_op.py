# Versao teste
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from gspread_formatting import *
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from PIL import Image
from datetime import date
from datetime import datetime
import sqlite3 
import hashlib

# Connect to Google Sheets

scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)
sa = gspread.service_account('service_account.json')

# ======================================= #

import base64

@st.cache_resource
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file) 
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-repeat: repeat;
    background-attachment: scroll; # doesn't work
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg('cemag_papel.png')

# Título do app 

with st.sidebar:
    image = Image.open('logo-cemagL.png')
    st.image(image, width=300)

def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
conn = sqlite3.connect('data.db')
c = conn.cursor()

# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data

# Contents of ~/my_app/streamlit_app.py

def page1():
    
    def create_op_plasma(df, n_op):
        
            # ======================================= #
        
            # Op extraída do pronest

            #df = pd.read_excel(r"H:\Drives compartilhados\Producao - Cemag\RELATÓRIOS E PROGRAMAS\Plasma\OP15611.xls")

            name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
            worksheet = 'Criadas'
                        
            sh = sa.open_by_key(name_sheet)
            wks = sh.worksheet(worksheet)

            cell_list = wks.findall(n_op)

            if len(cell_list)==0:

                df = df.dropna(how='all')
                
                tamanho_chapa = df[df.columns[16:17]][9:10].replace('×', 'x')
                qt_chapa = df[df.columns[2:3]][9:10]
                
                nome_coluna_1 = df[df.columns[0]].name
                aproveitamento_df = df['Unnamed: 16'][4:5]
                        
                df = df[17:df.shape[0]-2]
                
                df = df[[nome_coluna_1,'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 27', 'Unnamed: 32', 'Unnamed: 35']]
                df = df.dropna(how='all')
                
                espessura_df = df[df.columns[2:3]][2:3]

                df = df[[nome_coluna_1,'Unnamed: 19', 'Unnamed: 27', 'Unnamed: 32', 'Unnamed: 35']]
                
                df = df[2:]
            
                # quantidade de chapa
                
                qt_chapa_list = qt_chapa.values.tolist()
                
                # tamanho da chapa
                
                tamanho_chapa_list = tamanho_chapa.values.tolist()
                
                # aproveitamento
                
                aproveitamento_list = aproveitamento_df.values.tolist()
                
                # espessura
                
                espessura_list = espessura_df.values.tolist()
                
                # cabeçalho da tabela
                
                cabecalho_df = pd.DataFrame({'Peças':['Peças'], 'Quantidade':['Quantidade'], 
                                        'Tamanho chapa':['Tamanho chapa'],
                                        'Peso':['Peso'], 'Tempo':['Tempo']})
                cabecalho_list = cabecalho_df.values.tolist()
                
                lista = df.values.tolist()
            
                # Criando colunas na tabela para guardar no bando de dados

                df['Unnamed: 19'] = df['Unnamed: 19'].astype(int)
                df['espessura'] = espessura_list[0][0]
                df['aproveitamento'] = aproveitamento_list[0]
                df['tamanho da chapa'] = tamanho_chapa_list[0][0]
                df['qt. chapas'] = int(qt_chapa_list[0][0])
                df['op'] = n_op

                # reordenar colunas
                
                cols = df.columns.tolist()
                cols = cols[-1:] + cols[:-1]
                df = df[cols]
                
                df['data criada'] = date.today().strftime('%d/%m/%Y')
                df['Máquina'] = 'Plasma'
                df['op_espelho'] = ''
                df['opp'] = 'opp'
                
                # Guardar no banco de dados
                
                name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
                worksheet = 'Criadas'
                
                sh = sa.open_by_key(name_sheet)
                
                df_list = df.values.tolist()
                sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})
                
                st.markdown("<h2 style='text-align: center; font-size:25px; color: green'>OP aberta!</h2>", unsafe_allow_html=True)

            else:
                st.markdown("<h2 style='text-align: center; font-size:25px; color: red'>OP já estava aberta!</h2>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; font-size:50px; color: black'>Criar OP - Plasma</h2>", unsafe_allow_html=True)
    
    tabs_font_css = """
    <style>
    div[class*="element-container css-1hynsf2 e1tzin5v3"] label p {
    font-size: 26px;
    color: black;
    }
    </style>
    """

    st.write(tabs_font_css, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Escolha um arquivo", type="xls")
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        name_file = uploaded_file.name
        name_file = name_file[2:7]
        n_op = str(name_file)
    
        if n_op != '':
        
            if st.button('Gerar OP'):
                create_op_plasma(df, n_op)    
                
def page2():
    
    st.markdown("<h2 style='text-align: center; font-size:50px; color: black'>Finalizar OP</h2>", unsafe_allow_html=True)

    def finalizar_op(n_op):    
        
        #n_op = '102013'
        
        #verificando se op ja foi finalizada

        name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
        worksheet = 'Finalizadas'
                    
        sh = sa.open_by_key(name_sheet)
        wks = sh.worksheet(worksheet)

        cell_list = wks.findall(n_op)

        if len(cell_list) == 0:

            name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
            worksheet = 'Criadas'
            
            sh = sa.open_by_key(name_sheet)
            wks = sh.worksheet(worksheet)
        
            list1 = wks.get_all_records()
            table = pd.DataFrame(list1)
            #table = table.drop_duplicates()
            
            table['op'] = table['op'].astype(str)
        
            table = table.loc[(table.op == n_op)] # & (table.maquina == maq)]
            table = table.reset_index(drop=True)

            # caract_op['Aproveitamento'] = pd.to_numeric(caract_op['Aproveitamento'], errors='coerce')
            # caract_op['qt. chapa'] = pd.to_numeric(caract_op['qt. chapa'], errors='coerce')

            table['Aproveitamento'] = table['Aproveitamento'].astype(str)            
            table['Aproveitamento'] = table['Aproveitamento'].replace(",00","", regex=True).replace("%","", regex=True).replace("\.","",regex=True).replace(",","",regex=True)

            for i in range(len(table)):
                if table['Aproveitamento'][i][0] != '0':
                    table['Aproveitamento'][i] = '0.' + table['Aproveitamento'][i]

            table['Aproveitamento'] = pd.to_numeric(table['Aproveitamento'], errors = 'coerce')
            table['Aproveitamento'] = table['Aproveitamento'].apply(lambda x: '0,' + str(x) if x > 1 else x)

            table['qt. chapa'] = pd.to_numeric(table['qt. chapa'], errors = 'coerce')
            table['qt. chapa'] = table['qt. chapa'] / 100

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
            table['Mortas'] = ''
            
            #st.dataframe(table)
            
            gb = GridOptionsBuilder.from_dataframe(table)
            gb.configure_column('Mortas', editable=True)
            grid_options = gb.build()
            grid_response = AgGrid(table, gridOptions=grid_options, data_return_mode='AS_INPUT', update_model='MODEL_CHANGE\D')
            
            table = grid_response['data']
            
            df2 = table
            
            operador = st.selectbox("Operador", ('Selecione', 'Jefferson', 'Hermerson','Marcio','Alex'))

            if operador != "Selecione":

                if st.button('salvar'):
                    
                    new_carac['qt. chapa'] = new_carac['qt. chapa'].astype(int)
                    df2['Quantidade'] = df2['Quantidade'].astype(int)

                    df2['Aproveitamento'] = new_carac['Aproveitamento'][0]
                    df2['Tamanho da chapa'] = new_carac['Tamanho da chapa'][0]
                    df2['qt. chapa'] = new_carac['qt. chapa'][0]
                    df2['Espessura'] = new_carac['Espessura'][0]
                    df2['op'] = n_op
                    df2['op'] = df2['op'].astype(str)
                    df2['data finalização'] = datetime.now().strftime('%d/%m/%Y')
                    df2['Quantidade'] = (df2['Quantidade'] / caract_op['qt. chapa'][0]) * new_carac['qt. chapa'][0]
                    df2['Operador'] = operador

                    df2 = df2.loc[(df2.Quantidade > 0)]
                    df2 = df2.reset_index(drop=True)         

                    # reordenando colunas
                
                    df2 = df2[['op', 'Peças', 'Quantidade', 'Tamanho da chapa',
                            'qt. chapa','Aproveitamento', 'Espessura', 'Mortas', 'data finalização']]   

                    df2 = df2.drop_duplicates()
                            
                    # Guardar no banco de dados
                
                    name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
                    worksheet = 'Finalizadas'
                    
                    sh = sa.open_by_key(name_sheet)
                    
                    df_list = df2.values.tolist()
                    
                    sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})

                    try:
                        name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
                        worksheet = 'Sequenciamento Plasma'
                                    
                        sh = sa.open_by_key(name_sheet)
                        wks = sh.worksheet(worksheet)

                        headers = wks.row_values(5)

                        list1 = wks.get()
                        table = pd.DataFrame(list1)
                        table = table.set_axis(headers, axis=1, inplace=False)[5:]

                        linha_op_finalizada = table.loc[(table['Op'] == n_op)].index[0] + 1

                        wks.update('I' + str(linha_op_finalizada), operador)
                    except:
                        pass

                    st.markdown("<h2 style='text-align: center; font-size:25px; color: green'>OP FINALIZADA!!</h2>", unsafe_allow_html=True) 
        else:
            st.markdown("<h2 style='text-align: center; font-size:25px; color: red'>OP já foi finalizada!!</h2>", unsafe_allow_html=True) 
            

    # Número da OP
    
    n_op = 0

    tabs_font_css = """
    <style>
    div[class*="row-widget stTextInput css-pb6fr7 edfmue0"] label p {
    font-size: 26px;
    color: black;
    }
    </style>
    """

    st.write(tabs_font_css, unsafe_allow_html=True)

    try:        
        n_op = st.text_input("Número da op:")
    except:
        pass
    
    if n_op != '':
        finalizar_op(n_op) 
  
def page3():
    
    def create_op_laser(df, n_op, df1):
        
            # ======================================= #
        
            # Op extraída do lantek
    
            #df = pd.read_excel(r"H:\Drives compartilhados\Producao - Cemag\RELATÓRIOS E PROGRAMAS\Laser\op1278 L1.xlsx")
            #df1 = pd.read_excel(r"H:\Drives compartilhados\Producao - Cemag\RELATÓRIOS E PROGRAMAS\Laser\op1278 L1.xlsx",sheet_name='Nestings_Cost')
            #n_op = '14979'
            
            name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
            worksheet = 'Criadas'
                        
            sh = sa.open_by_key(name_sheet)
            wks = sh.worksheet(worksheet)

            cell_list = wks.findall(n_op)

            if len(cell_list)==0:

                df = df.dropna(how='all')            
                df1 = df1.dropna(how='all')            

                qt_chapas = df1[df1.columns[2:3]][3:4]
                qt_chapas_list = qt_chapas.values.tolist()[0][0]

                aprov1 = df1[df1.columns[2:3]][7:8] 
                aprov2 = df1[df1.columns[2:3]][9:10]
                aprov_list = str(1 - ( float(aprov2.values.tolist()[0][0]) / float(aprov1.values.tolist()[0][0]) ) )
                
                df = df[['Unnamed: 1','Unnamed: 4']]
                df = df.rename(columns={'Unnamed: 1':'Descrição',
                                        'Unnamed: 4': 'Quantidade'})
                df = df.dropna(how='all')
                
                df = df[10:len(df)-1]
                
                df = df.reset_index(drop=True)
                
                df['op'] = n_op
            
                cols = df.columns.tolist()
                cols = cols[-1:] + cols[:-1]
                df = df[cols]
                
                df['tamanho da peça'] = ''
                df['peso'] = ''
                df['tempo'] = ''
                #espessura = '14'
                df['espessura'] = espessura
                df['Aproveitamento'] = aprov_list
                #tamanho_chapa = '2800,00 x 1500,00 mm'
                df['Tamanho da chapa'] = tamanho_chapa
                df['qt. chapas'] = qt_chapas_list
                df['data criada'] = date.today().strftime('%d/%m/%Y')
                df['Máquina'] = 'Laser'
                df['op_espelho'] = ''
                df['opp'] = 'opp'

                # ======================================= #
                            
                # Guardar no banco de dados
                
                name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
                worksheet = 'Criadas'
                
                sh = sa.open_by_key(name_sheet)
                df_list = df.values.tolist()
                sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})
    
                st.markdown("<h2 style='text-align: center; font-size:25px; color: green'>OP aberta!</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='text-align: center; font-size:25px; color: red'>OP já estava aberta!</h2>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; font-size:50px; color: black'>Criar OP - Laser</h2>", unsafe_allow_html=True)
    
    name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'    
    worksheet = 'Chapas'
    
    sh = sa.open_by_key(name_sheet)
    wks = sh.worksheet(worksheet)

    headers = wks.row_values(1)

    list1 = wks.get()
    table = pd.DataFrame(list1)
    #table = table.set_axis(headers, axis=1, inplace=False)[1:]
    table = table.set_axis(headers, axis=1, copy=False)[1:]

    opcoes_espessura = table[['espessura1']]
    opcoes_espessura = opcoes_espessura[opcoes_espessura['espessura1'] != ''].values.tolist()
    
    opcoes_espessura_list = []

    for i in range(len(opcoes_espessura)):
        opcoes_espessura_list.append(opcoes_espessura[i][0])

    tabs_font_css = """
    <style>
    div[class*="stNumberInput"] label p {
    font-size: 26px;
    color: black;
    }
    div[class*="row-widget stSelectbox"] label p {
    font-size: 26px;
    color: black;
    }
    div[class*="element-container css-1hynsf2 e1tzin5v3"] label p {
    font-size: 26px;
    color: black;
    }
    </style>
    """

    st.write(tabs_font_css, unsafe_allow_html=True)

    comp = str(st.number_input("Comprimento:", max_value=4050))
    larg = str(st.number_input("Largura:", max_value=1550))
    #espessura = st.text_input("Espessura:")
    espessura = st.selectbox('Espessura',opcoes_espessura_list)
    
    tamanho_chapa = comp +",00 x "+ larg + ",00 mm"
    
    uploaded_file = st.file_uploader("Escolha um arquivo", type="xlsx")

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df1 = pd.read_excel(uploaded_file, sheet_name='Nestings_Cost')
        name_file = uploaded_file.name
        name_file = name_file[2:7]
        name_file = name_file.replace(' ','')
        n_op = name_file
    
        if n_op != '':
        
            if st.button('Gerar OP'):
                create_op_laser(df, n_op, df1)    
                
def page4():
    
    st.markdown("<h2 style='text-align: center; font-size:50px; color: black'>Duplicador de OP</h2>", unsafe_allow_html=True)

    tabs_font_css = """
    <style>
    div[class*="stTextInput"] label p {
    font-size: 26px;
    color: black;
    }
    </style>
    """

    st.write(tabs_font_css, unsafe_allow_html=True)

    peca = st.text_input("Peça:")
    
    if peca != '':
        
        name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
        worksheet = 'Criadas'

        sh = sa.open_by_key(name_sheet)
        wks = sh.worksheet(worksheet)

        list1 = wks.get_all_records()
        table = pd.DataFrame(list1)
        table = table.drop_duplicates()
        
        table['op'] = table['op'].astype(str)

        table = table.set_index('Peças').filter(like=peca, axis=0)
        table = table.set_index('opp').filter(like='opp', axis=0)

        table = table.reset_index(drop=True)

        table['qt. chapa'] = pd.to_numeric(table['qt. chapa'], errors = 'coerce') 
        table['qt. chapa'] = table['qt. chapa'] / 100

        caract_op = table[['op','Tamanho da chapa','qt. chapa','Espessura']]

        caract_op = caract_op.reset_index(drop=True)

        gb = GridOptionsBuilder.from_dataframe(caract_op)
        grid_options = gb.build()
        grid_response = AgGrid(caract_op, 
                    gridOptions=grid_options,
                    width='100%',
                    height=400,
                    fit_columns_on_grid_load = True,
                    update_model='MODEL_CHANGE\D')

        new_carac = grid_response['data']

    n_op = st.text_input("Op:")

    if n_op != '':

        name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
        worksheet = 'Criadas'
        
        sh = sa.open_by_key(name_sheet)
        wks = sh.worksheet(worksheet)

        list1 = wks.get_all_records()
        table = pd.DataFrame(list1)
        table = table.drop_duplicates()
        
        table['op'] = table['op'].astype(str)

        table = table.loc[table['op'] == n_op]
        table = table.reset_index()
        
        table['qt. chapa'] = pd.to_numeric(table['qt. chapa'], errors = 'coerce') 
        
        table['qt. chapa'] = table['qt. chapa'] / 100

        table['Aproveitamento'] = table['Aproveitamento'].astype(str)            
        table['Aproveitamento'] = table['Aproveitamento'].replace(",00","", regex=True).replace("%","", regex=True).replace("\.","",regex=True).replace(",","",regex=True)

        for i in range(len(table)):
            if table['Aproveitamento'][i][0] != '0':
                table['Aproveitamento'][i] = '0.' + table['Aproveitamento'][i]

        table['Aproveitamento'] = pd.to_numeric(table['Aproveitamento'], errors = 'coerce')
        table['Aproveitamento'] = table['Aproveitamento'].apply(lambda x: '0,' + str(x) if x > 1 else x)
        
        table1 = table[['Tamanho da chapa','Espessura','qt. chapa','maquina','Aproveitamento']][:1]

        maq_antiga = table['maquina'][0]
        qt_antiga = table['qt. chapa'][0]

        gb = GridOptionsBuilder.from_dataframe(table1)
        gb.configure_column('Tamanho da chapa', editable=True)
        gb.configure_column('Espessura', editable=True)
        gb.configure_column('qt. chapa', editable=True)
        grid_options = gb.build()
        grid_response = AgGrid(table1, 
                                gridOptions=grid_options,
                                width='100%',
                                height=400,
                                fit_columns_on_grid_load = True,
                                update_model='MODEL_CHANGE\D')

        new_carac = grid_response['data']

        qt_chapa = new_carac['qt. chapa'][0]
        aproveitamento_espelho = new_carac['Aproveitamento'][0]

        table2 = table.copy()

        try:
            table2 = table2.set_index('op').filter(like=n_op, axis=0)
            table2 = table2.reset_index()
            table2 = table2[['op','Peças', 'Quantidade']]
            st.dataframe(table2)
        except:
            st.text("Op não encontrada")

        if st.button("Duplicar"):

            name_sheet = '1t7Q_gwGVAEwNlwgWpLRVy-QbQo7kQ_l6QTjFjBrbWxE'
            worksheet = 'ultima_OP'
            
            sh = sa.open_by_key(name_sheet)
            wks = sh.worksheet(worksheet)

            list1 = wks.get_all_records()
            table = pd.DataFrame(list1)

            ult_op = table['ultima_op'].values.tolist()[0] + 1
    
            wks.update('A2', ult_op)
            
            table2['Quantidade'] = table2['Quantidade'].astype(int)
            
            table2['op'] = ult_op
            table2['op'] = table2['op'].astype(str)
            table2['Quantidade'] = (table2['Quantidade'] / int(qt_antiga)) * int(qt_chapa)
            table2['Tamanho da peça'] = ''
            table2['Peso'] = ''
            table2['Tempo'] = ''
            table2['Espessura'] = new_carac['Espessura'][0]
            table2['Aproveitamento'] = aproveitamento_espelho
            table2['Tamanho da chapa'] = new_carac['Tamanho da chapa'][0]
            table2['qt. chapa'] = new_carac['qt. chapa'].astype(int)[0]
            table2['Data abertura de op'] = date.today().strftime('%d/%m/%Y')
            table2['maquina'] = maq_antiga
            table2['op_espelho'] = n_op
            
            worksheet = 'Criadas'
            
            sh = sa.open_by_key(name_sheet)
            
            df_list = table2.values.tolist()
            
            sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})
            
            st.title('Número da nova op: ' + str(ult_op))
    
# Página inicial, login e senha
menu = ["Página inicial","Login","Crie uma conta nova"] 
choice = st.sidebar.selectbox("Menu",menu)

# Colocar algo na página inicial ou login
if choice == "Página inicial":
    st.markdown('') # "<h1 style='text-align: center; font-size:60px;'>Página inicial</h1>", unsafe_allow_html=True
    
elif choice == "Login":
    st.markdown('') #"<h1 style='text-align: center; font-size:60px;'>Login</h1>", unsafe_allow_html=True

    username = st.sidebar.text_input("Nome de usuário")
    password = st.sidebar.text_input("Senha",type='password')
    if st.sidebar.checkbox("Login"):
        # if password == '12345':
        create_usertable()
        hashed_pswd = make_hashes(password)

        result = login_user(username,check_hashes(password,hashed_pswd))
    
        if result:

                # Título do app 

                st.markdown("<h1 style='text-align: center; font-size:80px;'>Gerenciador de OP</h1>", unsafe_allow_html=True)

                st.sidebar.success("Logado como {}".format(username))

                page_names_to_funcs = {
                    "Criar OP - Plasma": page1,
                    "Criar OP - Laser": page3,
                    "Finalizar OP": page2,
                    "Duplicador de OP": page4,
                }
                selected_page = st.selectbox("Selecione a função", page_names_to_funcs.keys())
                page_names_to_funcs[selected_page]() 
        else:
                st.sidebar.error("Nome de usuário/Senha incorreto")

elif choice == "Crie uma conta nova":
    st.markdown("<h1 style='color: black; font-size:30px;'>Crie uma conta nova</h1>", unsafe_allow_html=True)
    new_user = st.text_input("Nome de usuário")
    new_password = st.text_input("Password",type='password')

    if st.button("Crie uma conta nova"):
        create_usertable()
        add_userdata(new_user,make_hashes(new_password))
        st.success("Você criou com sucesso uma conta válida")
        st.info("Vá para o menu Login para fazer o login")