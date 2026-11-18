from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("", "")


def executar_consulta(session, numero, titulo, query):
    print(f"\n{'=' * 70}")
    print(f"[{numero}] {titulo}")
    print(f"{'=' * 70}")
    resultados = list(session.run(query))
    if not resultados:
        print("  (Nenhum resultado retornado)")
        return
    for registro in resultados:
        linha = " | ".join(f"{k}: {v}" for k, v in registro.items())
        print(f"  - {linha}")


def main():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:

        # =====================================================================
        # PARTE 1: EQUIVALENTES ÀS CONSULTAS g.triples() DO MP3
        # =====================================================================
        executar_consulta(
            session, "MP3 - P1.1",
            "Propriedades e relacionamentos do sujeito fixo 'EspadaDiamante'",
            """
            MATCH (e:Item {id: 'EspadaDiamante'})
            OPTIONAL MATCH (e)-[r]->(destino)
            RETURN labels(e) AS rotulos, properties(e) AS propriedades,
                   collect(type(r) + ' -> ' + destino.id) AS relacoes_saida
            """
        )

        executar_consulta(
            session, "MP3 - P1.2",
            "Instâncias da classe 'Arma'",
            """
            MATCH (a:Arma)
            RETURN a.id AS id, a.nome AS nome
            """
        )

        executar_consulta(
            session, "MP3 - P1.3",
            "Relação Inversa 'eMaterialPara' (navegação reversa em REQUER_MATERIAL)",
            """
            MATCH (material:Material)<-[:REQUER_MATERIAL]-(item:Item)
            RETURN material.id AS material, item.id AS cria_item
            """
        )

        executar_consulta(
            session, "MP3 - P1.4",
            "Itens com raridade 'Épico'",
            """
            MATCH (i:Item {raridade: 'Épico'})
            RETURN i.id AS id, i.nome AS nome
            """
        )

        executar_consulta(
            session, "MP3 - P1.5",
            "Itens que empilham até 64 (tamanhoPilha = 64)",
            """
            MATCH (i:Item {tamanhoPilha: 64})
            RETURN i.id AS id, i.nome AS nome
            """
        )

        executar_consulta(
            session, "MP3 - P1.6",
            "Transitividade: 'EspadaFerro melhoraPara ?' (caminho de tamanho 1 ou mais)",
            """
            MATCH (origem:Equipamento {id: 'EspadaFerro'})-[:MELHORA_PARA*1..]->(destino:Equipamento)
            RETURN origem.id AS origem, destino.id AS melhora_para
            """
        )

        executar_consulta(
            session, "MP3 - P1.7",
            "Simetria: Élitro substitui PeitoralFerro?",
            """
            OPTIONAL MATCH (e1:Equipamento {id: 'Elitro'})-[:SUBSTITUI_NO_MESMO_ESPACO]-(e2:Equipamento {id: 'PeitoralFerro'})
            RETURN count(e1) > 0 AS substitui
            """
        )

        # =====================================================================
        # PARTE 2: EQUIVALENTES ÀS CONSULTAS SPARQL DO MP3
        # =====================================================================
        executar_consulta(
            session, "MP3 - SPARQL 1",
            "Equipamentos com durabilidade > 500",
            """
            MATCH (e:Equipamento)
            WHERE e.durabilidade > 500
            RETURN e.nome AS item, e.durabilidade AS durabilidade
            """
        )

        executar_consulta(
            session, "MP3 - SPARQL 2",
            "Durabilidade média por tipo de equipamento (Arma, Ferramenta, Armadura)",
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
            session, "MP3 - SPARQL 3",
            "Armas, dano e material de reparo",
            """
            MATCH (arma:Arma)-[:TEM_MATERIAL_REPARO]->(material:Material)
            RETURN arma.nome AS arma, arma.danoAtaque AS dano, material.nome AS materialReparo
            """
        )

        executar_consulta(
            session, "MP3 - SPARQL 4",
            "Existe item não-renovável Épico?",
            """
            OPTIONAL MATCH (i:Item {raridade: 'Épico', eRenovavel: false})
            RETURN count(i) > 0 AS existeItemEpicoNaoRenovavel
            """
        )

        executar_consulta(
            session, "MP3 - SPARQL 5 (CONSTRUCT)",
            "Projeção de triplas de reparo (equivalente ao CONSTRUCT do MP3)",
            """
            MATCH (item:Equipamento)-[:TEM_MATERIAL_REPARO]->(material:Material)
            RETURN item.id AS sujeito, 'podeSerReparadoCom' AS predicado, material.id AS objeto
            """
        )

        executar_consulta(
            session, "MP3 - SPARQL 6 (q9)",
            "Monstros, drops e poções (com OPTIONAL MATCH)",
            """
            MATCH (drop:DropMonstro)-[:DROPADO_POR]->(monstro:Monstro)
            OPTIONAL MATCH (pocao:Pocao)-[:PREPARADO_DE]->(drop)
            RETURN monstro.nome AS monstro, drop.nome AS drop, coalesce(pocao.nome, 'Nenhuma') AS pocao
            ORDER BY monstro
            """
        )

        # =====================================================================
        # PARTE 3: CONSULTAS COM TRAVESSIA NO GRAFO (2+ RELACIONAMENTOS ENCADEADOS)
        # =====================================================================
        executar_consulta(
            session, "TRAVESSIA 1",
            "Cadeia completa de obtenção de poções (Monstro -[:DROPA]-> Drop <-[:PREPARADO_DE]- Poção)",
            """
            MATCH (m:Monstro)-[:DROPA]->(drop:DropMonstro)<-[:PREPARADO_DE]-(p:Pocao)
            RETURN m.nome AS monstro, drop.nome AS ingrediente, p.nome AS pocaoFinal
            """
        )

        executar_consulta(
            session, "TRAVESSIA 2",
            "Itens fabricados a partir de drops de monstros (Monstro -[:DROPA]-> Drop <-[:REQUER_MATERIAL]- Item)",
            """
            MATCH (m:Monstro)-[:DROPA]->(drop:DropMonstro)<-[:REQUER_MATERIAL]-(item:Item)
            RETURN m.nome AS monstroOrigem, drop.nome AS materialDropado, item.nome AS itemFabricado
            """
        )

        executar_consulta(
            session, "TRAVESSIA 3",
            "Caminho completo de evolução de equipamentos (Tier 1 -> Tier 2 -> Tier 3)",
            """
            MATCH (base:Equipamento)-[:MELHORA_PARA]->(intermediario:Equipamento)-[:MELHORA_PARA]->(final:Equipamento)
            RETURN base.nome AS tier1, intermediario.nome AS tier2, final.nome AS tier3
            """
        )

        executar_consulta(
            session, "TRAVESSIA 4",
            "Materiais necessários para fabricar o equipamento que substitui o Élitro",
            """
            MATCH (:Equipamento {id: 'Elitro'})-[:SUBSTITUI_NO_MESMO_ESPACO]->(equip:Equipamento)-[:REQUER_MATERIAL]->(mat:Material)
            RETURN equip.nome AS equipamentoSubstituido, mat.nome AS materialNecessario
            """
        )

        # =====================================================================
        # PARTE 4: EQUIVALENTES AOS UPDATES DO MP3 E VERIFICAÇÃO DO EFEITO
        # =====================================================================
        print(f"\n{'=' * 70}")
        print("[MP3 - UPDATES] Executando modificações no grafo...")
        print(f"{'=' * 70}")

        # Update 1: Inserir Maçã de Combate (Mace)
        session.run("""
            MERGE (m:Arma:Equipamento:Item {id: 'MacaArma'})
            SET m.nome = 'Maçã de Combate (Mace)',
                m.durabilidade = 500,
                m.danoAtaque = 7.0,
                m.tamanhoPilha = 1,
                m.raridade = 'Épico',
                m.eRenovavel = false
        """)
        print("  -> [UPDATE 1] 'MacaArma' inserida com sucesso!")

        # Update 2: Remover propriedade eRenovavel do Élitro
        session.run("""
            MATCH (e:Item {id: 'Elitro'})
            REMOVE e.eRenovavel
        """)
        print("  -> [UPDATE 2] Propriedade 'eRenovavel' do Élitro removida.")

        # Update 3: Alterar durabilidade da Picareta de Ferro para 300
        session.run("""
            MATCH (p:Item {id: 'PicaretaFerro'})
            SET p.durabilidade = 300
        """)
        print("  -> [UPDATE 3] Durabilidade da 'PicaretaFerro' alterada para 300.")

        # Verificação visível dos efeitos dos Updates na saída
        executar_consulta(
            session, "VERIFICAÇÃO PÓS-UPDATE",
            "Confirmando estado atualizado dos nós afetados no Memgraph",
            """
            MATCH (n:Item)
            WHERE n.id IN ['MacaArma', 'Elitro', 'PicaretaFerro']
            RETURN n.id AS id, labels(n) AS rotulos, n.nome AS nome,
                   n.durabilidade AS durabilidade, n.eRenovavel AS eRenovavel
            """
        )

        executar_consulta(
            session, "MP3 - SPARQL 10 (PÓS-UPDATE)",
            "Itens 'Épico' não-renováveis após os updates (Élitro saiu, Maçã de Combate entrou)",
            """
            MATCH (i:Item {raridade: 'Épico', eRenovavel: false})
            RETURN i.nome AS item
            ORDER BY item
            """
        )

    driver.close()


if __name__ == "__main__":
    main()