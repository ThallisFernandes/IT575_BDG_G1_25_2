import random
from datetime import datetime, timedelta
import mysql.connector
from faker import Faker
from faker.providers import address

# Configurações - Intervalo de imóveis por bairro
MIN_IMOVEIS_POR_BAIRRO = 50
MAX_IMOVEIS_POR_BAIRRO = 500

fake = Faker('pt_BR')
fake.add_provider(address)

# Função para gerar nomes de bairros
def gerar_nome_bairro():
    prefixos = ['Vila', 'Jardim', 'Parque', 'Morro', 'Lagoa', 'Vale', 'Alto', 'Baixo', 'São', 'Santa', 'Nossa Senhora', 'Bela', 'Nova', 'Velha', 'Sítio']
    sufixos = ['Flores', 'Sol', 'Lua', 'Mar', 'Rio', 'Serra', 'Verde', 'Azul', 'Dourado', 'Branco', 'Negro', 'Centro', 'Leste', 'Oeste', 'Norte', 'Sul', 'Cristal', 'Primavera', 'Verão', 'Inverno', 'Outono', 'Esperança', 'Alegria', 'Paz', 'União', 'Liberdade']
    
    if random.random() > 0.5:
        return f"{random.choice(prefixos)} {random.choice(sufixos)}"
    else:
        return f"{random.choice(prefixos)} {fake.first_name()}"

# Função para gerar complementos
def gerar_complemento():
    if random.random() > 0.7:  
        tipos = ['Apto', 'Casa', 'Sala', 'Loja', 'Galpão', 'Box', 'Conjunto']
        numeros = ['101', '202', '303', 'A', 'B', 'C', '1', '2', '3']
        letras = ['A', 'B', 'C', 'D', 'E']
        
        complemento = random.choice(tipos)
        if random.random() > 0.5:
            complemento += f" {random.choice(numeros)}"
        if random.random() > 0.7:
            complemento += f" Bloco {random.choice(letras)}"
        
        return complemento
    return None

# Função para gerar números de endereço
def gerar_numero_endereco():
    numero = str(random.randint(1, 5000))
    if random.random() > 0.9:
        numero += random.choice(['A', 'B', 'C', 'S/N'])
    return numero

# Função para determinar número de imóveis por bairro
def determinar_imoveis_por_bairro(bairro_id, total_bairros, cidade_id):
    fator_cidade = 1.0
    if cidade_id in [1, 2]:
        fator_cidade = 1.5
    elif cidade_id in [3, 4, 5]:
        fator_cidade = 1.2
    
    # Bairros "centrais" têm mais imóveis
    if bairro_id <= total_bairros * 0.2:  
        fator_central = random.uniform(1.2, 1.8)
    else:
        fator_central = random.uniform(0.7, 1.3)
    
    base = random.normalvariate(200, 80)
    imoveis = int(base * fator_cidade * fator_central)
    imoveis = max(MIN_IMOVEIS_POR_BAIRRO, min(MAX_IMOVEIS_POR_BAIRRO, imoveis))
    
    return imoveis

# Geometrias simples sem operações complexas
def geometria_bairro_simples(bairro_id, cidade_id):
    coordenadas_cidades = {
        1: (-46.6333, -23.5505),  # São Paulo
        2: (-43.1729, -22.9068),   # Rio de Janeiro
        3: (-43.9378, -19.9208),   # Belo Horizonte
        4: (-38.5167, -12.9667),   # Salvador
        5: (-38.5247, -3.7275),    # Fortaleza,
    }
    
    base_lon, base_lat = coordenadas_cidades.get(cidade_id, (-46.6333, -23.5505))
    
    variacao_lon = (bairro_id % 10) * 0.01
    variacao_lat = (bairro_id // 10) * 0.01
    
    lon = base_lon + variacao_lon
    lat = base_lat + variacao_lat
    
    # Criar um polígono quadrado simples
    tamanho = 0.005  # ~ 500m
    return f'MULTIPOLYGON((( {lon} {lat}, {lon} {lat+tamanho}, {lon+tamanho} {lat+tamanho}, {lon+tamanho} {lat}, {lon} {lat} )))'

def geometria_logradouro_simples(logradouro_id):
    base_lon = -46.6333 + (logradouro_id * 0.0001)
    base_lat = -23.5505 + (logradouro_id * 0.0001)
    
    # Criar múltiplos pontos simples
    pontos = []
    for i in range(2):
        pontos.append(f'({base_lon + i*0.001} {base_lat + i*0.001})')
    
    return f'MULTIPOINT({", ".join(pontos)})'

def geometria_endereco_simples(endereco_id, bairro_id):
    # Gerar coordenadas baseadas no ID do bairro e endereço
    base_lon = -46.6333 + (bairro_id * 0.001) + (endereco_id * 0.00001)
    base_lat = -23.5505 + (bairro_id * 0.001) + (endereco_id * 0.00001)
    
    return f'POINT({base_lon} {base_lat})'

# Conectar ao banco de dados
conn = mysql.connector.connect(
    host='localhost',
    user='user_trab',
    password='it5752025',
    database='cadastro_imobiliario_it575'
)
cursor = conn.cursor()

print("\n>> Conexão com MySQL bem-sucedida!\n")

# PERGUNTA AO USUÁRIO: Limpar dados existentes?
resposta = input("Deseja limpar todos os dados existentes antes de inserir novos? (s/N): ").strip().lower()

if resposta == 's':
    print("\nLimpando dados existentes...")
    # Desabilitar verificações de chave estrangeira
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    tabelas_para_limpar = [
        'iptu', 'imovel_juridica', 'fisica_imovel', 'edificacao_imovel',
        'residencial', 'comercial', 'casa', 'apartamento', 'edificacao',
        'terreno', 'fisica', 'juridica', 'pessoa', 'imovel',
        'endereco', 'bairro_logradouro', 'logradouro', 'bairro'
    ]
    
    for tabela in tabelas_para_limpar:
        try:
            cursor.execute(f"DELETE FROM {tabela}")
            print(f"> Tabela {tabela} limpa")
        except mysql.connector.Error as err:
            print(f"[!] Erro ao limpar {tabela}: {err}")
    
    # Reabilitar verificações de chave estrangeira
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("> Dados antigos removidos!\n")
else:
    print("> Mantendo dados existentes...")

print("\nIniciando a inserção de dados...\n")

# Buscar estados e cidades existentes no banco
try:
    cursor.execute("SELECT id, nome FROM estado")
    estados = cursor.fetchall()

    cursor.execute("SELECT id, id_estado, nome FROM cidade")
    cidades = cursor.fetchall()

    print(f"> Encontrados {len(estados)} estados e {len(cidades)} cidades no banco")
except mysql.connector.Error as err:
    print(f"[!] Erro ao buscar estados/cidades: {err}")
    cursor.close()
    conn.close()
    exit(1)

# Criar bairros para as cidades
bairros_inseridos = []
bairro_counter = 1
try:
    for cidade in cidades:
        num_bairros = random.randint(8, 25)
        bairros_unicos = set()
        while len(bairros_unicos) < num_bairros:
            bairros_unicos.add(gerar_nome_bairro())
        
        for nome_bairro in bairros_unicos:
            bairros_inseridos.append((
                cidade[0],  # id_cidade
                nome_bairro,
                geometria_bairro_simples(bairro_counter, cidade[0])
            ))
            bairro_counter += 1

    cursor.executemany("INSERT INTO bairro (id_cidade, nome, geometria) VALUES (%s, %s, ST_GeomFromText(%s))", bairros_inseridos)
    conn.commit()
    print(f"> Inseridos {len(bairros_inseridos)} bairros")
except mysql.connector.Error as err:
    print(f"[!] Erro ao inserir bairros: {err}")
    conn.rollback()

# Buscar bairros inseridos
try:
    cursor.execute("SELECT id, id_cidade, nome FROM bairro")
    bairros = cursor.fetchall()
    print(f"> Total de bairros no banco: {len(bairros)}")
except mysql.connector.Error as err:
    print(f"[!] Erro ao buscar bairros: {err}")
    cursor.close()
    conn.close()
    exit(1)

# Inserir tipos de logradouro
try:
    tipos_logradouro = ['Rua', 'Avenida', 'Travessa', 'Alameda', 'Praça', 'Viela', 'Estrada', 'Rodovia']
    for tipo in tipos_logradouro:
        cursor.execute("INSERT IGNORE INTO tipo (descricao) VALUES (%s)", (tipo,))
    conn.commit()

    cursor.execute("SELECT id, descricao FROM tipo")
    tipos = cursor.fetchall()
except mysql.connector.Error as err:
    print(f"[!] Erro ao inserir tipos de logradouro: {err}")
    conn.rollback()

# Inserir logradouros
logradouros_inseridos = []
try:
    nomes_logradouro = []
    for i in range(300):
        if random.random() > 0.5:
            nome = f"{fake.first_name()} {fake.last_name()}"
        else:
            nome = fake.street_name()
        nomes_logradouro.append(nome)

    logradouro_counter = 1
    for nome in nomes_logradouro:
        logradouros_inseridos.append((
            random.choice(tipos)[0],
            nome,
            geometria_logradouro_simples(logradouro_counter)
        ))
        logradouro_counter += 1

    cursor.executemany("INSERT INTO logradouro (id_tipo, nome, geometria) VALUES (%s, %s, ST_GeomFromText(%s))", logradouros_inseridos)
    conn.commit()
    print(f"> Inseridos {len(logradouros_inseridos)} logradouros")
except mysql.connector.Error as err:
    print(f"[!] Erro ao inserir logradouros: {err}")
    conn.rollback()

# Buscar logradouros inseridos
try:
    cursor.execute("SELECT id, id_tipo, nome FROM logradouro")
    logradouros = cursor.fetchall()
except mysql.connector.Error as err:
    print(f"[!] Erro ao buscar logradouros: {err}")
    cursor.close()
    conn.close()
    exit(1)

# Associar bairros com logradouros
bairro_logradouro_associacoes = []
bairros_por_cidade = {}

try:
    for bairro in bairros:
        cidade_id = bairro[1]
        if cidade_id not in bairros_por_cidade:
            bairros_por_cidade[cidade_id] = []
        bairros_por_cidade[cidade_id].append(bairro[0])

    for logradouro_id in [log[0] for log in logradouros]:
        num_cidades = random.randint(1, 3)
        cidades_selecionadas = random.sample(list(bairros_por_cidade.keys()), 
                                            min(num_cidades, len(bairros_por_cidade)))
        
        for cidade_id in cidades_selecionadas:
            bairros_cidade = bairros_por_cidade[cidade_id]
            num_associacoes = random.randint(1, 4)  # Mais associações
            bairros_associados = random.sample(bairros_cidade, 
                                             min(num_associacoes, len(bairros_cidade)))
            
            for bairro_id in bairros_associados:
                bairro_logradouro_associacoes.append((bairro_id, logradouro_id))

    cursor.executemany("INSERT INTO bairro_logradouro (id_bairro, id_logradouro) VALUES (%s, %s)", bairro_logradouro_associacoes)
    conn.commit()
    print(f"> Criadas {len(bairro_logradouro_associacoes)} associações bairro-logradouro")
except mysql.connector.Error as err:
    print(f"[!] Erro ao associar bairros com logradouros: {err}")
    conn.rollback()

# Inserir número aleatório de endereços por bairro
enderecos_inseridos = []
endereco_counter = 0
distribuicao_bairros = []

try:
    print(f"\n> Gerando imóveis por bairro (entre {MIN_IMOVEIS_POR_BAIRRO} e {MAX_IMOVEIS_POR_BAIRRO})...")
    
    for bairro in bairros:
        bairro_id = bairro[0]
        bairro_nome = bairro[2]
        cidade_id = bairro[1]
        
        # Determinar número aleatório de imóveis para este bairro
        imoveis_no_bairro = determinar_imoveis_por_bairro(bairro_id, len(bairros), cidade_id)
        distribuicao_bairros.append((bairro_nome, imoveis_no_bairro))
        
        # Buscar logradouros associados a este bairro
        cursor.execute("SELECT id_logradouro FROM bairro_logradouro WHERE id_bairro = %s", (bairro_id,))
        logradouros_bairro = [row[0] for row in cursor.fetchall()]
        if not logradouros_bairro:
            logradouros_bairro = [random.choice(logradouros)[0]]
        
        print(f"  > Bairro '{bairro_nome}': {imoveis_no_bairro} imóveis")
        
        for i in range(imoveis_no_bairro):
            logradouro_id = random.choice(logradouros_bairro)
            
            enderecos_inseridos.append((
                bairro_id,
                logradouro_id,
                fake.postcode(),
                gerar_numero_endereco(),
                geometria_endereco_simples(endereco_counter, bairro_id),
                gerar_complemento()
            ))
            endereco_counter += 1
            
            # Inserir em lotes
            if len(enderecos_inseridos) >= 1000:
                cursor.executemany("""
                    INSERT INTO endereco 
                    (id_bairro, logradouro_id, cep, numero, geometria, complemento) 
                    VALUES (%s, %s, %s, %s, ST_GeomFromText(%s), %s)
                """, enderecos_inseridos)
                conn.commit()
                print(f"    > Inseridos {len(enderecos_inseridos)} endereços (lote)")
                enderecos_inseridos = []
    
    # Inserir endereços restantes
    if enderecos_inseridos:
        cursor.executemany("""
            INSERT INTO endereco 
            (id_bairro, logradouro_id, cep, numero, geometria, complemento) 
            VALUES (%s, %s, %s, %s, ST_GeomFromText(%s), %s)
        """, enderecos_inseridos)
        conn.commit()
    
    total_enderecos = endereco_counter
    print(f"> Inseridos {total_enderecos} endereços no total")

except mysql.connector.Error as err:
    print(f"[!] Erro ao inserir endereços: {err}")
    conn.rollback()

# Buscar endereços inseridos
try:
    cursor.execute("SELECT id, id_bairro FROM endereco")
    enderecos = cursor.fetchall()
except mysql.connector.Error as err:
    print(f"[!] Erro ao buscar endereços: {err}")
    cursor.close()
    conn.close()
    exit(1)

# Inserir imóveis
imoveis_inseridos = []
try:
    print(f"\n> Inserindo imóveis...")
    
    for endereco_id, bairro_id in enderecos:
        cursor.execute("SELECT id_cidade FROM bairro WHERE id = %s", (bairro_id,))
        resultado = cursor.fetchone()
        cidade_id = resultado[0] if resultado else 1
        
        cursor.execute("SELECT id_estado FROM cidade WHERE id = %s", (cidade_id,))
        resultado_estado = cursor.fetchone()
        estado_id = resultado_estado[0] if resultado_estado else 1
        
        if estado_id in [25, 33]:  # SP e RJ
            valor_venal = round(random.uniform(300000, 8000000), 2)
        elif estado_id in [35, 53, 31]:  # PR, DF, MG
            valor_venal = round(random.uniform(200000, 3000000), 2)
        else:
            valor_venal = round(random.uniform(50000, 1500000), 2)
        
        imoveis_inseridos.append((endereco_id, valor_venal))
        
        # Inserir em lotes
        if len(imoveis_inseridos) >= 1000:
            cursor.executemany("INSERT INTO imovel (id_endereco, valor_venal) VALUES (%s, %s)", imoveis_inseridos)
            conn.commit()
            print(f"  > Inseridos {len(imoveis_inseridos)} imóveis (lote)")
            imoveis_inseridos = []
    
    # Inserir imóveis restantes
    if imoveis_inseridos:
        cursor.executemany("INSERT INTO imovel (id_endereco, valor_venal) VALUES (%s, %s)", imoveis_inseridos)
        conn.commit()
    
    print(f"> Inseridos {len(enderecos)} imóveis")

except mysql.connector.Error as err:
    print(f"[!] Erro ao inserir imóveis: {err}")
    conn.rollback()

# Buscar imóveis inseridos
try:
    cursor.execute("SELECT id, valor_venal FROM imovel")
    imoveis = cursor.fetchall()
except mysql.connector.Error as err:
    print(f"[!] Erro ao buscar imóveis: {err}")
    cursor.close()
    conn.close()
    exit(1)

# Inserir IPTUs
iptus_inseridos = []
try:
    print(f"\n> Inserindo IPTUs...")
    
    for id_imovel, valor_venal in imoveis:
        aliquota = random.uniform(0.001, 0.005)
        valor_iptu = round(valor_venal * aliquota, 2)
        
        status_pagamento = random.choices([0, 1], weights=[0.25, 0.75])[0]
        
        ano_corrente = datetime.now().year
        meses_vencimento = [2, 3, 4, 5, 6]
        data_vencimento = datetime(ano_corrente, random.choice(meses_vencimento), 
                                  random.randint(1, 28))
        
        if status_pagamento == 1:
            dias_atraso = random.randint(0, 60)
            data_pagamento = data_vencimento + timedelta(days=dias_atraso)
            hora_pagamento = f"{random.randint(8, 17):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
        else:
            data_pagamento = None
            hora_pagamento = None

        iptus_inseridos.append((
            id_imovel,
            valor_iptu,
            status_pagamento,
            data_pagamento,
            data_vencimento.date(),
            hora_pagamento
        ))
        
        # Inserir em lotes
        if len(iptus_inseridos) >= 1000:
            cursor.executemany("""
                INSERT INTO iptu 
                (id_imovel, valor, status_pagamento, data_pagamento, data_vencimento, hora_pagamento) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, iptus_inseridos)
            conn.commit()
            print(f"  > Inseridos {len(iptus_inseridos)} IPTUs (lote)")
            iptus_inseridos = []
    
    # Inserir IPTUs restantes
    if iptus_inseridos:
        cursor.executemany("""
            INSERT INTO iptu 
            (id_imovel, valor, status_pagamento, data_pagamento, data_vencimento, hora_pagamento) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, iptus_inseridos)
        conn.commit()
    
    print(f"> Inseridos {len(imoveis)} IPTUs")

except mysql.connector.Error as err:
    print(f"[!] Erro ao inserir IPTUs: {err}")
    conn.rollback()

print("\n" + "="*50)
print("\tDADOS INSERIDOS COM SUCESSO!")
print("="*50)

# Estatísticas
try:
    cursor.execute("SELECT COUNT(*) FROM bairro")
    total_bairros = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM imovel")
    total_imoveis = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM iptu WHERE status_pagamento = 1")
    iptus_pagos = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(valor) FROM iptu")
    media_iptu = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(valor_venal), MAX(valor_venal), AVG(valor_venal) FROM imovel")
    min_valor, max_valor, avg_valor = cursor.fetchone()
    
    # Estatísticas de distribuição por bairro
    cursor.execute("""
        SELECT b.nome, COUNT(i.id) as total_imoveis
        FROM bairro b
        LEFT JOIN endereco e ON b.id = e.id_bairro
        LEFT JOIN imovel i ON e.id = i.id_endereco
        GROUP BY b.id, b.nome
        ORDER BY total_imoveis DESC
    """)
    
    distribuicao_real = cursor.fetchall()
    
    # Calcular estatísticas da distribuição
    imoveis_por_bairro = [item[1] for item in distribuicao_real]
    media_imoveis = sum(imoveis_por_bairro) / len(imoveis_por_bairro)
    min_imoveis = min(imoveis_por_bairro)
    max_imoveis = max(imoveis_por_bairro)

    print(f"> Total de bairros: {total_bairros}")
    print(f"> Total de imóveis: {total_imoveis}")
    print(f"> Média de imóveis por bairro: {media_imoveis:.1f}")
    print(f"> Menor bairro: {min_imoveis} imóveis")
    print(f"> Maior bairro: {max_imoveis} imóveis")
    print(f"> IPTUs pagos: {iptus_pagos} ({iptus_pagos/total_imoveis*100:.1f}%)")
    print(f"> Valor médio do IPTU: R$ {media_iptu:.2f}")
    print(f"> Valor venal mínimo: R$ {min_valor:,.2f}")
    print(f"> Valor venal máximo: R$ {max_valor:,.2f}")
    print(f"> Valor venal médio: R$ {avg_valor:,.2f}")
    
except mysql.connector.Error as err:
    print(f"[!] Erro ao calcular estatísticas: {err}")

cursor.close()
conn.close()