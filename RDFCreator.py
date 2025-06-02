import mysql.connector # type: ignore
from mysql.connector import Error # type: ignore
from rdflib import Graph, Literal, RDF, URIRef # type: ignore
from rdflib.namespace import RDFS, OWL # type: ignore
import os

# Exibir diretório de trabalho atual
print("Diretório de trabalho atual:", os.getcwd())

# Tentativa de conexão com o banco
try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database ="`dbviveiro" 
    )
    cursor = connection.cursor()
    print("Conexão com o banco de dados estabelecida com sucesso.")
except Error as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    exit(1)

# Criar o grafo RDF
g = Graph()
namespace = "http://example.org/viveiro#"
g.bind("viveiro", namespace)

# Definir classes e propriedades
Especie_Planta = URIRef(namespace + "Especie_Planta")
Muda = URIRef(namespace + "Muda")
Cliente = URIRef(namespace + "Cliente")
Venda = URIRef(namespace + "Venda")
Estoque = URIRef(namespace + "Estoque")
Categoria_Planta = URIRef(namespace + "Categoria_Planta")
pertence_a = URIRef(namespace + "pertence_a")
comprada_por = URIRef(namespace + "comprada_por")
contem = URIRef(namespace + "contem")
disponivel_em = URIRef(namespace + "disponivel_em")
classificada_como = URIRef(namespace + "classificada_como")

# Adicionar classes ao RDF
g.add((Especie_Planta, RDF.type, OWL.Class))
g.add((Muda, RDF.type, OWL.Class))
g.add((Cliente, RDF.type, OWL.Class))
g.add((Venda, RDF.type, OWL.Class))
g.add((Estoque, RDF.type, OWL.Class))
g.add((Categoria_Planta, RDF.type, OWL.Class))

# Consultar e adicionar dados
try:
    # Espécies de Plantas
    cursor.execute("SELECT * FROM Especie_Planta")
    for row in cursor.fetchall():
        especie_uri = URIRef(namespace + "especie_" + str(row[0]))
        g.add((especie_uri, RDF.type, Especie_Planta))
        g.add((especie_uri, RDFS.label, Literal(row[1])))
        g.add((especie_uri, URIRef(namespace + "preco_unitario"), Literal(row[2])))

    # Mudas
    cursor.execute("SELECT * FROM Muda")
    for row in cursor.fetchall():
        muda_uri = URIRef(namespace + "muda_" + str(row[0]))
        especie_uri = URIRef(namespace + "especie_" + str(row[1]))
        g.add((muda_uri, RDF.type, Muda))
        g.add((muda_uri, pertence_a, especie_uri))
        g.add((muda_uri, URIRef(namespace + "data_producao"), Literal(row[2])))

    # Clientes
    cursor.execute("SELECT * FROM Cliente")
    for row in cursor.fetchall():
        cliente_uri = URIRef(namespace + "cliente_" + str(row[0]))
        g.add((cliente_uri, RDF.type, Cliente))
        g.add((cliente_uri, RDFS.label, Literal(row[1])))
        g.add((cliente_uri, URIRef(namespace + "telefone"), Literal(row[2])))

    # Vendas
    cursor.execute("SELECT * FROM Venda")
    for row in cursor.fetchall():
        venda_uri = URIRef(namespace + "venda_" + str(row[0]))
        cliente_uri = URIRef(namespace + "cliente_" + str(row[1]))
        g.add((venda_uri, RDF.type, Venda))
        g.add((venda_uri, comprada_por, cliente_uri))
        g.add((venda_uri, URIRef(namespace + "data_venda"), Literal(row[2])))
        g.add((venda_uri, URIRef(namespace + "valor_total"), Literal(row[3])))

    # Relacionamento Venda-Muda
    cursor.execute("SELECT * FROM Venda_Muda")
    for row in cursor.fetchall():
        venda_uri = URIRef(namespace + "venda_" + str(row[0]))
        muda_uri = URIRef(namespace + "muda_" + str(row[1]))
        g.add((venda_uri, contem, muda_uri))

    # Estoque
    cursor.execute("SELECT * FROM Estoque")
    for row in cursor.fetchall():
        estoque_uri = URIRef(namespace + "estoque_" + str(row[0]))
        especie_uri = URIRef(namespace + "especie_" + str(row[1]))
        g.add((estoque_uri, RDF.type, Estoque))
        g.add((especie_uri, disponivel_em, estoque_uri))
        g.add((estoque_uri, URIRef(namespace + "quantidade"), Literal(row[2])))

    # Categorias
    cursor.execute("SELECT * FROM Categoria_Planta")
    for row in cursor.fetchall():
        categoria_uri = URIRef(namespace + "categoria_" + str(row[0]))
        g.add((categoria_uri, RDF.type, Categoria_Planta))
        g.add((categoria_uri, RDFS.label, Literal(row[1])))

    # Relacionamento Especie-Categoria
    cursor.execute("SELECT * FROM Especie_Categoria")
    for row in cursor.fetchall():
        especie_uri = URIRef(namespace + "especie_" + str(row[0]))
        categoria_uri = URIRef(namespace + "categoria_" + str(row[1]))
        g.add((especie_uri, classificada_como, categoria_uri))

except Error as e:
    print(f"Erro ao executar consultas SQL: {e}")
    cursor.close()
    connection.close()
    exit(1)

# Imprimir conteúdo do grafo para verificação
print("Conteúdo do grafo RDF:")
for triple in g:
    print(triple)

# Salvar o RDF
try:
    output_file = "ontologiaViveiro.rdf"
    g.serialize(output_file, format="xml")
    print(f"Arquivo RDF salvo com sucesso em: {os.path.abspath(output_file)}")
except Exception as e:
    print(f"Erro ao salvar o arquivo RDF: {e}")

#  Fechar conexão
cursor.close()
connection.close()