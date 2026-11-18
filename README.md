# Mini-Projeto 4 — Base de Conhecimento do Minecraft em Grafo de Propriedades (Memgraph)

Remodelagem da ontologia OWL/RDF de itens não-blocos do **Minecraft** (desenvolvida no Mini-Projeto 3) para um **banco de dados de grafos orientado a propriedades** utilizando **Memgraph**, **Docker** e consultas em **Cypher** via Python.

---

## Estrutura do Repositório

```text
.
├── docker-compose.yml   # Orquestração dos containers Memgraph e Memgraph Lab
├── carga.py             # Script de carga que recria e popula o grafo do zero
├── consultas.py         # Aplicação Python com consultas Cypher, travessias e updates
├── requirements.txt     # Dependências Python (driver Bolt)
└── README.md            # Documentação do modelo e instruções de execução
```

---

## Resumo do Modelo do Grafo de Propriedades

A base original (31 instâncias e suas relações semânticas) foi convertida integralmente para nós, múltiplos rótulos, relacionamentos direcionados e propriedades tipadas.

### 1. Rótulos dos Nós (Hierarquia de Classes)

Cada nó recebe múltiplos rótulos para preservar a herança taxonômica da ontologia original:

| Rótulo Raiz | Sub-rótulos Intermediários | Rótulos Específicos (Folhas) | Exemplos de Nós |
|---|---|---|---|
| `:Item` | `:Equipamento` | `:Arma`, `:Armadura`, `:Ferramenta` | EspadaDiamante, Elitro, PicaretaFerro |
| `:Item` | `:Consumivel` | `:Comida`, `:Pocao` | BifeCozido, MacaDourada, PocaoForca |
| `:Item` | `:Material` | `:MaterialCriacao`, `:DropMonstro` | Diamante, Graveto, PoBlaze, PerolaFim |
| `:Item` | `:Entidade` | `:Monstro` | Blaze, Enderman, Ghast, Aranha |

### 2. Tipos de Relacionamentos

| Relacionamento | Descrição |
|---|---|
| `(:Item)-[:REQUER_MATERIAL]->(:Material)` | Materiais necessários para fabricar o item (navegada no sentido inverso para substituir `mc:eMaterialPara`). |
| `(:Equipamento)-[:TEM_MATERIAL_REPARO]->(:Material)` | Material usado para reparar o equipamento na bigorna. |
| `(:Equipamento)-[:MELHORA_PARA]->(:Equipamento)` | Progressão de tier do equipamento (consultada com comprimento variável `*1..` para transitividade). |
| `(:Equipamento)-[:SUBSTITUI_NO_MESMO_ESPACO]->(:Equipamento)` | Relação simétrica materializada nos dois sentidos entre PeitoralFerro e Elitro. |
| `(:Pocao)-[:PREPARADO_DE]->(:Material)` | Ingrediente base utilizado no preparo da poção. |
| `(:Monstro)-[:DROPA]->(:DropMonstro)` e `(:DropMonstro)-[:DROPADO_POR]->(:Monstro)` | Relação bidirecional entre monstros e os itens deixados ao morrer. |

### 3. Propriedades dos Nós

| Categoria | Propriedades |
|---|---|
| Identificação | `id` (string), `nome` (string) |
| Atributos gerais | `tamanhoPilha` (int), `raridade` (string), `eRenovavel` (boolean) |
| Atributos específicos | `durabilidade` (int), `danoAtaque` (float), `valorNutricional` (int) |

---

## Instruções de Execução

### 1. Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.10+

### 2. Subir o Memgraph e o Memgraph Lab

Na raiz do projeto, inicie os containers em segundo plano:

```bash
docker compose up -d
```

Verifique se os dois serviços (`memgraph` e `memgraph-lab`) estão ativos:

```bash
docker compose ps
```

- **Endpoint Bolt (aplicação Python):** `bolt://localhost:7687`
- **Interface Visual (Memgraph Lab):** http://localhost:3000

### 3. Instalar Dependências Python

```bash
pip install -r requirements.txt
```

### 4. Carregar a Base de Dados

Execute o script de carga para limpar o grafo e inserir os 31 nós e 44 relacionamentos:

```bash
python carga.py
```

Saída esperada:

```plaintext
Carga concluída com sucesso! Nós: 31 | Relacionamentos: 44
```

### 5. Executar as Consultas Cypher, Travessias e Updates

```bash
python consultas.py
```

O script executa e imprime no terminal:

- **Parte 1 (MP3 - P1.1 a P1.7):** equivalentes às consultas de padrão de triplas (`g.triples()`), incluindo relação inversa, transitividade e simetria.
- **Parte 2 (MP3 - SPARQL 1 a 6):** equivalentes às consultas `SELECT`, agregação, `ASK`, `CONSTRUCT` e `OPTIONAL`.
- **Parte 3 (TRAVESSIA 1 a 4):** 4 consultas com caminhos encadeados de 2 relacionamentos no grafo.
- **Parte 4 (MP3 - UPDATES):** inserção de `MacaArma`, remoção de `eRenovavel` em `Elitro`, atualização de `durabilidade` em `PicaretaFerro` e consultas de verificação pós-update.

> **Nota:** Como a Parte 4 modifica o estado do grafo no banco, caso deseje reexecutar as consultas sobre a base original, rode `python carga.py` novamente antes de executar `python consultas.py`.

---

## Teste de Persistência dos Dados

O volume Docker `mg_lib` mapeia `/var/lib/memgraph` para persistir snapshots e logs (WAL) fora do container. Para validar a persistência:

1. Reinicie o container do Memgraph:

   ```bash
   docker compose restart memgraph
   ```

2. Acesse o Memgraph Lab em http://localhost:3000 (ou execute uma consulta via Python) e rode:

   ```cypher
   MATCH (n) RETURN count(n);
   ```

3. O total de nós retornados permanecerá idêntico ao estado anterior ao reinício (**31** após a carga inicial ou **32** após os updates).

> **Atenção:** `docker compose down` para os containers mantendo o volume `mg_lib` intacto. Utilizar `docker compose down -v` apaga o volume e remove todos os dados persistidos.