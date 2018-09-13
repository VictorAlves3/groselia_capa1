#Rodar em /c/Cerberon/sistema/imf/scripts
cd /c/Cerberon/sistema/imf/scripts
rm -rf /c/Cerberon/sistema/imf/scripts/*
cp -r /c/sistema/scripts/shell /c/Cerberon/sistema/imf/scripts/shell
cp -r /c/sistema/scripts/workflow /c/Cerberon/sistema/imf/scripts/workflow

# remover arquivos inuteis nesse ponto #

find . -name *@hk -exec sh -c 'mv "$1" "${1%@hk}@HK" && echo Extensão de "$1" corrigida' _ {} \;
find . -name *@prod -exec sh -c 'mv "$1" "${1%@prod}@PROD" && echo Extensão de "$1" corrigida' _ {} \;
#### Atenção ao usar isso, remove as versões de DEV da pasta, deve ser usado apenas na pasta do Cerberon
# find . -name *@HK -exec sh -c 'rm  "${1%@HK}" && echo Removendo "${1%@HK}"' _ {} \;
####
find . -type f -exec sh -c 'sed -i "s/\r//g" "$1" && echo Corrigindo terminação de "$1"'  _ {} \;