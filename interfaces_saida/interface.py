import os
import json

def carrega_arquivos():
    files = ["../interfaces_saida/describes/" + x for x in os.listdir("../interfaces_saida/describes/") if ".txt" in x]
    interfaces = []
    for arquivo in files:
        interface = open(arquivo,"r").read()
        interfaces.append((interface,arquivo.split("/")[3].replace(".txt","")))
    return interfaces

def gera_interfaces():
    interfaces = carrega_arquivos()

    for interface, nome in interfaces:
        linhas = interface.split("\n")[5:-2]
        campos = [x.split("|")[2].strip() for x in linhas]
        registros = []
        saida = {}
        for linha in linhas:
            reg = {}
            registro = linha.split("|")
            registro = [x.strip() for x in registro]
            reg["output"] = registro[2]
            reg["data_type"] = registro[3]
            reg["data_size"] = registro[4]
            reg["data_precision"] = registro[5].replace("(","").replace(")","")
            reg["nullable"] = registro[6]
            if reg["data_type"] == "NUMBER":
                if not "null" in reg["data_precision"]:
                    reg["data_type"] = "double"
                else:
                    reg["data_type"] = "int"
            elif reg["data_type"] == "VARCHAR2":
                reg["data_type"] = "texto"

            registros.append(reg)
        saida["column_order"] = campos
        saida["column_definition"] = registros
        with open("../interfaces_saida/interfaces/" + nome + ".json","w") as fl:
            json.dump(saida,fl,indent=4)



gera_interfaces()
