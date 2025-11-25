import json
import mysql.connector
import requests
import os

# Conectar ao banco de dados
conn = mysql.connector.connect(
    host='localhost',
    user='user_trab',
    password='it5752025',
    database='cadastro_imobiliario_it575'
)
cursor = conn.cursor()

print(">> Conexão com MySQL bem-sucedida!")

# Criar tabela cidade se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`cidade` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_estado` INT NOT NULL,
  `nome` VARCHAR(100) NOT NULL,
  `geometria` MULTIPOLYGON NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_cidade_estado_idx` (`id_estado` ASC) VISIBLE,
  CONSTRAINT `fk_cidade_estado`
    FOREIGN KEY (`id_estado`)
    REFERENCES `cadastro_imobiliario_it575`.`estado` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;
""")

# Função para baixar arquivos do GitHub
def baixar_arquivo_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] Erro ao baixar {url}: {e}")
        return None

# Função para converter coordenadas para o formato correto
def corrigir_coordenadas(geometry):
    """Corrige as coordenadas para o formato esperado pelo MySQL"""
    if geometry['type'] == 'MultiPolygon':
        coordinates = geometry['coordinates']
        return {
            'type': 'MultiPolygon',
            'coordinates': coordinates
        }
    elif geometry['type'] == 'Polygon':
        # Converte Polygon para MultiPolygon
        coordinates = geometry['coordinates']
        return {
            'type': 'MultiPolygon',
            'coordinates': [coordinates]
        }
    else:
        raise ValueError(f"Tipo de geometria não suportado: {geometry['type']}")

# Mapeamento de siglas para IDs de estado (baseado na tabela estado)
def obter_mapeamento_estados():
    """Obtém o mapeamento de siglas para IDs da tabela estado"""
    cursor.execute("SELECT id, sigla FROM estado")
    resultados = cursor.fetchall()
    return {sigla: id_estado for id_estado, sigla in resultados}

# Repositório GitHub para cidades
REPOSITORIO_BASE = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson"

# Mapeamento de UF para código numérico do repositório
mapeamento_uf_codigo = {
    # Região Norte
    'AC': '12', 'AM': '13', 'AP': '16', 'PA': '15', 
    'RO': '11', 'RR': '14', 'TO': '17',
    # Região Nordeste
    'AL': '27', 'BA': '29', 'CE': '23', 'MA': '21',
    'PB': '25', 'PE': '26', 'PI': '22', 'RN': '24', 'SE': '28',
    # Região Sudeste
    'ES': '32', 'MG': '31', 'RJ': '33', 'SP': '35',
    # Região Sul
    'PR': '41', 'RS': '43', 'SC': '42',
    # Região Centro-Oeste
    'DF': '53', 'GO': '52', 'MT': '51', 'MS': '50'
}

print(">> Obtendo mapeamento de estados...")
mapeamento_estados = obter_mapeamento_estados()
print(f">> Mapeamento obtido: {len(mapeamento_estados)} estados")

print(">> Iniciando download dos dados das cidades...")

# Contador para IDs de cidades
contador_id = 1
total_cidades = 0

for uf, codigo in mapeamento_uf_codigo.items():
    print(f"> Baixando cidades para: {uf} (código: {codigo})")
    
    # URL dos arquvos
    url = f"{REPOSITORIO_BASE}/geojs-{codigo}-mun.json"
    
    # Baixar dados
    data = baixar_arquivo_github(url)
    
    if data is None:
        print(f"> > > Pulando {uf} devido a erro no download")
        continue
    
    try:
        # Obter ID do estado
        id_estado = mapeamento_estados.get(uf)
        if id_estado is None:
            print(f"[!] Estado {uf} não encontrado na tabela estado")
            continue
        
        # Processar as features (cidades)
        if 'features' in data:
            cidades_processadas = 0
            for feature in data['features']:
                try:
                    properties = feature.get('properties', {})
                    geometry = feature.get('geometry', {})
                    
                    if not geometry:
                        continue
                    
                    # Extrair nome da cidade
                    nome_cidade = (properties.get('name') or 
                                  properties.get('nome') or 
                                  properties.get('NM_MUNICIP') or
                                  properties.get('name_') or
                                  properties.get('municipality') or
                                  f"Cidade_{contador_id}")
                    
                    # Corrigir a geometria para o formato correto
                    geometry_corrigida = corrigir_coordenadas(geometry)
                    geometry_json = json.dumps(geometry_corrigida)
                    
                    # Inserir na tabela cidade
                    cursor.execute("""
                        INSERT INTO cidade (id, id_estado, nome, geometria)
                        VALUES (%s, %s, %s, ST_GeomFromGeoJSON(%s));
                    """, (contador_id, id_estado, nome_cidade, geometry_json))
                    
                    contador_id += 1
                    cidades_processadas += 1
                    total_cidades += 1
                    
                except Exception as e:
                    print(f"  [!] Erro ao processar cidade {contador_id} em {uf}: {e}")
                    continue
            
            conn.commit()
            print(f">>> {cidades_processadas} cidades processadas para {uf}")
            
        else:
            print(f"[!] Nenhuma feature encontrada no JSON para {uf}")
            
    except Exception as e:
        print(f"[!] Erro ao processar cidades de {uf}: {e}")

# Verificar quantos registros foram inseridos
cursor.execute("SELECT COUNT(*) FROM cidade")
total_inserido = cursor.fetchone()[0]

print(f"\n>>>> Processamento concluído!")
print(f">>> Total de cidades inseridas: {total_inserido}")
print(f">>> Próximo ID disponível: {contador_id}")

# Estatísticas por estado
cursor.execute("""
    SELECT e.sigla, COUNT(c.id) as total_cidades
    FROM estado e
    LEFT JOIN cidade c ON e.id = c.id_estado
    GROUP BY e.id, e.sigla
    ORDER BY e.sigla
""")
estatisticas = cursor.fetchall()

print(f"\n>> Estatísticas por estado:")
for sigla, total in estatisticas:
    print(f"  {sigla}: {total} cidades")

cursor.close()
conn.close()