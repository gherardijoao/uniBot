import os
import glob
from .ai_service import RAGService

# Support for PDF extraction
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


def extract_text_from_pdf(path: str) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf não está instalado. Instale com `pip install pypdf`")
    reader = PdfReader(path)
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)


def main(data_dir: str = None):
    base = data_dir or os.path.join(os.path.dirname(__file__), '..', 'data')
    base = os.path.abspath(base)
    if not os.path.exists(base):
        print(f"Data dir {base} não existe. Crie o diretório e adicione arquivos .txt ou .pdf")
        return

    txt_files = glob.glob(os.path.join(base, '*.txt'))
    pdf_files = glob.glob(os.path.join(base, '*.pdf'))
    files = txt_files + pdf_files
    if not files:
        print(f"Nenhum arquivo .txt ou .pdf encontrado em {base}")
        return

    docs = []
    metadatas = []
    for p in files:
        if p.lower().endswith('.pdf'):
            try:
                text = extract_text_from_pdf(p)
                docs.append(text)
                metadatas.append({"source": os.path.basename(p)})
            except Exception as e:
                print(f"Falha ao extrair {p}: {e}")
        else:
            with open(p, 'r', encoding='utf-8') as fh:
                docs.append(fh.read())
                metadatas.append({"source": os.path.basename(p)})

    rag = RAGService()
    rag.ingest_documents(docs, metadatas=metadatas)
    print(f"Ingestão concluída: {len(docs)} documentos adicionados à coleção.")


if __name__ == '__main__':
    main()
