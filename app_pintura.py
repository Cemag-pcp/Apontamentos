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
    
    def mostrar_novo_dataframe_4217():
        
        F = 'FALSE'
        T = 'TRUE'

        novo_dataframe = pd.DataFrame(tabela_antiga)  # Supondo que `novo_filtro` seja o resultado da grade interativa
        novo_dataframe['FINALIZADO?'] = novo_dataframe['FINALIZADO?'].apply(lambda x: x.replace("SIM",T).replace("NÃO",F))
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""]
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != "None"]
        novo_dataframe.reset_index(drop=True,inplace=True)
        novo_dataframe = novo_dataframe.replace('None','')

        if novo_dataframe['MÁQUINA'][0] == '':
            st.error('This is an error', icon="🚨")

            st.dataframe(novo_dataframe)
        else:

            id_alterado = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""][['ID']].values.tolist()[0][0]

            novo_dataframe1 = novo_dataframe.iloc[:,5:7]
            novo_dataframe2 = novo_dataframe.iloc[:,8:]

            novo_dataframe_lista1 = novo_dataframe1.values.tolist()
            novo_dataframe_lista2 = novo_dataframe2.values.tolist()
            
            name_sheet = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
            worksheet = 'OPERADOR 4217'
            sh = sa.open(name_sheet)
            wks = sh.worksheet(worksheet)
            list = wks.get()

            header = wks.row_values(5)
            
            table = pd.DataFrame(list)
            table =  table.iloc[:,0:15]
            table = table.set_axis(header, axis=1)
            table = table.iloc[5:]

            linha_para_alterar = str(table[table['ID'] == id_alterado].index[0] + 1)

            ###### Atualizar o indice na planilha

            # wks.update("F" + linha_para_alterar + ':G' + linha_para_alterar, novo_dataframe_lista1)
            # wks.update("I" + linha_para_alterar, novo_dataframe_lista2)

            wks.update("F" + '800' + ':G' + '800', novo_dataframe_lista1)
            wks.update("I" + '800', novo_dataframe_lista2)
            
            st.success('This is a success message!', icon="✅")
            
            st.dataframe(novo_dataframe1)
            st.dataframe(novo_dataframe2)
        
    def operador_4217():

        name_sheet = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet = 'OPERADOR 4217'
        sh = sa.open(name_sheet)
        wks = sh.worksheet(worksheet)
        list = wks.get()
        table = pd.DataFrame(list)

        table = table.iloc[4:]

        table.reset_index(drop=True)

        table = table.rename(columns={0:'ID',1:'DATA',2:'CÓDIGO',3:'DESCRIÇÃO',4:'QTD PROG',5:'QTD REALIZADA',6:'MÁQUINA',7:'FINALIZADO?',8:'Nº DE MORTAS',9:'MOTIVO',10:'OBSERVAÇÃO',11:'PENDENTE',12:'',13:'CONCAT',14:'QUERY'})
        
        table = table.loc[(table['QTD REALIZADA'] == '') & (table['CÓDIGO'] != '') & (table['MÁQUINA'] == '') & (table['FINALIZADO?'] == 'FALSE')]

        table['FINALIZADO?'] = ''

        table.reset_index(drop=True)

        dropdown_tipo = ('VIRADEIRA 1','VIRADEIRA 2','VIRADEIRA 3','VIRADEIRA 4','VIRADEIRA 5','PRENSA','FORJARIA','MONTAGEM')

        return dropdown_tipo, table

    dropdown_tipo, table = operador_4217()
    checkbox_state = st.session_state.get('checkbox_state', False)

# Exiba o checkbox
    checkbox_state = st.checkbox('Tabela', value=checkbox_state)

    # Verifique se o checkbox está marcado ou se foi previamente marcado
    if checkbox_state == True:
        gb = GridOptionsBuilder.from_dataframe(table)
        gb.configure_default_column(min_column_width=10)
        gb.configure_column('QTD REALIZADA', editable=True)
        gb.configure_column('MÁQUINA', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
        gb.configure_column('FINALIZADO?', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['SIM','NÃO']})
        gb.configure_column('Nº DE MORTAS', editable=True)
        # Adicione coluna de morta
        
        grid_options = gb.build()

        grid_response = AgGrid(table,
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
        try: 
            mostrar_novo_dataframe_4217()
        except:
            st.error('Clique no botão Update', icon="🚨")
    if checkbox_state == False:
        mostrar_novo_dataframe_4217()

    # Atualize o estado do checkbox quando o botão "Salvar" for clicado
    st.session_state['checkbox_state'] = checkbox_state
           
def page2():

    def mostrar_novo_dataframe_3654():
        
        F = 'FALSE'
        T = 'TRUE'

        novo_dataframe = pd.DataFrame(tabela_antiga)  # Supondo que `novo_filtro` seja o resultado da grade interativa
        novo_dataframe['FINALIZADO?'] = novo_dataframe['FINALIZADO?'].apply(lambda x: x.replace("SIM",T).replace("NÃO",F))
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""]
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != "None"]
        novo_dataframe.reset_index(drop=True,inplace=True)
        novo_dataframe = novo_dataframe.replace('None','')
        
        if novo_dataframe['MÁQUINA'][0] == '':
            st.error('This is an error', icon="🚨")

            st.dataframe(novo_dataframe)
        else:

            id_alterado = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""][['ID']].values.tolist()[0][0]

            novo_dataframe1 = novo_dataframe.iloc[:,5:7]
            novo_dataframe2 = novo_dataframe.iloc[:,8:]

            novo_dataframe_lista1 = novo_dataframe1.values.tolist()
            novo_dataframe_lista2 = novo_dataframe2.values.tolist()
            
            name_sheet2 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
            worksheet2 = 'OPERADOR 3654'
            sh2 = sa.open(name_sheet2)
            wks2 = sh2.worksheet(worksheet2)
            list2 = wks2.get()

            header = wks2.row_values(5)
            
            table2 = pd.DataFrame(list2)
            table2 =  table2.iloc[:,0:12]
            table2 = table2.set_axis(header, axis=1)
            table2 = table2.iloc[5:]

            linha_para_alterar = str(table2[table2['ID'] == id_alterado].index[0] + 1)

            ###### Atualizar o indice na planilha

            # wks2.update("F" + linha_para_alterar + ':G' + linha_para_alterar, novo_dataframe_lista1)
            # wks2.update("I" + linha_para_alterar, novo_dataframe_lista2)

            wks2.update("F" + '800' + ':G' + '800', novo_dataframe_lista1)
            wks2.update("I" + '800', novo_dataframe_lista2)
            
            st.success('This is a success message!', icon="✅")

            st.dataframe(novo_dataframe1)
            st.dataframe(novo_dataframe2)
          
    def operador_3654():

        name_sheet2 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet2 = 'OPERADOR 3654'
        sh2 = sa.open(name_sheet2)
        wks2 = sh2.worksheet(worksheet2)
        list2 = wks2.get()
        table2 = pd.DataFrame(list2)

        table2 = table2.iloc[4:]

        table2.reset_index(drop=True)

        table2 = table2.rename(columns={0:'ID',1:'DATA',2:'CÓDIGO',3:'DESCRIÇÃO',4:'QTD PROG',5:'QTD REALIZADA',6:'MÁQUINA',7:'FINALIZADO?',8:'Nº DE MORTAS',9:'MOTIVO',10:'OBSERVAÇÃO',11:'PENDENTE',12:'',13:'CONCAT',14:'QUERY'})
        
        table2 = table2.loc[(table2['QTD REALIZADA'] == '') & (table2['CÓDIGO'] != '') & (table2['MÁQUINA'] == '') & (table2['FINALIZADO?'] == 'FALSE')]

        table2['FINALIZADO?'] = ''

        table2.reset_index(drop=True)

        dropdown_tipo = ('VIRADEIRA 1','VIRADEIRA 2','VIRADEIRA 3','VIRADEIRA 4','VIRADEIRA 5','PRENSA','FORJARIA','MONTAGEM')

        return dropdown_tipo, table2

    dropdown_tipo, table2 = operador_3654()

    gb = GridOptionsBuilder.from_dataframe(table2)
    gb.configure_default_column(min_column_width=10)
    gb.configure_column('QTD REALIZADA', editable=True)
    gb.configure_column('MÁQUINA', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
    gb.configure_column('FINALIZADO?', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['SIM','NÃO']})
    gb.configure_column('Nº DE MORTAS',editable=True)
    #add coluna de morta
    
    grid_options = gb.build()

    grid_response = AgGrid(table2,
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
        mostrar_novo_dataframe_3654()
                
def page3():

    def mostrar_novo_dataframe_4238():
        
        F = 'FALSE'
        T = 'TRUE'

        novo_dataframe = pd.DataFrame(tabela_antiga)  # Supondo que `novo_filtro` seja o resultado da grade interativa
        novo_dataframe['FINALIZADO?'] = novo_dataframe['FINALIZADO?'].apply(lambda x: x.replace("SIM",T).replace("NÃO",F))
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""]
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != "None"]
        novo_dataframe.reset_index(drop=True,inplace=True)
        novo_dataframe = novo_dataframe.replace('None','')

        if novo_dataframe['MÁQUINA'][0] == '':
            st.error('This is an error', icon="🚨")

            st.dataframe(novo_dataframe)
        else:
            id_alterado = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""][['ID']].values.tolist()[0][0]

            novo_dataframe1 = novo_dataframe.iloc[:,5:7]
            novo_dataframe2 = novo_dataframe.iloc[:,8:]

            novo_dataframe_lista1 = novo_dataframe1.values.tolist()
            novo_dataframe_lista2 = novo_dataframe2.values.tolist()
            
            name_sheet3 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
            worksheet3 = 'OPERADOR 4238'
            sh3 = sa.open(name_sheet3)
            wks3 = sh3.worksheet(worksheet3)
            list3 = wks3.get()

            header = wks3.row_values(4)
            
            table3 = pd.DataFrame(list3)
            table3 =  table3.iloc[:,0:15]
            table3 = table3.set_axis(header, axis=1)
            table3 = table3.iloc[5:]

            linha_para_alterar = str(table3[table3['ID'] == id_alterado].index[0] + 1)

            ###### Atualizar o indice na planilha

            # wks3.update("F" + linha_para_alterar + ':G' + linha_para_alterar, novo_dataframe_lista1)
            # wks3.update("I" + linha_para_alterar, novo_dataframe_lista2)

            wks3.update("F" + '800' + ':G' + '800', novo_dataframe_lista1)
            wks3.update("I" + '800', novo_dataframe_lista2)
            
            st.success('This is a success message!', icon="✅")

            st.dataframe(novo_dataframe1)
            st.dataframe(novo_dataframe2)

    def operador_4238():

        name_sheet3 = 'RQ PCP-003-001 (APONTAMENTO ESTAMPARIA) / RQ PCP-009-000 (SEQUENCIAMENTO ESTAMPARIA) e RQ CQ-015-000 (Inspeção da Estamparia)'
        worksheet3 = 'OPERADOR 4238'
        sh3 = sa.open(name_sheet3)
        wks3 = sh3.worksheet(worksheet3)
        list3 = wks3.get()
        table3 = pd.DataFrame(list3)

        table3 = table3.iloc[4:]

        table3.reset_index(drop=True)

        table3 = table3.rename(columns={0:'ID',1:'DATA',2:'CÓDIGO',3:'DESCRIÇÃO',4:'QTD PROG',5:'QTD REALIZADA',6:'MÁQUINA',7:'FINALIZADO?',8:'Nº DE MORTAS',9:'MOTIVO',10:'OBSERVAÇÃO',11:'PENDENTE',12:'',13:'CONCAT',14:'QUERY'})
        
        table3 = table3.loc[(table3['QTD REALIZADA'] == '') & (table3['CÓDIGO'] != '') & (table3['MÁQUINA'] == '') & (table3['FINALIZADO?'] == 'FALSE')]

        table3['FINALIZADO?'] = ''

        table3.reset_index(drop=True)

        dropdown_tipo = ('VIRADEIRA 1','VIRADEIRA 2','VIRADEIRA 3','VIRADEIRA 4','VIRADEIRA 5','PRENSA','FORJARIA','MONTAGEM')

        return dropdown_tipo, table3

    dropdown_tipo, table3 = operador_4238()

    gb = GridOptionsBuilder.from_dataframe(table3)
    gb.configure_default_column(min_column_width=10)
    gb.configure_column('QTD REALIZADA', editable=True)
    gb.configure_column('MÁQUINA', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': dropdown_tipo})
    gb.configure_column('FINALIZADO?', editable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['SIM','NÃO']})
    gb.configure_column('Nº DE MORTAS',editable=True)
    #add coluna de morta
    
    grid_options = gb.build()

    grid_response = AgGrid(table3,
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
        mostrar_novo_dataframe_4238()

def page4():
    
    def mostrar_novo_dataframe_4200():
        
        F = 'FALSE'
        T = 'TRUE'

        novo_dataframe = pd.DataFrame(tabela_antiga)  # Supondo que `novo_filtro` seja o resultado da grade interativa
        novo_dataframe['FINALIZADO?'] = novo_dataframe['FINALIZADO?'].apply(lambda x: x.replace("SIM",T).replace("NÃO",F))
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != ""]
        novo_dataframe = novo_dataframe[novo_dataframe['QTD REALIZADA'] != "None"]
        novo_dataframe.reset_index(drop=True,inplace=True)

        if novo_dataframe['MÁQUINA'][0] == '':
            st.error('This is an error', icon="🚨")

            st.dataframe(novo_dataframe)
        else:

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

            # wks4.update("F" + linha_para_alterar + ':G' + linha_para_alterar, novo_dataframe_lista1)
            # wks4.update("I" + linha_para_alterar, novo_dataframe_lista2)

            wks4.update("F" + '800' + ':G' + '800', novo_dataframe_lista1)
            wks4.update("I" + '800', novo_dataframe_lista2)

            st.success('This is a success message!', icon="✅")

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
    gb.configure_column('Nº DE MORTAS',editable=True)
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
    
    if st.button('Salvar'):
        mostrar_novo_dataframe_4200()
                
page_names_to_funcs = {
    "OPERADOR 4217": page1,
    "OPERADOR 3654": page2,
    "OPERADOR 4238": page3,
    "OPERADOR 4200": page4,
}

selected_page = st.sidebar.selectbox("Selecione a função", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]() 