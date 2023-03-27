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
    worksheet2 = 'Setores'
    worksheet3 = 'bd_historico_manutencao'

    sh = sa.open(name_sheet)

    wks = sh.worksheet(worksheet)
    wks2 = sh.worksheet(worksheet2)
    wks3 = sh.worksheet(worksheet3)
    
    list1 = wks.get_all_records()
    table = pd.DataFrame(list1)

    list2 = wks2.get_all_records()
    table2 = pd.DataFrame(list2)

    list3 = wks3.get_all_records()
    table3 = pd.DataFrame(list3)

    return table, wks, sh, table2, table3

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

def salvar_agendamento(df):
        
    scope = ['https://www.googleapis.com/auth/spreadsheets',
        "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)
    sa = gspread.service_account('service_account.json')  

    name_sheet = 'Plano 52 semanas - Manutenção Preventiva'
    worksheet = 'Agendamento'
    
    sh = sa.open(name_sheet)
    
    df_list = df.values.tolist()

    sh.values_append(worksheet, {'valueInputOption': 'RAW'}, {'values': df_list})

def ler_arquivo(df):
    

    df = pd.read_excel('df_manutencao.xlsx')
    df_maquinas = pd.DataFrame(data = df, columns=['Setor','Código da máquina','Descrição da máquina','Classificação','Última Manutenção','Periodicidade'])
    
    # Converte a coluna de data para o tipo datetime
    df_maquinas['Última Manutenção'] = pd.to_datetime(df_maquinas['Última Manutenção'])
    
    # Cria um DataFrame vazio para armazenar o planejamento de manutenção
    df_manutencao = pd.DataFrame(columns=['Última Manutenção', 'Código da máquina'])
    manut_outras_maquinas = False

    # Loop pelas máquinas
    for i, row in df_maquinas.iterrows():
        # Define as variáveis da máquina atual
        periodicidade = row['Periodicidade']
        
        if periodicidade == 'Quinzenal':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
            primeira_manutencao = row['Última Manutenção']
            periodicidade = row['Periodicidade']
            grupo = row['Setor']
            classificacao = row['Classificação']

            semana_inicial = primeira_manutencao.isocalendar().week
            data_manutencao = primeira_manutencao + 14 * BDay()
            
            # Loop pelas semanas
            for j in range(52-semana_inicial):
                # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                while data_manutencao.weekday() in [5, 6]:
                    data_manutencao = data_manutencao + 1 * BDay()
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Setor': grupo, 'Classificação': classificacao},ignore_index=True)
                    
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 14 * BDay()
        
        if periodicidade == 'Bimestral':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
            classificacao = row['Classificação']
            primeira_manutencao = row['Última Manutenção']
            periodicidade = row['Periodicidade']
            grupo = row['Setor']
            
            semana_inicial = primeira_manutencao.isocalendar().week
            data_manutencao = primeira_manutencao + 39 * BDay()
            
            # Loop pelas semanas
            for j in range(52-semana_inicial):
                # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                while data_manutencao.weekday() in [5, 6]:
                    data_manutencao = data_manutencao + 1 * BDay()
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Setor': grupo, 'Classificação': classificacao},ignore_index=True)
                                        
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 39 * BDay()
                
        if periodicidade == 'Semanal':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
            classificacao = row['Classificação']
            primeira_manutencao = row['Última Manutenção']
            periodicidade = row['Periodicidade']
            grupo = row['Setor']
            
            semana_inicial = primeira_manutencao.isocalendar().week
            data_manutencao = primeira_manutencao + 6 * BDay()
            
            # Loop pelas semanas
            for j in range(52-semana_inicial):
                # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                while data_manutencao.weekday() in [5, 6]:
                    data_manutencao = data_manutencao + 1 * BDay()
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Setor': grupo, 'Classificação': classificacao},ignore_index=True)
                                        
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 6 * BDay()

        if periodicidade == 'Semestral':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
            classificacao = row['Classificação']
            primeira_manutencao = row['Última Manutenção']
            periodicidade = row['Periodicidade']
            grupo = row['Setor']
            
            semana_inicial = primeira_manutencao.isocalendar().week
            data_manutencao = primeira_manutencao + 59 * BDay()
            
            # Loop pelas semanas
            for j in range(52-semana_inicial):
                # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                while data_manutencao.weekday() in [5, 6]:
                    data_manutencao = data_manutencao + 1 * BDay()
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Setor': grupo, 'Classificação': classificacao},ignore_index=True)
                                        
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 59 * BDay()
                
    df_manutencao['Week_Number'] = df_manutencao['Última Manutenção'].dt.isocalendar().week
    df_manutencao['year'] = df_manutencao['Última Manutenção'].dt.isocalendar().year
    
    df_manutencao['Week_Number'] = df_manutencao['Week_Number'].astype(int) 
    
    df_manutencao = df_manutencao.loc[(df_manutencao['year'] == 2023)] 
    
    df_manutencao['Última Manutenção'] = df_manutencao['Última Manutenção'].dt.strftime("%d-%m-%Y") 
        
    ############### 52 semanas ##################
    
    lista_maq = df_manutencao['Código da máquina'].unique()
    
    df_filter = df_manutencao.loc[(df_manutencao['Código da máquina'] == lista_maq[i])] 
    
    df_vazio = pd.DataFrame()
    
    list_52 = ['Setor', 'Código da máquina', 'Descrição da máquina','Classificação', 'Periodicidade','Última manutenção']
    
    for li in range(1,53):
        list_52.append(li)
        
    index = 0
    
    df_vazio = pd.DataFrame()
    
    for i in range(len(lista_maq)):
            
        df_52semanas = pd.DataFrame(columns=list_52, index=[index]) 
        df_filter = df_manutencao.loc[(df_manutencao['Código da máquina'] == lista_maq[i])] 
        df_filter = df_filter.reset_index(drop=True)

        df_52semanas['Código da máquina'] = df_filter['Código da máquina'][0]
        df_52semanas['Descrição da máquina'] = df_filter['Descrição da máquina'][0]
        df_52semanas['Periodicidade'] = df_filter['Periodicidade'][0]
        df_52semanas['Classificação'] = df_filter['Classificação'][0]
        df_52semanas['Setor'] = df_filter['Setor'][0]
        df_52semanas['Última manutenção'] = df_filter['primeira_manutencao'][0]
        
        index = index + 1
        
        for k in range(len(df_filter)):
            number_week = df_filter['Week_Number'][k]
            df_52semanas[number_week] = df_filter['Última Manutenção'][k]
            
        df_vazio = df_vazio.append(df_52semanas) 
    
    df_vazio = df_vazio.replace(np.nan, '')
    
    return df_vazio

def gerador_de_semanas(grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade):

    lista_campos = []
    
    lista_campos.append([grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade])
    
    df_maquinas = pd.DataFrame(data = lista_campos, columns=['Grupo','Código da máquina','Descrição da máquina','Classificação','Última Manutenção','Periodicidade'])
    
    # Converte a coluna de data para o tipo datetime
    df_maquinas['Última Manutenção'] = pd.to_datetime(df_maquinas['Última Manutenção'])
    
    # Cria um DataFrame vazio para armazenar o planejamento de manutenção
    df_manutencao = pd.DataFrame(columns=['Última Manutenção', 'Código da máquina'])
    manut_outras_maquinas = False

    # Loop pelas máquinas
    for i, row in df_maquinas.iterrows():
        # Define as variáveis da máquina atual
        periodicidade = row['Periodicidade']
        
        if periodicidade == 'Quinzenal':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
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
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                    
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 14 * BDay()
        
        if periodicidade == 'Bimestral':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
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
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                                        
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 39 * BDay()
                
        if periodicidade == 'Semanal':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
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
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                                        
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 6 * BDay()

        if periodicidade == 'Semestral':
            nome_maquina = row['Código da máquina']
            desc_maquina = row['Descrição da máquina']
            classificacao = row['Classificação']
            primeira_manutencao = row['Última Manutenção']
            periodicidade = row['Periodicidade']
            grupo = row['Grupo']
            
            semana_inicial = primeira_manutencao.isocalendar().week
            data_manutencao = primeira_manutencao + 180 * BDay()
            
            # Loop pelas semanas
            for j in range(52-semana_inicial):
                # Se a data de manutenção cair em um final de semana, avança para a segunda-feira seguinte
                while data_manutencao.weekday() in [5, 6]:
                    data_manutencao = data_manutencao + 1 * BDay()
        
                df_manutencao = df_manutencao.append({'primeira_manutencao': primeira_manutencao.strftime("%d/%m/%Y"), 'Última Manutenção': data_manutencao,'Código da máquina': nome_maquina,
                                                    'Descrição da máquina': desc_maquina,'Periodicidade': periodicidade, 'Grupo': grupo, 'Classificação': classificacao},ignore_index=True)
                                        
                # Avança para a próxima data de manutenção
                data_manutencao = data_manutencao + 180 * BDay()


    df_manutencao['Week_Number'] = df_manutencao['Última Manutenção'].dt.isocalendar().week
    df_manutencao['year'] = df_manutencao['Última Manutenção'].dt.isocalendar().year
    
    df_manutencao['Week_Number'] = df_manutencao['Week_Number'].astype(int) 
    
    df_manutencao = df_manutencao.loc[(df_manutencao['year'] == 2023)] 
    
    df_manutencao['Última Manutenção'] = df_manutencao['Última Manutenção'].dt.strftime("%d-%m-%Y") 
    
    ############### 52 semanas ##################
    
    lista_maq = df_manutencao['Código da máquina'].unique()
    
    df_filter = df_manutencao.loc[(df_manutencao['Código da máquina'] == lista_maq[i])] 
    
    df_vazio = pd.DataFrame()
    
    list_52 = ['Grupo', 'Código da máquina', 'Descrição da máquina','Classificação', 'Periodicidade','Última manutenção']
    
    for li in range(1,53):
        list_52.append(li)
        
    index = 0
    
    df_vazio = pd.DataFrame()
    
    for i in range(len(lista_maq)):
            
        df_52semanas = pd.DataFrame(columns=list_52, index=[index]) 
        df_filter = df_manutencao.loc[(df_manutencao['Código da máquina'] == lista_maq[i])] 
        df_filter = df_filter.reset_index(drop=True)
        df_52semanas['Código da máquina'] = df_filter['Código da máquina'][i]
        df_52semanas['Descrição da máquina'] = df_filter['Descrição da máquina'][i]
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

def minutos(hora_inicio, hora_fim):
    
    hora_fim  = str(hora_fim)
    hora_inicio = str(hora_inicio)

    # Criar dois objetos datetime.time com as horas de início e fim
    hora_inicio = datetime.time(int(hora_inicio[:2]),int(hora_inicio[3:5]),int(hora_inicio[6:8])) # 12:00:00
    hora_fim = datetime.time(int(hora_fim[:2]),int(hora_fim[3:5]),int(hora_fim[6:8])) # 14:00:00

    # Converter os objetos datetime.time em objetos datetime.datetime usando a função datetime.combine
    # Usar uma data arbitrária como primeiro argumento da função
    data = datetime.date(2023, 3, 21) # 21/03/2023
    dt_inicio = datetime.datetime.combine(data, hora_inicio)
    dt_fim = datetime.datetime.combine(data, hora_fim)

    # Subtrair os dois objetos datetime.datetime e obter um objeto datetime.timedelta
    diferenca = dt_fim - dt_inicio

    # Usar o método total_seconds do objeto datetime.timedelta para obter o resultado em segundos
    segundos = diferenca.total_seconds()

    # Dividir por 60 para obter o resultado em minutos
    minutos = segundos / 60

    return minutos

def page1(): # cadastro de peças

    st.markdown("<h1 style='text-align: center; font-size:40px; color: Black'>Cadastro de equipamentos</h1>", unsafe_allow_html=True)
    st.markdown("<h1          </h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Cadastrar equipamento", "Importar arquivo"])

    with tab1:
        with st.form('cadastrar maquina', clear_on_submit=False):
            
            table, wks, sh, table2,table3 = exibir()
            setores_cadastrados = table2['Setor'].unique().tolist()
            
            lista_setores = ['Selecione']

            for setor in range(len(setores_cadastrados)):
                lista_setores.append(setores_cadastrados[setor])

            grupo = st.selectbox("Setor", lista_setores)
            
            c1,c2 = st.columns(2)        
            
            with c1:
                codigo_maquina = st.text_input("Código único da máquina", placeholder="Exemplo: SO-MS-10").upper()
                maquina = st.text_input("Descrição da máquina", placeholder='Exemplo: Máquina de solda')
            
            with c2:
                periodicidade = st.multiselect('Selecione a periodicidade',['Semanal','Quinzenal','Bimestral','Semestral'],
                                                max_selections=1,
                                                help='Você pode selecionar apenas uma opção.')
                
                ultima_manutencao = st.date_input("Última manutenção")
            
            classificacao = st.select_slider("Criticidade",
                                              options=['A','B','C'])
            
            submitted_button = st.form_submit_button("Cadastrar")

            if submitted_button:
                
                # verificando se os campos estão preenchidos
                if grupo != 'Selecione' and maquina != '' and ultima_manutencao != '' and classificacao != '' and periodicidade != '' and codigo_maquina != '':
                    
                    for string in range(len(table)):
                        table['Código da máquina'][string] = table['Código da máquina'][string].upper()

                    # verificando se a máquina ja existe na lista de cadastro
                    try:
                        if codigo_maquina in table['Código da máquina'].values.tolist():
                            st.warning("Código único da máquina ja existe", icon="⚠️")
                        else:
                            df = gerador_de_semanas(grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade)

                            save_db(df)

                            st.success("", icon="✅")
                    except:
                        df = gerador_de_semanas(grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade)

                        save_db(df)

                        st.success("", icon="✅")
                else:
                    st.warning("Preencha todos os campos!", icon="⚠️")

    with tab2:
        
        uploaded_file = st.file_uploader("Escolha o arquivo", type="xlsx")

        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)

            df = ler_arquivo(df)

            save_db(df)

            st.success('', icon="✅")   
    
def page2(): # informar manutencao
    
    st.markdown("<h1 style='text-align: center; font-size:40px; color: Black'>Última manutenção</h1>", unsafe_allow_html=True)
    st.markdown("<h1          </h1>", unsafe_allow_html=True)

    table,wks,sh,table2, table3 = exibir()
    
    lista_setores = ['Selecione']
    setores_cadastrados = table2['Setor'].unique().tolist()

    for setor in range(len(setores_cadastrados)):
        lista_setores.append(setores_cadastrados[setor])

    c3,c4,c5 = st.columns(3)
    with c3:
        st.write('')

    with c4:
        style = "<style>h2 {text-align: center; font-size:20px}</style>"
        st.markdown(style, unsafe_allow_html=True)
        c4.header('Filtros')
        grupo = st.selectbox("Setor", lista_setores)

    with c5:
        st.write('')

    table['codigo_descricao'] = table['Código da máquina'] + " - " + table['Descrição da máquina']

    if grupo != 'Selecione':
        maquinas_cadastradas = table[table['Setor'] == grupo] 
        codigos_descricao = maquinas_cadastradas[['Código da máquina', 'codigo_descricao']]
        maquinas_cadastradas = codigos_descricao['codigo_descricao'].unique().tolist() 
    else:
        maquinas_cadastradas = table
        codigos_descricao = maquinas_cadastradas[['Código da máquina', 'codigo_descricao']]
        maquinas_cadastradas = codigos_descricao['codigo_descricao'].unique().tolist() 

    lista_maquinas = ['Selecione']

    for maquinas in range(len(maquinas_cadastradas)):
        lista_maquinas.append(maquinas_cadastradas[maquinas]) 

    with st.form("informar ultima manutencao", clear_on_submit=False):
        c1,c2 = st.columns(2)
        
        with c1:
            codigo_maquina = st.selectbox("ID da máquina", lista_maquinas)
            ultima_manutencao = st.date_input("Data da última manutenção")
        with c2:   
            pessoa = st.multiselect("Pessoa(s)", ['4347 - Leandro', '4363 - Davi', '4147 - Ryan', '3864 - Ivanildo', '4256 - Augusto'])
            pessoa = ','.join(pessoa)
            tempo_manutencao = st.number_input('Tempo da manutenção em minutos',format="%.i", min_value=0, max_value=2000)

        observacao = st.text_area("Observação")
        
        submitted = st.form_submit_button("Submit")
                
        if submitted:

            if codigo_maquina != 'Selecione' and pessoa != '' and tempo_manutencao != 0:
                
                codigo_maquina = codigos_descricao[codigos_descricao['codigo_descricao'] == codigo_maquina].reset_index(drop=True)['Código da máquina'][0]

                filtrar_maquina = table[table['Código da máquina'] == codigo_maquina].reset_index()
                filtrar_maquina = filtrar_maquina[['index','Setor',
                                                'Código da máquina','Descrição da máquina',
                                                'Classificação','Periodicidade','Última Manutenção']]
                
                index_planilha = filtrar_maquina['index'][0]

                grupo=filtrar_maquina['Setor'][0]
                classificacao=filtrar_maquina['Classificação'][0]
                periodicidade=filtrar_maquina['Periodicidade'][0]
                maquina=filtrar_maquina['Descrição da máquina'][0]
                
                filtrar_maquina['Comentário'] = observacao
                filtrar_maquina['Pessoa'] = pessoa
                filtrar_maquina['Tempo de manutenção'] = tempo_manutencao

                manutencao_gerada = gerador_de_semanas(grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade)

                maquina_lista  = manutencao_gerada.values.tolist()            
                wks.update("A" + str(index_planilha + 2), maquina_lista) 

                filtrar_maquina = filtrar_maquina[['Setor','Código da máquina',
                                                'Descrição da máquina','Classificação',
                                                'Periodicidade','Última Manutenção','Pessoa',
                                                'Comentário', 'Tempo de manutenção']].values.tolist()
                
                sh.values_append('bd_historico_manutencao', {'valueInputOption': 'RAW'}, {'values': filtrar_maquina})

                st.success("", icon="✅")

            else:
                st.warning("Preencha todos os campos", icon='⚠️')

def page3(): # script para agendar as manutencoes
    
    table, wks, sh, table2, table3 = exibir()

    data = date.today().strftime(format="%d/%m/%Y")
    data = pd.to_datetime(data, format="%d/%m/%Y") + timedelta(3) # rodar na sexta porém com data segunda-feira
    
    lista_indices = []
    lista_colunas = []

    for i in range(1,7):
        indices = []
        colunas = []
        for coluna in table.columns:
            data_str = data.strftime(format='%d-%m-%Y')
            idx = table.index[table[coluna] == data_str].tolist()
            indices.extend([(i) for i in idx])
            colunas.extend([(i,coluna) for i in idx])

        lista_indices.append(indices)
        lista_colunas.append(colunas)
        semana = lista_colunas[0][0][0]

        data = data + timedelta(1)
    
    maquinas_merge = pd.DataFrame()
    
    for j in range(6):

        if len(table.iloc[lista_indices[j]]) > 0:

            # DataFrame com informações das máquinas

            table_maquinas = table.iloc[lista_indices[j]].reset_index(drop=True).sort_values(by='Classificação')

            maquinas = pd.DataFrame(table_maquinas['Código da máquina'].copy())

            media_tempos = table3[['Código da máquina','Criticidade','tempo de manutencao']]
            media_tempos = pd.DataFrame(media_tempos.groupby(['Código da máquina','Criticidade']).mean()).reset_index()
            media_tempos['Data real'] = semana
            i = i-1
            
            maquinas = maquinas.merge(media_tempos)

            maquinas_merge = maquinas_merge.append(maquinas).reset_index(drop=True)

        else:
            pass

    # Criando as listas de equipamentos e tempos

    equipamentos = maquinas_merge['Código da máquina'].values.tolist()
    tempos = maquinas_merge['tempo de manutencao'].values.tolist()
    
    df_planejamento = pd.DataFrame(data=equipamentos, columns=['Código da máquina'])
    df_planejamento['Dia'] = ''

    data = date.today().strftime(format="%d/%m/%Y")
    data = pd.to_datetime(data, format="%d/%m/%Y") + timedelta(3) # data de hoje (segunda-feira)
    
    # Criando a variável de tempo máximo
    tempo_maximo = 180

    # Criando o laço de repetição
    for i in range(len(equipamentos)):
        # Verificando se o tempo do equipamento cabe no dia atual
        if tempos[i] <= tempo_maximo:

            tempo_maximo = tempo_maximo - tempos[i]

        else:
            # Incrementando o dia atual
            data = data + 1 * BDay()
            tempo_maximo = 180 - tempos[i]

        df_planejamento['Dia'][i] = data
    
    df_planejamento = df_planejamento[['Dia','Código da máquina']]
    df_planejamento = df_planejamento.merge(maquinas_merge, how='inner')
    
    df_planejamento['Dia'] = pd.to_datetime(df_planejamento['Dia'])
    df_planejamento['Dia'] = df_planejamento['Dia'].dt.strftime("%d/%m/%Y")

    df_planejamento['Data real'] = semana
    df_planejamento['Data real'] = semana

    table = table[['Código da máquina', 'Descrição da máquina', 'Setor']]
    df_planejamento = df_planejamento.merge(table)

    df_planejamento = df_planejamento[['Data real','Dia','Código da máquina', 'Descrição da máquina', 'Setor', 'Criticidade', 'tempo de manutencao']]

    salvar_agendamento(df_planejamento)

def page4(): # criar testes
    opcoes = ['Opção 1', 'Opção 2', 'Opção 3']
    selecionados = st.multiselect('Selecione as opções', opcoes, help='Selecione as opções que deseja visualizar.', max_selections=1)

page_names_to_funcs = {
    "Cadastrar": page1,
    "Informar manutenção": page2,
    "testes": page4,
}

selected_page = st.sidebar.selectbox("Selecione a função", page_names_to_funcs.keys())

with st.sidebar:
    st.markdown("Planilha com informações sobre agendamentos e 52 semanas: "
                "https://docs.google.com/spreadsheets/d/1omsYVEAcN2SsIDGyJTiavMPoTomMcCI6uMKZ9Kset9o/edit#gid=0")

page_names_to_funcs[selected_page]()