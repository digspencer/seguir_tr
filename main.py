# Carrega arquivo .env ( variaveis de ambiente )
from dotenv import load_dotenv
load_dotenv()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_experimental_option("detach", True)




#erro limite semanal
LimiteSemanalException = type("LimiteSemanalException", (Exception,), {})
PoliciaChegou = type("PoliciaChegou", (Exception,), {})
def main():
    navegador = webdriver.Chrome(options=options)
    wait =  WebDriverWait(navegador, 1) # Tempo maximo de espera 10 segundos
    actions = ActionChains(navegador)
    #Entrando no navegador
    navegador.get(f'https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww%2Elinkedin%2Ecom%2Ffeed%2F&fromSignIn=true&trk=cold_join_sign_in')

    def aguarda(xpath:str, lista=False):
        tentativas = 3
        while tentativas != 0:
            try:
                if not lista:
                    return wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                return wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            except:
                time.sleep(1)
                tentativas -= 1
            
    def login():
            # Digitando o email    
            #navegador.find_element('xpath', '//*[@id="username"]').send_keys(os.environ['LINKEDIN_USUARIO'])    
            campo_usuario = aguarda('//*[@id="username"]')
            campo_usuario.send_keys(os.environ['LINKEDIN_USUARIO'])
            # Digitando a senha
            #navegador.find_element('xpath', '//*[@id="password"]').send_keys(os.environ['LINKEDIN_SENHA'])
            campo_senha = aguarda('//*[@id="password"]')
            campo_senha.send_keys(os.environ['LINKEDIN_SENHA'])
            # Clicando no botão de Login
            #navegador.find_element('xpath', '//*[@id="organic-div"]/form/div[3]/button').click()
            btn_login = aguarda('//*[@id="organic-div"]/form/div[3]/button')
            btn_login.click()

    def aplica_filtro():
            # Colocando 'Tech Recruiters Python' na barra de pesquisa     
            #navegador.find_element('xpath', '//*[@id="global-nav-typeahead"]/input').send_keys("Tech Recruiter")
            campo_buscar = aguarda('//*[@id="global-nav-typeahead"]/input')
            campo_buscar.send_keys("Tech Recruiter")
            # Confirma buscar    
            #navegador.find_element('xpath', '//*[@id="global-nav-typeahead"]/input').send_keys(Keys.RETURN)
            campo_buscar.send_keys(Keys.RETURN)

            # Aplica filtro Pessoas    
            #navegador.find_element('xpath', '//*[@id="search-reusables__filters-bar"]/ul/li[1]/button').click()
            btn_pessoas = aguarda('//*[@id="search-reusables__filters-bar"]/ul/li[1]/button')
            btn_pessoas.click()
    
    def aguarda_btn_avancar():
        # Necessario porque e a unica forma confiavel de verificar se filtro carregou adequadamente
        while True:
            try:
                navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                btn = navegador.find_element(By.XPATH, "//button[contains(@aria-label, 'Avançar')]")
                navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                return btn
            except:
                time.sleep(1)
    
    def conectar_com_as_pessoas():
        texo_confirmar_usuario_email = "Para confirmar que este usuário é seu conhecido, insira o endereço de e-mail do mesmo para se conectar. Você também pode incluir uma nota pessoal. "
        while True:
            
            # Verifica se avanar existe para garantir que foi carregado
            aguarda_btn_avancar()

            botoes_conectar = navegador.find_elements('xpath', "//button[contains(@aria-label, 'conectar')]")        
            try:
                for btn in botoes_conectar:    
                    navegador.execute_script("arguments[0].scrollIntoView(true);", btn)
                    navegador.execute_script("arguments[0].click();", btn)            
                    
                    # Verifica poupup confirmar email
                    cnf_email = navegador.find_elements(By.XPATH, f'//label[contains(text(), \"{texo_confirmar_usuario_email}")]')
                    if cnf_email:
                        continue

                    #btn_conectar = navegador.find_element('xpath', "//button[contains(@aria-label, 'Enviar agora')]")
                    btn_conectar = aguarda("//button[contains(@aria-label, 'Enviar agora')]")
                    btn_conectar.click()
                                
                # Clica em avancar
                btn_avancar = aguarda_btn_avancar()
                if not btn_avancar.is_enabled():
                    navegador.quit()
                    return
                btn_avancar.click()
            except Exception as e:
                # Verifica se esgotou o limite semanal
                limite_modal = navegador.find_elements('xpath', '//button[@aria-label="Entendi"]')
                if limite_modal:
                    raise LimiteSemanalException("Deu ruim !")
                else:
                    raise e

    try:
        login()
        aplica_filtro()
        conectar_com_as_pessoas()
    except Exception as e:
        policia = navegador.find_elements(By.XPATH, "//*[contains(text(),'Vamos fazer uma verificação rápida de segurança')]")
        if policia:
            raise PoliciaChegou("Fudeu !!!")
        raise e

if __name__ == '__main__':
    while True:
        print('Iniciando')
        try:
            main()
        except LimiteSemanalException:
            print(f"Limite semanal atingido")
            break
        except PoliciaChegou:
            print("Pulica chegou !")
            break
            #input("Digite para continuar...")
    print('Terminou')
