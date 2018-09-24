import os
import json

def carrega_arquivos():
    files_base_path = "../interfaces_saida/describes/"
    files = [files_base_path + x for x in os.listdir(files_base_path) if ".txt" in x]
    interfaces = []
    for arquivo in files:
        interface = open(arquivo,"r").read()
        interfaces.append((interface,arquivo.split("/")[3].replace(".txt","")))
    return interfaces

def gera_interfaces():
    # Loading
    interfaces = carrega_arquivos()

    for interface, nome in interfaces:
        linhas = interface.split("\n")[5:-2]
        campos = [x.split("|")[2].strip() for x in linhas]
        registros = []
        saida = {}

        # Getting fields
        for linha in linhas:
            reg = {}
            registro = linha.split("|")
            registro = [x.strip() for x in registro]
            reg["output"] = registro[2]
            reg["data_type"] = registro[3]
            reg["data_size"] = registro[4]
            reg["data_precision"] = registro[5].replace("(","").replace(")","")
            reg["nullable"] = registro[6]
            # Ajusting
            if reg["data_type"] == "NUMBER":
                if not "null" in reg["data_precision"]:
                    reg["data_type"] = "double"
                    reg["data_size"] = "{}.{}".format(reg["data_size"],reg["data_precision"])
                else:
                    reg["data_type"] = "int"
            elif "VARCHAR2" or "CHAR" in reg["data_type"]:
                reg["data_type"] = "texto"
            else:
                reg["data_type"] = reg["data_type"].lower()

            if reg["nullable"] == "Y":
                reg["is_not_null"] = "false"
            else:
                reg["is_not_null"] = "true"
            # Cleaning
            reg.pop("nullable")
            reg.pop("data_precision")

            registros.append(reg)

        # Making json
        saida["column_order"] = campos
        saida["column_definition"] = registros

        with open("../interfaces_saida/interfaces/" + nome + ".json","w") as fl:
            json.dump(saida,fl,indent=4)



gera_interfaces()
