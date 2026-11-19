from neo4j import GraphDatabase


URI = "bolt://localhost:7687"
AUTH = ("", "")


def rodar(session, desc, query):
    print(f"\n> {desc}")
    res = list(session.run(query))
    if not res:
        print("  sem resultados")
        return
    for r in res:
        print(" ", " | ".join(f"{k}: {v}" for k, v in r.items()))


def main():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:

        # Buscas equivalentes ao g.triples() do MP3
        rodar(session, "Propriedades e relações da EspadaDiamante", """
            MATCH (e:Item {id: 'EspadaDiamante'})
            OPTIONAL MATCH (e)-[r]->(destino)
            RETURN labels(e) AS rotulos, properties(e) AS props,
                   collect(type(r) + ' -> ' + destino.id) AS saidas
        """)

        rodar(session, "Instâncias de Arma", """
            MATCH (a:Arma)
            RETURN a.id AS id, a.nome AS nome
        """)

        rodar(session, "eMaterialPara (inverso de REQUER_MATERIAL)", """
            MATCH (material:Material)<-[:REQUER_MATERIAL]-(item:Item)
            RETURN material.id AS material, item.id AS item
        """)

        rodar(session, "Itens de raridade Épico", """
            MATCH (i:Item {raridade: 'Épico'})
            RETURN i.id AS id, i.nome AS nome
        """)

        rodar(session, "Itens com tamanhoPilha = 64", """
            MATCH (i:Item {tamanhoPilha: 64})
            RETURN i.id AS id, i.nome AS nome
        """)

        rodar(session, "melhoraPara a partir de EspadaFerro (transitivo)", """
            MATCH (origem:Equipamento {id: 'EspadaFerro'})-[:MELHORA_PARA*1..]->(destino:Equipamento)
            RETURN origem.id AS origem, destino.id AS destino
        """)

        rodar(session, "Elitro substitui PeitoralFerro? (simétrico)", """
            OPTIONAL MATCH (e1:Equipamento {id: 'Elitro'})-[:SUBSTITUI_NO_MESMO_ESPACO]-(e2:Equipamento {id: 'PeitoralFerro'})
            RETURN count(e1) > 0 AS substitui
        """)

        # Consultas SPARQL do MP3 convertidas para Cypher
        rodar(session, "Equipamentos com durabilidade > 500", """
            MATCH (e:Equipamento)
            WHERE e.durabilidade > 500
            RETURN e.nome AS item, e.durabilidade AS durabilidade
        """)

        rodar(session, "Média de durabilidade por subclasse", """
            UNWIND ['Arma', 'Ferramenta', 'Armadura'] AS subclasse
            MATCH (e:Equipamento)
            WHERE subclasse IN labels(e) AND e.durabilidade IS NOT NULL
            RETURN subclasse AS classe, count(DISTINCT e) AS total,
                   round(avg(e.durabilidade) * 10) / 10.0 AS media
            ORDER BY media DESC
        """)

        rodar(session, "Armas, dano e material de reparo", """
            MATCH (arma:Arma)-[:TEM_MATERIAL_REPARO]->(material:Material)
            RETURN arma.nome AS arma, arma.danoAtaque AS dano, material.nome AS reparo
        """)

        rodar(session, "Existe item Épico não-renovável? (ASK)", """
            OPTIONAL MATCH (i:Item {raridade: 'Épico', eRenovavel: false})
            RETURN count(i) > 0 AS existe
        """)

        rodar(session, "Triplas de reparo (CONSTRUCT)", """
            MATCH (item:Equipamento)-[:TEM_MATERIAL_REPARO]->(material:Material)
            RETURN item.id AS sujeito, 'podeSerReparadoCom' AS predicado, material.id AS objeto
        """)

        rodar(session, "Monstros, drops e poções (OPTIONAL)", """
            MATCH (drop:DropMonstro)-[:DROPADO_POR]->(monstro:Monstro)
            OPTIONAL MATCH (pocao:Pocao)-[:PREPARADO_DE]->(drop)
            RETURN monstro.nome AS monstro, drop.nome AS drop, coalesce(pocao.nome, 'Nenhuma') AS pocao
            ORDER BY monstro
        """)

        # Travessias no grafo
        rodar(session, "Travessia 1: Monstro -> Drop <- Poção", """
            MATCH (m:Monstro)-[:DROPA]->(drop:DropMonstro)<-[:PREPARADO_DE]-(p:Pocao)
            RETURN m.nome AS monstro, drop.nome AS drop, p.nome AS pocao
        """)

        rodar(session, "Travessia 2: Monstro -> Drop <- Item fabricado", """
            MATCH (m:Monstro)-[:DROPA]->(drop:DropMonstro)<-[:REQUER_MATERIAL]-(item:Item)
            RETURN m.nome AS monstro, drop.nome AS drop, item.nome AS item
        """)

        rodar(session, "Travessia 3: Evolução Tier 1 -> Tier 2 -> Tier 3", """
            MATCH (base:Equipamento)-[:MELHORA_PARA]->(inter:Equipamento)-[:MELHORA_PARA]->(final:Equipamento)
            RETURN base.nome AS tier1, inter.nome AS tier2, final.nome AS tier3
        """)

        rodar(session, "Travessia 4: Material do item que substitui o Elitro", """
            MATCH (:Equipamento {id: 'Elitro'})-[:SUBSTITUI_NO_MESMO_ESPACO]->(equip:Equipamento)-[:REQUER_MATERIAL]->(mat:Material)
            RETURN equip.nome AS equipamento, mat.nome AS material
        """)

        # Updates
        print("\n> Aplicando updates...")

        session.run("""
            MERGE (m:Arma:Equipamento:Item {id: 'MacaArma'})
            SET m.nome = 'Maçã de Combate (Mace)',
                m.durabilidade = 500,
                m.danoAtaque = 7.0,
                m.tamanhoPilha = 1,
                m.raridade = 'Épico',
                m.eRenovavel = false
        """)

        session.run("""
            MATCH (e:Item {id: 'Elitro'})
            REMOVE e.eRenovavel
        """)

        session.run("""
            MATCH (p:Item {id: 'PicaretaFerro'})
            SET p.durabilidade = 300
        """)

        rodar(session, "Nós modificados após updates", """
            MATCH (n:Item)
            WHERE n.id IN ['MacaArma', 'Elitro', 'PicaretaFerro']
            RETURN n.id AS id, labels(n) AS rotulos, n.nome AS nome,
                   n.durabilidade AS durabilidade, n.eRenovavel AS eRenovavel
        """)

        rodar(session, "Itens Épico não-renováveis pós-update", """
            MATCH (i:Item {raridade: 'Épico', eRenovavel: false})
            RETURN i.nome AS item
            ORDER BY item
        """)

    driver.close()


if __name__ == "__main__":
    main()
