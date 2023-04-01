from django.test import TestCase
from django.contrib.auth.models import User
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from clientes.models import Cliente, EnderecoEntrega
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

class ClienteModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="johndoe",
            email="johndoe@test.com",
            password="testpass"
        )

    def test_cliente_creation(self):
        cliente = Cliente.objects.create(
            user=self.user,
            cpf="12345678901",
            celular="11987654321",
            whatsapp=True,
            propaganda=False
        )

        self.assertEqual(cliente.user, self.user)
        self.assertEqual(cliente.cpf, "12345678901")
        self.assertEqual(cliente.celular, "11987654321")
        self.assertTrue(cliente.whatsapp)
        self.assertFalse(cliente.propaganda)

    def test_cliente_str(self):
        cliente = Cliente.objects.create(
            user=self.user,
            cpf="12345678901",
            celular="11987654321",
            whatsapp=True,
            propaganda=False
        )

        self.assertEqual(str(cliente), self.user.username)


class EnderecoEntregaModelTest(TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/accounts/login/")
        self.user = User.objects.create_user(
            username="johndoe",
            email="johndoe@test.com",
            password="testpass"
        )
        self.cliente = Cliente.objects.create(
            user=self.user,
            cpf="12345678901",
            celular="11987654321",
            whatsapp=True,
            propaganda=False
        )

    # def test_enderecoentrega_creation(self):
    #     endereco = EnderecoEntrega.objects.create(
    #         cliente=self.cliente,
    #         cep="12345678",
    #         rua="Rua X",
    #         numero="123",
    #         bairro="Bairro Y",
    #         cidade="Cidade Z",
    #         estado="SP",
    #         complemento="Complemento A"
    #     )
    #
    #     self.assertEqual(endereco.cliente, self.cliente)
    #     self.assertEqual(endereco.cep, "12345678")
    #     self.assertEqual(endereco.rua, "Rua X")
    #     self.assertEqual(endereco.numero, "123")
    #     self.assertEqual(endereco.bairro, "Bairro Y")
    #     self.assertEqual(endereco.cidade, "Cidade Z")
    #     self.assertEqual(endereco.estado, "SP")
    #     self.assertEqual(endereco.complemento, "Complemento A")

    def test_login(self):
        email_input = self.driver.find_element("name", "email")
        password_input = self.driver.find_element("id","password")
        submit_button = self.driver.find_element("id","submit")

        email_input.send_keys("ageraseev@gmail.com")

        password_input.send_keys("Garbage@87")

        submit_button.click()

        assert self.driver.current_url == "http://localhost:8000/"

    # def test_edit_celular(self):
    #     self.test_login()
    #
    #     dashboard_link = self.driver.find_element("id", "dashboard")
    #     time.sleep(3)
    #     dashboard_link.click()
    #     time.sleep(3)
    #
    #     edit_button = self.driver.find_element("id", "btn-edit-celular")
    #     edit_button.click()
    #
    #     celular_input = self.driver.find_element("id", "input-celular")
    #     celular_input.clear()
    #     celular_input.send_keys("123456789")
    #
    #     save_button = self.driver.find_element("id", "btn-save-celular")
    #     save_button.click()
    #
    #     assert celular_input.get_attribute("value") == "123456789"
    #
    # def test_edit_cpf(self):
    #     self.test_login()
    #
    #     dashboard_link = self.driver.find_element("id", "dashboard")
    #     time.sleep(3)
    #     dashboard_link.click()
    #     time.sleep(3)
    #
    #     edit_button = self.driver.find_element("id", "btn-edit-cpf")
    #     edit_button.click()
    #
    #     cpf_input = self.driver.find_element("id", "cpf")
    #     cpf_input.clear()
    #     cpf_input.send_keys("36944557878")
    #     self.driver.execute_script("arguments[0].scrollIntoView();", cpf_input)
    #     time.sleep(3)
    #     save_button = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "btn-save-cpf")))
    #     save_button.click()
    #
    #     assert cpf_input.get_attribute("value") == "36944557878"



    def test_add_endereco(self):
        self.test_login()

        dashboard_link = self.driver.find_element("id", "dashboard")

        dashboard_link.click()

        botao_add_enderecco = self.driver.find_element("id", "adicionar_endereco")
        self.driver.execute_script("arguments[0].scrollIntoView({ offsetTop: 200});", botao_add_enderecco)
        time.sleep(1)


        # add_button = self.driver.find_element("id", "adicionar_endereco")
        botao_add_enderecco.click()
        time.sleep(1)


        cep_input = self.driver.find_element("id", "cep")
        cep_input.send_keys("12233400")

        time.sleep(1)
        rua_input = self.driver.find_element("id", "rua")
        time.sleep(1)
        assert "Avenida Ouro Fino" in self.driver.page_source
        self.driver.execute_script("arguments[0].scrollIntoView();", rua_input)
        time.sleep(2)
        rua_input.send_keys("")
        time.sleep(2)
        rua_input.clear()
        rua_input.send_keys("Rua X")

        numero_input = self.driver.find_element("id", "numero")
        numero_input.clear()
        numero_input.send_keys("123")

        bairro_input = self.driver.find_element("id", "bairro")
        assert "Bosque dos Eucaliptos" in self.driver.page_source
        bairro_input.clear()
        bairro_input.send_keys("Bairro Y")

        cidade_input = self.driver.find_element("id", "cidade")
        assert "São José dos Campos" in self.driver.page_source
        cidade_input.clear()
        cidade_input.send_keys("Cidade Z")

        estado_input = self.driver.find_element("id", "estado")
        assert "SP" in self.driver.page_source

        estado_input.clear()
        estado_input.send_keys("MG")
        self.driver.execute_script("arguments[0].scrollIntoView();", estado_input)


        complemento_input = self.driver.find_element("id", "complemento")
        complemento_input.send_keys("Complemento A")

        save_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "salvar"))
        )
        time.sleep(1)
        self.driver.execute_script("arguments[0].scrollIntoView();", save_button)
        time.sleep(1)
        save_button.click()
        time.sleep(2)

        assert "Rua X" in self.driver.page_source
        assert "Bairro Y" in self.driver.page_source

        # lista_enderecos = self.driver.find_elements(By.XPATH, "//ul[@class='list-group']/li")
        # time.sleep(1)
        # for endereco in lista_enderecos:
        #     if 'Rua X , 123, Bairro Y' in endereco.text:
        #         time.sleep(1)
        #         botao_excluir = endereco.find_element(By.XPATH, ".//button[@id='excluir-endereco']")
        #         time.sleep(1)
        #         botao_excluir.click()
        #         break