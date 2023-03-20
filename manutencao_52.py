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
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

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
    
    # df = pd.read_excel('df_manutencao.xlsx')
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
        df_52semanas['Código da máquina'] = df_filter['Código da máquina'][i]
        df_52semanas['Descrição da máquina'] = df_filter['Descrição da máquina'][i]
        df_52semanas['Periodicidade'] = df_filter['Periodicidade'][i]
        df_52semanas['Classificação'] = df_filter['Classificação'][i]
        df_52semanas['Setor'] = df_filter['Setor'][i]
        df_52semanas['Última manutenção'] = df_filter['primeira_manutencao'][i]
        
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

def page1():

    st.markdown("<h1 style='text-align: center; font-size:60px; color: White'>Cadastro de máquinas</h1>", unsafe_allow_html=True)
    st.markdown("<h1          </h1>", unsafe_allow_html=True)

    with st.form('cadastrar maquina', clear_on_submit=True):

        table, wks, sh, table2,table3 = exibir()
        setores_cadastrados = table2['Setor'].unique().tolist()
        
        lista_setores = ['Selecione']

        for setor in range(len(setores_cadastrados)):
            lista_setores.append(setores_cadastrados[setor])

        grupo = st.selectbox("Setor", lista_setores)
        codigo_maquina = st.text_input("Código único da máquina", placeholder="Exemplo: SO-MS-10").upper()
        maquina = st.text_input("Descrição da máquina", placeholder='Exemplo: Máquina de solda')
        classificacao = st.select_slider("Classificação", options=['A','B','C'])
        ultima_manutencao = st.date_input("Última manutenção")
        periodicidade = st.selectbox('Selecione a periodicidade',('Selecione','Semanal','Quinzenal','Bimestral'))
        submitted_button = st.form_submit_button("Run")

        if submitted_button:
            
            # verificando se os campos estão preenchidos
            if grupo != 'Selecione' and maquina != '' and ultima_manutencao != '' and classificacao != '' and periodicidade != 'Selecione' and codigo_maquina != '':
                
                for string in range(len(table)):
                    table['Código da máquina'][string] = table['Código da máquina'][string].upper()

                # verificando se a máquina ja existe na lista de cadastro
                try:
                    if codigo_maquina in table['Código da máquina'].values.tolist():
                        st.warning("Código único da máquina ja existe", icon="⚠️")
                    else:
                        df = gerador_de_semanas(grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade)

                        save_db(df)

                        st.markdown("<h1 style='text-align: center; font-size:20px; color: Green'>Máquina cadastrada</h1>", unsafe_allow_html=True)
                except:
                    df = gerador_de_semanas(grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade)

                    save_db(df)

                    st.success("", icon="✅")
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

        st.success('', icon="✅")
    
def page3():
    
    st.markdown("<h1 style='text-align: center; font-size:60px; color: White'>Última manutenção</h1>", unsafe_allow_html=True)
    st.markdown("<h1          </h1>", unsafe_allow_html=True)

    table,wks,sh,table2, table3 = exibir()
   
    maquinas_cadastradas = table['Código da máquina'].unique().tolist() 

    lista_maquinas = ['Selecione']

    for maquinas in range(len(maquinas_cadastradas)):
        lista_maquinas.append(maquinas_cadastradas[maquinas])

    with st.form("informar ultima manutencao", clear_on_submit=True):
    
        codigo_maquina = st.selectbox("ID da máquina", lista_maquinas)
        ultima_manutencao = st.date_input("Data da última manutenção")
        tempo_manutencao = st.number_input('Tempo de manutenção (EM MINUTOS):')
        
        submitted = st.form_submit_button("Submit")
                
        if submitted:

            if tempo_manutencao != 0 and codigo_maquina != 'Selecione':
            
                filtrar_maquina = table[table['Código da máquina'] == codigo_maquina].reset_index()
                filtrar_maquina = filtrar_maquina[['index','Setor','Código da máquina','Descrição da máquina','Classificação','Periodicidade','Última Manutenção']]
                index_planilha = filtrar_maquina['index'][0]

                grupo=filtrar_maquina['Setor'][0]
                classificacao=filtrar_maquina['Classificação'][0]
                periodicidade=filtrar_maquina['Periodicidade'][0]
                maquina=filtrar_maquina['Descrição da máquina'][0]
                
                filtrar_maquina['Tempo de manutenção'] = tempo_manutencao    

                manutencao_gerada = gerador_de_semanas(grupo,codigo_maquina,maquina,classificacao,ultima_manutencao,periodicidade)

                maquina_lista  = manutencao_gerada.values.tolist()            
                wks.update("A" + str(index_planilha + 2), maquina_lista) 

                filtrar_maquina = filtrar_maquina[['Setor','Código da máquina','Descrição da máquina','Classificação','Periodicidade','Última Manutenção','Tempo de manutenção']].values.tolist()
                sh.values_append('bd_historico_manutencao', {'valueInputOption': 'RAW'}, {'values': filtrar_maquina})

                st.success("", icon="✅")

            else:
                st.warning("Preencha todos os campos", icon='⚠️')

def page4():
    
    table, wks, sh, table2, table3 = exibir()

    data = date.today().strftime(format="%d/%m/%Y")
    data = pd.to_datetime(data, format="%d/%m/%Y") # data de hoje (segunda-feira)
    lista_indices = []

    for i in range(1,7):
        indices = []
        for coluna in table.columns:
            data_str = data.strftime(format='%d-%m-%Y')
            idx = table.index[table[coluna] == data_str].tolist()
            indices.extend([(i) for i in idx])

        lista_indices.append(indices)        
        data = data + timedelta(1)
    
    maquinas_merge = pd.DataFrame()
    
    for j in range(6):

        if len(table.iloc[lista_indices[j]]) > 0:

            # DataFrame com informações das máquinas

            table_maquinas = table.iloc[lista_indices[j]].reset_index(drop=True).sort_values(by='Classificação')

            maquinas = pd.DataFrame(table_maquinas['Código da máquina'].copy())

            media_tempos = table3[['Código da máquina','Descrição da máquina','Criticidade','tempo de manutencao']]
            media_tempos = pd.DataFrame(media_tempos.groupby(['Código da máquina','Descrição da máquina','Criticidade']).mean()).reset_index()

            maquinas = maquinas.merge(media_tempos)

            maquinas_merge = maquinas_merge.append(maquinas).reset_index(drop=True)

        else:
            pass

    # Criando as listas de equipamentos e tempos

    equipamentos = maquinas_merge['Código da máquina'].values.tolist()
    tempos = maquinas_merge['tempo de manutencao'].values.tolist()
    
    df_planejamento = pd.DataFrame(data=equipamentos, columns=['Código da máquina'])
    df_planejamento['Dia'] = ''

    # Criando a variável de tempo máximo
    tempo_maximo = 540

    # Criando o laço de repetição
    for i in range(len(equipamentos)):
        # Verificando se o tempo do equipamento cabe no dia atual
        if tempos[i] <= tempo_maximo:
            # Imprimindo o equipamento e o dia da manutenção
            #print(f"O equipamento {equipamentos[i]} será mantido no dia {dia_atual}.")
            # Atualizando o tempo máximo
            tempo_maximo = tempo_maximo - tempos[i]
        else:
            # Incrementando o dia atual
            data = data + timedelta(1)
            # Imprimindo o equipamento e o novo dia da manutenção
            #print(f"O equipamento {equipamentos[i]} será mantido no dia {dia_atual}.")
            # Atualizando o tempo máximo
            tempo_maximo = 540 - tempos[i]

        df_planejamento['Dia'][i] = data
    
    df_planejamento = df_planejamento[['Dia','Código da máquina']]
    df_planejamento = df_planejamento.merge(maquinas_merge)
    
    df_planejamento['Dia'] = pd.to_datetime(df_planejamento['Dia'])
    df_planejamento['Dia'] = df_planejamento['Dia'].dt.strftime("%d/%m/%Y")

    salvar_agendamento(df_planejamento)

page_names_to_funcs = {
    "Cadastrar": page1,
    "Upload de arquivo": page2,
    "Informar manutenção": page3,
}

selected_page = st.sidebar.selectbox("Selecione a função", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()