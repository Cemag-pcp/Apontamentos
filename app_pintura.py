import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

import streamlit as st
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from gspread_formatting import *

from PIL import Image
from datetime import datetime, date
import datetime
import numpy as np

#Base gerador de ordem de producao

# Connect to Google Sheets
# ======================================= #

st.markdown("<h1 style='text-align: center; color:white;font-size:60px;>Apontamento de produção Estamparia</h1>", unsafe_allow_html=True)

with st.sidebar:
    image = Image.open('logo-cemagL.png')
    st.image(image, width=300)
#st.write(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

#@st.cache(allow_output_mutation=True)

scope = ['https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)
sa = gspread.service_account('service_account.json')    

def page1():
    
    def operador_4217(table1):

        name_sheet1 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet1 = 'OPERADOR 4217'
        sh1 = sa.open(name_sheet1)
        wks1 = sh1.worksheet(worksheet1)
        list1 = wks1.get()
        table1 = pd.DataFrame(list1)     
        
        table1 = table1.iloc[4:]

        table1.reset_index(drop=True)

        table1 = table1.rename(columns={0:'ID',1:'DATA',2:'CÓDIGO',3:'DESCRIÇÃO',4:'QTD PROG',5:'QTD REALIZADA',6:'MÁQUINA',7:'FINALIZADO?',8:'Nº DE MORTAS',9:'MOTIVO',10:'OBSERVAÇÃO',11:'PENDENTE',12:'',13:'CONCAT',14:'QUERY'})

        table1 = table1.loc[(table1['QTD REALIZADA'] == '') & (table1['CÓDIGO'] != '') & (table1['MÁQUINA'] == '')]

        table1.reset_index(drop=True)

        dropdown_tipo = ('VIRADEIRA 1','VIRADEIRA 2','VIRADEIRA 3','VIRADEIRA 4','VIRADEIRA 5','PRENSA','FORJARIA','MONTAGEM')

        gb = GridOptionsBuilder.from_dataframe(table1)
        gb.configure_default_column(min_column_width=10)
        gb.configure_column('QTD PROG', editable=True,)
        gb.configure_column('QTD REALIZADA', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
        gb.configure_column('MÁQUINA', editable=True)

        grid_options = gb.build()

        grid_response = AgGrid(table1,
                                gridOptions=grid_options,
                                data_return_mode='AS_INPUT',
                                #custom_css=custom_css,
                                width='100%',
                                update_mode='MANUAL',
                                height=500,
                                fit_columns_on_grid_load = True,
                                enable_enterprise_modules=True,
                                theme='streamlit',
                                allow_unsafe_jscode=True
                                )    

        novo_filtro = grid_response['data']

        button_estamparia = st.button('Salvar')

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
                                    update_mode='MANUAL',
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
                
                try:
                    for tipo in range(filter_new):
                        if filter_new['TIPO'][tipo] == '':
                            filter_new['TIPO'][tipo] = 'PO'
                except:
                    pass

                filter_new = filter_new.values.tolist()
                sh1.values_append('Pintura', {'valueInputOption': 'RAW'}, {'values': filter_new})

def page2():

    def operador_3654(table2):
        name_sheet2 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet2 = 'OPERADOR 3654 '
        sh2 = sa.open(name_sheet2)
        wks2 = sh2.worksheet(worksheet2)
        list2 = wks2.get()
        table2 = pd.DataFrame(list2)  

        table2 = table2.iloc[4:]

        table2.reset_index(drop=True)

        table2 = table2.rename(columns={0:'ID',1:'DATA',2:'CÓDIGO',3:'DESCRIÇÃO',4:'QTD PROG',5:'QTD REALIZADA',6:'MÁQUINA',7:'FINALIZADO?',8:'Nº DE MORTAS',9:'MOTIVO',10:'OBSERVAÇÃO',11:'PENDENTE',12:'',13:'CONCAT',14:'QUERY'})

        table2 = table2.loc[(table2['QTD REALIZADA'] == '') & (table2['CÓDIGO'] != '') & (table2['MÁQUINA'] == '')]

        table2.reset_index(drop=True)

        dropdown_tipo = ('VIRADEIRA 1','VIRADEIRA 2','VIRADEIRA 3','VIRADEIRA 4','VIRADEIRA 5','PRENSA','FORJARIA','MONTAGEM')

        gb = GridOptionsBuilder.from_dataframe(table2)
        gb.configure_default_column(min_column_width=10)
        gb.configure_column('QTD PROG', editable=True,)
        gb.configure_column('QTD REALIZADA', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
        gb.configure_column('MÁQUINA', editable=True)

        grid_options = gb.build()

        grid_response = AgGrid(table2,
                                gridOptions=grid_options,
                                data_return_mode='AS_INPUT',
                                #custom_css=custom_css,
                                width='100%',
                                update_mode='MANUAL',
                                height=500,
                                fit_columns_on_grid_load = True,
                                enable_enterprise_modules=True,
                                theme='streamlit',
                                allow_unsafe_jscode=True
                                )    
        
        novo_filtro = grid_response['data']

        button_estamparia = st.button('Salvar')

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
                                    update_mode='MANUAL',
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
                
                table1 = table1.loc[(table1['STATUS'] == '')]

                for flags in range(len(lista_flags)):

                    mudanca_status = table1.loc[(table1['FLAG']) == lista_flags[flags][0]]
                    mudanca_status = mudanca_status.index[0] 

                    wks1.update("L" + str(mudanca_status+2), 'OK')

        if n_op != '':
            consultar_2(wks1, n_op,sh1,table1)

def page3():

    def operador_4238(table3):
        name_sheet3 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet3= 'OPERADOR 4238'
        sh1 = sa.open(name_sheet3)
        wks2 = sh1.worksheet(worksheet3)
        list3 = wks2.get()
        table3 = pd.DataFrame(list3)  

        table3 = table3.iloc[4:]

        table3.reset_index(drop=True)

        table3 = table3.rename(columns={0:'ID',1:'DATA',2:'CÓDIGO',3:'DESCRIÇÃO',4:'QTD PROG',5:'QTD REALIZADA',6:'MÁQUINA',7:'FINALIZADO?',8:'Nº DE MORTAS',9:'MOTIVO',10:'OBSERVAÇÃO',11:'PENDENTE',12:'',13:'CONCAT',14:'QUERY'})

        table3 = table3.loc[(table3['QTD REALIZADA'] == '') & (table3['CÓDIGO'] != '') & (table3['MÁQUINA'] == '')]

        table3.reset_index(drop=True)

        dropdown_tipo = ('VIRADEIRA 1','VIRADEIRA 2','VIRADEIRA 3','VIRADEIRA 4','VIRADEIRA 5','PRENSA','FORJARIA','MONTAGEM')

        gb = GridOptionsBuilder.from_dataframe(table3)
        gb.configure_default_column(min_column_width=10)
        gb.configure_column('QTD PROG', editable=True,)
        gb.configure_column('QTD REALIZADA', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
        gb.configure_column('MÁQUINA', editable=True)

        grid_options = gb.build()

        grid_response = AgGrid(table3,
                                gridOptions=grid_options,
                                data_return_mode='AS_INPUT',
                                #custom_css=custom_css,
                                width='100%',
                                update_mode='MANUAL',
                                height=500,
                                fit_columns_on_grid_load = True,
                                enable_enterprise_modules=True,
                                theme='streamlit',
                                allow_unsafe_jscode=True
                                )    
        
        filter_ = grid_response['data']

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
                                    update_mode='MANUAL',
                                    height=500,
                                    try_to_convert_back_to_original_types = False,
                                    fit_columns_on_grid_load = True,
                                    allow_unsafe_jscode=True,
                                    enable_enterprise_modules=True,
                                    theme='streamlit',
                                    )    

            filter_new = grid_response['data']

            button2 = st.button('Salvar')

def page4():
    
    def mostrar_novo_dataframe():
        
        F = 'FALSE'
        T = 'TRUE'

        novo_dataframe = pd.DataFrame(tabela_antiga)  # Supondo que `novo_filtro` seja o resultado da grade interativa
        novo_dataframe['FINALIZADO?'] = novo_dataframe['FINALIZADO?'].apply(lambda x: x.replace("SIM",T).replace("NÃO",F))
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""]
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != "None"]

        id_alterado = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""][['ID']].values.tolist()[0][0]

        novo_dataframe1 = novo_dataframe.iloc[:,5:7]
        novo_dataframe2 = novo_dataframe.iloc[:,8:]

        novo_dataframe_lista1 = novo_dataframe1.values.tolist()
        novo_dataframe_lista2 = novo_dataframe2.values.tolist()
        
        name_sheet4 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet4 = 'OPERADOR 4200'
        sh4 = sa.open(name_sheet4)
        wks4 = sh4.worksheet(worksheet4)
        list4 = wks4.get()

        header = wks4.row_values(5)
        
        table4 = pd.DataFrame(list4)
        table4 =  table4.iloc[:,0:14]
        table4 = table4.set_axis(header, axis=1)
        table4 = table4.iloc[5:]

        linha_para_alterar = str(table4[table4['ID'] == id_alterado].index[0] + 1)

        ###### Atualizar o indice na planilha

        wks4.update("F" + '177:G' + '177', novo_dataframe_lista1)
        wks4.update("I" + '177', novo_dataframe_lista2)
        
        st.dataframe(novo_dataframe1)
        st.dataframe(novo_dataframe2)
        
        
    def operador_4200():

        name_sheet4 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet4 = 'OPERADOR 4200'
        sh4 = sa.open(name_sheet4)
        wks4 = sh4.worksheet(worksheet4)
        list4 = wks4.get()
        table4 = pd.DataFrame(list4)

        table4 = table4.iloc[4:]

        table4.reset_index(drop=True)

        table4 = table4.rename(columns={0:'ID',1:'DATA',2:'CÓDIGO',3:'DESCRIÇÃO',4:'QTD PROG',5:'QTD REALIZADA',6:'MÁQUINA',7:'FINALIZADO?',8:'Nº DE MORTAS',9:'MOTIVO',10:'OBSERVAÇÃO',11:'PENDENTE',12:'',13:'CONCAT',14:'QUERY'})
        
        table4 = table4.loc[(table4['QTD REALIZADA'] == '') & (table4['CÓDIGO'] != '') & (table4['MÁQUINA'] == '') & (table4['FINALIZADO?'] == 'FALSE')]

        table4['FINALIZADO?'] = ''

        table4.reset_index(drop=True)

        dropdown_tipo = ('VIRADEIRA 1','VIRADEIRA 2','VIRADEIRA 3','VIRADEIRA 4','VIRADEIRA 5','PRENSA','FORJARIA','MONTAGEM')

        return dropdown_tipo, table4

    dropdown_tipo, table4 = operador_4200()

    gb = GridOptionsBuilder.from_dataframe(table4)
    gb.configure_default_column(min_column_width=10)
    gb.configure_column('QTD REALIZADA', editable=True)
    gb.configure_column('MÁQUINA', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
    gb.configure_column('FINALIZADO?', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['SIM','NÃO']})
    #add coluna de morta
    
    grid_options = gb.build()

    grid_response = AgGrid(table4,
                            gridOptions=grid_options,
                            data_return_mode='AS_INPUT',
                            width='100%',
                            update_mode='MANUAL',
                            theme='streamlit',
                            allow_unsafe_jscode=True
                            )    
    
    tabela_antiga = grid_response['data']

    # Crie o botão para mostrar o novo dataframe
    if st.button('Salvar'):
        mostrar_novo_dataframe()
                
    
page_names_to_funcs = {
    "OPERADOR 4217": page1,
    "OPERADOR 3654": page2,
    "OPERADOR 4238": page3,
    "OPERADOR 4200": page4,
}

selected_page = st.sidebar.selectbox("Selecione a função", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]() 