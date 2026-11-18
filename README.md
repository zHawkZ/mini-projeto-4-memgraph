# Mini-Projeto 4: Base de Conhecimento do Minecraft no Memgraph

Migração da base de conhecimento do Minecraft (originalmente desenvolvida em RDF/OWL e SPARQL no Mini-Projeto 3) para um modelo de **Grafo de Propriedades** persistido no **Memgraph** via Docker e consultado com **Cypher**.

## Resumo do Modelo do Grafo

* **Rótulos (Labels):** Representam a hierarquia de classes da ontologia original (`Item`, `Equipamento`, `Arma`, `Ferramenta`, `Armadura`, `Consumivel`, `Comida`, `Pocao`, `Material`, `MaterialCriacao`, `DropMonstro`, `Entidade`, `Monstro`). Cada nó acumula todos os rótulos de sua hierarquia (ex.: `:Arma:Equipamento:Item`).
* **Propriedades dos Nós:** `id`, `nome`, `durabilidade`, `danoAtaque`, `tamanhoPilha`, `valorNutricional`, `raridade`, `eRenovavel`.
* **Relacionamentos:**
  * `(:Item)-[:REQUER_MATERIAL]->(:Material)`: Materiais necessários para fabricação.
  * `(:Equipamento)-[:TEM_MATERIAL_REPARO]->(:Material)`: Material utilizado para reparar o equipamento.
  * `(:Equipamento)-[:MELHORA_PARA]->(:Equipamento)`: Progressão de tier entre equipamentos.
  * `(:Equipamento)-[:SUBSTITUI_NO_MESMO_ESPACO]->(:Equipamento)`: Relação simétrica entre equipamentos que ocupam o mesmo slot.
  * `(:Monstro)-[:DROPA]->(:DropMonstro)` e `(:DropMonstro)-[:DROPADO_POR]->(:Monstro)`: Relação entre monstros e seus drops.
  * `(:Pocao)-[:PREPARADO_DE]->(:Material)`: Ingrediente necessário para preparar a poção.

## Estrutura do Repositório

* `docker-compose.yml`: Orquestração dos containers `memgraph` e `memgraph-lab`, com volume `mg_lib` para persistência.
* `carga.py`: Script Python que limpa o banco e cria toda a base de nós e relacionamentos do zero.
* `consultas.py`: Aplicação Python que executa todas as consultas do Mini-Projeto 3 em Cypher, 4 consultas com travessia de múltiplos relacionamentos e os updates com verificação.

## Instruções de Execução

1. Subir os containers Docker: `docker compose up -d` (verifique com `docker compose ps`; interface visual em `http://localhost:3000`).
2. Instalar a dependência Python: `pip install neo4j`
3. Carregar a base no Memgraph: `python3 carga.py`
4. Executar as consultas e updates: `python3 consultas.py`
5. Testar a persistência: `docker compose restart memgraph && sleep 3 && python3 consultas.py` (use `docker compose down` para parar mantendo os dados, ou `docker compose down -v` para apagar o volume).
