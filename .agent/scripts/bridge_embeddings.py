"""
bridge_embeddings.py - Phase 2: Cross-document semantic embeddings using sentence-transformers.

Generates embeddings from note pack content, finds semantically similar passages,
and creates [:SEMANTICALLYSIMILAR] relationships in Neo4j.
"""

import argparse
import os
import sys
import importlib
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# Auto-install logic
# ---------------------------------------------------------------------------

def _ensure_deps():
    """Auto-install required packages if missing."""
    required = {"numpy", "sentence-transformers", "neo4j"}
    for pkg in required:
        try:
            importlib.import_module(pkg.replace("-", "_"))
        except ImportError:
            print(f"[{Path(__file__).name}] Installing missing dependency: {pkg}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg, "-q"]
            )


def _ensure_model(model_name: str):
    """Download the sentence-transformers model if not already cached."""
    try:
        from sentence_transformers import SentenceTransformer
        SentenceTransformer(model_name)
    except Exception:
        print(f"[{Path(__file__).name}] Downloading model {model_name}...")
        from sentence_transformers import SentenceTransformer
        SentenceTransformer(model_name)


_ensure_deps()

import numpy as np
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """Split text into overlapping character-based chunks.

    Args:
        text: Input text to chunk.
        chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------------------------
# Note pack I/O
# ---------------------------------------------------------------------------

def load_pack_content(pack_path: str) -> str:
    """Read Original.md + Analysis.md from a note pack directory and return
    combined content.

    Args:
        pack_path: Path to the note pack directory.

    Returns:
        Combined text content of Original.md and Analysis.md.
    """
    pack = Path(pack_path)
    parts = []

    for filename in ("Original.md", "Analysis.md"):
        fpath = pack / filename
        if fpath.exists():
            parts.append(fpath.read_text(encoding="utf-8"))

    return "\n\n".join(parts)


def discover_packs(base_dir: str = ".raw") -> List[str]:
    """List all note pack directories under *base_dir*.

    A note pack is any subdirectory containing an Original.md file.

    Args:
        base_dir: Root directory to search for note packs.

    Returns:
        Sorted list of pack directory paths.
    """
    root = Path(base_dir)
    if not root.is_dir():
        print(f"[{Path(__file__).name}] Warning: base_dir '{base_dir}' not found.")
        return []

    packs = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and (entry / "Original.md").exists():
            packs.append(str(entry))

    return packs


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

def generate_embeddings(
    texts: List[str],
    model_name: str = "all-MiniLM-L6-v2",
) -> np.ndarray:
    """Generate embeddings for a list of texts using sentence-transformers.

    Args:
        texts: List of text strings to embed.
        model_name: Sentence-transformers model name.

    Returns:
        NumPy array of shape (len(texts), embedding_dim).
    """
    _ensure_model(model_name)
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True)
    return np.array(embeddings)


# ---------------------------------------------------------------------------
# Nearest-neighbour search
# ---------------------------------------------------------------------------

def find_nearest_neighbors(
    query_embedding: np.ndarray,
    all_embeddings: np.ndarray,
    texts: List[str],
    threshold: float = 0.7,
    top_k: int = 5,
) -> List[Tuple[str, float]]:
    """Find the nearest neighbours of *query_embedding* among *all_embeddings*
    using cosine similarity.

    Args:
        query_embedding: The query embedding vector (1-D).
        all_embeddings: Matrix of all candidate embeddings (N x D).
        texts: Corresponding text for each row in *all_embeddings*.
        threshold: Minimum cosine similarity to include a result.
        top_k: Maximum number of neighbours to return.

    Returns:
        List of (text, score) tuples sorted descending by score.
    """
    # Normalise vectors for cosine similarity
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-12)
    all_norm = all_embeddings / (
        np.linalg.norm(all_embeddings, axis=1, keepdims=True) + 1e-12
    )

    similarities = np.dot(all_norm, query_norm)

    # Sort descending
    indices = np.argsort(similarities)[::-1]

    results = []
    for idx in indices:
        score = float(similarities[idx])
        if score < threshold:
            break
        results.append((texts[idx], score))
        if len(results) >= top_k:
            break

    return results


# ---------------------------------------------------------------------------
# Neo4j relationship creation
# ---------------------------------------------------------------------------

def _get_or_create_entity(tx, name: str, type_: str, source: str):
    """MERGE an :Entity node and return its internal ID."""
    query = """
    MERGE (e:Entity {name: $name, type: $type, source: $source})
    ON CREATE SET e.count = 1, e.updated_at = timestamp()
    ON MATCH SET e.count = coalesce(e.count, 0) + 1, e.updated_at = timestamp()
    RETURN elementId(e) AS id
    """
    result = tx.run(query, name=name, type=type_, source=source)
    return result.single()["id"]


def create_similarity_relationships(
    driver,
    pack_name: str,
    chunk_texts: List[str],
    similar_chunks: List[List[Tuple[str, float]]],
    scores: List[List[float]],
):
    """Create [:SEMANTICALLYSIMILAR] relationships between Entity nodes.

    For each chunk in *chunk_texts*, an Entity node is created (or merged)
    with type='Chunk'. Then for each similar chunk returned from the NN search
    a [:SEMANTICALLYSIMILAR {score}] relationship is created.

    Args:
        driver: Neo4j driver instance.
        pack_name: Name of the pack these chunks belong to.
        chunk_texts: List of chunk text strings (the query chunks).
        similar_chunks: For each query chunk, the list of (similar_text, score)
            tuples returned by *find_nearest_neighbors*.
        scores: For each query chunk, list of scores corresponding to
            *similar_chunks* (same nesting).
    """
    with driver.session() as session:
        for i, chunk in enumerate(chunk_texts):
            source_name = f"{pack_name}::chunk::{i}"
            source_id = session.execute_write(
                _get_or_create_entity, source_name, "Chunk", pack_name
            )

            for j, (sim_text, score) in enumerate(similar_chunks[i]):
                target_name = f"{pack_name}::sim::{i}_{j}"
                target_id = session.execute_write(
                    _get_or_create_entity, target_name, "Chunk", pack_name
                )

                # Create the relationship
                session.run(
                    """
                    MATCH (a:Entity), (b:Entity)
                    WHERE elementId(a) = $source_id AND elementId(b) = $target_id
                    MERGE (a)-[r:SEMANTICALLYSIMILAR {score: $score}]->(b)
                    """,
                    source_id=source_id,
                    target_id=target_id,
                    score=score,
                )


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(
    driver,
    base_dir: str = ".raw",
    threshold: float = 0.7,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    top_k: int = 5,
    model: str = "all-MiniLM-L6-v2",
    dry_run: bool = False,
    verbose: bool = False,
):
    """Orchestrate the full embedding → similarity pipeline.

    Args:
        driver: Neo4j driver instance.
        base_dir: Root directory for note packs.
        threshold: Minimum cosine similarity threshold.
        chunk_size: Character chunk size.
        chunk_overlap: Character overlap between chunks.
        top_k: Maximum neighbours per query chunk.
        model: Sentence-transformers model name.
        dry_run: If True, print actions without writing to Neo4j.
        verbose: If True, print progress information.
    """
    packs = discover_packs(base_dir)
    if not packs:
        print("No note packs found. Exiting.")
        return

    if verbose:
        print(f"Discovered {len(packs)} pack(s): {[Path(p).name for p in packs]}")

    all_chunks: List[str] = []
    pack_chunk_map: List[Tuple[str, int, int]] = []  # (pack_name, start_idx, end_idx)

    for pack_path in packs:
        pack_name = Path(pack_path).name
        content = load_pack_content(pack_path)
        chunks = chunk_text(content, chunk_size=chunk_size, overlap=chunk_overlap)
        start = len(all_chunks)
        all_chunks.extend(chunks)
        end = len(all_chunks)
        pack_chunk_map.append((pack_name, start, end))

        if verbose:
            print(f"  {pack_name}: {len(chunks)} chunk(s) ({len(content)} chars)")

    if not all_chunks:
        print("No text to embed. Exiting.")
        return

    # Generate embeddings for all chunks at once
    if verbose:
        print(f"Generating embeddings for {len(all_chunks)} chunk(s) using '{model}'...")
    embeddings = generate_embeddings(all_chunks, model_name=model)

    if verbose:
        print(f"Embeddings shape: {embeddings.shape}")

    # For each pack, find cross-document similarities
    for pack_name, start, end in pack_chunk_map:
        if verbose:
            print(f"\nProcessing pack '{pack_name}' (chunks {start}:{end})...")

        pack_chunks = all_chunks[start:end]
        pack_embeddings = embeddings[start:end]

        pack_similar_chunks = []
        pack_scores = []

        for i, (chunk_text_, emb) in enumerate(zip(pack_chunks, pack_embeddings)):
            neighbours = find_nearest_neighbors(
                emb, embeddings, all_chunks,
                threshold=threshold, top_k=top_k,
            )
            # Filter out self-match
            neighbours = [(t, s) for t, s in neighbours if t != chunk_text_]

            sim_texts = [t for t, _ in neighbours]
            sim_scores = [s for _, s in neighbours]
            pack_similar_chunks.append(sim_texts)
            pack_scores.append(sim_scores)

            if verbose:
                print(f"    Chunk {i}: {len(neighbours)} neighbour(s)")

        if dry_run:
            print(f"  [DRY RUN] Would create similarity relationships for '{pack_name}'")
        else:
            create_similarity_relationships(
                driver, pack_name, pack_chunks, pack_similar_chunks, pack_scores
            )
            if verbose:
                print(f"  Created SEMANTICALLYSIMILAR relationships for '{pack_name}'")

    if verbose:
        print("\nPipeline complete.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _get_neo4j_driver():
    """Create a Neo4j driver from environment variables or defaults."""
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD", "")
    return GraphDatabase.driver(uri, auth=(user, password))


def main():
    parser = argparse.ArgumentParser(
        description="bridge_embeddings - Cross-document semantic similarity pipeline"
    )
    parser.add_argument(
        "--pack",
        type=str,
        default=None,
        help="Specific note pack name to process (default: all packs)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Cosine similarity threshold (default: 0.7)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=512,
        help="Character chunk size (default: 512)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=64,
        help="Character overlap between chunks (default: 64)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Maximum neighbours per query chunk (default: 5)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Sentence-transformers model name (default: all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing to Neo4j",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default=".raw",
        help="Root directory for note packs (default: .raw)",
    )

    args = parser.parse_args()

    # If a specific pack is requested, override base_dir
    if args.pack:
        base_dir = args.pack if os.path.isdir(args.pack) else os.path.join(args.base_dir, args.pack)
        if not os.path.isdir(base_dir):
            print(f"Error: pack directory not found: {base_dir}")
            sys.exit(1)
        driver = _get_neo4j_driver()
        run_pipeline(
            driver,
            base_dir=base_dir,
            threshold=args.threshold,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            top_k=args.top_k,
            model=args.model,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )
    else:
        driver = _get_neo4j_driver()
        run_pipeline(
            driver,
            base_dir=args.base_dir,
            threshold=args.threshold,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            top_k=args.top_k,
            model=args.model,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    main()
