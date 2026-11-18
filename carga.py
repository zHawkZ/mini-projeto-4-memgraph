from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("", "")

QUERY_CARGA = """
MATCH (n) DETACH DELETE n;

// =================================================================
// 1. MATERIAIS (MaterialCriacao / DropMonstro -> Material -> Item)
// =================================================================
CREATE (diamante:MaterialCriacao:Material:Item {
    id: "Diamante", nome: "Diamante", tamanhoPilha: 64, raridade: "Incomum", eRenovavel: false
})
CREATE (barraFerro:MaterialCriacao:Material:Item {
    id: "BarraFerro", nome: "Barra de Ferro", tamanhoPilha: 64, raridade: "Comum", eRenovavel: true
})
CREATE (barraOuro:MaterialCriacao:Material:Item {
    id: "BarraOuro", nome: "Barra de Ouro", tamanhoPilha: 64, raridade: "Comum", eRenovavel: true
})
CREATE (barraNetherite:MaterialCriacao:Material:Item {
    id: "BarraNetherite", nome: "Barra de Netherite", tamanhoPilha: 64, raridade: "Raro", eRenovavel: false
})
CREATE (graveto:MaterialCriacao:Material:Item {
    id: "Graveto", nome: "Graveto", tamanhoPilha: 64, raridade: "Comum", eRenovavel: true
})
CREATE (linha:DropMonstro:MaterialCriacao:Material:Item {
    id: "Linha", nome: "Linha", tamanhoPilha: 64, raridade: "Comum", eRenovavel: true
})
CREATE (poBlaze:DropMonstro:MaterialCriacao:Material:Item {
    id: "PoBlaze", nome: "Pó de Blaze", tamanhoPilha: 64, raridade: "Incomum", eRenovavel: true
})
CREATE (perolaFim:DropMonstro:Material:Item {
    id: "PerolaFim", nome: "Pérola do Fim", tamanhoPilha: 16, raridade: "Incomum", eRenovavel: true
})
CREATE (estrelaNether:DropMonstro:Material:Item {
    id: "EstrelaNether", nome: "Estrela do Nether", tamanhoPilha: 64, raridade: "Raro", eRenovavel: true
})
CREATE (lagrimaGhast:DropMonstro:Material:Item {
    id: "LagrimaGhast", nome: "Lágrima de Ghast", tamanhoPilha: 64, raridade: "Incomum", eRenovavel: true
})

// =================================================================
// 2. ARMAS (Arma -> Equipamento -> Item)
// =================================================================
CREATE (espadaFerro:Arma:Equipamento:Item {
    id: "EspadaFerro", nome: "Espada de Ferro", durabilidade: 250,
    danoAtaque: 6.0, tamanhoPilha: 1, raridade: "Comum", eRenovavel: true
})
CREATE (espadaDiamante:Arma:Equipamento:Item {
    id: "EspadaDiamante", nome: "Espada de Diamante", durabilidade: 1561,
    danoAtaque: 7.0, tamanhoPilha: 1, raridade: "Incomum", eRenovavel: false
})
CREATE (espadaNetherite:Arma:Equipamento:Item {
    id: "EspadaNetherite", nome: "Espada de Netherite", durabilidade: 2031,
    danoAtaque: 8.0, tamanhoPilha: 1, raridade: "Raro", eRenovavel: false
})
CREATE (arco:Arma:Equipamento:Item {
    id: "Arco", nome: "Arco", durabilidade: 384,
    danoAtaque: 9.0, tamanhoPilha: 1, raridade: "Comum", eRenovavel: true
})

// =================================================================
// 3. ARMADURAS (Armadura -> Equipamento -> Item)
// =================================================================
CREATE (peitoralFerro:Armadura:Equipamento:Item {
    id: "PeitoralFerro", nome: "Peitoral de Ferro", durabilidade: 240,
    tamanhoPilha: 1, raridade: "Comum", eRenovavel: true
})
CREATE (peitoralDiamante:Armadura:Equipamento:Item {
    id: "PeitoralDiamante", nome: "Peitoral de Diamante", durabilidade: 528,
    tamanhoPilha: 1, raridade: "Incomum", eRenovavel: false
})
CREATE (peitoralNetherite:Armadura:Equipamento:Item {
    id: "PeitoralNetherite", nome: "Peitoral de Netherite", durabilidade: 592,
    tamanhoPilha: 1, raridade: "Raro", eRenovavel: false
})
CREATE (elitro:Armadura:Equipamento:Item {
    id: "Elitro", nome: "Élitro", durabilidade: 432,
    tamanhoPilha: 1, raridade: "Épico", eRenovavel: false
})

// =================================================================
// 4. FERRAMENTAS (Ferramenta -> Equipamento -> Item)
// =================================================================
CREATE (picaretaFerro:Ferramenta:Equipamento:Item {
    id: "PicaretaFerro", nome: "Picareta de Ferro", durabilidade: 250,
    tamanhoPilha: 1, raridade: "Comum", eRenovavel: true
})
CREATE (picaretaDiamante:Ferramenta:Equipamento:Item {
    id: "PicaretaDiamante", nome: "Picareta de Diamante", durabilidade: 1561,
    tamanhoPilha: 1, raridade: "Incomum", eRenovavel: false
})
CREATE (varaPesca:Ferramenta:Equipamento:Item {
    id: "VaraPesca", nome: "Vara de Pesca", durabilidade: 64,
    tamanhoPilha: 1, raridade: "Comum", eRenovavel: true
})

// =================================================================
// 5. COMIDAS (Comida -> Consumivel -> Item)
// =================================================================
CREATE (bifeCozido:Comida:Consumivel:Item {
    id: "BifeCozido", nome: "Bife Cozido", valorNutricional: 8,
    tamanhoPilha: 64, raridade: "Comum", eRenovavel: true
})
CREATE (pao:Comida:Consumivel:Item {
    id: "Pao", nome: "Pão", valorNutricional: 5,
    tamanhoPilha: 64, raridade: "Comum", eRenovavel: true
})
CREATE (macaDourada:Comida:Consumivel:Item {
    id: "MacaDourada", nome: "Maçã Dourada", valorNutricional: 4,
    tamanhoPilha: 64, raridade: "Raro", eRenovavel: true
})
CREATE (macaDouradaEncantada:Comida:Consumivel:Item {
    id: "MacaDouradaEncantada", nome: "Maçã Dourada Encantada", valorNutricional: 4,
    tamanhoPilha: 64, raridade: "Épico", eRenovavel: false
})

// =================================================================
// 6. POÇÕES (Pocao -> Consumivel -> Item)
// =================================================================
CREATE (pocaoForca:Pocao:Consumivel:Item {
    id: "PocaoForca", nome: "Poção de Força",
    tamanhoPilha: 1, raridade: "Comum", eRenovavel: true
})
CREATE (pocaoCura:Pocao:Consumivel:Item {
    id: "PocaoCura", nome: "Poção de Cura",
    tamanhoPilha: 1, raridade: "Comum", eRenovavel: true
})

// =================================================================
// 7. MONSTROS (Monstro -> Entidade -> Item)
// =================================================================
CREATE (blaze:Monstro:Entidade:Item {id: "Blaze", nome: "Blaze"})
CREATE (enderman:Monstro:Entidade:Item {id: "Enderman", nome: "Enderman"})
CREATE (ghast:Monstro:Entidade:Item {id: "Ghast", nome: "Ghast"})
CREATE (aranha:Monstro:Entidade:Item {id: "Aranha", nome: "Aranha"})

// =================================================================
// 8. RELACIONAMENTOS
// =================================================================

// REQUER_MATERIAL (Crafting)
CREATE (espadaFerro)-[:REQUER_MATERIAL]->(barraFerro)
CREATE (espadaFerro)-[:REQUER_MATERIAL]->(graveto)
CREATE (espadaDiamante)-[:REQUER_MATERIAL]->(diamante)
CREATE (espadaDiamante)-[:REQUER_MATERIAL]->(graveto)
CREATE (espadaNetherite)-[:REQUER_MATERIAL]->(barraNetherite)
CREATE (espadaNetherite)-[:REQUER_MATERIAL]->(espadaDiamante)
CREATE (arco)-[:REQUER_MATERIAL]->(graveto)
CREATE (arco)-[:REQUER_MATERIAL]->(linha)

CREATE (peitoralFerro)-[:REQUER_MATERIAL]->(barraFerro)
CREATE (peitoralDiamante)-[:REQUER_MATERIAL]->(diamante)
CREATE (peitoralNetherite)-[:REQUER_MATERIAL]->(barraNetherite)
CREATE (peitoralNetherite)-[:REQUER_MATERIAL]->(peitoralDiamante)

CREATE (picaretaFerro)-[:REQUER_MATERIAL]->(barraFerro)
CREATE (picaretaFerro)-[:REQUER_MATERIAL]->(graveto)
CREATE (picaretaDiamante)-[:REQUER_MATERIAL]->(diamante)
CREATE (picaretaDiamante)-[:REQUER_MATERIAL]->(graveto)
CREATE (varaPesca)-[:REQUER_MATERIAL]->(graveto)
CREATE (varaPesca)-[:REQUER_MATERIAL]->(linha)

CREATE (macaDourada)-[:REQUER_MATERIAL]->(barraOuro)

// TEM_MATERIAL_REPARO
CREATE (espadaFerro)-[:TEM_MATERIAL_REPARO]->(barraFerro)
CREATE (espadaDiamante)-[:TEM_MATERIAL_REPARO]->(diamante)
CREATE (espadaNetherite)-[:TEM_MATERIAL_REPARO]->(barraNetherite)
CREATE (peitoralFerro)-[:TEM_MATERIAL_REPARO]->(barraFerro)
CREATE (peitoralDiamante)-[:TEM_MATERIAL_REPARO]->(diamante)
CREATE (peitoralNetherite)-[:TEM_MATERIAL_REPARO]->(barraNetherite)
CREATE (picaretaFerro)-[:TEM_MATERIAL_REPARO]->(barraFerro)
CREATE (picaretaDiamante)-[:TEM_MATERIAL_REPARO]->(diamante)

// MELHORA_PARA
CREATE (espadaFerro)-[:MELHORA_PARA]->(espadaDiamante)
CREATE (espadaDiamante)-[:MELHORA_PARA]->(espadaNetherite)
CREATE (peitoralFerro)-[:MELHORA_PARA]->(peitoralDiamante)
CREATE (peitoralDiamante)-[:MELHORA_PARA]->(peitoralNetherite)
CREATE (picaretaFerro)-[:MELHORA_PARA]->(picaretaDiamante)

// SUBSTITUI_NO_MESMO_ESPACO (Simétrica)
CREATE (peitoralFerro)-[:SUBSTITUI_NO_MESMO_ESPACO]->(elitro)
CREATE (elitro)-[:SUBSTITUI_NO_MESMO_ESPACO]->(peitoralFerro)

// PREPARADO_DE
CREATE (pocaoForca)-[:PREPARADO_DE]->(poBlaze)
CREATE (pocaoCura)-[:PREPARADO_DE]->(lagrimaGhast)

// DROPA / DROPADO_POR
CREATE (blaze)-[:DROPA]->(poBlaze)
CREATE (poBlaze)-[:DROPADO_POR]->(blaze)
CREATE (enderman)-[:DROPA]->(perolaFim)
CREATE (perolaFim)-[:DROPADO_POR]->(enderman)
CREATE (ghast)-[:DROPA]->(lagrimaGhast)
CREATE (lagrimaGhast)-[:DROPADO_POR]->(ghast)
CREATE (aranha)-[:DROPA]->(linha)
CREATE (linha)-[:DROPADO_POR]->(aranha);
"""


def carregar_dados():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        for comando in QUERY_CARGA.strip().split(";"):
            if comando.strip():
                session.run(comando)

        res_nos = session.run("MATCH (n) RETURN count(n) AS total").single()["total"]
        res_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"]
        print(f"Carga concluída com sucesso! Nós: {res_nos} | Relacionamentos: {res_rels}")
    driver.close()


if __name__ == "__main__":
    carregar_dados()