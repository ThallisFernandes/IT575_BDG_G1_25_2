import mysql.connector

# Conectar ao banco de dados
conn = mysql.connector.connect(
    host='localhost',
    user='*****',
    password='*****',
    database='cadastro_imobiliario_it575'
)
cursor = conn.cursor()

# Mapeamento dos estados (ID -> nome correto)
estados_por_id = {
    1: 'Acre',
    2: 'Alagoas',
    3: 'Amapá',
    4: 'Amazonas',
    5: 'Bahia',
    6: 'Ceará',
    7: 'Distrito Federal',
    8: 'Espirito Santo',
    9: 'Goiás',
    10: 'Maranhão',
    11: 'Mato Grosso do Sul',
    12: 'Mato Grosso',
    13: 'Minas Gerais',
    14: 'Pará',
    15: 'Paraíba',
    16: 'Paraná',
    17: 'Pernambuco',
    18: 'Piauí',
    19: 'Rio de Janeiro',
    20: 'Rio Grande do Norte',
    21: 'Rio Grande do Sul',
    22: 'Rondônia',
    23: 'Roraima',
    24: 'Santa Catarina',
    25: 'São Paulo',
    26: 'Sergipe',
    27: 'Tocantins'
}

print(">> Iniciando atualização dos nomes dos estados por ID...")

# Atualizar cada estado por ID
for id_estado, nome_correto in estados_por_id.items():
    try:
        cursor.execute("""
            UPDATE estado 
            SET nome = %s 
            WHERE id = %s
        """, (nome_correto, id_estado))
        
        if cursor.rowcount > 0:
            print(f">>> Atualizado ID {id_estado}: {nome_correto}")
        else:
            print(f"[!] Estado com ID {id_estado} não encontrado")
            
    except Exception as e:
        print(f"[!] Erro ao atualizar ID {id_estado}: {e}")

# Confirmar as alterações
conn.commit()

# Verificar os resultados
cursor.execute("SELECT id, sigla, nome FROM estado ORDER BY id")
resultados = cursor.fetchall()

print(f"\n>>>> Atualização concluída!")
print("\n>> Estados na tabela após atualização:")
for id_estado, sigla, nome in resultados:
    print(f"  {id_estado};{sigla};{nome}")

cursor.close()

conn.close()
