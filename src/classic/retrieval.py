from whoosh import index
from whoosh.qparser import QueryParser, OrGroup
import os, yaml,spacy

nlp = spacy.load('en_core_web_sm')

def load_config():
    return yaml.safe_load(open("config.yaml", "r"))


_cfg = load_config()
_ix = index.open_dir(_cfg["paths"]["whoosh_index"])
_qp = QueryParser("text", schema=_ix.schema, group=OrGroup)

def build_query(claim : str) -> str :
    """
    Enrichit la requête avec les entités nommées du claim.
    Exemple : "Morocco hosted the 2010 FIFA World Cup."
      -> "Morocco hosted the 2010 FIFA World Cup. Morocco 2010 FIFA World Cup"
    """
    doc = nlp(claim)
    ents = " ".join([ent.text for ent in doc.ents])
    if ents :
        return f"{claim} {ents}"
    return claim


def bm25_top_k(claim : str , k : int = None):
    """
    Retourne les top-k phrases BM25 (sans rerank).
    Chaque élément est un dict {page, sent_id, text, score}.
    """
    if k is None :
        k = _cfg["retrieval"]["bm25_top_k"]

    query_str = build_query(claim)
    query = _qp.parse(query_str)

    results = []

    with _ix.searcher() as searcher:
        hits = searcher.search(query, limit=k)
        for hit in hits:
            results.append({
                "page" : hit["page"],
                "sent_id" : hit["sent_id"],
                "text" : hit["text"],
                "score" : float(hit.score)
            })
    return results

def retrieve_candidates(claim: str, m: int = None):
    """
    Version simplifiée : pour l'instant, on prend juste
    les top-m BM25 (sans rerank sophistiqué).
    """
    if m is None:
        m = _cfg["retrieval"]["m"]   # ex. 10

    hits = bm25_top_k(claim, k=_cfg["retrieval"]["m"])
    return hits[:m]  # pour l'instant, top-m = premiers résultats


if __name__ == "__main__":
    test_claim = "Morocco hosted the 2010 FIFA World Cup."
    results = bm25_top_k(test_claim, k=5)
    for res in results:
        print(f"[{res['score']:.4f}] {res['page']}::{res['sent_id']} - {res['text']}")