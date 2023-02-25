import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from gspread_formatting import *
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import time
from PIL import Image
from datetime import datetime, date
from datetime import timedelta
import datetime
import numpy as np

#Base gerador de ordem de producao

# Connect to Google Sheets
# ======================================= #

st.markdown("<h1 style='text-align: center; font-size:60px; color: White'>Apontamento de produção Pintura</h1>", unsafe_allow_html=True)

#with st.sidebar:
image = Image.open('logo-cemagL.png')
st.image(image, width=300)
#st.write(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

#@st.cache(allow_output_mutation=True)
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

def page1():
    
    wks1, sh1, table, table1 = load_datas()

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
        #gb.configure_column('QT_ITENS', cellStyle={'color': 'white', 'font-size': '15px'}, suppressMenu=True, wrapHeaderText=True, autoHeaderHeight=True)
        #gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        #custom_css = {".ag-header-cell-text": {"font-size": "15px", 'text-overflow': 'revert;', 'font-weight': 700},
        #".ag-theme-streamlit": {'transform': "scale(0.8)", "transform-origin": '0 0'}}
        grid_options = gb.build()

        grid_response = AgGrid(table_geral,
                                gridOptions=grid_options,
                                data_return_mode='AS_INPUT',
                                #custom_css=custom_css,
                                width='100%',
                                update_mode='VALUE_CHANGED',
                                height=500,
                                fit_columns_on_grid_load = True,
                                enable_enterprise_modules=True,
                                theme='streamlit',
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
            
            filter_new = filter_new.values.tolist()
            sh1.values_append('Pintura', {'valueInputOption': 'RAW'}, {'values': filter_new})

    if n_op != '':
        consultar(n_op,table)

def page2():
    
    wks1, sh1,table, table1 = load_datas()

    n_op = st.date_input("Data da carga")
    n_op = n_op.strftime("%d/%m/%Y")

    def consultar_2(wks1, n_op, sh1, table1):
            
        filter_ = table1.loc[(table1['DATA DA CARGA'] == n_op)]        
                        
        filter_ = filter_.reset_index(drop=True)
        
        filter_ = filter_.loc[(filter_['STATUS'] != 'OK')]

        filter_ = filter_.rename(columns={'QT APONT.':'PROD.','DATA DA CARGA':'DT. CARGA'})

        table_geral = filter_[['CODIGO', 'PEÇA', 'CAMBÃO', 'TIPO', 'PROD.','DT. CARGA','STATUS']]#, 'FLAG','SETOR']]

        gb = GridOptionsBuilder.from_dataframe(table_geral)
        gb.configure_default_column(min_column_width=100)
        gb.configure_column('STATUS', editable=True)
        #gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        grid_options = gb.build()

        grid_response = AgGrid(table_geral,
                                gridOptions=grid_options,
                                data_return_mode='AS_INPUT',
                                width='100%',
                                update_mode='VALUE_CHANGED',
                                height=500,
                                try_to_convert_back_to_original_types = False,
                                fit_columns_on_grid_load = True,
                                allow_unsafe_jscode=True,
                                enable_enterprise_modules=True,
                                theme='streamlit',
                                )    

        filter_new = grid_response['data']

        button2 = st.button('Salvar')

        if button2:
            
            filter_new['COR'] = ''
            filter_new['QT PLAN.'] = ''
            filter_new['COR'] = ''
            filter_new['SETOR'] = 'Pintura'
            filter_new['DATA FINALIZADA'] = datetime.datetime.now().strftime('%d/%m/%Y')
            
            filter_new['FLAG'] = '' 

            filter_new = filter_new[['FLAG','CODIGO', 'PEÇA','QT PLAN.','COR','PROD.','CAMBÃO','TIPO','DT. CARGA','DATA FINALIZADA','SETOR','STATUS']]#, 'FLAG','SETOR']]

            filter_new['CAMBÃO'] = filter_new['CAMBÃO'].astype(str)

            filter_new['FLAG'] = filter_new['CODIGO'] + filter_new['DATA FINALIZADA'] + filter_new['CAMBÃO']
            filter_new['FLAG'] = filter_new['FLAG'].replace('/','', regex=True)

            filter_new = filter_new.loc[(filter_new['STATUS'] != '')]

            lista_flags = filter_new[['FLAG']].values.tolist()
            
            for flags in range(len(lista_flags)):

                mudanca_status = table1.loc[(table1['FLAG']) == lista_flags[flags][0]]
                mudanca_status = mudanca_status.index[0]
                
                wks1.update("L" + str(mudanca_status+2), 'OK') 


    if n_op != '':
        consultar_2(wks1, n_op,sh1,table1)

page_names_to_funcs = {
    "Gerar Cambão": page1,
    "Cambão": page2,
}

selected_page = st.sidebar.selectbox("Selecione a função", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]() 