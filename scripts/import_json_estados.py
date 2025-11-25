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
try:
    print(">> Conexão com MySQL bem-sucedida!")
except Exception as e:
    print(f"[!] Erro na conexão: {e}")

# Criar tabela se não existir (COM COLUNA SIGLA)
cursor.execute("""
CREATE TABLE IF NOT EXISTS `cadastro_imobiliario_it575`.`estado` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `sigla` VARCHAR(2) NOT NULL,
  `geometria` MULTIPOLYGON NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `nome_UNIQUE` (`nome` ASC) VISIBLE,
  UNIQUE INDEX `sigla_UNIQUE` (`sigla` ASC) VISIBLE)
ENGINE = InnoDB;
""")

# Função para baixar arquivos do GitHub
def baixar_arquivo_github(uf, repositorio_base):
    url = f"{repositorio_base}/br_{uf}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] Erro ao baixar {uf}: {e}")
        return None

# Função para converter coordenadas para o formato correto
def corrigir_coordenadas(geometry):
    """Corrige as coordenadas para o formato esperado pelo MySQL"""
    if geometry['type'] == 'MultiPolygon':
        # Para MultiPolygon, garantimos a estrutura correta
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

# Repositório GitHub
REPOSITORIO_BASE = "https://raw.githubusercontent.com/giuliano-macedo/geodata-br-states/main/geojson/br_states"

# Lista de estados (UF)
estados = [
    'ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go',
    'ma', 'mt', 'ms', 'mg', 'pa', 'pb', 'pr', 'pe', 'pi',
    'rj', 'rn', 'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to'
]

print(">> Iniciando download dos dados do GitHub...")

# Contador para IDs
contador_id = 1

# Iterar sobre os arquivos JSON dos estados
for uf in estados:
    print(f"> Baixando dados para: {uf.upper()}")
    
    # Baixar dados do GitHub
    data = baixar_arquivo_github(uf, REPOSITORIO_BASE)
    
    if data is None:
        print(f"> > > Pulando {uf.upper()} devido a erro no download")
        continue
    
    try:
        # O JSON é uma FeatureCollection, precisamos acessar features[0]
        if 'features' in data and len(data['features']) > 0:
            feature = data['features'][0]
            properties = feature['properties']
            geometry = feature['geometry']
            
            # Extrair nome e sigla
            nome = properties.get('name', uf.upper())
            sigla = properties.get('sigla', uf.upper())
            
            print(f"  Geometria tipo: {geometry['type']}")
            
            # Corrigir a geometria para o formato correto
            geometry_corrigida = corrigir_coordenadas(geometry)
            geometry_json = json.dumps(geometry_corrigida)
            
            print(f"  Inserindo: {nome} ({sigla})")

            # Inserir usando ST_GeomFromGeoJSON
            cursor.execute("""
                INSERT INTO estado (id, nome, sigla, geometria)
                VALUES (%s, %s, %s, ST_GeomFromGeoJSON(%s));
                """, (contador_id, nome, sigla, geometry_json))

            conn.commit()
            print(f">>> Estado inserido: {nome} ({sigla})")
            contador_id += 1
        else:
            print(f"[!] Nenhuma feature encontrada no JSON para {uf}")
            
    except KeyError as e:
        print(f"[!] Erro na estrutura do JSON para {uf}: {e}")
    except mysql.connector.IntegrityError as e:
        print(f"[!] Erro de duplicata para {uf}: {e}")
    except Exception as e:
        print(f"[!] Erro ao processar {uf.upper()}: {e}")
        # Debug detalhado do erro de geometria
        if 'geometry' in locals():
            print(f"    Tipo de geometria: {geometry.get('type', 'N/A')}")
            print(f"    Estrutura geometry: {json.dumps(geometry, indent=2)[:500]}...")

# Verificar quantos registros foram inseridos
cursor.execute("SELECT COUNT(*) FROM estado")
total = cursor.fetchone()[0]
print(f"\n>>>> Processamento concluído! {total} estados inseridos no banco.")

cursor.close()
conn.close()