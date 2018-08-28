import pandas as pds
import os
import json

def run():
    files = ["./ddrs/" + x for x in os.listdir("./ddrs")]

    for ddr in files:
        principal(ddr)

    return 0


def principal(nome_arquivo):
    ddr = load_excel(nome_arquivo)
    indice, fluxos = separa_abas(ddr)
    sigla = (indice.keys()[1].split("-")[-1].strip() + "0")[-3:].lower()

    print("""
#############################################
###    trabalhando com ddr da sigla """ + sigla + """   ###
############################################# """)

    gera_fluxos(sigla, indice)

    print("         GERANDO INTERFACES        ")

    for fluxo in fluxos:
        gera_interface(fluxo, sigla)

    return 0


def trata_campos(dict_campo):
    entrada = dict_campo["input"]
    saida = dict_campo["output"]
    tipo = dict_campo["type"]
    tipo_dado = dict_campo["data_type"]
    tamanho = dict_campo["data_size"]
    dict_campo.pop("input")

    if entrada == "Campo Não Carregado":
        dict_campo["type"] = "null"
        dict_campo["output"] = saida

    elif entrada.split()[0].upper() == "GAP":
        dict_campo["type"] = "gap"
        dict_campo["output"] = saida

    elif entrada == "Fixo":
        dict_campo["type"] = "fixed"
        dict_campo["output"] = saida
        dict_campo["input"] = tipo

    elif entrada == "Parâmetro":
        dict_campo["input"] = entrada
        dict_campo["type"] = "alias"
        dict_campo["output"] = saida

    else:
        dict_campo["input"] = entrada
        dict_campo["type"] = "column"
        dict_campo["output"] = saida

    if tipo_dado == "Numérico":
        if "." in tamanho:
            dict_campo["data_type"] = "double"
            dict_campo["data_size"] = tamanho
        else:
            dict_campo["data_type"] = "int"
            dict_campo["data_size"] = tamanho.split(".")[0]
    elif tipo_dado == "Texto":
        dict_campo["data_type"] = "texto"
        dict_campo["data_size"] = tamanho.split(".")[0]

    # ajusta input
    if dict_campo.get("input"):
        dict_campo["input"] = dict_campo["input"].replace("\n"," ").strip()


    return dict_campo


# carrega layout
def load_excel(path_arquivo):
    ddr = pds.read_excel(path_arquivo, sheet_name=None)
    return ddr


def load_json(path_arquivo):
    json_data = open(path_arquivo).read()
    config_json = json.loads(json_data)
    return config_json


def separa_abas(ddr):
    abas = {x[0] : ddr[x[0]] for x in ddr.items()}
    indice = None
    fluxos = []

    for nome , aba in abas.items():
        if "controle" in nome.lower():
            indice = aba
        elif "00" in nome and len(nome) <= 3:
            fluxos.append(aba)

    return indice, fluxos


def gera_interface(aba, sigla):
    interface_path = "./sigla/" + sigla + "/interface/"
    linhas = aba.values
    nome = aba.keys()[1]
    descricao = linhas[0][1]
    chave_primaria = linhas[1][1].replace("\n"," ").strip()
    linhas_campos = linhas[5:]
    interface_name = nome[7:]
    campos = []

    print(">>> gerando interface " + nome)

    for linha in linhas_campos:
        campo = {}
        campo["output"] = str(linha[0])
        campo["input"] = str(linha[7])
        campo["type"] = str(linha[8])
        campo["data_type"] = str(linha[3])
        campo["data_size"] = str(linha[4])
        campo = trata_campos(campo)
        campos.append(campo)

    if not os.path.exists(interface_path):
        os.makedirs(interface_path)

    with open(interface_path + interface_name.lower() + "_" + sigla + ".json","w",encoding='utf8') as file:
        json.dump(campos,file,indent=4, ensure_ascii=False)
        file.close()

    return 0


def gera_fluxos(sigla, indice):
    config_json_path = "./config_model.json"
    config_json = load_json(config_json_path)
    fluxos = []

    for linha in indice.values:
        linha_concat = " ".join([str(x).lower() for x in linha])
        if sigla in linha_concat:
            fluxo = (str(linha[0]).lower(), str(linha[3]).lower())
            fluxos.append(fluxo)

    sigla_base_path = "./sigla/" + sigla + '/'
    schema_path = sigla_base_path + "schema/"
    tabela = "wf_ex_imf_"

    # configurar json_config
    config_json["codigo_sistema"] = sigla
    config_json["codigo_sistema_origem"] = sigla

    # cria pastas da sigla
    if not os.path.exists(sigla_base_path):
        os.makedirs(sigla_base_path)

    if not os.path.exists(schema_path):
        os.makedirs(schema_path)
    print("         GERANDO FLUXOS       ")
    for fluxo in fluxos:
        print(">>> gerando fluxo " + fluxo[0])
        fluxo_py = sigla_base_path + tabela + fluxo[0] + "_" + sigla + ".py"
        fluxo_json = sigla_base_path + tabela +  fluxo[0] + "_" + sigla + ".json"
        config_json = configura_dict_config(config_json, fluxo[0])
        config_json["codigo_conteudo"] = fluxo[1]

        with open(fluxo_json,"w") as file:
            json.dump(config_json,file,indent=4)

        open(fluxo_py,"w").close()

    return 0


def configura_dict_config(dict_entrada, fluxo):
    fluxo = fluxo.lower()
    if "cto" in fluxo:
        dict_entrada["tipo_processamento"] = "odscto"
    elif "blce" in fluxo:
        dict_entrada["tipo_processamento"] = "odsddo"

    if "mes" in fluxo:
        dict_entrada["periodicidade"] = "m"
        dict_entrada["periodicidade_upper"] = "M"
    elif "dia" in fluxo:
        dict_entrada["periodicidade"] = "d"
        dict_entrada["periodicidade_upper"] = "D"

    return dict_entrada


# main
try:
    run()
except Exception as identifier:
    print(identifier)

input("precione enter para finalizar")



