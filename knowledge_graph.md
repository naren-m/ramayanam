
### 🧠 Prompt to Implement Ramayana Knowledge Graph (JSON-LD)

> I have a JSON-LD ontology schema defining classes and properties for building a knowledge graph of the *Ramayana* epic.
> The schema includes entity types like `Person`, `Place`, `Event`, `Object`, and `Concept`, as well as relationships like `hasSpouse`, `hasParent`, `devoteeOf`, and `rules`.
>
> I’d like you to:
>
> 1. Load the attached JSON-LD schema (or use the structure I’ll paste below).
> 2. Create a **JSON-LD knowledge graph instance** containing at least 10-15 entities from the *Ramayana*, including characters like Rama, Sita, Hanuman, Ravana, and events like Sita’s abduction and the war in Lanka.
> 3. Use the defined ontology properties to connect the entities (e.g., `Rama hasSpouse Sita`, `Hanuman devoteeOf Rama`, etc.).
> 4. Include multilingual labels where appropriate (`rdfs:label` for English, `schema:name` for Sanskrit or other).
> 5. Structure it so it works cleanly in a JSON-LD validator (like [https://json-ld.org/playground/](https://json-ld.org/playground/)).
>
> Optionally:
>
> * Add comments or metadata for source texts (like which Kanda or chapter the info is from).
> * Use `owl:sameAs` links for Rama and other characters from Wikidata (if known).
> * Wrap it as a function/script if needed to generate larger graphs from extracted triples.
>
> Here's the schema to use (or refer to the schema.jsonld file I’ll upload):



## implementation guide

---

### 📘 **Ramayana Knowledge Graph — Implementation Details for Agent**

#### 📌 Purpose

Create a **semantic knowledge graph in JSON-LD** format representing the key entities, concepts, and relationships in the *Ramayana*. This graph will be usable for querying, visualizing, and expanding with semantic tools.

---

### 📂 Files & Structure

1. **`schema.jsonld`**
   Contains the ontology — classes like `Person`, `Place`, `Event`, and properties like `hasSpouse`, `devoteeOf`, etc.

2. **`data.jsonld` (to be created)**
   Will contain instance data following the schema — nodes and relationships representing characters, events, etc.

---

### ✅ Requirements

#### 1. **Use the provided schema**

* Use the `@context` and vocabulary terms from `schema.jsonld`.
* Maintain consistent `@id` format (e.g., `http://example.org/entity/Rama`).

#### 2. **Create Instances (10–20)**

* Include at least these characters:

  * Rama, Sita, Lakshmana, Hanuman, Ravana, Dasharatha, Bharata, Vibhishana
* Include at least 2–3 places:

  * Ayodhya, Lanka, Panchavati
* Include at least 2 events:

  * Sita’s abduction, the war in Lanka

#### 3. **Relationships**

Use semantic properties from the schema:

* `hasSpouse`, `hasParent`, `devoteeOf`, `rules`, `embodies`, `hasSibling`, `killed`

#### 4. **Labels & Language Support**

* Add `rdfs:label` in English
* Add `schema:name` in Sanskrit or Tamil (if known)

```json
"label": "Rama",
"name": "राम"
```

#### 5. **Optional Enhancements**

* Add `sourceText`, `book`, `chapter` if known (to `@graph` entry or as separate named graph).
* Use `owl:sameAs` to link to Wikidata for well-known entities.
* Add `type`: `rdf:type` or `@type` should match the schema class.

---

### ✍🏽 Example Triplet

```json
{
  "@id": "http://example.org/entity/Rama",
  "@type": "Person",
  "label": "Rama",
  "name": "राम",
  "hasSpouse": {
    "@id": "http://example.org/entity/Sita"
  },
  "hasParent": {
    "@id": "http://example.org/entity/Dasharatha"
  },
  "embodies": {
    "@id": "http://example.org/entity/Dharma"
  }
}
```

---

### ⚠️ Constraints

* Do not invent relationships that contradict core *Ramayana* sources (Valmiki Ramayana preferred unless noted).
* Avoid circular references unless supported by inverse properties in the schema.
* Keep URIs consistent (use `"http://example.org/entity/...` for instances and `"http://example.org/ontology/...` for classes).
* Validate final JSON-LD via [https://json-ld.org/playground/](https://json-ld.org/playground/)

---

### 🔄 Reusability Goals

* This JSON-LD should be ready to:

  * Convert to RDF/Turtle
  * Ingest into tools like GraphDB, Blazegraph, or Neo4j (via Cypher generation)
  * Feed into a Q\&A bot
  * Power timeline or relationship visualizations

---

### 🤖 Agent Tips

If using LLMs or agents to generate this graph:

* Start by listing entities and their known attributes.
* Use the schema as a constraint validator before emitting JSON.
* Favor accuracy over completion — a smaller, correct graph is better than a large noisy one.
* If unsure, annotate facts as `confidenceScore: 0.7` or `sourceText: "Inferred"`.

## 🧠 1. **Where This Schema Fits in the Architecture**

### 🔧 In the Architecture Stack

| Layer                             | Role of Schema                                                                                                 |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **Data Storage**                  | Tags and classifies content in PostgreSQL / RDF                                                                |
| **Search Index (Elastic)**        | Indexed by type (TextUnit, Person, Concept, etc.) for filtered, faceted search                                 |
| **Vector Store (Weaviate, etc.)** | Uses relationships like `mentionsConcept` to cluster by theme/meaning                                          |
| **Backend API Layer**             | Serves content by class (`Text`, `Translation`, etc.), and uses relationships like `hasUnit`, `hasCommentary`  |
| **AI Chat Engine (RAG)**          | Maps passages to `TextUnit`, uses metadata like `mentionsConcept`, `hasCommentary` for grounding answers       |
| **Frontend Display**              | Displays dynamic structured data (e.g. show all `hasCommentary` of a verse or compare multiple `Translations`) |

---

## 📚 2. **What This Schema Enables**

### ✅ Search and Filtering

* Find all **TextUnits** mentioning a **Concept** (`mentionsConcept`)
* Filter **TextUnits** from a **Text** by chapter/hierarchy via `hasUnit`
* Search for all **Translations** of a given **TextUnit** via `translatedAs`

### 🧠 AI Reasoning & Chat

* Enables **contextual grounding**:

  > *"Show me all verses discussing *dharma*"* → resolved via `mentionsConcept: dharma`
* Powers **citation in chat**:

  > *"This commentary by Shankara (hasCommentary) interprets this sloka as..."*
* Supports **RAG context graphs** — e.g., graph traversal from sloka → theme → similar verse

---

## 🕵️ 3. **Concrete Example**

Let’s say you query:

> “Where is the concept of **karma** explained in Ramayana?”

The flow might be:

1. **User → Chat Interface** → backend detects `ChatIntent: EXPLAIN`, `Concept: karma`
2. **Backend** hits KG:

   * `TextUnits` where `mentionsConcept = karma`
3. **RAG**: Uses these units as context for LLM
4. **AI** responds:

   > *“Karma is mentioned in Ayodhya Kanda 105.3, where Rama says...”*
   > *(linked via `hasUnit`, `mentionsConcept`, `translatedAs`)*
5. **Frontend** shows:

   * Original sloka
   * Translation(s)
   * Commentary
   * Discussion thread

---

## 🧩 4. **Schema as Plug-in for LLM Grounding**

* Each **TextUnit** can be part of a **RAG document chunk**, and related metadata fields help **rank or disambiguate answers**.
* `mentionsConcept`, `hasCommentary`, `translatedAs`, `hasUnit` → all form **edges in the knowledge graph** that guide the LLM toward grounded, precise answers.

---

## 🔄 5. **Dynamic Features This Schema Enables**

| Feature                     | Enabled By                                                  |
| --------------------------- | ----------------------------------------------------------- |
| **Cross-text comparison**   | Multiple `Text` → `TextUnit` → shared `mentionsConcept`     |
| **Multi-language support**  | `translatedAs`, `Translation.style`, `Translation.language` |
| **Commentary sidebar**      | `hasCommentary` relationship                                |
| **Theme-based exploration** | `Concept` + `mentionsConcept`                               |
| **User annotation tools**   | Can extend `Commentary` class with `author`, `timestamp`    |
| **Chat-to-verse grounding** | `discussesTextUnit` from `ChatMessage` class                |

---

## ✅ TL;DR Summary

This schema is the **semantic layer** that sits **beneath your backend, AI, and UI layers**. It:

* Standardizes entities: Texts, verses, concepts, characters, places
* Structures relationships: Translation, commentary, concept mentions, lineage
* Powers smart AI answers, contextual recommendations, and rich UI features
* Keeps the platform **scalable**, **flexible**, and **knowledge-driven**

Would you like a **diagram** of how this maps to the full architecture stack or how a typical AI query uses this graph?

Here is the updated version of your JSON-LD schema with the enhancements to support your universal sacred text analysis platform. I've **added classes and properties** for:

* Generic sacred text modeling (`Text`, `TextUnit`, `Translation`, `Commentary`)
* Structural relationships (like `hasUnit`, `translatedAs`, etc.)
* Concept mentions and commentary support
* Optional stubs for future `ChatMessage` integration

```json
{
  "@context": {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "schema": "http://schema.org/",
    "name": "schema:name",
    "label": "rdfs:label",
    "comment": "rdfs:comment",
    "type": "@type",
    "Class": "rdfs:Class",
    "Property": "rdf:Property"
  },
  "@graph": [
    {
      "@id": "http://example.org/ontology/Person",
      "@type": "Class",
      "label": "Person",
      "comment": "A human or humanoid character in the Ramayana."
    },
    {
      "@id": "http://example.org/ontology/Place",
      "@type": "Class",
      "label": "Place",
      "comment": "A geographic or mythological location."
    },
    {
      "@id": "http://example.org/ontology/Event",
      "@type": "Class",
      "label": "Event",
      "comment": "A significant narrative happening."
    },
    {
      "@id": "http://example.org/ontology/Object",
      "@type": "Class",
      "label": "Object",
      "comment": "A notable physical item."
    },
    {
      "@id": "http://example.org/ontology/Concept",
      "@type": "Class",
      "label": "Concept",
      "comment": "An abstract philosophical or ethical idea."
    },
    {
      "@id": "http://example.org/ontology/Text",
      "@type": "Class",
      "label": "Text",
      "comment": "A sacred text such as Ramayana, Mahabharata, Gita, etc."
    },
    {
      "@id": "http://example.org/ontology/TextUnit",
      "@type": "Class",
      "label": "TextUnit",
      "comment": "A logical unit within a text such as Sloka, Verse, or Chapter."
    },
    {
      "@id": "http://example.org/ontology/Translation",
      "@type": "Class",
      "label": "Translation",
      "comment": "A translated version of a text unit."
    },
    {
      "@id": "http://example.org/ontology/Commentary",
      "@type": "Class",
      "label": "Commentary",
      "comment": "A scholarly or traditional explanation attached to a TextUnit."
    },
    {
      "@id": "http://example.org/ontology/ChatMessage",
      "@type": "Class",
      "label": "ChatMessage",
      "comment": "A single message exchanged between user and AI assistant."
    },
    {
      "@id": "http://example.org/relations/hasSpouse",
      "@type": "Property",
      "label": "hasSpouse",
      "comment": "Spousal relationship between two Persons.",
      "rdfs:domain": { "@id": "http://example.org/ontology/Person" },
      "rdfs:range": { "@id": "http://example.org/ontology/Person" },
      "owl:inverseOf": { "@id": "http://example.org/relations/hasSpouse" }
    },
    {
      "@id": "http://example.org/relations/hasParent",
      "@type": "Property",
      "label": "hasParent",
      "comment": "Parent relationship between two Persons.",
      "rdfs:domain": { "@id": "http://example.org/ontology/Person" },
      "rdfs:range": { "@id": "http://example.org/ontology/Person" },
      "owl:inverseOf": { "@id": "http://example.org/relations/hasChild" }
    },
    {
      "@id": "http://example.org/relations/hasChild",
      "@type": "Property",
      "label": "hasChild",
      "comment": "Child relationship between two Persons.",
      "rdfs:domain": { "@id": "http://example.org/ontology/Person" },
      "rdfs:range": { "@id": "http://example.org/ontology/Person" },
      "owl:inverseOf": { "@id": "http://example.org/relations/hasParent" }
    },
    {
      "@id": "http://example.org/relations/devoteeOf",
      "@type": "Property",
      "label": "devoteeOf",
      "comment": "Devotional relationship from a Person to a Deity or Person.",
      "rdfs:domain": { "@id": "http://example.org/ontology/Person" },
      "rdfs:range": { "@id": "http://example.org/ontology/Person" }
    },
    {
      "@id": "http://example.org/relations/rules",
      "@type": "Property",
      "label": "rules",
      "comment": "Rulership relationship linking a Person to a Place.",
      "rdfs:domain": { "@id": "http://example.org/ontology/Person" },
      "rdfs:range": { "@id": "http://example.org/ontology/Place" },
      "owl:inverseOf": { "@id": "http://example.org/relations/ruledBy" }
    },
    {
      "@id": "http://example.org/relations/ruledBy",
      "@type": "Property",
      "label": "ruledBy",
      "comment": "Inverse of rules relationship.",
      "rdfs:domain": { "@id": "http://example.org/ontology/Place" },
      "rdfs:range": { "@id": "http://example.org/ontology/Person" },
      "owl:inverseOf": { "@id": "http://example.org/relations/rules" }
    },
    {
      "@id": "http://example.org/relations/hasUnit",
      "@type": "Property",
      "label": "hasUnit",
      "comment": "Links a Text to its constituent TextUnits.",
      "rdfs:domain": { "@id": "http://example.org/ontology/Text" },
      "rdfs:range": { "@id": "http://example.org/ontology/TextUnit" }
    },
    {
      "@id": "http://example.org/relations/translatedAs",
      "@type": "Property",
      "label": "translatedAs",
      "comment": "Links a TextUnit to its Translation.",
      "rdfs:domain": { "@id": "http://example.org/ontology/TextUnit" },
      "rdfs:range": { "@id": "http://example.org/ontology/Translation" }
    },
    {
      "@id": "http://example.org/relations/hasCommentary",
      "@type": "Property",
      "label": "hasCommentary",
      "comment": "Links a TextUnit to associated commentaries.",
      "rdfs:domain": { "@id": "http://example.org/ontology/TextUnit" },
      "rdfs:range": { "@id": "http://example.org/ontology/Commentary" }
    },
    {
      "@id": "http://example.org/relations/mentionsConcept",
      "@type": "Property",
      "label": "mentionsConcept",
      "comment": "Links a TextUnit to an abstract Concept it mentions.",
      "rdfs:domain": { "@id": "http://example.org/ontology/TextUnit" },
      "rdfs:range": { "@id": "http://example.org/ontology/Concept" }
    },
    {
      "@id": "http://example.org/relations/discussesTextUnit",
      "@type": "Property",
      "label": "discussesTextUnit",
      "comment": "Indicates that a chat message discusses a specific TextUnit.",
      "rdfs:domain": { "@id": "http://example.org/ontology/ChatMessage" },
      "rdfs:range": { "@id": "http://example.org/ontology/TextUnit" }
    }
  ]
}

Below is a **prototype blueprint** that shows how you can keep your **JSON-LD knowledge graph (KG)** as the “single source of truth,” yet still obtain:

* ⚡ ultra-fast keyword & faceted search (PostgreSQL + Elasticsearch)
* 🧠 semantic similarity search (vector DB)
* 🔗 traceable KG references for RAG workflows
* 🗺️ optional visual exploration in Neo4j

---

## 1 Data-flow Overview

```mermaid
flowchart LR
    subgraph Source of Truth
        A[JSON-LD KG files]:::file
    end
    subgraph ETL Pipeline
        A -->|rdflib / Jena parsing| B[Staging DataFrames]
        B --> C[PostgreSQL<br>𝙧𝙚𝙡¹]
        B --> D[Elasticsearch<br>index]
        B --> E[(Embedding Job)]:::compute
        E --> F[Vector DB<br>(Weaviate / Pinecone)]
        B --> G[Neo4j import (optional)]
    end
    classDef file fill:#e6f3ff,stroke:#4682b4;
    classDef compute fill:#fff2cc,stroke:#c69c1d;
```

* **rel¹** = normalized relational tables that mirror your ontology classes (Text, TextUnit, Translation, …).

---

## 2 ETL Step-by-Step

| Step                            | Tooling                                        | What Happens                                    | Key Output Fields                            |
| ------------------------------- | ---------------------------------------------- | ----------------------------------------------- | -------------------------------------------- |
| **2.1 Parse JSON-LD**           | `rdflib`, Apache Jena, or JSON-LD API          | Read triples/quads → create in-memory graphs    | `@id`, `@type`, literals                     |
| **2.2 Normalize to DataFrames** | pandas                                         | One DF per class (Person, TextUnit, …)          | ✔ primary key = `kg_id` (the `@id`)          |
| **2.3 Write to Postgres**       | SQLAlchemy / COPY                              | Create tables & foreign keys                    | fast relational look-ups                     |
| **2.4 Index to Elastic**        | Logstash or Python bulk API                    | For each TextUnit & Translation insert docs     | `kg_id`, text, language, hierarchy, concepts |
| **2.5 Generate Embeddings**     | sentence-transformers, OpenAI Embeddings, etc. | `embedding = model.encode(full_text)`           | 768-D float vector                           |
| **2.6 Upsert to Vector DB**     | Weaviate / Pinecone client                     | `vector`, `metadata={"kg_id": …, "text_id": …}` | semantic search                              |
| **2.7 (Opt) Import to Neo4j**   | neosemantics (`n10s.rdf.import`)               | RDF → Property Graph                            | visual Cypher queries                        |

---

## 3 Relational & Index Schema Sketch

```sql
-- core lookup table
CREATE TABLE kg_entity (
  kg_id TEXT PRIMARY KEY,     -- e.g. http://example.org/entity/2.47
  class  TEXT NOT NULL        -- TextUnit, Person, ...
);

-- text units
CREATE TABLE text_unit (
  kg_id TEXT PRIMARY KEY REFERENCES kg_entity,
  text_id TEXT REFERENCES kg_entity,      -- parent Text
  original_text TEXT NOT NULL,
  hierarchy JSONB,
  language TEXT
);

-- translations
CREATE TABLE translation (
  kg_id TEXT PRIMARY KEY REFERENCES kg_entity,
  unit_id TEXT REFERENCES text_unit(kg_id),
  language TEXT,
  text TEXT,
  style TEXT
);
```

*Elastic mapping* — already in your plan; be sure to store `kg_id` as a **keyword** field so a hit can be re-joined with KG metadata instantly.

---

## 4 Vector DB Upsert – Python Mini-Prototype

```python
import json, rdflib
from sentence_transformers import SentenceTransformer
import weaviate

# ----- 1. load JSON-LD & grab TextUnits ----------
g = rdflib.Graph()
g.parse("ramayana_sample.jsonld", format="json-ld")

query = """
SELECT ?unit ?text WHERE {
  ?unit rdf:type <http://example.org/ontology/TextUnit> ;
        rdfs:label ?text .
}
"""
text_units = [(str(row.unit), str(row.text)) for row in g.query(query)]

# ----- 2. embed -----------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")
vectors = model.encode([t[1] for t in text_units], normalize_embeddings=True)

# ----- 3. push to Weaviate ------------------------
client = weaviate.Client("http://localhost:8080")

for (kg_id, raw_text), vec in zip(text_units, vectors):
    client.data_object.create(
        data         = {"text": raw_text, "kg_id": kg_id},
        class_name   = "TextUnit",
        vector       = vec.tolist(),
        uuid         = kg_id.split("/")[-1]  # keep IDs aligned
    )
```

Now a semantic query returns objects whose `metadata["kg_id"]` links straight back to Postgres / KG.

---

## 5 How RAG Uses All Three Stores

1. **User question** ➜ embedding → **vector DB**
   *Top-k* `TextUnit` candidates returned with **`kg_id`**.
2. Fetch **metadata** from **Postgres** (exact hierarchy, concepts) and/or **Elastic** (neighbor verses).
3. Assemble grounded context (verse, translation, commentary) for the LLM.

   ```markdown
   > Verse 2.47 (Bhagavad Gita)  
   > कर्मण्येवाधिकारस्ते …  
   > Translation (English, Swami Chinmayananda): “You have the right to action …”
   > Concepts: karma, duty
   ```
4. LLM answers with citations (`kg_id` → hyperlink into UI).
5. Optionally, a **“Graph” tab** fires a Cypher query in Neo4j to visualize the TextUnit’s connections (mentionsConcept → Concept nodes, etc.).

---

## 6 Why This “Hybrid” Works

| Concern                           | Addressed By                                     |
| --------------------------------- | ------------------------------------------------ |
| **Exact search / filters**        | PostgreSQL + Elastic keyword & full-text indices |
| **Semantic similarity**           | Vector DB embeddings                             |
| **Explainability & traceability** | `kg_id` joins back to JSON-LD KG                 |
| **Ad-hoc graph questions / viz**  | Neo4j property graph import                      |
| **Single source of truth**        | JSON-LD files version-controlled in Git          |

---

## 7 Next Steps You Can Try Quickly

1. **Pick one text** (e.g., Bhagavad Gita) → export \~100 verses & translations into JSON-LD using the schema.
2. Run the **Python prototype** above to push vectors.
3. Create a simple **FastAPI endpoint**:
   `POST /semantic-search {"query": "karma and duty"}` → returns top verses + metadata.
4. Spin up Neo4j Desktop with the *n10s* plugin and import the same JSON-LD; run:

   ```cypher
   MATCH (v:TextUnit {kg_id: 'http://example.org/entity/2.47'})-[r]->(c)
   RETURN v,r,c
   ```

   …to see the verse and its connected concepts.

With this pipeline in place, you retain the **rich semantics of RDF/JSON-LD**, yet gain the **speed of Elastic** and **semantic power of vectors**—all tied together by the canonical `kg_id`.

Let me know if you’d like sample Docker-Compose files, a fuller embedding script, or a small Neo4j import snippet!



Absolutely. Below is a **clear, detailed prompt** you can give to your LLM agent—whether OpenAI GPT-4, Claude, or a local model—to handle **retrieval-augmented question answering (RAG)** over your semantic sacred-text platform.

This prompt assumes you’ve already retrieved relevant passages (via vector search) and want the LLM to generate a faithful, grounded answer.

---

### 🧠 LLM Agent Prompt Template for Sacred Text QA

````text
You are a helpful, respectful, and precise assistant that explains and analyzes verses from Hindu sacred texts such as the Ramayana, Mahabharata, Bhagavad Gita, and Upanishads.

The user has asked a question. You are given:
- Their question
- Relevant verse excerpts from sacred texts (along with translations, source metadata, and key themes)

Your job is to:
1. Answer the user’s question **clearly and concisely**, using only the provided sources.
2. **Cite specific verses** using the `text_name`, `chapter`, and `verse_number` when appropriate.
3. If a concept appears in multiple texts, you may **compare or cross-reference** them—but stay grounded to the texts provided.
4. If the user’s question is vague, help them refine or clarify it using respectful language.

❗ Do not invent facts, summaries, or opinions beyond the provided content. You must stay **truthful to the original verse meaning and translation**.

---

### User Question:
{{ user_question }}

---

### Retrieved Text Passages (Up to 5):

1. **Text**: {{text_name_1}}  
   **Location**: Chapter {{chapter}}, Verse {{verse_number}}  
   **Sanskrit**: {{original_text}}  
   **Translation**: {{translation}}  
   **Themes**: {{concepts}}  
   **KG ID**: {{kg_id}}

2. **Text**: {{text_name_2}}  
   **Location**: {{...}}  
   ...

---

### Guidelines:

- Begin with a **direct answer** to the user’s question.
- Use **quotes or paraphrased verses** with attribution.
- Where helpful, **explain meanings or concepts** (e.g., “karma”, “dharma”, “bhakti”) based on the themes.
- End with an invitation to explore more, e.g., “Would you like to see related verses or commentary?”

---

### Your Output Format (Markdown):
```markdown
**Answer**:  
<your concise explanation here>

**Reference**:  
- {{text_name_1}}, Chapter {{chapter}}, Verse {{verse_number}}  
- {{text_name_2}}, …

---
````

````

---

### ✅ Example Filled Prompt (for Developer Reference)

Let’s say the user asks:

> What does the Gita say about performing duties without attachment?

Your system retrieves:

```json
[
  {
    "text_name": "Bhagavad Gita",
    "chapter": 2,
    "verse_number": 47,
    "original_text": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
    "translation": "You have the right to perform your prescribed duty, but not to the fruits of the action.",
    "concepts": ["karma", "non-attachment", "duty"],
    "kg_id": "http://example.org/entity/2.47"
  },
  {
    "text_name": "Bhagavad Gita",
    "chapter": 3,
    "verse_number": 19,
    "original_text": "तस्मादसक्तः सततं कार्यं कर्म समाचर।",
    "translation": "Therefore, without attachment, always perform the work that has to be done.",
    "concepts": ["karma yoga", "detachment"],
    "kg_id": "http://example.org/entity/3.19"
  }
]
````

🧠 LLM Output (expected):

```markdown
**Answer**:  
The Bhagavad Gita emphasizes performing one’s duty without attachment to outcomes. In Chapter 2, Verse 47, it says, “You have the right to perform your prescribed duty, but not to the fruits of the action,” highlighting the principle of acting without expecting results. Similarly, Chapter 3, Verse 19 advises, “Therefore, without attachment, always perform the work that has to be done,” reinforcing the idea of selfless action as a path to liberation.

**Reference**:  
- Bhagavad Gita, Chapter 2, Verse 47  
- Bhagavad Gita, Chapter 3, Verse 19
```
