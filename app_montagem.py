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

st.markdown("<h1 style='text-align: center; font-size:60px; color: White'>Apontamento de produção</h1>", unsafe_allow_html=True)

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
    worksheet = 'Montagem'
    sh = sa.open(name_sheet)
    wks = sh.worksheet(worksheet)
    list1 = wks.get_all_records()
    table = pd.DataFrame(list1)
    table = table.drop_duplicates()
        
    name_sheet1 = 'Base ordens de produçao finalizada'
    worksheet1 = 'Montagem'
    sh1 = sa.open(name_sheet1)
    wks1 = sh1.worksheet(worksheet1)
    list2 = wks1.get_all_records()
    table1 = pd.DataFrame(list2)
    
    return sh1, table1, table#, lista_unicos

def consultar(celula, n_op,table1,table):
        
    filter_ = table.loc[(table['DATA DA CARGA'] == n_op) & (table['CELULA'] == celula)]
    
    filter_['QT. PRODUZIDA'] = 0
            
    filter_ = filter_.reset_index(drop=True)

    if len(table1.loc[(table1['DATA DA CARGA'] == n_op) & (table1['SETOR'] == celula)]) != 0:
        
        tab2 = table1.loc[(table1['DATA DA CARGA'] == n_op) & (table1['SETOR'] == celula)]   
        
        filter_['QT. PRODUZIDA'] = 0
        
        filter_ = filter_[['UNICO','CODIGO', 'DESCRICAO', 'QT_ITENS', 'QT. PRODUZIDA', 'DATA DA CARGA']]

        df3 = tab2[['CODIGO']]        
        df3 = pd.merge(filter_,df3, on=['CODIGO'], how='left').drop_duplicates(keep = 'last', subset=['CODIGO'])
                
        qt_total = tab2[['CODIGO','QT APONT.']].groupby(['CODIGO']).sum().reset_index()        
        qt_total.drop(qt_total[qt_total['QT APONT.'] == 0].index, inplace=True)
        
        df3 = pd.merge(df3, qt_total, on=['CODIGO'], how='left')
        df3 = df3.replace(np.nan,0)
            
        table_geral = df3
        table_geral = table_geral[['UNICO', 'CODIGO', 'DESCRICAO', 'QT_ITENS','DATA DA CARGA', 'QT. PRODUZIDA', 'QT APONT.']]
        
    else:
        
        table_geral = filter_.copy()
        table_geral['QT APONT.'] = 0
        table_geral['QT. PRODUZIDA'] = 0 
        table_geral = table_geral[['UNICO', 'CODIGO', 'DESCRICAO', 'QT_ITENS','DATA DA CARGA', 'QT. PRODUZIDA','QT APONT.']]
  
        
    return table_geral

n_op = st.date_input("Data da carga")
n_op = n_op.strftime("%d/%m/%Y")

celula = 'SELECIONE'

celula = st.selectbox(
'Escolha a célula',
('SELECIONE', 'EIXO SIMPLES','EIXO COMPLETO','PLAT. TANQUE. CAÇAM.','IÇAMENTO','FUEIRO', 'LATERAL', 'CHASSI'))

#button1 = st.button('Procurar')

# if st.session_state.get('button') != True:

#     st.session_state['button'] = button1

# if st.session_state['button'] == True:
if celula != 'SELECIONE':

    sh1, table1, table = load_datas()
    table_geral = consultar(celula, n_op,table1,table)

    table_geral = table_geral[['CODIGO','DESCRICAO','QT_ITENS','QT. PRODUZIDA','QT APONT.']]
    table_geral = table_geral.drop_duplicates(subset=['CODIGO'] , keep='last')
    table_geral = table_geral.reset_index(drop=True)
    table_geral['CODIGO'] = table_geral['CODIGO'].astype(str)

    for i in range(len(table_geral)):
        try:
            if len(table_geral['CODIGO'][i]) == 5:
                table_geral['CODIGO'][i] = '0' + table_geral['CODIGO'][i]
        except:
            pass
    
    gb = GridOptionsBuilder.from_dataframe(table_geral)
    gb.configure_default_column(min_column_width=110)
    gb.configure_column('QT. PRODUZIDA', editable=True)
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

        filter_new['DATA DA CARGA'] = n_op  
        filter_new['DATA FINALIZADA'] = datetime.datetime.now().strftime('%d/%m/%Y')
        filter_new = filter_new.replace({'QT. PRODUZIDA':{'':0}})
        #filter_new['QT APONT.'] = filter_new['QT APONT.'].astype(int)
        #filter_new['QT APONT.'] = filter_new.loc[(filter_new['QT APONT.'] > 0)]
        filter_new = filter_new.drop(columns={'QT APONT.'})
        filter_new['QT. PRODUZIDA'] = filter_new['QT. PRODUZIDA'].astype(int)
        filter_new = filter_new.loc[(filter_new['QT. PRODUZIDA']>0)]
        filter_new['SETOR'] = celula
        unico = n_op.replace("/","")

        filter_new['CODIGO'] = filter_new['CODIGO'].astype(str) 
        
        for i in range(len(filter_new)):
            try:
                if len(filter_new['CODIGO'][i]) == 5:
                    filter_new['CODIGO'][i] = '0' + filter_new['CODIGO'][i]
            except:
                pass

        filter_new['UNICO'] = unico + filter_new['CODIGO']

        filter_new = filter_new[['UNICO','CODIGO','DESCRICAO','QT_ITENS','QT. PRODUZIDA', 'DATA DA CARGA', 'DATA FINALIZADA', 'SETOR']]

        filter_new = filter_new.values.tolist()
        sh1.values_append('Montagem', {'valueInputOption': 'RAW'}, {'values': filter_new})

        celula = 'SELECIONE'