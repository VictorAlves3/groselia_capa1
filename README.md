# Groselia_capa1
### Facilitadores de trabalho para equipe capa1

```diff
- # rode gere as interaces antes das siglas sempre
```
# Gera interfaces
1. Coloque os describes na pasta interfaces_saida/describes
2. Execute o script interface.py

# Gera sigla
1. Adicione as ddrs na pasta siglas/ddr/
1. Rode o arquivo gera_sigla.py
1. Ajustar os seguintes campos manualmente nas interfaces
    * Campos que são parametro
    * Campos que são fixed
    * Campos que vem de tabelas
1. Ajustar json de fluxos com especifidades necessarias
1. Incluir funcionalidades devidas para cada fluxo
1. Criar layouts de entrada
## Campos inferidos apartir da ddr
### json
* codigo_sistema
* codigo_sistema_origem
* periodicidade
* periodiciade_upper
* codigo_contenido
### interface
* input
* output
* tipo_dado
* tamanho_dado
* tipo_campo
