
global prod_list
global vend_list

prod_list = []
vend_list = []

def ler_arq():
    #Leitura arquivo de entrada PRODUTOS.TXT
    arq_produtos = open('PRODUTOS.TXT', 'r', encoding='UTF-8')
    leitura_dados1 = arq_produtos.readline()

    while leitura_dados1 != '':
        leitura_dados1 = leitura_dados1.split(';')

        prod_list.append(
            [
                int(leitura_dados1[0]),
                int(leitura_dados1[1]),
                int(leitura_dados1[2])
            ]
        )

        leitura_dados1 = arq_produtos.readline()

    arq_produtos.close()
    prod_list.sort()

    #Leitura arquivo de entrada VENDAS.TXT
    arq_vendas = open('VENDAS.TXT', 'r', encoding='UTF-8')
    leitura_dados2 = arq_vendas.readline()

    linha = 1
    ausente = False
    while leitura_dados2 != '':
        leitura_dados2 = leitura_dados2.split(';')
        vend_list.append(
            [
                int(leitura_dados2[0]),
                int(leitura_dados2[1]),
                int(leitura_dados2[2]),
                int(leitura_dados2[3]),
                linha,
                ausente
            ]
        )
        leitura_dados2 = arq_vendas.readline()
        linha +=1

    arq_vendas.close()
ler_arq()

#Declaração de váriaveis
global vend_canc
global vend_aprov
global valid_list
global estq_list
global necess_list
global transf_list
global qtvend_list
global estq_pos
global cod_list

vend_canc   = []
vend_aprov  = []
valid_list  = []
estq_list   = []
necess_list = []
transf_list = []
qtvend_list = []
estq_pos    = []
cod_list    = []

global diverg
diverg = {
          135     : "Venda cancelada",
          190     : "Venda não finalizada",
          999     : "Erro desconhecido. Acionar equipe de TI."
         }

def checagem():
    for item in vend_list:
        i = 0
        while i < len(prod_list):
            if item[0] == prod_list[i][0]:
                valid_list.append(item) # lista de validos
                cod_list.append(item[0]) #lista de códigos das vendas que estão na lista de produtos
            i += 1
    valid_list.sort()

    for item in vend_list:
        if item[0] not in cod_list:
            if item[2] == 999:
                vend_canc.append(item)
            else:
                item[5] = True  #altera o valor da situação caso o código não esteja na lista de produtos
                vend_canc.append(item)

    for item in valid_list:
        if item[2] == 100 or item[2] == 102:
            vend_aprov.append(item) # lista de aprovados
        else:
            vend_canc.append(item) # lista de cancelados

    vend_canc.sort(key=lambda x: x[4]) #sort no ultima elemento da lista(linhas de erro)
    vend_aprov.sort()
    vend_list.sort()
checagem()

def calcula_estq():
    # Estoque após vendas
    soma_vend = 0
    for item in prod_list:
        soma_vend = 0
        i = 0
        while i < len(vend_aprov):
            if item[0] == vend_aprov[i][0]:
                soma_vend += vend_aprov[i][1]
            i += 1
        qtvend_list.append([item[0], soma_vend]) # adiciona o código e a quantidade de vendas de cada um
        estq_pos.append([item[0], item[1] - soma_vend]) # adiciona o código e a quantidade de estoque após as vendas

    # Necessidade de reposição e Transferência para CO
    for qtd in estq_pos:
        i = 0
        while i < len(prod_list):
            qt_min = prod_list[i][2]
            if qtd[0] == prod_list[i][0]:
                if qtd[1] < qt_min:
                    necess = qt_min - qtd[1]
                else:
                    necess = 0
                necess_list.append(necess)

                if 0 < necess < 10:
                    transf = 10
                else:
                    transf = necess
                transf_list.append(transf)
            i += 1

calcula_estq()

def arq_output():
    #Arquivo TRANSFERE.TXT(1)
    arq_transfere = open('TRANSFERE.TXT', 'w', encoding = 'UTF-8')

    arq_transfere.write("Necessidade de Transferência Armazém para CO\n\n"
                f"{('Produto')} {('QtCO'):>13} {('QtMin'):>15} "
                f"{('QtVendas'):>15} {('Estq.após'):>15} {('Necess.'):>15} "
                f"{('Transf. de '):>16} \n")

    arq_transfere.write(f"{('Vendas'):>69} {('Arm p/ CO'):>31}\n")

    for i in range(len(prod_list)):
        arq_transfere.write(f"{prod_list[i][0]} {prod_list[i][1]:>15} {prod_list[i][2]:>15} "
                            f"{qtvend_list[i][1]:>15} {estq_pos[i][1]:>15} {necess_list[i]:>15} "
                            f"{transf_list[i]:>15} \n")

    arq_transfere.close()

    #Arquivo DIVERGENCIAS.TXT(2)
    arq_diverg = open('DIVERGENCIAS.TXT', 'w', encoding = 'UTF-8')

    for erro in vend_canc:
        err_linha = erro[4]
        if erro[5] == True:
            arq_diverg.write(f"Linha {err_linha} - Código de Produto não encontrado {erro[0]}\n")
        else:
            arq_diverg.write(f"Linha {err_linha} - {diverg[erro[2]]}\n")

    arq_diverg.close()

    #Arquivo TOTCANAIS.TXT(Tarefa bônus)
    def vendas_canal():
        soma_Repre = soma_web = soma_Andro = soma_Ipho = 0
        for item in vend_list:
            if item[2] == 100 or item[2] == 102:
                if item[3] == 1:
                    soma_Repre += item[1]
                elif item[3] == 2:
                    soma_web += item[1]
                elif item[3] == 3:
                    soma_Andro += item[1]
                else:
                    soma_Ipho += item[1]
        return soma_Repre, soma_web, soma_Andro, soma_Ipho

    arq_canais = open('TOTCANAIS.TXT', 'w', encoding = 'UTF-8')
    Repre, Web, Andro, Ipho = vendas_canal()

    arq_canais.write("Quantidades de Vendas por canal\n\n")

    arq_canais.write(f"{('Canal'):<1} {('QtVendas'):>35}\n")

    arq_canais.write(f"1 - Representantes {Repre:>22}\n"
                     f"2 - Website {Web:>29}\n"
                     f"3 - App móvel Android {Andro:>19}\n"
                     f"4 - App móvel Iphone {Ipho:>20}\n")
    arq_canais.close()

    print("Análise do Estoque Operacional concluída.")

arq_output()
