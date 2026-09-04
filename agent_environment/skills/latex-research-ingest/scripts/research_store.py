#!/usr/bin/env python3
"""Local PDF ingestion and retrieval for LaTeX research repositories."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


STORE_DIR = ".agent-runtime/research"
TEXT_DIR = "text"
MANIFEST = "manifest.json"
VECTOR_STORE = "vector-store.json"
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_'-]{1,}|[0-9]+(?:\.[0-9]+)?")
STOPWORDS = {
    "the", "and", "for", "that", "with", "from", "this", "are", "was",
    "were", "has", "have", "had", "not", "but", "can", "may", "its",
    "into", "which", "where", "when", "then", "than", "these", "those",
    "their", "there", "such", "also", "between", "within", "without",
    "using", "used", "use", "per", "all", "one", "two", "each", "both",
}


@dataclass
class Chunk:
    chunk_id: str
    source_id: str
    source_path: str
    title: str
    page_start: int
    page_end: int
    text: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_id_for(path: Path, digest: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", path.stem).strip("-").lower()[:60]
    return f"{digest[:12]}-{slug or 'pdf'}"


def ensure_store(root: Path) -> Path:
    store = root / STORE_DIR
    (store / TEXT_DIR).mkdir(parents=True, exist_ok=True)
    return store


def run_pdftotext(path: Path) -> str | None:
    if not shutil.which("pdftotext"):
        return None
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.decode("utf-8", errors="replace")


def run_python_pdf_extract(path: Path) -> str:
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return "\f".join(pages)
    except Exception:
        pass

    try:
        import PyPDF2  # type: ignore

        reader = PyPDF2.PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return "\f".join(pages)
    except Exception as exc:
        raise RuntimeError(f"Could not extract text from {path}: {exc}") from exc


def extract_pdf_text(path: Path) -> str:
    text = run_pdftotext(path)
    if text is not None and text.strip():
        return text
    return run_python_pdf_extract(path)


def normalize_space(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_texts(raw_text: str) -> list[str]:
    pages = raw_text.split("\f")
    return [normalize_space(page) for page in pages]


def word_spans(text: str) -> list[re.Match[str]]:
    return list(re.finditer(r"\S+", text))


def chunk_pages(
    source_id: str,
    source_path: str,
    title: str,
    pages: list[str],
    chunk_words: int = 700,
    overlap_words: int = 120,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    current_words: list[str] = []
    current_page_start = 1
    chunk_index = 0

    def emit(page_end: int, keep_overlap: bool = True) -> None:
        nonlocal chunk_index, current_words, current_page_start
        if not current_words:
            return
        text = " ".join(current_words).strip()
        if len(text) < 80:
            current_words = []
            return
        chunk_index += 1
        chunk_id = f"{source_id}:chunk:{chunk_index:04d}"
        chunks.append(
            Chunk(
                chunk_id=chunk_id,
                source_id=source_id,
                source_path=source_path,
                title=title,
                page_start=current_page_start,
                page_end=page_end,
                text=text,
            )
        )
        if keep_overlap and overlap_words > 0:
            current_words = current_words[-overlap_words:]
            current_page_start = max(current_page_start, page_end)
        else:
            current_words = []
            current_page_start = page_end

    for page_number, page in enumerate(pages, start=1):
        words = [match.group(0) for match in word_spans(page)]
        if not current_words:
            current_page_start = page_number
        for word in words:
            current_words.append(word)
            if len(current_words) >= chunk_words:
                emit(page_number)
    emit(len(pages), keep_overlap=False)
    return chunks


def tokenize(text: str) -> list[str]:
    tokens = []
    for match in TOKEN_RE.finditer(text.lower()):
        token = match.group(0).strip("'_-")
        if len(token) < 2 or token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def vectorize_chunks(chunks: list[Chunk]) -> tuple[list[dict], dict[str, float]]:
    doc_freq: Counter[str] = Counter()
    term_counts: list[Counter[str]] = []
    for chunk in chunks:
        counts = Counter(tokenize(chunk.text))
        term_counts.append(counts)
        doc_freq.update(counts.keys())

    n_docs = max(len(chunks), 1)
    idf = {term: math.log((1 + n_docs) / (1 + freq)) + 1 for term, freq in doc_freq.items()}
    records: list[dict] = []
    for chunk, counts in zip(chunks, term_counts):
        weights = {}
        for term, count in counts.items():
            weights[term] = (1 + math.log(count)) * idf[term]
        norm = math.sqrt(sum(value * value for value in weights.values())) or 1.0
        vector = {term: round(value / norm, 8) for term, value in weights.items()}
        records.append(
            {
                "chunk_id": chunk.chunk_id,
                "source_id": chunk.source_id,
                "source_path": chunk.source_path,
                "title": chunk.title,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "text": chunk.text,
                "vector": vector,
            }
        )
    return records, idf


def load_json(path: Path, default):
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def ingest(root: Path, pdf_paths: list[Path]) -> int:
    store = ensure_store(root)
    manifest_path = store / MANIFEST
    manifest = load_json(manifest_path, {"version": 1, "sources": []})
    sources_by_id = {source["source_id"]: source for source in manifest.get("sources", [])}
    all_chunks: list[Chunk] = []

    existing_store = load_json(store / VECTOR_STORE, {"chunks": []})
    replaced_source_ids: set[str] = set()

    for raw_path in pdf_paths:
        path = raw_path if raw_path.is_absolute() else (root / raw_path)
        path = path.resolve()
        if not path.is_file():
            print(f"warning: missing PDF: {path}", file=sys.stderr)
            continue
        digest = sha256_file(path)
        source_id = source_id_for(path, digest)
        replaced_source_ids.add(source_id)
        rel_path = os.path.relpath(path, root)
        title = path.stem.replace("-", " ").replace("_", " ")

        print(f"extracting {rel_path}")
        raw_text = extract_pdf_text(path)
        pages = page_texts(raw_text)
        text_path = store / TEXT_DIR / f"{source_id}.txt"
        text_body = "\n\n".join(f"[[page {i}]]\n{page}" for i, page in enumerate(pages, start=1))
        text_path.write_text(text_body, encoding="utf-8")

        chunks = chunk_pages(source_id, rel_path, title, pages)
        all_chunks.extend(chunks)
        sources_by_id[source_id] = {
            "source_id": source_id,
            "path": rel_path,
            "sha256": digest,
            "title": title,
            "pages": len(pages),
            "text": os.path.relpath(text_path, root),
            "chunks": len(chunks),
            "updated_at": utc_now(),
        }
        print(f"  pages={len(pages)} chunks={len(chunks)} source_id={source_id}")

    if not replaced_source_ids:
        print("No PDFs ingested.", file=sys.stderr)
        return 1

    for record in existing_store.get("chunks", []):
        if record.get("source_id") not in replaced_source_ids:
            all_chunks.append(
                Chunk(
                    chunk_id=record["chunk_id"],
                    source_id=record["source_id"],
                    source_path=record["source_path"],
                    title=record["title"],
                    page_start=int(record["page_start"]),
                    page_end=int(record["page_end"]),
                    text=record["text"],
                )
            )

    chunk_records, idf = vectorize_chunks(all_chunks)
    vector_store = {
        "version": 1,
        "kind": "local-tfidf",
        "created_by": "latex-research-ingest",
        "updated_at": utc_now(),
        "chunk_count": len(chunk_records),
        "idf": {term: round(value, 8) for term, value in idf.items()},
        "chunks": chunk_records,
    }
    save_json(store / VECTOR_STORE, vector_store)

    manifest["sources"] = sorted(sources_by_id.values(), key=lambda item: item["path"])
    manifest["updated_at"] = utc_now()
    save_json(manifest_path, manifest)
    print(f"wrote {store / VECTOR_STORE}")
    return 0


def query_vector(query: str, idf: dict[str, float]) -> dict[str, float]:
    counts = Counter(tokenize(query))
    weights = {}
    for term, count in counts.items():
        if term in idf:
            weights[term] = (1 + math.log(count)) * idf[term]
    norm = math.sqrt(sum(value * value for value in weights.values())) or 1.0
    return {term: value / norm for term, value in weights.items()}


def retrieve(root: Path, query: str, limit: int) -> int:
    store_path = root / STORE_DIR / VECTOR_STORE
    if not store_path.is_file():
        print(f"No vector store found at {store_path}. Run ingest first.", file=sys.stderr)
        return 1
    store = load_json(store_path, {})
    qvec = query_vector(query, store.get("idf", {}))
    if not qvec:
        print("No query terms overlap the vector store vocabulary.", file=sys.stderr)
        return 1

    scored = []
    for chunk in store.get("chunks", []):
        vector = chunk.get("vector", {})
        score = sum(qweight * vector.get(term, 0.0) for term, qweight in qvec.items())
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)

    for rank, (score, chunk) in enumerate(scored[:limit], start=1):
        page = f"p. {chunk['page_start']}" if chunk["page_start"] == chunk["page_end"] else f"pp. {chunk['page_start']}-{chunk['page_end']}"
        snippet = re.sub(r"\s+", " ", chunk["text"]).strip()
        if len(snippet) > 900:
            snippet = snippet[:900].rsplit(" ", 1)[0] + " ..."
        print(f"[{rank}] score={score:.4f} {chunk['source_path']} {page} {chunk['chunk_id']}")
        print(snippet)
        print()
    return 0


def list_sources(root: Path) -> int:
    manifest_path = root / STORE_DIR / MANIFEST
    manifest = load_json(manifest_path, {"sources": []})
    sources = manifest.get("sources", [])
    if not sources:
        print("No ingested sources.")
        return 0
    for source in sources:
        print(f"{source['source_id']}\t{source['path']}\tpages={source.get('pages')} chunks={source.get('chunks')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Extract PDFs and build the local vector store")
    ingest_parser.add_argument("root", help="Repository root")
    ingest_parser.add_argument("pdfs", nargs="+", help="PDF files to ingest")

    retrieve_parser = subparsers.add_parser("retrieve", help="Retrieve chunks from the local vector store")
    retrieve_parser.add_argument("root", help="Repository root")
    retrieve_parser.add_argument("query", help="Search query")
    retrieve_parser.add_argument("--limit", type=int, default=5)

    list_parser = subparsers.add_parser("list", help="List ingested sources")
    list_parser.add_argument("root", help="Repository root")

    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")

    if args.command == "ingest":
        return ingest(root, [Path(pdf) for pdf in args.pdfs])
    if args.command == "retrieve":
        return retrieve(root, args.query, args.limit)
    if args.command == "list":
        return list_sources(root)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
