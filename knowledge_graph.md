
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

---

Would you like me to bundle all this as a `README.md` for your GitHub repo or workspace? Or auto-generate a few sample JSON-LD files to get you started?
