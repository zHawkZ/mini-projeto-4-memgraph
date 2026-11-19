from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("", "")


def executar_consulta(session, titulo, query):
    print(f"\n--- {titulo} ---")
    resultados = list(session.run(query))
    if not resultados:
        print("  Nenhum resultado encontrado.")
        return
    for registro in resultados:
        linha = " | ".join(f"{k}: {v}" for k, v in registro.items())
        print(f"  {linha}")


def main():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:

        # 1. Equivalentes às buscas por triplas e inferências OWL do MP3
        executar_consulta(
            session,
            "Dados da EspadaDiamante (no MP3 usava g.triples)",
            """
            MATCH (e:Item {id: 'EspadaDiamante'})
            OPTIONAL MATCH (e)-[r]->(destino)
            RETURN labels(e) AS rotulos, properties(e) AS propriedades,
                   collect(type(r) + ' -> ' + destino.id) AS relacoes_saida
            """
        )

        executar_consulta(
            session,
            "Instâncias de Arma (equivalente a RDF.type mc:Arma)",
            """
            MATCH (a:Arma)
            RETURN a.id AS id, a.nome AS nome
            """
        )

        executar_consulta(
            session,
            "Relação inversa eMaterialPara (invertendo a seta de REQUER_MATERIAL)",
            """
            MATCH (material:Material)<-[:REQUER_MATERIAL]-(item:Item)
            RETURN material.id AS material, item.id AS cria_item
            """
        )

        executar_consulta(
            session,
            "Itens de raridade Épico",
            """
            MATCH (i:Item {raridade: 'Épico'})
            RETURN i.id AS id, i.nome AS nome
            """
        )

        executar_consulta(
            session,
            "Itens com tamanhoPilha = 64",
            """
            MATCH (i:Item {tamanhoPilha: 64})
            RETURN i.id AS id, i.nome AS nome
            """
        )

        executar_consulta(
            session,
            "Transitividade em melhoraPara (substituindo owl:TransitiveProperty)",
            """
            MATCH (origem:Equipamento {id: 'EspadaFerro'})-[:MELHORA_PARA*1..]->(destino:Equipamento)
            RETURN origem.id AS origem, destino.id AS melhora_para
            """
        )

        executar_consulta(
            session,
            "Simetria entre Elitro e PeitoralFerro (substituindo owl:SymmetricProperty)",
            """
            OPTIONAL MATCH (e1:Equipamento {id: 'Elitro'})-[:SUBSTITUI_NO_MESMO_ESPACO]-(e2:Equipamento {id: 'PeitoralFerro'})
            RETURN count(e1) > 0 AS substitui
            """
        )

        # 2. Equivalentes às consultas SPARQL do MP3
        executar_consulta(
            session,
            "Equipamentos com durabilidade > 500 (SPARQL FILTER)",
            """
            MATCH (e:Equipamento)
            WHERE e.durabilidade > 500
            RETURN e.nome AS item, e.durabilidade AS durabilidade
            """
        )

        executar_consulta(
            session,
            "Média de durabilidade por subclasse (SPARQL GROUP BY + AVG)",
            """
            UNWIND ['Arma', 'Ferramenta', 'Armadura'] AS subclasse
            MATCH (e:Equipamento)
            WHERE subclasse IN labels(e) AND e.durabilidade IS NOT NULL
            RETURN subclasse AS classe, count(DISTINCT e) AS total,
                   round(avg(e.durabilidade) * 10) / 10.0 AS mediaDurabilidade
            ORDER BY mediaDurabilidade DESC
            """
        )

        executar_consulta(
            session,
            "Armas, dano e material de reparo",
            """
            MATCH (arma:Arma)-[:TEM_MATERIAL_REPARO]->(material:Material)
            RETURN arma.nome AS arma, arma.danoAtaque AS dano, material.nome AS materialReparo
            """
        )

        executar_consulta(
            session,
            "Existe item não-renovável Épico? (equivalente ao SPARQL ASK)",
            """
            OPTIONAL MATCH (i:Item {raridade: 'Épico', eRenovavel: false})
            RETURN count(i) > 0 AS existeItemEpicoNaoRenovavel
            """
        )

        executar_consulta(
            session,
            "Projeção de triplas de reparo (equivalente ao SPARQL CONSTRUCT)",
            """
            MATCH (item:Equipamento)-[:TEM_MATERIAL_REPARO]->(material:Material)
            RETURN item.id AS sujeito, 'podeSerReparadoCom' AS predicado, material.id AS objeto
            """
        )

        executar_consulta(
            session,
            "Monstros, drops e poções (equivalente ao SPARQL OPTIONAL)",
            """
            MATCH (drop:DropMonstro)-[:DROPADO_POR]->(monstro:Monstro)
            OPTIONAL MATCH (pocao:Pocao)-[:PREPARADO_DE]->(drop)
            RETURN monstro.nome AS monstro, drop.nome AS drop, coalesce(pocao.nome, 'Nenhuma') AS pocao
            ORDER BY monstro
            """
        )

        # 3. Travessias multi-salto no grafo
        executar_consulta(
            session,
            "Travessia 1: Monstro -> Drop <- Poção",
            """
            MATCH (m:Monstro)-[:DROPA]->(drop:DropMonstro)<-[:PREPARADO_DE]-(p:Pocao)
            RETURN m.nome AS monstro, drop.nome AS ingrediente, p.nome AS pocaoFinal
            """
        )

        executar_consulta(
            session,
            "Travessia 2: Monstro -> Drop <- Item fabricado",
            """
            MATCH (m:Monstro)-[:DROPA]->(drop:DropMonstro)<-[:REQUER_MATERIAL]-(item:Item)
            RETURN m.nome AS monstroOrigem, drop.nome AS materialDropado, item.nome AS itemFabricado
            """
        )

        executar_consulta(
            session,
            "Travessia 3: Evolução completa Tier 1 -> Tier 2 -> Tier 3",
            """
            MATCH (base:Equipamento)-[:MELHORA_PARA]->(intermediario:Equipamento)-[:MELHORA_PARA]->(final:Equipamento)
            RETURN base.nome AS tier1, intermediario.nome AS tier2, final.nome AS tier3
            """
        )

        executar_consulta(
            session,
            "Travessia 4: Material do equipamento que substitui o Elitro",
            """
            MATCH (:Equipamento {id: 'Elitro'})-[:SUBSTITUI_NO_MESMO_ESPACO]->(equip:Equipamento)-[:REQUER_MATERIAL]->(mat:Material)
            RETURN equip.nome AS equipamentoSubstituido, mat.nome AS materialNecessario
            """
        )

        # 4. Updates (equivalentes ao SPARQL INSERT/DELETE)
        print("\n--- Executando updates no grafo ---")

        session.run("""
            MERGE (m:Arma:Equipamento:Item {id: 'MacaArma'})
            SET m.nome = 'Maçã de Combate (Mace)',
                m.durabilidade = 500,
                m.danoAtaque = 7.0,
                m.tamanhoPilha = 1,
                m.raridade = 'Épico',
                m.eRenovavel = false
        """)
        print("  MacaArma inserida (MERGE + SET).")

        session.run("""
            MATCH (e:Item {id: 'Elitro'})
            REMOVE e.eRenovavel
        """)
        print("  Propriedade eRenovavel removida do Elitro (REMOVE).")

        session.run("""
            MATCH (p:Item {id: 'PicaretaFerro'})
            SET p.durabilidade = 300
        """)
        print("  Durabilidade da PicaretaFerro atualizada para 300 (SET).")

        executar_consulta(
            session,
            "Estado dos nós após os updates",
            """
            MATCH (n:Item)
            WHERE n.id IN ['MacaArma', 'Elitro', 'PicaretaFerro']
            RETURN n.id AS id, labels(n) AS rotulos, n.nome AS nome,
                   n.durabilidade AS durabilidade, n.eRenovavel AS eRenovavel
            """
        )

        executar_consulta(
            session,
            "Itens Épico não-renováveis após os updates",
            """
            MATCH (i:Item {raridade: 'Épico', eRenovavel: false})
            RETURN i.nome AS item
            ORDER BY item
            """
        )

    driver.close()


if __name__ == "__main__":
    main()
