# Agent Transcript 02 — Debugging and Knowledge Base Ingestion

## Goal

Load Lenny's Podcast transcripts into PostgreSQL + pgvector and make them available to the RAG retrieval layer.

## Initial Problem

The ingestion script was executed directly:

```bash
python scripts/ingest.py