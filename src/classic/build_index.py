from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer
import os, yaml,orjson, glob

def load_config():
    return yaml.safe_load(open("config.yaml", "r"))

schema = Schema(
    doc_id=ID(stored=True, unique=True),      # "page::sent_id"
    page=ID(stored=True),                     # titre de page
    sent_id=ID(stored=True),                  # numéro de phrase
    text=TEXT(stored=True, analyzer=StemmingAnalyzer())  # contenu pour BM25
)

def iter_sentences(data_path):
    """Itère sur les phrases annotées dans les fichiers JSONL."""
    files = glob.glob(os.path.join("data/wiki-pages", "*.jsonl"))
    for file in files:
        with open(file , "rb") as f:
            for line in f :
                obj = orjson.loads(line)
                page = obj["id"]
                for row in obj["lines"].split("\n"):
                    if not row:
                        continue
                    sid, sent = row.split("\t", 1)
                    doc_id = f"{page}::{sid}"
                    yield doc_id, page, sid, sent

def main():
    cfg = load_config()
    wiki_dir = cfg["paths"]["wiki_pages"]
    idx_dir = cfg["paths"]["whoosh_index"]

    os.makedirs(idx_dir, exist_ok=True)

    if not index.exists_in(idx_dir):
        ix = index.create_in(idx_dir, schema)
    else:
        ix = index.open_dir(idx_dir)

    writer = ix.writer(limitmb=512)
    MAX_DOCS = 20_000_000

    n = 0
    for doc_id, page, sid, txt in iter_sentences(wiki_dir):
        writer.update_document(
            doc_id=doc_id,
            page=page,
            sent_id=sid,
            text=txt
        )
        n += 1
        if n % 100000 == 0:
            print(f"{n} phrases indexées...")
        if n >= MAX_DOCS:
            print(f"Atteint la limite MAX_DOCS={MAX_DOCS}, arrêt de l'indexation.")
            break
    writer.commit()
    print(f"Indexation terminée : {n} phrases.")

if __name__ == "__main__":
    main()