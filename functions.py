from datetime import date
import datetime
from connection import dbamv
import cx_Oracle
from connection import mvintegra
from connection import (dbamv, mvintegra, sysdba)

#Extrai e formata os telefones
def telephone(number_string):
    number_list = []
    if(number_string is None):
        return number_list
     
    while len(number_string)>=8:
            
        number_string = number_string.replace(".", "-").replace("- ", "-").replace(" -", "-")                                             #Trocar todos os pontos por traços

        number_string = number_string.replace("(", "").replace(")", "")                                                                   #Remove parenteses. Exemplo = (38) 999343888 -> 38 999343888

        number_string = number_string.strip().replace("E", "/").replace("+", "/").replace(";", "/").replace(" /", "/").replace("/ ", "/") #Troco qualquer caracter que posso delimitar os números pelo delimitador '/' e removo espaços antes e depois desse caracter.

        if len(number_string) < 11:
            if number_string[0] !=3 and number_string[1] != 8:
                number_string.insert()
         
        if number_string[0] == '0':                                           #Remove o 0 de number_strings iniciadas com 0. Exemplo: 038 999343888 -> 38 99343888
            number_string = number_string.replace("0", "", 1)

        while(number_string.find(' ') <= 7 and number_string.find(' ') >= 0): #Remove todos os espaços da number_string da posição 0 a posição 7. Exemplo: 38 9 99934 3888 -> 38999343888 
            number_string = number_string.replace(" ", "", 1)
             
        while(number_string.find('-') <= 7 and number_string.find('-') >= 0): #Remove todos os caracteres '-' da number_string da posição 0 a posição 7. Exemplo: 38-9-99934-3888 -> 38999343888 
            number_string = number_string.replace("-", "", 1)
        if number_string.find('-') >= 8 and number_string.find('-') <=11 :
            number_string = number_string.replace("-", "/", 1)
        number_string = number_string.replace(" ", "/")
                
        if number_string.find('/') > -1:                                      #Vefifica se number_string contém o caracter delimitador '/'
            number_string = number_string.split('/', 1)                       #Corta a number_string a partir da primeira ocorrência do caracter delimitador, gerando um array com duas posições
            if number_string[0].isnumeric() and len(number_string[0]) >=8:    #Verifica se a number_number_string é composta apenas por caracteres númericos e se a number_string é maior ou igual a 8, a fim de captar apenas números validos
                number_list.append(number_string[0])                          #Insere na number_list dos números extraidos
            number_string = number_string[1]                                  #A number_string recebe a subnumber_string resultante do processo de extração
        else:
            number_string = number_string.split('/', 1)
            if number_string[0].isnumeric() and len(number_string[0]) >=8:
                number_list.append(number_string[0])                          #Recebe um number_string vazia, o que denota o fim do while
            number_string = ''
        return number_list
    
#Retorna a lista de intercorrência
def requests(days=0):
    connection = mvintegra()
    cursor_1 = connection.cursor()
    cursor_2 = connection.cursor()


    current_date = datetime.datetime.now()            #Data atual
    date = current_date - datetime.timedelta(days = days)
    date = date.strftime("%d/%m/%Y")                                #Formata a data para o padrão usual

    select_requests = "select PM.CD_PAR_MED, PM.DT_SOLICITACAO, (SELECT E.CD_ESPECIALID_INTEGRA from ESPECIALID E where PM.CD_ESPECIALID = E.CD_ESPECIALID) AS cd_especialid, PR.NR_CPF_CGC, LE.DS_LEITO, UI.DS_UNID_INT, P.NM_PACIENTE, PM.DS_SOLICITACAO from PAR_MED PM, ATENDIME A, PACIENTE P,prestador pr, LEITO LE, UNID_INT UI where PM.DS_SITUACAO = 'Solicitado' AND PM.DT_SOLICITACAO >= to_date('{}') AND PM.CD_PRESTADOR_REQUISITADO = PR.CD_PRESTADOR(+) AND PM.CD_ATENDIMENTO = A.CD_ATENDIMENTO AND A.CD_PACIENTE = P.CD_PACIENTE AND A.CD_LEITO = LE.CD_LEITO(+) AND LE.CD_UNID_INT = UI.CD_UNID_INT(+)".format(date)
    requests = cursor_1.execute(select_requests)

    list_requests = []

    for request in requests:
        count = 0        #Contador que será incrementado caso o mesma já tenha sido cadastrada na tabela MENSAGEM_EMAIL, ou seja, se a mesma já foi encaminha para um responsável
        request_sent = "select * from MENSAGEM_EMAIL M where M.CD_IDENTIFICADOR_MENSAGEM = {} AND M.DS_ASSUNTO = 'INTERCORRÊNCIA'".format(request[0])

        for request in cursor_2.execute(request_sent): #buaca uma setenca
            count = count + 1

        if(count == 0):
            request = {'cod_solicitacao': request[0], 'data': request[1], 'cod_especialidade': request[2], 'cpf_prestador': request[3], 'leito': request[4],'nome_paciente': request[6], 'unidade_internacao': request[5],'ds_solicitacao': request[7]}
            list_requests.append(request) #coloca o dic dentro da lista
                                 
    connection.commit()
                                 
    return list_requests

#Retorna os servidores em plantão de uma especilidade
def employees(cod_especialid, days=0):
    connection = sysdba()
    cursor = connection.cursor() 
    
    current_date = datetime.datetime.now()
    current_date = current_date.strftime("%d.%m.%Y")  #foi feita a conversão da data
    print(current_date)

    select_employees = "select S.NOME, S.TELEFONE, S.CELULAR from SERVIDORES S, REGINTERCORRENCIA RI WHERE RI.MIF = S.MIF AND RI.CODFUNCAO = {} and RI.DATA = '{}'".format(cod_especialid, current_date) #alterar dados

    list_employees = []

    for employee in cursor.execute(select_employees):
        employee = {'nome': employee[0], 'telefone': employee[1], 'celular': employee[2]}
        list_employees.append(employee)
        
    connection.commit()
    
    return list_employees

#Cadastra a mensagem na tabela MENSAGEM_EMAIL
def register(mensage):
        connection = mvintegra()
        cursor2 = connection.cursor()
        
        date_create = datetime.datetime.now()
        date_create = date_create.strftime("%Y/%m/%d %H:%M:%S") #verificar pois vem uma string em vez de data
        #aux = mensage['receiver']['nome'] + ' - - ' + mensage['receiver']['contact'] + ' - - ' + mensage['receiver']['data']
        #mensage['destinatario'] = aux
        param = cursor2.var(
        cx_Oracle.STRING,
        255,
        arraysize=cursor2.arraysize,
        outconverter=int
        ) #esse paramentro esta vindo nulo 
        
        statement = "insert into MENSAGEM_EMAIL(DS_REMETENTE, DS_DESTINATARIO, DS_ASSUNTO, TP_STATUS, DT_CRIACAO, CD_IDENTIFICADOR_MENSAGEM, CD_MENSAGEM_EMAIL) values (:1, :2, :3, :4, to_date(:d, :f), :7,dbamv.seq_mensagem_email.nextval)" 
        cursor2.execute(statement, { "1":mensage['sender'], "2":mensage['receiver'], "3":mensage['subject'], "4":mensage['status'], "d":date_create, "f":'yyyy-mm-dd hh24:mi:ss',"7":mensage['identifier']})

        connection.commit()
#end function

