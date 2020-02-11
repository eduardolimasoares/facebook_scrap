# JURUTI-BOT is a bot to scrap facebook comments do data analysis
from bs4 import BeautifulSoup
from scrapy.utils.response import open_in_browser
import scrapy
import logging
from scrapy.utils.log import configure_logging
import re
import csv
from datetime import datetime
now = datetime.now()


file_name = open('out_web_scrap.csv', 'w', encoding='utf-8')

fieldnames = ['postagem', 'nome', 'comentario', 'curtidas', 'data', 'link']  # adding header to file
writer = csv.DictWriter(file_name, fieldnames=fieldnames, dialect='excel', delimiter=',')
writer.writeheader()


class DiarioOnlineSpider(scrapy.Spider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    name = 'page_scrap'
  # start_url i a url enterpoint
    start_urls = ['']

    def parse(self, response):
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('***********-----------------JURUTI-BOT-----------------*************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        # self.log('********************************************************************')
        return scrapy.FormRequest.from_response(
            response,
            formdata={'email': email,
                'pass': password},
            callback=self.after_login
        )

    def after_login(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        all_htree = soup.find('h3')
        if 'Entrar com um toque' in all_htree.get_text():

            url = 'https://mobile.facebook.com/login/save-device/cancel/?flow=interstitial_nux&amp;nux_source=regular_login'
            yield scrapy.Request(url=url, callback=self.after_login)
        else:

            self.log(response.url)
            yield scrapy.Request(
                #enter the page to scrap
                'https://mobile.facebook.com/',
                callback=self.fim_linha
            )

    def fim_linha(self, response):
        print('Entrnado em fim_linha')

        soup = BeautifulSoup(response.body, 'lxml')


        all_links = soup.find_all('a')
        for link in all_links:
            if 'História completa' in link.get_text():

                url = 'https://mobile.facebook.com' + str(link.get('href'))
                yield scrapy.Request(url=url, callback=self.parse_detail)

            elif 'Mostrar mais' in link.get_text():

                mostra_mais = 'https://mobile.facebook.com' + str(link.get('href'))
                yield scrapy.Request(url=mostra_mais, callback=self.fim_linha)
            else:
                continue



    def parse_detail(self, response):

        soup = BeautifulSoup(response.body, 'lxml')
        campo_hora = soup.find_all('abbr')
        for campo in campo_hora:
            comment = campo.parent.parent

            tag_a = comment.find('a')

            if tag_a.get_text() != 'Curtir Página' and tag_a.get_text() != 'Salvar' and tag_a.get_text() != 'Fotos da capa':
                self.log(tag_a.get_text())
                link = response.url
                postagem = soup.title.string
                nome = tag_a.get_text()
                comentario = comment.div.get_text()
                informacoes = comment.div.next_sibling.next_sibling.get_text()

                if informacoes.split(' · ')[0] != 'Curtir' and informacoes.split(' · ')[0] != 'Editado':
                    curtidas = informacoes.split(' · ')[0]
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[5])

                elif informacoes.split(' · ')[0] == 'Editado' and informacoes.split(' · ')[1] == 'Curtir':
                    curtidas = informacoes.split(' · ')[1]
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[5])

                elif informacoes.split(' · ')[0] == 'Editado' and informacoes.split(' · ')[2] == 'Curtir':
                    curtidas = informacoes.split(' · ')[1]
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[6])

                elif informacoes.split(' · ')[0] == 'Curtir':
                    curtidas = '0'
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[4])

                yield {
                    'postagem': postagem,
                    # 'nome': nome,
                    # 'comentario': comentario,
                    # 'curtidas': curtidas,
                    # 'data': data_postagem,
                    # 'link': link
                }
                writer.writerow({
                    'postagem': postagem,
                    'nome': nome,
                    'comentario': comentario,
                    'curtidas': curtidas,
                    'data': data_postagem,
                    'link': link
                })
            else:
                continue
        captura_mais_comentarios = soup.find_all('a')
        for mais_comentarios in captura_mais_comentarios:
            if 'Ver mais comentários…' in mais_comentarios.get_text():
                proxima_pagina_comentarios = 'https://mobile.facebook.com' + str(mais_comentarios.get('href'))
                yield scrapy.Request(url=proxima_pagina_comentarios, callback=self.parse_detail)

            elif 'respostas' in mais_comentarios.get_text():
                proxima_pagina_comentarios = 'https://mobile.facebook.com' + str(mais_comentarios.get('href'))
                # yield scrapy.Request(url=proxima_pagina_comentarios, callback=self.parse_comments_answers)
                request = scrapy.Request(url=proxima_pagina_comentarios,
                             callback=self.parse_comments_answers,
                             cb_kwargs=dict(postagem=postagem))
                yield request
            
            else:
                continue
                

    def parse_comments_answers(self, response, postagem):

        soup = BeautifulSoup(response.body, 'lxml')
        campo_hora = soup.find_all('abbr')
        for campo in campo_hora:
            comment = campo.parent.parent

            tag_a = comment.find('a')
            if tag_a.get_text() != 'Curtir Página' and tag_a.get_text() != 'Salvar':

                link = response.url
                postagem = postagem
                nome = tag_a.get_text()
                comentario = comment.div.get_text()
                informacoes = comment.div.next_sibling.next_sibling.get_text()

                if informacoes.split(' · ')[0] != 'Curtir' and informacoes.split(' · ')[0] != 'Editado' and informacoes.split(' · ')[1] == 'Curtir':
                    curtidas = informacoes.split(' · ')[0]
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[4])

                elif informacoes.split(' · ')[0] == 'Editado' and informacoes.split(' · ')[2] == 'Curtir':
                    curtidas = informacoes.split(' · ')[1]
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[5])

                elif informacoes.split(' · ')[0] == 'Editado' and informacoes.split(' · ')[1] == 'Curtir':
                    curtidas = '0'
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[4])
        
                elif informacoes.split(' · ')[0] == 'Curtir' and informacoes.split(' · ')[1] == 'Reagir':
                    curtidas = '0'
                    data_postagem = str(now.day) + '/' + str(now.month) + ' ' + str(now.hour) +':' + str(now.minute) + ' ' + str(informacoes.split(' · ')[3])

                # print(postagem, nome, comentario, curtidas, data_postagem)
                # yield {
                #     'postagem': postagem,
                #     'nome': nome,
                #     'comentario': comentario,
                #     'curtidas': curtidas,
                #     'data': data_postagem,
                #     'link': link
                # }
                writer.writerow({
                    'postagem': postagem,
                    'nome': nome,
                    'comentario': comentario,
                    'curtidas': curtidas,
                    'data': data_postagem,
                    'link': link
                })
            else:
                continue
        captura_mais_comentarios = soup.find_all('a')
        for mais_comentarios in captura_mais_comentarios:
            if 'Visualizar respostas anteriores' in mais_comentarios.get_text():
                proxima_pagina_comentarios = 'https://mobile.facebook.com' + str(mais_comentarios.get('href'))
                request = scrapy.Request(url=proxima_pagina_comentarios,
                             callback=self.parse_comments_answers,
                             cb_kwargs=dict(postagem=postagem))
                yield request

            
            else:
                continue



