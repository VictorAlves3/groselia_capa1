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
    codigo_sistema = (indice.keys()[1].split("-")[-1].strip())[-2:].lower()

    print("""
#############################################
###    trabalhando com ddr do codigo_sistema """ + codigo_sistema + """   ###
############################################# """)

    gera_fluxos(codigo_sistema, indice)

    print("         GERANDO INTERFACES        ")

    for fluxo in fluxos:
        gera_interface(fluxo, codigo_sistema)

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


def gera_interface(aba, codigo_sistema):
    describes = load_describes()
    interface_path = "./siglas/{}0/interface/".format(codigo_sistema)
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
        campo["data_size"] = str(linha[4]).replace("(","").replace(")","").replace(",",".")
        campo = trata_campos(campo)
        campos.append(campo)

    nome_describe = nome.lower().replace("he0_","")
    try:
        describe = describes[nome_describe]
    except:
        print("describe do fluxo {} não encontrado".format(nome_describe))
        return 0

    lista = describe["column_definition"]
    lista = { x["output"] :lista.index(x) for x in lista if len(x["output"]) > 3}

    for campo in campos:
        if len(campo["output"]) > 3 :
            try:
                if "input" in campo.keys():
                    describe["column_definition"][lista[campo["output"]]]["input"] = campo["input"]

                describe["column_definition"][lista[campo["output"]]]["type"] = campo["type"]
                describe["column_definition"][lista[campo["output"]]]["data_size"] = campo["data_size"]

            except:
                print("erro no campo: {}".format(campo))

    if not os.path.exists(interface_path):
        os.makedirs(interface_path)

    with open(interface_path + interface_name.lower() + "_" + codigo_sistema + ".json","w",encoding='utf8') as file:
        json.dump(describe,file,indent=4, ensure_ascii=False)
        file.close()

    return 0


def gera_fluxos(codigo_sistema, indice):
    config_json_path = "./config_model.json"
    config_json = load_json(config_json_path)
    fluxos = []
    colunas = [list(x) for x in indice.values if "Nome" in str(x[0])][0]
    col = {str(x).strip() : colunas.index(x) for x in colunas}

    for linha in indice.values:
        linha_concat = " ".join([str(x).lower() for x in linha])
        if codigo_sistema + "0" in linha_concat:
            fluxo = [str(x) for x in linha]
            fluxos.append(fluxo)

    codigo_sistema_base_path = "./siglas/{}0/".format(codigo_sistema)
    schema_path = codigo_sistema_base_path + "schema/"
    tabela = "wf_ex_imf_"

    # configurar json_config
    config_json["codigo_sistema"] = codigo_sistema


    # cria pastas da codigo_sistema
    if not os.path.exists(codigo_sistema_base_path):
        os.makedirs(codigo_sistema_base_path)

    if not os.path.exists(schema_path):
        os.makedirs(schema_path)

    print("         GERANDO FLUXOS       ")

    for fluxo in fluxos:
        print(">>> gerando fluxo " + fluxo[0])
        config_json["codigo_sistema_origem"] = fluxo[col["Sigla"]]
        config_json["codigo_conteudo"] = fluxo[col["Contenido"]]
        fluxo_py = "{}{}{}_{}_{}0.py".format(codigo_sistema_base_path, tabela, fluxo[col["Nome"]], config_json["codigo_conteudo"], codigo_sistema).lower()
        fluxo_json = "{}{}{}_{}_{}0.json".format(codigo_sistema_base_path, tabela, fluxo[col["Nome"]], config_json["codigo_conteudo"], codigo_sistema).lower()
        config_json = configura_dict_config(config_json, fluxo[0])

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

def load_describes():
    describes_path = "../interfaces_saida/interfaces"
    describes = ["{}/{}".format(describes_path,x) for x in os.listdir(describes_path)]
    describes = {x.split("/")[3].split(".")[0].replace("he0_",""):json.loads(open(x,"r").read()) for x in describes}

    return describes
# main


run()


input("precione enter para finalizar")



