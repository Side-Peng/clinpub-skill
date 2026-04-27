# Tests

This directory contains tests for the clinpub tool scripts.

## Running Tests

```bash
# Test data profiler
python tests/test_data_profiler.py

# Test NCBI search (requires network)
python tests/test_ncbi_search.py
```

## Test Coverage TODO

- [ ] test_data_profiler.py — data profiling from sample CSV
- [ ] test_ncbi_search.py — NCBI search with mock responses
- [ ] test_pubmed_search.py — PubMed query conversion
- [ ] test_pdf_reader.py — PDF metadata extraction
- [ ] test_tavily_search.py — Tavily search (requires API key)
