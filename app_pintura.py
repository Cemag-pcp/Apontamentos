import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

import streamlit as st
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from gspread_formatting import *

from PIL import Image
from datetime import datetime, date

import time
import datetime
import numpy as np

import base64
import hashlib # Security # passlib,hashlib,bcrypt,scrypt
import sqlite3 # DB Management

def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False

# DB Management
import sqlite3 
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

#Base gerador de ordem de producao

# Connect to Google Sheets
# ======================================= #

with st.sidebar:
    image = Image.open('logo-cemagL.png')
    st.image(image, width=300)

@st.cache_resource #(allow_output_mutation=True)
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

#@st.cache(allow_output_mutation=True)
#@st.experimental_singleton
def load_datas():

    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive"]
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')    

    name_sheet = 'Base gerador de ordem de producao'
    worksheet = 'Pintura'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list1 = wks.get_all_records()
    table = pd.DataFrame(list1)
    table = table.drop_duplicates()
        
    name_sheet1 = 'Base ordens de produçao finalizada'
    worksheet1 = 'Pintura'
    sh1 = sa.open(name_sheet1)
    wks1 = sh1.worksheet(worksheet1)
    list2 = wks1.get_all_records()
    table1 = pd.DataFrame(list2)
    
    return wks1, sh1,table, table1#, lista_unicos

#@st.cache(allow_output_mutation=True)
def load_datas1():

    scope = ['https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive"]
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')    

    name_sheet = 'Base gerador de ordem de producao'
    worksheet = 'Pintura'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list1 = wks.get_all_records()
    table = pd.DataFrame(list1)
    table = table.drop_duplicates()
        
    name_sheet1 = 'Base ordens de produçao finalizada'
    worksheet1 = 'Pintura'
    sh1 = sa.open(name_sheet1)
    wks1 = sh1.worksheet(worksheet1)
    list2 = wks1.get_all_records()
    table1 = pd.DataFrame(list2)
    
    return wks1, sh1,table, table1#, lista_unicos

def page1():
    
    wks1, sh1, table, table1 = load_datas()

    ultimo_id = table1['id'].max() + 1

    tabs_font_css = """
    <style>
    div[class*="stDateInput"] label p {
    font-size: 26px;
    color: black;
    }
    </style>
    """

    st.write(tabs_font_css, unsafe_allow_html=True)

    n_op = st.date_input("Data da carga")
    n_op = n_op.strftime("%d/%m/%Y")

    def consultar(n_op,table):

        filter_ = table.loc[(table['DATA DA CARGA'] == n_op)]        
        
        filter_['PROD.'] = ''
                
        filter_ = filter_.reset_index(drop=True)
            
        filter_['COR'] = ''
        
        for i in range(len(filter_)):    
            filter_['COR'][i] = filter_['CODIGO'][i][6:]
        
        #filter_['UNICO'] = filter_['CODIGO'] + n_op
        filter_ = filter_.rename(columns={'DESCRICAO':'DESC.', 'QT_ITENS':'PLAN.'})
        table_geral = filter_[['UNICO','CODIGO', 'DESC.', 'PLAN.', 'COR', 'PROD.']]
        table_geral['CAMBÃO'] = ''
        table_geral['TIPO'] = ''
        
        table_geral = table_geral[['CODIGO','DESC.','PLAN.','COR','PROD.','CAMBÃO','TIPO']]

        table_geral = table_geral.drop_duplicates(subset = ['CODIGO'], keep='last')

        dropdown_tipo = ('PO','PU','')

        gb = GridOptionsBuilder.from_dataframe(table_geral)
        gb.configure_default_column(min_column_width=10)
        gb.configure_column('PROD.', editable=True,)
        gb.configure_column('TIPO', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
        gb.configure_column('CAMBÃO', editable=True)
        
        cellstyle_jscode = JsCode("""
        function(params){
            if (params.value == 'AV') {
                return {
                    'color': 'black', 
                    'backgroundColor': 'yellow',
                }
            }
            if (params.value == 'VJ') {
                return {
                    'color': 'white', 
                    'backgroundColor': 'green',
                }
            }
            if (params.value == 'CO') {
                return {
                    'color': 'white', 
                    'backgroundColor': 'gray',
                }
            }
            if (params.value == 'LC') {
                return {
                    'color': 'white', 
                    'backgroundColor': 'orange',
                }
            }
            if (params.value == 'VM') {
                return {
                    'color': 'white', 
                    'backgroundColor': 'red',
                }
            } 
            if (params.value == 'AN') {
                return {
                    'color': 'white', 
                    'backgroundColor': 'blue',
                }
            }                        
        }
        """)

        gb.configure_column('COR', cellStyle=cellstyle_jscode)

        grid_options = gb.build()

        grid_response = AgGrid(table_geral,
                                gridOptions=grid_options,
                                data_return_mode='AS_INPUT',
                                #custom_css=custom_css,
                                width='100%',
                                #update_mode='MANUAL',
                                height=500,
                                fit_columns_on_grid_load = True,
                                enable_enterprise_modules=True,
                                theme='streamlit',
                                allow_unsafe_jscode=True
                                )    

        filter_new = grid_response['data']

        button2 = st.button('Salvar')

        if button2:
            
            filter_new['DATA DA CARGA'] = n_op  
            filter_new['DATA FINALIZADA'] = datetime.datetime.now().strftime('%d/%m/%Y')
            filter_new['UNICO'] = ''

            # for i in range(len(filter_new)):
            #     filter_new['UNICO'][i] = filter_new['CODIGO'] + filter_new['DATA DA CARGA'][i] + str(filter_new['CAMBÃO'][i])
            #     filter_new['UNICO'][i] = filter_new['UNICO'][i].replace('/','', regex=True) 
            
            filter_new = filter_new.replace({'PROD.':{'':0}})
            filter_new['PROD.'] = filter_new['PROD.'].astype(int)
            filter_new['SETOR'] = 'Pintura'
            #filter_new = filter_new.loc[(filter_new['QT. PRODUZIDA']>0) & (filter_new['TIPO'] != '') & (filter_new['CAMBÃO'] != 0)]

            #compare = table_geral.compare(filter_new, align_axis=1, keep_shape=False, keep_equal=False)
            #compare

            list_index = []

            for i in range(len(filter_new)):
                if filter_new['PROD.'][i] == 0 and filter_new['TIPO'][i] == '' and filter_new['CAMBÃO'][i] == '':  
                    ind = filter_new['PROD.'].index[i]
                    list_index.append(ind)
            
            filter_new = filter_new.drop(list_index, axis=0)

            filter_new = filter_new[['UNICO','CODIGO','DESC.','PLAN.','COR','PROD.','CAMBÃO','TIPO','DATA DA CARGA','DATA FINALIZADA','SETOR']]

            filter_new['UNICO'] = filter_new['CODIGO'] + filter_new['DATA FINALIZADA'] + filter_new['CAMBÃO']
            filter_new['UNICO'] = filter_new['UNICO'].replace("/",'',regex=True)
          
            filter_new['PROD.'] = filter_new['PROD.'].astype(int)
            filter_new['PLAN.'] = filter_new['PLAN.'].astype(int)
            filter_new['CAMBÃO'] = filter_new['CAMBÃO'].astype(int)

            try:
                for tipo in range(filter_new):
                    if filter_new['TIPO'][tipo] == '':
                        filter_new['TIPO'][tipo] = 'PO'
            except:
                pass

            filter_new = filter_new.values.tolist()
            sh1.values_append('Pintura', {'valueInputOption': 'RAW'}, {'values': filter_new})
        
    if n_op != '':
        consultar(n_op,table)

def page2():
    
    time.sleep(1.5)
    wks1, sh1,table, table1 = load_datas1()

    tabs_font_css = """
    <style>
    div[class*="stDateInput"] label p {
    font-size: 26px;
    color: black;
    }
    </style>
    """

    st.write(tabs_font_css, unsafe_allow_html=True)

    n_op = st.date_input("Data da carga")
    n_op = n_op.strftime("%d/%m/%Y")

    def consultar_2(wks1, n_op, sh1, table1):
            
        filter_ = table1.loc[(table1['DATA DA CARGA'] == n_op)]        
                        
        filter_ = filter_.reset_index(drop=True)
        
        filter_ = filter_.loc[(filter_['STATUS'] == '')]

        filter_ = filter_.rename(columns={'QT APONT.':'PROD.','DATA DA CARGA':'DT. CARGA'})

        table_geral = filter_[['id','CODIGO', 'PEÇA', 'CAMBÃO', 'TIPO', 'PROD.','DT. CARGA','STATUS']]#, 'FLAG','SETOR']]

        #coluna_id = filter_[['id']]
        
        gb = GridOptionsBuilder.from_dataframe(table_geral)
        gb.configure_default_column(min_column_width=100)
        gb.configure_column('STATUS', editable=True)
        #gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        grid_options = gb.build()

        grid_response = AgGrid(table_geral,
                                gridOptions=grid_options,
                                data_return_mode='AS_INPUT',
                                width='100%',
                                #update_mode='MANUAL',
                                height=500,
                                try_to_convert_back_to_original_types = False,
                                fit_columns_on_grid_load = True,
                                allow_unsafe_jscode=True,
                                enable_enterprise_modules=True,
                                theme='streamlit',
                                )    

        filter_new = grid_response['data']

        return filter_new,table1,wks1
    
    def salvar(filter_new,table1,wks1):  
                    
        filter_new['COR'] = ''
        filter_new['QT PLAN.'] = ''
        filter_new['COR'] = ''
        filter_new['SETOR'] = 'Pintura'
        filter_new['DATA FINALIZADA'] = datetime.datetime.now().strftime('%d/%m/%Y')
        
        filter_new['FLAG'] = '' 

        filter_new = filter_new[['FLAG','CODIGO', 'PEÇA','QT PLAN.','COR','PROD.','CAMBÃO','TIPO','DT. CARGA','DATA FINALIZADA','SETOR','STATUS','id']]#, 'FLAG','SETOR']]

        filter_new['CAMBÃO'] = filter_new['CAMBÃO'].astype(str)

        # filter_new['FLAG'] = filter_new['CODIGO'] + filter_new['DATA FINALIZADA'] + filter_new['CAMBÃO']
        # filter_new['FLAG'] = filter_new['FLAG'].replace('/','', regex=True)

        filter_new = filter_new.loc[(filter_new['STATUS'] != '')]

        table1 = table1.loc[(table1['STATUS'] == '')]
        
        lista_ids = filter_new['id'].values.tolist()
        
        mudanca_status = table1[table1['id'].isin(lista_ids)]
        
        for id in range(len(lista_ids)):
            wks1.update("L" + str(mudanca_status.index[id] + 2), 'OK')

    if n_op != '':
        #time.sleep(1.5)
        filter_new,table1,wks1 = consultar_2(wks1, n_op,sh1,table1)

    if st.button('Salvar'):
        salvar(filter_new,table1,wks1)

# Página inicial, login e senha
menu = ["Página inicial","Login"] # "SignUp"
choice = st.sidebar.selectbox("Menu",menu)

# Colocar algum tutorial de como usar o streamlit
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

                st.markdown("<h1 style='text-align: center; font-size:60px;'>Apontamento de produção Pintura</h1>", unsafe_allow_html=True)

                st.sidebar.success("Logado como {}".format(username))

                page_names_to_funcs = {
                    "Gerar Cambão": page1,
                    "Finalizar Cambão": page2,
                }
                selected_page = st.selectbox("Selecione a função", page_names_to_funcs.keys())
                page_names_to_funcs[selected_page]() 
        else:
                st.sidebar.error("Nome de usuário/Senha incorreto")
                
# elif choice == "SignUp":
#     st.subheader("Create New Account")
#     new_user = st.text_input("Username")
#     new_password = st.text_input("Password",type='password')

#     if st.button("Signup"):
#         create_usertable()
#         add_userdata(new_user,make_hashes(new_password))
#         st.success("You have successfully created a valid Account")
#         st.info("Go to Login Menu to login")

with st.sidebar:
    st.write("<h1 style='text-align: center; font-size:10px; color: black'>Versão 16</h1>", unsafe_allow_html=True)
    
    if st.button("Atualizar"):
    # Clears all singleton caches:
        st.experimental_singleton.clear()
    else:
        pass