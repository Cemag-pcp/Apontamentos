import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from gspread_formatting import *
from datetime import datetime, date
from datetime import timedelta
import datetime
import numpy as np
from pandas.tseries.offsets import BDay
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
### campos ###

def exibir():
        
    scope = ['https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')  

    name_sheet = 'Plano 52 semanas - Manutenção Preventiva'
    worksheet = '52 semanas'

    sh = sa.open(name_sheet)

    wks = sh.worksheet(worksheet)
        
    list1 = wks.get_all_records()
    table = pd.DataFrame(list1)

    return table, wks, sh

def save_db(df):
        
    scope = ['https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')  

    name_sheet = 'Plano 52 semanas - Manutenção Preventiva'
    worksheet = '52 semanas'
    
    sh = sa.open(name_sheet)
    
    df_list = df.values.tolist()

    sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})

def ler_arquivo(df):
        
        df_maquinas = pd.DataFrame(data = df, columns=['Grupo','Máquina','Classificação','Última Manutenção','Periodicidade'])
        
        # Converte a coluna de data para o tipo datetime
        df_maquinas['Última Manutenção'] = pd.to_datetime(df_maquinas['Última Manutenção'])
        
        # Cria um DataFrame vazio para armazenar o planejamento de manutenção
        df_manutencao = pd.DataFrame(columns=['Última Manutenção', 'Máquina'])
        manut_outras_maquinas = False

        # Loop pelas máquinas
        for i, row in df_maquinas.iterrows():
            # Define as variáveis da máquina atual
            periodicidade = row['Periodicidade']
            
            if periodicidade == 'Quinzenal':
                nome_maquina = row['Máquina']
                classificacao = row['Classificação']
                primeira_manutencao = row['Última Manutenção']
                periodicidade = row['Periodicidade']
                grupo = row['Grupo']
                
                semana_inicial = primeira_manutencao.isocalendar().week
                data_manutencao = primeira_manutencao + 14 * BDay()
                
                # Loop pelas semanas
                for j in range(52-semana_inicial):
                    # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                    while data_manutencao.weekday() in [5, 6]:
                        data_manutencao = data_manutencao + 1 * BDay()
            
                    df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Máquina': nome_maquina,
                                                        'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                        
                    # Avança para a próxima data de manutenção
                    data_manutencao = data_manutencao + 14 * BDay()
            
            if periodicidade == 'Bimestral':
                nome_maquina = row['Máquina']
                classificacao = row['Classificação']
                primeira_manutencao = row['Última Manutenção']
                periodicidade = row['Periodicidade']
                grupo = row['Grupo']
                
                semana_inicial = primeira_manutencao.isocalendar().week
                data_manutencao = primeira_manutencao + 39 * BDay()
                
                # Loop pelas semanas
                for j in range(52-semana_inicial):
                    # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                    while data_manutencao.weekday() in [5, 6]:
                        data_manutencao = data_manutencao + 1 * BDay()
            
                    df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Máquina': nome_maquina,
                                                        'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                        
                    # Avança para a próxima data de manutenção
                    data_manutencao = data_manutencao + 39 * BDay()
                    
            if periodicidade == 'Semanal':
                nome_maquina = row['Máquina']
                classificacao = row['Classificação']
                primeira_manutencao = row['Última Manutenção']
                periodicidade = row['Periodicidade']
                grupo = row['Grupo']
                
                semana_inicial = primeira_manutencao.isocalendar().week
                data_manutencao = primeira_manutencao + 6 * BDay()
                
                # Loop pelas semanas
                for j in range(52-semana_inicial):
                    # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                    while data_manutencao.weekday() in [5, 6]:
                        data_manutencao = data_manutencao + 1 * BDay()
            
                    df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Máquina': nome_maquina,
                                                        'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                        
                    # Avança para a próxima data de manutenção
                    data_manutencao = data_manutencao + 6 * BDay()
                    
        df_manutencao['Week_Number'] = df_manutencao['Última Manutenção'].dt.isocalendar().week
        df_manutencao['year'] = df_manutencao['Última Manutenção'].dt.isocalendar().year
        
        df_manutencao['Week_Number'] = df_manutencao['Week_Number'].astype(int) 
        
        df_manutencao = df_manutencao.loc[(df_manutencao['year'] == 2023)] 
        
        df_manutencao['Última Manutenção'] = df_manutencao['Última Manutenção'].dt.strftime("%d-%m-%Y") 
        
        ############### 52 semanas ##################
        
        lista_maq = df_manutencao['Máquina'].unique()
        
        df_filter = df_manutencao.loc[(df_manutencao['Máquina'] == lista_maq[i])] 
        
        df_vazio = pd.DataFrame()
        
        list_52 = ['Grupo', 'Máquina','Classificação', 'Periodicidade','Última manutenção']
        
        for li in range(1,53):
            list_52.append(li)
            
        index = 0
        
        df_vazio = pd.DataFrame()
        
        for i in range(len(lista_maq)):
                
            df_52semanas = pd.DataFrame(columns=list_52, index=[index]) 
            df_filter = df_manutencao.loc[(df_manutencao['Máquina'] == lista_maq[i])] 
            df_filter = df_filter.reset_index(drop=True)
            df_52semanas['Máquina'] = df_filter['Máquina'][i]
            df_52semanas['Periodicidade'] = df_filter['Periodicidade'][i]
            df_52semanas['Classificação'] = df_filter['Classificação'][i]
            df_52semanas['Grupo'] = df_filter['Grupo'][i]
            df_52semanas['Última manutenção'] = df_filter['primeira_manutencao'][i]
            
            index = index + 1
            
            for k in range(len(df_filter)):
                number_week = df_filter['Week_Number'][k]
                df_52semanas[number_week] = df_filter['Última Manutenção'][k]
                
            df_vazio = df_vazio.append(df_52semanas) 
        
        df_vazio = df_vazio.replace(np.nan, '')
        
        return df_vazio

def gerador_de_semanas(grupo,maquina,classificacao,ultima_manutencao,periodicidade):

        lista_campos = []
        
        lista_campos.append([grupo,maquina,classificacao,ultima_manutencao,periodicidade])
        
        df_maquinas = pd.DataFrame(data = lista_campos, columns=['Grupo','Máquina','Classificação','Última Manutenção','Periodicidade'])
        
        # Converte a coluna de data para o tipo datetime
        df_maquinas['Última Manutenção'] = pd.to_datetime(df_maquinas['Última Manutenção'])
        
        # Cria um DataFrame vazio para armazenar o planejamento de manutenção
        df_manutencao = pd.DataFrame(columns=['Última Manutenção', 'Máquina'])
        manut_outras_maquinas = False

        # Loop pelas máquinas
        for i, row in df_maquinas.iterrows():
            # Define as variáveis da máquina atual
            periodicidade = row['Periodicidade']
            
            if periodicidade == 'Quinzenal':
                nome_maquina = row['Máquina']
                primeira_manutencao = row['Última Manutenção']
                periodicidade = row['Periodicidade']
                grupo = row['Grupo']
                
                semana_inicial = primeira_manutencao.isocalendar().week
                data_manutencao = primeira_manutencao + 14 * BDay()
                
                # Loop pelas semanas
                for j in range(52-semana_inicial):
                    # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                    while data_manutencao.weekday() in [5, 6]:
                        data_manutencao = data_manutencao + 1 * BDay()
            
                    df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Máquina': nome_maquina,
                                                        'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                        
                    # Avança para a próxima data de manutenção
                    data_manutencao = data_manutencao + 14 * BDay()
            
            if periodicidade == 'Bimestral':
                nome_maquina = row['Máquina']
                classificacao = row['Classificação']
                primeira_manutencao = row['Última Manutenção']
                periodicidade = row['Periodicidade']
                grupo = row['Grupo']
                
                semana_inicial = primeira_manutencao.isocalendar().week
                data_manutencao = primeira_manutencao + 39 * BDay()
                
                # Loop pelas semanas
                for j in range(52-semana_inicial):
                    # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                    while data_manutencao.weekday() in [5, 6]:
                        data_manutencao = data_manutencao + 1 * BDay()
            
                    df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Máquina': nome_maquina,
                                                        'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                        
                    # Avança para a próxima data de manutenção
                    data_manutencao = data_manutencao + 39 * BDay()
                    
            if periodicidade == 'Semanal':
                nome_maquina = row['Máquina']
                classificacao = row['Classificação']
                primeira_manutencao = row['Última Manutenção']
                periodicidade = row['Periodicidade']
                grupo = row['Grupo']
                
                semana_inicial = primeira_manutencao.isocalendar().week
                data_manutencao = primeira_manutencao + 6 * BDay()
                
                # Loop pelas semanas
                for j in range(52-semana_inicial):
                    # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                    while data_manutencao.weekday() in [5, 6]:
                        data_manutencao = data_manutencao + 1 * BDay()
            
                    df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Máquina': nome_maquina,
                                                        'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                        
                    # Avança para a próxima data de manutenção
                    data_manutencao = data_manutencao + 6 * BDay()
                    
        df_manutencao['Week_Number'] = df_manutencao['Última Manutenção'].dt.isocalendar().week
        df_manutencao['year'] = df_manutencao['Última Manutenção'].dt.isocalendar().year
        
        df_manutencao['Week_Number'] = df_manutencao['Week_Number'].astype(int) 
        
        df_manutencao = df_manutencao.loc[(df_manutencao['year'] == 2023)] 
        
        df_manutencao['Última Manutenção'] = df_manutencao['Última Manutenção'].dt.strftime("%d-%m-%Y") 
        
        ############### 52 semanas ##################
        
        lista_maq = df_manutencao['Máquina'].unique()
        
        df_filter = df_manutencao.loc[(df_manutencao['Máquina'] == lista_maq[i])] 
        
        df_vazio = pd.DataFrame()
        
        list_52 = ['Grupo', 'Máquina','Classificação', 'Periodicidade','Última manutenção']
        
        for li in range(1,53):
            list_52.append(li)
            
        index = 0
        
        df_vazio = pd.DataFrame()
        
        for i in range(len(lista_maq)):
                
            df_52semanas = pd.DataFrame(columns=list_52, index=[index]) 
            df_filter = df_manutencao.loc[(df_manutencao['Máquina'] == lista_maq[i])] 
            df_filter = df_filter.reset_index(drop=True)
            df_52semanas['Máquina'] = df_filter['Máquina'][i]
            df_52semanas['Periodicidade'] = df_filter['Periodicidade'][i]
            df_52semanas['Classificação'] = df_filter['Classificação'][i]
            df_52semanas['Grupo'] = df_filter['Grupo'][i]
            df_52semanas['Última manutenção'] = df_filter['primeira_manutencao'][i]
            
            index = index + 1
            
            for k in range(len(df_filter)):
                number_week = df_filter['Week_Number'][k]
                df_52semanas[number_week] = df_filter['Última Manutenção'][k]
                
            df_vazio = df_vazio.append(df_52semanas) 
        
        df_vazio = df_vazio.replace(np.nan, '')
        
        return df_vazio

def page1():

    st.markdown("<h1 style='text-align: center; font-size:60px; color: White'>Cadastro de máquinas</h1>", unsafe_allow_html=True)
    st.markdown("<h1          </h1>", unsafe_allow_html=True)

    with st.form('cadastrar maquina', clear_on_submit=True):

        grupo = st.text_input("Setor")
        maquina = st.text_input("Máquina")
        classificacao = st.select_slider("Classificação", options=['A','B','C'])
        ultima_manutencao = st.date_input("Última manutenção")
        periodicidade = st.selectbox('Selecione a periodicidade',('Semanal','Quinzenal','Bimestral'))
        submitted_button = st.form_submit_button("Run")

        if submitted_button:
            
            # verificando se os campos estão preenchidos
            if grupo != '' and maquina != '' and ultima_manutencao != '' and classificacao != '':

                table, wks, sh = exibir()

                # verificando se a máquina ja existe na lista de cadastro
                try:
                    if maquina in table['Máquina'].values.tolist(): 
                        st.warning("Máquina existente", icon="⚠️")
                    else:
                        df = gerador_de_semanas(grupo,maquina,classificacao,ultima_manutencao,periodicidade)

                        save_db(df)

                        st.markdown("<h1 style='text-align: center; font-size:20px; color: Green'>Máquina cadastrada</h1>", unsafe_allow_html=True)
                except:
                    df = gerador_de_semanas(grupo,maquina,classificacao,ultima_manutencao,periodicidade)

                    save_db(df)

                    st.markdown("<h1 style='text-align: center; font-size:20px; color: Green'>Máquina cadastrada</h1>", unsafe_allow_html=True)
            else:
                st.warning("Preencha todos os campos!", icon="⚠️")
            
def page2():

    st.markdown("<h1 style='text-align: center; font-size:60px; color: White'>Upload de arquivo</h1>", unsafe_allow_html=True)
    st.markdown("<h1          </h1>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Escolha o arquivo", type="xlsx")

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        df = ler_arquivo(df)

        save_db(df)

def page3():
    
    st.markdown("<h1 style='text-align: center; font-size:60px; color: White'>Última manutenção</h1>", unsafe_allow_html=True)
    st.markdown("<h1          </h1>", unsafe_allow_html=True)

    table,wks,sh = exibir()
    maquinas_cadastradas = table['Máquina'].unique().tolist()
    
    with st.form("informar ultima manutencao"):
    
        maquina = st.selectbox("ID da máquina", maquinas_cadastradas)
        ultima_manutencao = st.date_input("Data da última manutenção")
        
        submitted = st.form_submit_button("Submit")
                
        if submitted:
            filtrar_maquina = table[table['Máquina'] == maquina].reset_index()
            index_planilha = filtrar_maquina['index'][0]

            grupo=filtrar_maquina['Setor'][0]
            classificacao=filtrar_maquina['Classificação'][0]
            periodicidade=filtrar_maquina['Periodicidade'][0]

            manutencao_gerada = gerador_de_semanas(grupo,maquina,classificacao,ultima_manutencao,periodicidade)

            maquina_lista  = manutencao_gerada.values.tolist()            
            wks.update("A" + str(index_planilha + 2), maquina_lista) 

def page4():
    
    scope = ['https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')  

    name_sheet = 'Solicitação de Serviços de Manutenção (respostas)'
    worksheet = 'Respostas ao formulário 1'
    
    sh = sa.open(name_sheet)
    wks1 = sh.worksheet(worksheet)
    list1 = wks1.get()
    controle_os = pd.DataFrame(list1).reset_index()
    linha_em_branco = controle_os['index'][len(controle_os)-1:len(controle_os)].tolist()[0]

    table, wks, sh = exibir()

    indices = []
    for coluna in table.columns:
        idx = table.index[table[coluna] == '19-12-2023'].tolist()
        indices.extend([(i) for i in idx])

    print(indices)

    Setor = table['Setor'].iloc[indices].reset_index(drop=True)   
    table = table['Máquina'].iloc[indices].reset_index(drop=True)
    table = pd.DataFrame(table)

    if len(table) > 0:
        table['Motivo'] = 'Dia de manutençao preventiva - 19-12-2023'
        table['Data'] = pd.to_datetime('today').normalize().strftime("%d-%m-%Y")
        table['email'] = ''
        table['matricula'] = 'Robô'
        table['Setor'] = Setor
        table['Máquina parada?'] = 'Não'

    
    tabela1_list = table.values.tolist()

    wks1.update('A' + str(linha_em_branco + 2), tabela1_list)

page_names_to_funcs = {
    "Cadastrar": page1,
    "Upload de arquivo": page2,
    "Informar manutenção": page3,
}

selected_page = st.sidebar.selectbox("Selecione a função", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()