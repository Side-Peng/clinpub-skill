#!/usr/bin/env python3
"""
PDF Reader - Extract text and metadata from academic PDFs

Optimized for reading academic papers with structure preservation.
Supports multi-column layouts, metadata extraction, and section detection.

Usage:
    python pdf_reader.py paper.pdf
    python pdf_reader.py paper.pdf --pages 1-5
    python pdf_reader.py paper.pdf --metadata
    python pdf_reader.py paper.pdf --sections

Dependencies:
    pip install pymupdf

Author: Clinical Data Analysis Skill
"""

import os
import sys
import re
import json
import argparse
from typing import Optional, List, Dict, Any, Tuple

try:
    import fitz  # pymupdf
except ImportError:
    print("Error: pymupdf required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


# ============================================================================
# Metadata Extraction
# ============================================================================

def extract_metadata(pdf_path: str) -> Dict[str, Any]:
    """Extract metadata from PDF."""
    doc = fitz.open(pdf_path)
    meta = doc.metadata

    result = {
        "file": os.path.basename(pdf_path),
        "pages": len(doc),
        "title": meta.get("title", "").strip(),
        "author": meta.get("author", "").strip(),
        "subject": meta.get("subject", "").strip(),
        "keywords": meta.get("keywords", "").strip(),
        "creator": meta.get("creator", "").strip(),
        "producer": meta.get("producer", "").strip(),
        "creation_date": meta.get("creationDate", "").strip(),
        "modification_date": meta.get("modDate", "").strip(),
    }

    # Try to extract DOI from text (first 2 pages)
    doi = extract_doi_from_text(doc, max_pages=2)
    if doi:
        result["doi"] = doi

    # Try to extract abstract from first page
    abstract = extract_abstract_from_text(doc)
    if abstract:
        result["abstract"] = abstract

    doc.close()
    return result


def extract_doi_from_text(doc, max_pages: int = 2) -> Optional[str]:
    """Try to extract DOI from PDF text."""
    doi_pattern = re.compile(r'(10\.\d{4,9}/[^\s&"\'<>]+)')
    for page_num in range(min(max_pages, len(doc))):
        text = doc[page_num].get_text()
        match = doi_pattern.search(text)
        if match:
            doi = match.group(1).rstrip('.')
            return doi
    return None


def extract_abstract_from_text(doc) -> Optional[str]:
    """Try to extract abstract from first page."""
    if len(doc) == 0:
        return None

    text = doc[0].get_text()

    # Common abstract patterns
    patterns = [
        r'(?:Abstract|ABSTRACT)[:\s]*\n?(.*?)(?:\n\n|\nKeywords|\nKey\s*[Ww]ords|\nIntroduction|\nINTRODUCTION)',
        r'(?:Abstract|ABSTRACT)[:\s]*(.*?)(?:\n\n|\nKeywords|\nKey\s*[Ww]ords)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            abstract = match.group(1).strip()
            # Clean up
            abstract = re.sub(r'\s+', ' ', abstract)
            if len(abstract) > 50:  # Reasonable abstract length
                return abstract

    return None


# ============================================================================
# Text Extraction
# ============================================================================

def extract_text_from_pdf(
    pdf_path: str,
    pages: Optional[str] = None,
    preserve_layout: bool = False,
    clean: bool = True
) -> str:
    """
    Extract text from PDF with optional page range.

    Args:
        pdf_path: Path to PDF file
        pages: Page range string (e.g., "1-5", "1,3,5", "3-", "-5")
        preserve_layout: If True, try to preserve visual layout
        clean: If True, clean up common PDF artifacts

    Returns:
        Extracted text as string
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    # Parse page range
    page_list = parse_page_range(pages, total_pages)

    texts = []
    for page_num in page_list:
        page = doc[page_num]

        if preserve_layout:
            # Use text blocks for layout preservation
            blocks = page.get_text("blocks")
            # Sort by y-coordinate first, then x-coordinate
            blocks.sort(key=lambda b: (b[1], b[0]))
            page_text = ""
            for block in blocks:
                if block[6] == 0:  # Text block (not image)
                    page_text += block[4] + "\n"
        else:
            page_text = page.get_text("text")

        if clean:
            page_text = clean_pdf_text(page_text)

        texts.append(f"--- Page {page_num + 1} ---\n{page_text}")

    doc.close()
    return "\n\n".join(texts)


def extract_text_by_sections(pdf_path: str) -> List[Dict[str, str]]:
    """
    Extract text organized by detected sections (academic paper structure).

    Returns:
        List of dicts with 'section' and 'content' keys
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"
    doc.close()

    full_text = clean_pdf_text(full_text)

    # Common section headers in academic papers
    section_patterns = [
        r'^(?:Abstract|ABSTRACT)\s*$',
        r'^(?:Introduction|INTRODUCTION)\s*$',
        r'^(?:Background|BACKGROUND)\s*$',
        r'^(?:Methods|METHODS|Materials and Methods|MATERIALS AND METHODS|'
        r'Methodology|METHODOLOGY|Study Design|STUDY DESIGN)\s*$',
        r'^(?:Results|RESULTS)\s*$',
        r'^(?:Discussion|DISCUSSION)\s*$',
        r'^(?:Conclusions?|CONCLUSIONS?)\s*$',
        r'^(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*$',
        r'^(?:Acknowledgments?|ACKNOWLEDGMENTS?|Acknowledgements?|ACKNOWLEDGEMENTS?)\s*$',
        r'^(?:Supplementary|SUPPLEMENTARY|Appendix|APPENDIX)\s*$',
        r'^(?:Limitations|LIMITATIONS)\s*$',
        r'^(?:Findings|FINDINGS)\s*$',
    ]

    combined_pattern = '|'.join(section_patterns)
    header_regex = re.compile(combined_pattern, re.MULTILINE)

    # Find all section headers
    matches = list(header_regex.finditer(full_text))

    if not matches:
        return [{"section": "Full Text", "content": full_text}]

    sections = []

    # Text before first section
    if matches[0].start() > 100:
        preamble = full_text[:matches[0].start()].strip()
        if preamble:
            sections.append({"section": "Preamble", "content": preamble})

    # Extract each section
    for i, match in enumerate(matches):
        section_name = match.group().strip()
        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(full_text)

        content = full_text[start:end].strip()

        # Clean section name
        section_name = re.sub(r'\s+', ' ', section_name)

        if content:
            sections.append({
                "section": section_name,
                "content": content
            })

    return sections


# ============================================================================
# Page Range Parsing
# ============================================================================

def parse_page_range(pages_str: Optional[str], total_pages: int) -> List[int]:
    """
    Parse page range string into list of 0-based page indices.

    Supports:
        "1-5"     -> pages 1,2,3,4,5
        "1,3,5"   -> pages 1,3,5
        "3-"      -> pages 3 to end
        "-5"      -> pages 1 to 5
        "all"     -> all pages
        None      -> all pages
    """
    if not pages_str or pages_str.lower() == "all":
        return list(range(total_pages))

    pages = []
    parts = pages_str.split(",")

    for part in parts:
        part = part.strip()

        if "-" in part:
            if part.startswith("-"):
                # "-5" -> pages 1 to 5
                end = int(part[1:])
                pages.extend(range(min(end, total_pages)))
            elif part.endswith("-"):
                # "3-" -> pages 3 to end
                start = int(part[:-1]) - 1
                pages.extend(range(max(0, start), total_pages))
            else:
                # "1-5" -> pages 1 to 5
                start, end = part.split("-")
                start_idx = max(0, int(start) - 1)
                end_idx = min(int(end), total_pages)
                pages.extend(range(start_idx, end_idx))
        else:
            page_num = int(part) - 1
            if 0 <= page_num < total_pages:
                pages.append(page_num)

    # Remove duplicates and sort
    return sorted(set(pages))


# ============================================================================
# Text Cleaning
# ============================================================================

def clean_pdf_text(text: str) -> str:
    """Clean up common PDF text extraction artifacts."""
    # Fix hyphenated line breaks (e.g., "analy-\nsis" -> "analysis")
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)

    # Remove excessive whitespace but preserve paragraph breaks
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove page numbers (standalone numbers on their own line)
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)

    # Remove header/footer artifacts
    text = re.sub(r'^\s*(?:Downloaded from|https?://\S+)\s*$', '', text, flags=re.MULTILINE)

    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)

    # Collapse multiple blank lines into two
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


# ============================================================================
# DOI-based Download Helper
# ============================================================================

def get_fulltext_url_from_doi(doi: str) -> Optional[str]:
    """
    Get potential full-text URL from DOI.
    Returns Unpaywall API URL for open access check.
    """
    # Unpaywall API (free, no key needed for basic use)
    # This provides OA links if available
    email = "clinical-analysis@example.com"  # Placeholder
    return f"https://api.unpaywall.org/v2/{doi}?email={email}"


# ============================================================================
# Output Formatting
# ============================================================================

def format_metadata(meta: Dict[str, Any]) -> str:
    """Format metadata for display."""
    lines = []
    lines.append("=" * 70)
    lines.append("PDF Metadata")
    lines.append("=" * 70)
    lines.append(f"File: {meta['file']}")
    lines.append(f"Pages: {meta['pages']}")

    if meta.get("title"):
        lines.append(f"Title: {meta['title']}")
    if meta.get("author"):
        lines.append(f"Author: {meta['author']}")
    if meta.get("doi"):
        lines.append(f"DOI: {meta['doi']}")
    if meta.get("abstract"):
        lines.append(f"\nAbstract:\n{meta['abstract']}")
    if meta.get("keywords"):
        lines.append(f"Keywords: {meta['keywords']}")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_sections(sections: List[Dict[str, str]]) -> str:
    """Format sections for display."""
    lines = []
    lines.append("=" * 70)
    lines.append("PDF Sections")
    lines.append("=" * 70)

    for sec in sections:
        lines.append(f"\n## {sec['section']}")
        lines.append("-" * 40)
        # Show first 500 chars of each section
        content = sec["content"]
        if len(content) > 500:
            content = content[:500] + f"\n... ({len(sec['content'])} chars total)"
        lines.append(content)

    return "\n".join(lines)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="PDF Reader - Extract text and metadata from academic PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract all text
    %(prog)s paper.pdf

    # Extract specific pages
    %(prog)s paper.pdf --pages 1-5

    # Show metadata only
    %(prog)s paper.pdf --metadata

    # Extract by sections
    %(prog)s paper.pdf --sections

    # Extract with layout preservation
    %(prog)s paper.pdf --layout

    # Save to file
    %(prog)s paper.pdf --output extracted.txt

    # JSON output
    %(prog)s paper.pdf --json
        """
    )

    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("--pages", help="Page range (e.g., '1-5', '1,3,5', '3-')")
    parser.add_argument("--metadata", action="store_true", help="Show metadata only")
    parser.add_argument("--sections", action="store_true", help="Extract by detected sections")
    parser.add_argument("--layout", action="store_true", help="Preserve visual layout")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--output", "-o", help="Save to file")
    parser.add_argument("--no-clean", action="store_true", help="Skip text cleaning")

    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        print(f"Error: File not found: {args.pdf}", file=sys.stderr)
        sys.exit(1)

    result = {}

    if args.metadata:
        meta = extract_metadata(args.pdf)
        if args.json:
            print(json.dumps(meta, indent=2, ensure_ascii=False))
        else:
            print(format_metadata(meta))
        return

    if args.sections:
        sections = extract_text_by_sections(args.pdf)
        if args.json:
            result["sections"] = sections
        else:
            print(format_sections(sections))
            return

    # Default: extract text
    text = extract_text_from_pdf(
        args.pdf,
        pages=args.pages,
        preserve_layout=args.layout,
        clean=not args.no_clean
    )

    if args.json:
        meta = extract_metadata(args.pdf)
        result["metadata"] = meta
        result["text"] = text
        result["pages_extracted"] = args.pages or "all"
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        output = text

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
