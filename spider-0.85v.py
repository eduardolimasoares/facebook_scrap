# versao 0.86
from bs4 import BeautifulSoup
from scrapy.utils.response import open_in_browser
import scrapy
import logging
from scrapy.utils.log import configure_logging
import re
import csv
from datetime import datetime
now = datetime.now()


file_name = open('dataset.csv', 'w', encoding='utf-8')

fieldnames = ['postagem', 'nome', 'comentario', 'curtidas', 'data', 'link']  # adding header to file
writer = csv.DictWriter(file_name, fieldnames=fieldnames, dialect='excel', delimiter=';')
writer.writeheader()


class DiarioOnlineSpider(scrapy.Spider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    name = 'diario_online'
    # allowed_domains = ['mobile.facebook.com/login/']
    start_urls = ['http://mobile.facebook.com/login/']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'email': 'email.@email.com',
                'pass': 'password'},
            callback=self.after_login
        )

    def after_login(self, response):

        soup = BeautifulSoup(response.body, 'lxml')

        all_htree = soup.find('h3')
        if 'Entrar com um toque' in all_htree.get_text():

            url = 'https://mobile.facebook.com/login/save-device/cancel/?flow=interstitial_nux&amp;nux_source=regular_login'
            yield scrapy.Request(url=url, callback=self.after_login)
        else:

            # self.log(response.url)
            yield scrapy.Request(
                'https://mobile.facebook.com/page',
                callback=self.fim_linha
            )

    def fim_linha(self, response):


        soup = BeautifulSoup(response.body, 'lxml')


        # url = 'https://mobile.facebook.com/doldiarioonline/photos/a.292900254138425/2815898971838528/?type=3&refid=17&_ft_=mf_story_key.2815899781838447%3Atop_level_post_id.2815898971838528%3Atl_objid.2815898971838528%3Acontent_owner_id_new.291906430904474%3Athrowback_story_fbid.2815899781838447%3Apage_id.291906430904474%3Aphoto_id.2815898971838528%3Astory_location.4%3Astory_attachment_style.cover_photo%3Apage_insights.%7B%22291906430904474%22%3A%7B%22page_id%22%3A291906430904474%2C%22actor_id%22%3A291906430904474%2C%22dm%22%3A%7B%22isShare%22%3A0%2C%22originalPostOwnerID%22%3A0%7D%2C%22psn%22%3A%22EntCoverPhotoEdgeStory%22%2C%22post_context%22%3A%7B%22object_fbtype%22%3A22%2C%22publish_time%22%3A1581345640%2C%22story_name%22%3A%22EntCoverPhotoEdgeStory%22%2C%22story_fbid%22%3A%5B2815899781838447%5D%7D%2C%22role%22%3A1%2C%22sl%22%3A4%7D%7D%3Athid.291906430904474%3A306061129499414%3A62%3A0%3A1583049599%3A-7201742097596129302&__tn__=%2AW-R#footer_action_list%3E%20(referer:%20https://mobile.facebook.com/doldiarioonline?sectionLoadingID=m_timeline_loading_div_1583049599_0_36_timeline_unit%3A1%3A00000000001581347512%3A04611686018427387904%3A09223372036854775763%3A04611686018427387904&unit_cursor=timeline_unit%3A1%3A00000000001581347512%3A04611686018427387904%3A09223372036854775763%3A04611686018427387904&timeend=1583049599&timestart=0&tm=AQCw0Xm__7L2uAlH&refid=17'
        # yield scrapy.Request(url=url, callback=self.parse_detail)

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
            self.log('comment')

            tag_a = comment.find('a')

            if tag_a.get_text() != 'Curtir Página' and tag_a.get_text() != 'Salvar' and tag_a.get_text() != 'Fotos da capa':
                self.log(tag_a.get_text())
                link = response.url
                postagem_to_split = soup.title.string
                postagem = postagem_to_split.replace('\n', ' ').replace('.', ' ').replace(',', ' ')


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
