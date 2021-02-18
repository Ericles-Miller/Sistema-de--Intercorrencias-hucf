
from selenium import webdriver
import time
import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import(
    visibility_of_any_elements_located,
    number_of_windows_to_be,
    new_window_is_opened
)

from functions import ( requests, employees, telephone, register ) #módulo externo que contém a funções referentes ao acesso banco de dados


#Funções uteis na automatizção

def verify_element(by, elemento, self):                 #Verifica se elemento da DOM existe
    print(f'Tentando encontrar "{elemento} by {by}"')
    elementos = self.driver.find_elements(by, elemento)
    if elementos:
        return True
    return False

def find_window(url: str, self):                       #Verifica se existe uma janela aberta no Browser
    wids = self.driver.window_handles
    for window in wids:
        self.driver.switch_to.window(window)
        if url in self.driver.current_url:
            print()
            return True
        else:
            return False

class WhatsappBot:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('lang=pt-br')
        #options.add_argument('--user-data-dir=C:/Users/mensagem/AppData/Local/Google/Chrome/User Data/Default')
        #options.add_argument('--profile-directory=Default')
        self.driver = webdriver.Chrome(executable_path=r'./chromedriver.exe', options=options)

    def SendMessages(self):

        self.driver.get('https://web.whatsapp.com') #Inicia o whatsapp web
        time.sleep(8)                              #Tempo - mudar para 8
        wdw = WebDriverWait(self.driver, 8)        #Espera

        for request in requests(5):                #A cada intercorrência
            for employee in employees(request['cod_especialidade'], 0):      #Funcionários na escala com a especilidade requerida
                
                message = (                         #Mensagem que será enviada
                f"Olá {employee['nome']}, "\
                "está é uma mensagem automatizada, a qual se referente à uma intercorrência. Segue as informações pertinentes à solicitação. " \
                f"Data da solicitação: {request['data']}. " \
                f"Nome do Paciente: {request['nome_paciente']}. " \
                f"Leito: {request['leito']}. " \
                f"Unidade de Internacão: {request['unidade_internacao']}."\
                f"\n\nDESCRIÇÃO DE SOLICITAÇÃO:{request['ds_solicitacao']}"
                )

                contacts = telephone(employee['telefone']) #Números telefonicos do respectivo funcinário

                if( len(contacts) > 0):                    #Se a quanidade números é maior que 0             
                    cont = 0
                    for contact in contacts:
                        contact = contacts
                        self.driver.get(f'https://api.whatsapp.com/send?phone=55{contact}')

                        
                        #button 'INICIAR CONVERSA'
                        locator = (By.XPATH, '//a[@id="action-button"]')
                        wdw.until(
                            visibility_of_any_elements_located(locator),
                            'INICIAR CONVERSA. Espera de 30seg.'
                        )
                        button = self.driver.find_element(*locator)
                        button.click()

                        #link 'use o WhatsApp Web'
                        locator = (By.XPATH, '//*[@class="_8ibw"]/a')
                        wdw.until(
                            visibility_of_any_elements_located(locator),
                            '"Use o WhatsApp Web" não está visível. Espera de 30seg.'
                        )
                        link = self.driver.find_element(*locator)
                        link.click()

                        locator = (By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]') #Caixa do chat
                        time.sleep(20)
                        
                        #Verifica se o elemento existe, ou seja, se um Whatsapp válido. Caso seja valido entra no contato
                        if verify_element(*locator, self):         
                            #chat_box
                            locator = (By.XPATH, '//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
                            wdw.until(
                                visibility_of_any_elements_located(locator),
                                'Barra do chat não está visível. Espera de 30seg.'
                            )
                            chat_box = self.driver.find_element(*locator)
                            chat_box.click()

                            #Escreve a mensagem no chat e envia
                            chat_box.send_keys(message)
                            chat_box.send_keys(Keys.ENTER)
                            time.sleep(3)
                           
                            #Pega informações referentes à mensagem enviada
                            locator = (By.CSS_SELECTOR, ".message-out")
                            msgs = self.driver.find_elements(*locator)
                            for msg in reversed(msgs):
                                data_id = msg.get_attribute('data-id')
                                if data_id[0] == 't':
                                    break
                            
                            '''#status da mensagem
                            locator = (By.XPATH, f"//div[@data-id='{data_id}']//span[@data-testid='msg-check']")
                            wdw.until(
                                visibility_of_any_elements_located(locator),
                                'Não foi possível captar a informação. Espera de 30seg.'
                            )
                            status_msg = self.driver.find_element(*locator).get_attribute('aria-label')'''
                            status_msg = 'E'
                    

                            #data e remetente da mensagem
                            locator = (By.XPATH, f"//div[@data-id='{data_id}']//div[@class='copyable-text']")
                            wdw.until(
                                visibility_of_any_elements_located(locator),
                                'Não foi possível captar a informação. Espera de 30seg.'
                            )
                            date_msg = self.driver.find_element(*locator).get_attribute('data-pre-plain-text')
                            remetente_msg = data_id[5:data_id.rfind('-')]
                            remetente_msg = str(remetente_msg)
                            contact = str(contact)
                            data_id = str(data_id)
                            employee['nome'] = str(employee['nome'])
                            dad_receiver =  contact + ' -- ' + employee['nome'] +' -- ' + data_id
                            #dad_receiver = [contact + '-' + employee['nome'] + '-' + data_id]
                            message = {'sender': remetente_msg, 'subject': 'INTERCORRÊNCIA', 'identifier': request['cod_solicitacao'], 'receiver': dad_receiver, 'description': message, 'status': status_msg, 'date_create': date_msg}
                            register(message) #Cadastra no Banco
    
bot = WhatsappBot()
while(1):
    bot.SendMessages()
    time.sleep(30)
