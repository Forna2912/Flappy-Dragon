import pygame
import random
import requests
import json
import os

TELA_LARGURA = 500
TELA_ALTURA = 800
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load("imgs/torre.png"))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load("imgs/grama.png"))
IMAGEM_BACKGROUND = pygame.transform.scale2x(pygame.image.load("imgs/fundo.png"))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load("imgs/verde1.png")),
    pygame.transform.scale2x(pygame.image.load("imgs/verde2.png")),
    pygame.transform.scale2x(pygame.image.load("imgs/verde3.png")),
]

pygame.font.init()
FONTE_PONTOS = pygame.font.Font('Adventurer.ttf', 50)
pygame.display.set_caption("Flappy Dragon")


class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 4

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        # calcular o deslocamento
        self.tempo += 1
        self.deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # restringir o deslocamento
        if self.deslocamento > 16:
            self.deslocamento = 16
        elif self.deslocamento < 0:
            self.deslocamento -= 2

        self.y += self.deslocamento  
 

    def desenhar(self, tela):
        # definir qual imagem do passaro vai usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO*4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem > self.TEMPO_ANIMACAO*4 :
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0


        # se o passaro tiver caindo eu não vou bater asa
        if self.deslocamento == 16  :
            self.imagem = self.IMGS[2]
            self.contagem_imagem = self.TEMPO_ANIMACAO*3

        tela.blit(self.imagem, (self.x,self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)


class Cano:
    DISTANCIA = 200
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        distancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros:
        passaro.desenhar(tela)
    for cano in canos:
        cano.desenhar(tela)

    texto = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))
    chao.desenhar(tela)
    pygame.display.update()

def mover_botoes(tela,botao_sair,botao_record,botao_play,posicao_botao_play,posicao_botao_record,posicao_botao_sair,copia_tela):
    tela.blit(copia_tela,(0,0))
    tela.blit(botao_sair,posicao_botao_sair)
    tela.blit(botao_record,posicao_botao_record)
    tela.blit(botao_play,posicao_botao_play)
    
    pygame.display.update()


def main():
    passaros = [Passaro(230, 350)]
    chao = Chao(740)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio = pygame.time.Clock()
    botao_play_precionado = False
    botao_sair_precionado = False
    botao_record_precionado = False
    botao_check_precionado = False
    altura_botoes = TELA_ALTURA // 1.5
    altura_botoes_precionados = TELA_ALTURA // 1.47
    tela_records = False
    carregar_top10 = None
    
    #tela inicial
    botao_play = pygame.transform.scale2x(pygame.image.load("imgs/botao_play.png"))
    botao_record = pygame.transform.scale2x(pygame.image.load("imgs/botao_record.png"))
    botao_sair = pygame.transform.scale2x(pygame.image.load("imgs/botao_sair.png"))
    botao_check = pygame.transform.scale2x(pygame.image.load("imgs/botao_check.png"))
    fonte_record = pygame.font.Font('Adventurer.ttf', 36)
    
    posicao_botao_play = botao_play.get_rect()
    posicao_botao_sair = botao_sair.get_rect()
    posicao_botao_record = botao_record.get_rect()
    posicao_botao_check = botao_check.get_rect()
    posicao_botao_check.center = (TELA_LARGURA // 2, altura_botoes)
    posicao_botao_play.center = (TELA_LARGURA // 4, altura_botoes)
    posicao_botao_record.center = (TELA_LARGURA // 2, altura_botoes)
    posicao_botao_sair.center = (TELA_LARGURA // (4/3), altura_botoes)




    #NOME DO JOGO
    exibir_nome_jogo = True
    fonte_nome_jogo = pygame.font.Font('Adventurer.ttf', 50)
    nome_jogo = fonte_nome_jogo.render('FLAPPY', True, (0, 0, 0))
    nome_jogo2 = fonte_nome_jogo.render('DRAGON', True, (0, 0, 0))
    posicao_nome_jogo = nome_jogo.get_rect()
    posicao_nome_jogo2 = nome_jogo2.get_rect()
    posicao_nome_jogo.center = (TELA_LARGURA // 2, TELA_ALTURA // 7)
    posicao_nome_jogo2.center = (TELA_LARGURA // 2, (TELA_ALTURA // 7)+nome_jogo.get_height())

    
    #record do usuario
    with open('record_num.txt', 'r') as arquivo:
        record_num = arquivo.read()


    # Variável para armazenar o caractere digitado
    fonte_nome_usuario = pygame.font.Font(None, 150)
    primeiro_caractere_text = ""
    segundo_caractere_text = ""
    terceiro_caractere_text = ""
    nome_completo=""

    barra_branca1 = pygame.transform.scale2x(pygame.image.load("imgs/barra.png"))
    barra_branca2 = pygame.transform.scale2x(pygame.image.load("imgs/barra.png"))
    barra_branca3 = pygame.transform.scale2x(pygame.image.load("imgs/barra.png"))
    barra_branca1_rect = barra_branca1.get_rect(center=(TELA_LARGURA // 3.5, TELA_ALTURA //1.81))
    barra_branca2_rect = barra_branca2.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA //1.81))
    barra_branca3_rect = barra_branca3.get_rect(center=(TELA_LARGURA // 1.4, TELA_ALTURA //1.81))
    digitar_nome_text = fonte_record.render("Digite seu usuário",True,(255, 255, 255))
    digitar_nome_text_rect = digitar_nome_text.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA //2.9))

    
    tela_escolher_nome = True
    if os.path.exists('nome.txt'):
        tela_escolher_nome = False
        fonte_nome_jogo = pygame.font.Font('Adventurer.ttf', 100)
        nome_jogo = fonte_nome_jogo.render('FLAPPY', True, (0, 0, 0))
        nome_jogo2 = fonte_nome_jogo.render('DRAGON', True, (0, 0, 0))
        posicao_nome_jogo = nome_jogo.get_rect()
        posicao_nome_jogo2 = nome_jogo2.get_rect()
        posicao_nome_jogo.center = (TELA_LARGURA // 2, TELA_ALTURA // 4)
        posicao_nome_jogo2.center = (TELA_LARGURA // 2, (TELA_ALTURA // 4)+nome_jogo.get_height())
        with open('nome.txt','r') as arquivo:
            nome_completo = arquivo.read()

    while True:
        # Tela de escolha de nome
        while tela_escolher_nome:
            relogio.tick(30)
            for evento in pygame.event.get():
                if evento.type == pygame.KEYDOWN:
                    # Verifica se o caractere é uma letra ou número
                    if evento.unicode.isalnum() and len(nome_completo) == 0:
                        primeiro_caractere_text = evento.unicode
                        nome_completo = nome_completo + primeiro_caractere_text
                    elif evento.unicode.isalnum() and len(nome_completo) == 1:
                        segundo_caractere_text = evento.unicode
                        nome_completo = nome_completo + segundo_caractere_text
                    elif evento.unicode.isalnum() and len(nome_completo) == 2:
                        terceiro_caractere_text = evento.unicode
                        nome_completo = nome_completo + terceiro_caractere_text
                    elif evento.key == pygame.K_BACKSPACE and len(nome_completo)==3:
                        terceiro_caractere_text = ""
                        nome_completo = nome_completo[:-1]
                    elif evento.key == pygame.K_BACKSPACE and len(nome_completo)==2:
                        segundo_caractere_text = ""
                        nome_completo = nome_completo[:-1]
                    elif evento.key == pygame.K_BACKSPACE and len(nome_completo)==1:
                        primeiro_caractere_text = ""
                        nome_completo = nome_completo[:-1]
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    if posicao_botao_check.collidepoint(evento.pos):
                        botao_check_precionado = True
                        botao_check=pygame.transform.scale2x(pygame.image.load("imgs/botao_precionado_check.png"))
                        posicao_botao_check.center = (TELA_LARGURA // 2, altura_botoes_precionados)
                elif evento.type == pygame.MOUSEBUTTONUP:
                    if botao_check_precionado and posicao_botao_check.collidepoint(evento.pos):
                        if len(nome_completo)==3:
                            requisicao=requests.get('https://flappy-dragon-c73ce-default-rtdb.firebaseio.com/.json')
                            dict=requisicao.json()
                            todos_nomes = list(dict.keys())
                            if nome_completo not in todos_nomes:
                                with open('nome.txt', 'w') as arquivo:
                                    arquivo.write(nome_completo)
                                data = json.dumps({f'{nome_completo}':{'record':0}})
                                requests.patch('https://flappy-dragon-c73ce-default-rtdb.firebaseio.com/.json',data=data)
                                tela_escolher_nome = False
                                botao_check_precionado = False
                                fonte_nome_jogo = pygame.font.Font('Adventurer.ttf', 100)
                                nome_jogo = fonte_nome_jogo.render('FLAPPY', True, (0, 0, 0))
                                nome_jogo2 = fonte_nome_jogo.render('DRAGON', True, (0, 0, 0))
                                posicao_nome_jogo = nome_jogo.get_rect()
                                posicao_nome_jogo2 = nome_jogo2.get_rect()
                                posicao_nome_jogo.center = (TELA_LARGURA // 2, TELA_ALTURA // 4)
                                posicao_nome_jogo2.center = (TELA_LARGURA // 2, (TELA_ALTURA // 4)+nome_jogo.get_height())
                            else:
                                erro = fonte_record.render("Nome já existe!",True,(255, 255, 255))  
                                posicao_erro = erro.get_rect()
                                posicao_erro.center = (TELA_LARGURA // 2, TELA_ALTURA // 1.2)
                        else:
                            erro = fonte_record.render("Nome incompleto!",True,(255, 255, 255))   
                            posicao_erro = erro.get_rect()
                            posicao_erro.center = (TELA_LARGURA // 2, TELA_ALTURA // 1.2)

                        

                    botao_check=pygame.transform.scale2x(pygame.image.load("imgs/botao_check.png"))
                    posicao_botao_check.center = (TELA_LARGURA // 2, altura_botoes)

            tela.blit(IMAGEM_BACKGROUND, (0, 0))




            primeiro_caractere = fonte_nome_usuario.render(primeiro_caractere_text, True,(255, 255, 255))
            primeiro_caractere_rect = primeiro_caractere.get_rect(center=(TELA_LARGURA // 3.5, TELA_ALTURA //2.1))
            segundo_caractere = fonte_nome_usuario.render(segundo_caractere_text, True,(255, 255, 255))
            segundo_caractere_rect = segundo_caractere.get_rect(center=(TELA_LARGURA // 2, TELA_ALTURA //2.1))
            terceiro_caractere = fonte_nome_usuario.render(terceiro_caractere_text, True,(255, 255, 255))
            terceiro_caractere_rect = terceiro_caractere.get_rect(center=(TELA_LARGURA // 1.4, TELA_ALTURA //2.1))


            try:
                tela.blit(erro,posicao_erro)
            except:
                pass
            tela.blit(nome_jogo,posicao_nome_jogo)
            tela.blit(nome_jogo2,posicao_nome_jogo2)   
            chao.mover()
            chao.desenhar(tela)
            tela.blit(botao_check,posicao_botao_check)
            tela.blit(primeiro_caractere, primeiro_caractere_rect)
            tela.blit(segundo_caractere, segundo_caractere_rect)
            tela.blit(terceiro_caractere, terceiro_caractere_rect)
            tela.blit(digitar_nome_text,digitar_nome_text_rect)
            tela.blit(barra_branca1,barra_branca1_rect)
            tela.blit(barra_branca2,barra_branca2_rect)
            tela.blit(barra_branca3,barra_branca3_rect)


            pygame.display.update()






    
        # Loop da tela inicial
        tela_inicial = True
        while tela_inicial:
            relogio.tick(30)
            for evento in pygame.event.get():
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    if posicao_botao_play.collidepoint(evento.pos):
                        botao_play_precionado = True
                        botao_play=pygame.transform.scale2x(pygame.image.load("imgs/botao_play_precionado.png"))
                        posicao_botao_play.center = (TELA_LARGURA // 4, altura_botoes_precionados)
                    elif posicao_botao_sair.collidepoint(evento.pos):
                        botao_sair_precionado = True
                        botao_sair=pygame.transform.scale2x(pygame.image.load("imgs/botao_precionado_sair.png"))
                        posicao_botao_sair.center = (TELA_LARGURA // (4/3), altura_botoes_precionados)
                    elif posicao_botao_record.collidepoint(evento.pos) and not tela_records:
                        botao_record_precionado = True
                        botao_record=pygame.transform.scale2x(pygame.image.load("imgs/botao_precionado_record.png"))
                        posicao_botao_record.center = (TELA_LARGURA // 2, altura_botoes_precionados)
                    elif posicao_botao_record.collidepoint(evento.pos) and tela_records:
                        botao_record_precionado = True
                        botao_record=pygame.transform.scale2x(pygame.image.load("imgs/botao_precionado_voltar.png"))
                        posicao_botao_record.center = (TELA_LARGURA // 2, altura_botoes_precionados)
                
                elif evento.type == pygame.MOUSEBUTTONUP:
                    if botao_play_precionado and posicao_botao_play.collidepoint(evento.pos):
                        tela_inicial = False
                        botao_play_precionado = False
                        altura_botoes = TELA_ALTURA // 1.5
                        altura_botoes_precionados = TELA_ALTURA // 1.47
                        exibir_nome_jogo = True
                        tela_records = False
                    elif botao_sair_precionado and posicao_botao_sair.collidepoint(evento.pos):
                        pygame.quit()
                    elif botao_record_precionado and posicao_botao_record.collidepoint(evento.pos):
                        botao_record_precionado = False         
                        if altura_botoes < 633:
                            botao_record = pygame.transform.scale2x(pygame.image.load("imgs/botao_record.png"))
                            while altura_botoes < 633:
                                #mudar posiçao botoes
                                relogio.tick(30)
                                altura_botoes += 5
                                altura_botoes_precionados += 5
                                posicao_botao_play.center = (TELA_LARGURA // 4, altura_botoes)
                                posicao_botao_record.center = (TELA_LARGURA // 2, altura_botoes)
                                posicao_botao_sair.center = (TELA_LARGURA // (4/3), altura_botoes)

                                #blitar tudo da tela toda 
                                tela.blit(IMAGEM_BACKGROUND, (0, 0))
                                chao.mover()
                                chao.desenhar(tela)
                                tela.blit(nome_jogo,posicao_nome_jogo)
                                tela.blit(nome_jogo2,posicao_nome_jogo2)    

                                #botoes
                                tela.blit(botao_play,posicao_botao_play)
                                tela.blit(botao_sair,posicao_botao_sair)
                                tela.blit(botao_record,posicao_botao_record)

                                pygame.display.update()
                            exibir_nome_jogo = False
                            tela_records = True
                            carregar_top10 = True
                        else:
                            botao_record = pygame.transform.scale2x(pygame.image.load("imgs/botao_voltar.png"))
                            while altura_botoes > TELA_ALTURA // 1.5:
                                relogio.tick(30)
                                altura_botoes -= 5
                                altura_botoes_precionados -= 5
                                posicao_botao_play.center = (TELA_LARGURA // 4, altura_botoes)
                                posicao_botao_record.center = (TELA_LARGURA // 2, altura_botoes)
                                posicao_botao_sair.center = (TELA_LARGURA // (4/3), altura_botoes)

                                #blitar tudo da tela toda 
                                tela.blit(IMAGEM_BACKGROUND, (0, 0))
                                chao.mover()
                                chao.desenhar(tela) 

                                #botoes
                                tela.blit(botao_play,posicao_botao_play)
                                tela.blit(botao_sair,posicao_botao_sair)
                                tela.blit(botao_record,posicao_botao_record)
                                
                                pygame.display.update()
                                
                            exibir_nome_jogo = True
                            tela_records = False
                            
                            
                    botao_play=pygame.transform.scale2x(pygame.image.load("imgs/botao_play.png"))
                    posicao_botao_play.center = (TELA_LARGURA // 4, altura_botoes)
                    botao_sair = pygame.transform.scale2x(pygame.image.load("imgs/botao_sair.png"))
                    posicao_botao_sair.center = (TELA_LARGURA // (4/3), altura_botoes)
                    if not tela_records:
                        botao_record = pygame.transform.scale2x(pygame.image.load("imgs/botao_record.png"))
                        posicao_botao_record.center = (TELA_LARGURA // 2, altura_botoes)
                    else:
                        botao_record = pygame.transform.scale2x(pygame.image.load("imgs/botao_voltar.png"))
                        posicao_botao_record.center = (TELA_LARGURA // 2, altura_botoes)
            
            # Desenhe o fundo e o texto na tela
            tela.blit(IMAGEM_BACKGROUND, (0, 0))
            chao.mover()
            chao.desenhar(tela)
            
            if exibir_nome_jogo:
                #nome do jogo
                tela.blit(nome_jogo,posicao_nome_jogo)
                tela.blit(nome_jogo2,posicao_nome_jogo2)    

            #botoes
            tela.blit(botao_play,posicao_botao_play)
            tela.blit(botao_sair,posicao_botao_sair)
            tela.blit(botao_record,posicao_botao_record)

            if tela_records:
                if carregar_top10:
                    carregar_top10 = False
                    ranking=requests.get('https://flappy-dragon-c73ce-default-rtdb.firebaseio.com/.json')
                    ranking_dict=ranking.json()
                    top10=sorted(ranking_dict.items(), key=lambda x: x[1]['record'], reverse=True)[:10]
                    print(top10)
                    # texto top 10
                    fonte_ranking = pygame.font.Font('Adventurer.ttf', 30)

                    #TITULOS
                    ranking_nome_label = fonte_record.render('NOME',True,(255, 255, 255))
                    ranking_pontuacao_label = fonte_record.render('PONTUAÇÃO',True,(255, 255, 255))
                

                    #NOMES
                    top1_nome = fonte_ranking.render(f'{top10[0][0]}',True,(255, 255, 255))
                    top2_nome = fonte_ranking.render(f'{top10[1][0]}',True,(255, 255, 255))
                    top3_nome = fonte_ranking.render(f'{top10[2][0]}',True,(255, 255, 255))
                    top4_nome = fonte_ranking.render(f'{top10[3][0]}',True,(255, 255, 255))
                    top5_nome = fonte_ranking.render(f'{top10[4][0]}',True,(255, 255, 255))
                    top6_nome = fonte_ranking.render(f'{top10[5][0]}',True,(255, 255, 255))
                    top7_nome = fonte_ranking.render(f'{top10[6][0]}',True,(255, 255, 255))
                    top8_nome = fonte_ranking.render(f'{top10[7][0]}',True,(255, 255, 255))
                    top9_nome = fonte_ranking.render(f'{top10[8][0]}',True,(255, 255, 255))
                    top10_nome = fonte_ranking.render(f'{top10[9][0]}',True,(255, 255, 255))

                    altura_nomes = top1_nome.get_height()+10
                    
                    top1_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5))
                    top2_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+altura_nomes))
                    top3_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+2*altura_nomes))
                    top4_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+3*altura_nomes))
                    top5_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+4*altura_nomes))
                    top6_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+5*altura_nomes))
                    top7_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+6*altura_nomes))
                    top8_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+7*altura_nomes))
                    top9_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+8*altura_nomes))
                    top10_nome_rect  = top1_nome.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4.5+9*altura_nomes))

                    ranking_nome_label_rect = ranking_nome_label.get_rect(center=(TELA_LARGURA // 3, TELA_ALTURA // 4-2*altura_nomes))
                    ranking_pontuacao_label_rect = ranking_pontuacao_label.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4-2*altura_nomes))

                    #PONTUAÇÃO
                    top1_pontuacao = fonte_ranking.render(f'{top10[0][1]["record"]}',True,(255, 255, 255))
                    top2_pontuacao = fonte_ranking.render(f'{top10[1][1]["record"]}',True,(255, 255, 255))
                    top3_pontuacao = fonte_ranking.render(f'{top10[2][1]["record"]}',True,(255, 255, 255))
                    top4_pontuacao = fonte_ranking.render(f'{top10[3][1]["record"]}',True,(255, 255, 255))
                    top5_pontuacao = fonte_ranking.render(f'{top10[4][1]["record"]}',True,(255, 255, 255))
                    top6_pontuacao = fonte_ranking.render(f'{top10[5][1]["record"]}',True,(255, 255, 255))
                    top7_pontuacao = fonte_ranking.render(f'{top10[6][1]["record"]}',True,(255, 255, 255))
                    top8_pontuacao = fonte_ranking.render(f'{top10[7][1]["record"]}',True,(255, 255, 255))
                    top9_pontuacao = fonte_ranking.render(f'{top10[8][1]["record"]}',True,(255, 255, 255))
                    top10_pontuacao = fonte_ranking.render(f'{top10[9][1]["record"]}',True,(255, 255, 255))

                    top1_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5))
                    top2_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+altura_nomes))
                    top3_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+2*altura_nomes))
                    top4_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+3*altura_nomes))
                    top5_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+4*altura_nomes))
                    top6_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+5*altura_nomes))
                    top7_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+6*altura_nomes))
                    top8_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+7*altura_nomes))
                    top9_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+8*altura_nomes))
                    top10_pontuacao_rect  = top1_pontuacao.get_rect(center=(TELA_LARGURA // 1.5, TELA_ALTURA // 4.5+9*altura_nomes))
                

                #nome e record
                seu_record = fonte_ranking.render(f'Seu record: {record_num}', True, (255, 255, 255))
                posicao_seu_record = seu_record.get_rect()
                posicao_seu_record.center = (TELA_LARGURA // 4.3, TELA_ALTURA // 15)
                seu_nome = fonte_ranking.render(f'Seu nome: {nome_completo}', True, (255, 255, 255))
                posicao_seu_nome = seu_record.get_rect()
                posicao_seu_nome.center = (TELA_LARGURA // 1.3, TELA_ALTURA // 15)

                tela.blit(ranking_nome_label,ranking_nome_label_rect)
                tela.blit(ranking_pontuacao_label,ranking_pontuacao_label_rect)
                tela.blit(top1_nome,top1_nome_rect)
                tela.blit(top2_nome,top2_nome_rect)
                tela.blit(top3_nome,top3_nome_rect)
                tela.blit(top4_nome,top4_nome_rect)
                tela.blit(top5_nome,top5_nome_rect)
                tela.blit(top6_nome,top6_nome_rect)
                tela.blit(top7_nome,top7_nome_rect)
                tela.blit(top8_nome,top8_nome_rect)
                tela.blit(top9_nome,top9_nome_rect)
                tela.blit(top10_nome,top10_nome_rect)

                tela.blit(top1_pontuacao,top1_pontuacao_rect)
                tela.blit(top2_pontuacao,top2_pontuacao_rect)
                tela.blit(top3_pontuacao,top3_pontuacao_rect)
                tela.blit(top4_pontuacao,top4_pontuacao_rect)
                tela.blit(top5_pontuacao,top5_pontuacao_rect)
                tela.blit(top6_pontuacao,top6_pontuacao_rect)
                tela.blit(top7_pontuacao,top7_pontuacao_rect)
                tela.blit(top8_pontuacao,top8_pontuacao_rect)
                tela.blit(top9_pontuacao,top9_pontuacao_rect)
                tela.blit(top10_pontuacao,top10_pontuacao_rect)
                
                tela.blit(seu_record,posicao_seu_record)
                tela.blit(seu_nome,posicao_seu_nome)



            pygame.display.flip()






        ultimo_cano=Cano(700)
        passaros = [Passaro(230, 350)]
        canos = [ultimo_cano]

        #loop jogo
        jogo = True
        while jogo:
            relogio.tick(30)

            # interação com o usuário
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    rodando = False
                    pygame.quit()
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        for passaro in passaros:
                            passaro.pular()

            # mover as coisas
            for passaro in passaros:
                passaro.mover()
            chao.mover()

            
            adicionar_cano = False
            remover_canos = []
            for cano in canos:
                for i, passaro in enumerate(passaros):
                    if cano.colidir(passaro):  
                        passaros.pop(i)
                        with open('record_num.txt', 'r+') as arquivo:
                            record_novo = f'{pontos}'
                            record_int=int(arquivo.read())
                            if pontos > record_int:
                                arquivo.seek(0)
                                arquivo.write(record_novo)
                                record_num=pontos
                                requests.patch(f'https://flappy-dragon-c73ce-default-rtdb.firebaseio.com/.json',data=json.dumps({nome_completo:{'record':pontos}}))              
                    if not cano.passou and passaro.x > cano.x:
                        cano.passou = True
                        adicionar_cano = True
                cano.mover()
                if cano.x + cano.CANO_TOPO.get_width() < 0:
                    remover_canos.append(cano)
            
        
            if adicionar_cano:
                pontos += 1
                ultimo_cano=Cano(600)
                canos.append(ultimo_cano)
            for cano in remover_canos:
                canos.remove(cano)
            if ultimo_cano in remover_canos:
                tela_inicial=True
                jogo=False
                pontos = 0
                
            
            for i, passaro in enumerate(passaros):
                if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                    passaros.pop(i)
                    with open('record_num.txt', 'r+') as arquivo:
                        record_novo = f'{pontos}'
                        record_int=int(arquivo.read())
                        if pontos > record_int:
                            arquivo.seek(0)
                            arquivo.write(record_novo)
                            record_num=pontos
                            requests.patch(f'https://flappy-dragon-c73ce-default-rtdb.firebaseio.com/.json',data=json.dumps({nome_completo:{'record':pontos}}))  
                     
            desenhar_tela(tela, passaros, canos, chao, pontos)


if __name__ == '__main__':
    main()
