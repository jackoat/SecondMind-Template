"""
bridge_entities.py — Entity extraction pipeline for note packs.

Extracts named entities from note pack content using spaCy,
merges them into Neo4j, and creates [:CONTAINS] relationships
between packs and entities.

Dependencies:
  pip install spacy
  python -m spacy download en_core_web_sm

Usage:
  python -m .agent.scripts.bridge_entities [--pack PACK_NAME]
"""

import os
import sys
import json
import logging
import argparse
from typing import List, Dict, Optional
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Auto-install logic
_SPACY_INSTALLED = False
try:
    import spacy
    _SPACY_INSTALLED = True
except ImportError:
    logger.info("spaCy not found. Installing...")
    os.system(f"{sys.executable} -m pip install spacy")
    import spacy
    _SPACY_INSTALLED = True

# Auto-download model
_MODEL_READY = False
try:
    nlp = spacy.load("en_core_web_sm")
    _MODEL_READY = True
except OSError:
    logger.info("Downloading spaCy model en_core_web_sm...")
    os.system(f"{sys.executable} -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    _MODEL_READY = True

from bridge_graph import Neo4jBridge, get_note_pack_file_path


def extract_entities(text: str) -> List[Dict]:
    """Extract named entities from text using spaCy."""
    doc = nlp(text)
    entities = []
    seen = set()
    for ent in doc.ents:
        key = (ent.text.lower(), ent.label_)
        if key not in seen:
            seen.add(key)
            entities.append({
                "name": ent.text.strip(),
                "type": ent.label_,
                "source": "bridge_entities",
                "count": 1,
            })
    # Merge duplicates by name+type
    merged = {}
    for e in entities:
        key = (e["name"].lower(), e["type"])
        if key in merged:
            merged[key]["count"] += 1
        else:
            merged[key] = e
    return list(merged.values())


def process_pack(pack_name: str, bridge: Neo4jBridge, base_dir: str = ".raw"):
    """Extract entities from a note pack and merge into Neo4j."""
    entities = []

    for file_key in ["original", "analysis"]:
        file_path = get_note_pack_file_path(pack_name, file_key, base_dir)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                text = f.read()
            pack_entities = extract_entities(text)
            entities.extend(pack_entities)
            logger.info(f"  Extracted {len(pack_entities)} entities from {file_key}")

    # Merge entities into graph
    for e in entities:
        bridge.merge_pack_node("Entity", e["name"],
                              type_=e["type"],
                              source=e["source"],
                              count=e["count"])
        # Create relationship between pack and entity
        query = """
        MATCH (p:NotePack {name: $pack_name})
        MATCH (e:Entity {name: $entity_name})
        MERGE (p)-[:CONTAINS]->(e)
        """
        bridge.run(query, pack_name=pack_name, entity_name=e["name"])

    logger.info(f"  Merged {len(entities)} entities for pack '{pack_name}'")
    return entities


def process_all_packs(bridge: Neo4jBridge, base_dir: str = ".raw"):
    """Process all note packs in the base directory."""
    if not os.path.isdir(base_dir):
        logger.warning(f"Base directory '{base_dir}' not found.")
        return {}

    all_results = {}
    for item in sorted(os.listdir(base_dir)):
        pack_path = os.path.join(base_dir, item)
        if os.path.isdir(pack_path) and not item.startswith("."):
            has_original = os.path.exists(os.path.join(pack_path, "Original.md"))
            has_analysis = os.path.exists(os.path.join(pack_path, "Analysis.md"))
            if has_original or has_analysis:
                logger.info(f"Processing pack: {item}")
                entities = process_pack(item, bridge, base_dir)
                all_results[item] = entities
    return all_results


def main():
    parser = argparse.ArgumentParser(description="Extract entities from note packs into Neo4j")
    parser.add_argument("--pack", type=str, help="Specific pack name to process (default: all)")
    parser.add_argument("--base-dir", type=str, default=".raw", help="Base directory for note packs")
    args = parser.parse_args()

    with Neo4jBridge() as bridge:
        if args.pack:
            process_pack(args.pack, bridge, args.base_dir)
        else:
            process_all_packs(bridge, args.base_dir)


if __name__ == "__main__":
    main()
