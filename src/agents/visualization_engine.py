"""Visualization engine for generating interactive HTML diagrams from the literature."""

import json
from typing import Optional

from anthropic import Anthropic
from loguru import logger

from src.agents.prompts import VISUALIZATION_SYSTEM_PROMPT, VISUALIZATION_USER_PROMPT
from src.config.settings import settings
from src.rag.retriever import Retriever


class VisualizationEngine:
    """Generates interactive HTML visualizations from the literature corpus."""

    def __init__(self, retriever: Optional[Retriever] = None):
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.retriever = retriever or Retriever()
        self._load_papers_metadata()

    def _load_papers_metadata(self):
        """Load papers metadata for the papers list."""
        try:
            import json
            from pathlib import Path

            candidates = [
                Path("./data/papers_metadata.json"),
                Path(__file__).parent.parent.parent / "data" / "papers_metadata.json",
            ]
            for p in candidates:
                if p.exists():
                    with open(p) as f:
                        self.papers = json.load(f)
                    return
            self.papers = []
        except Exception as e:
            logger.warning(f"Could not load papers metadata: {e}")
            self.papers = []

    def _format_papers_list(self) -> str:
        """Format a compact list of all papers for the prompt."""
        lines = []
        for p in self.papers:
            authors = p.get("authors", "Unknown")
            if isinstance(authors, list):
                authors = "; ".join(authors)
            year = p.get("year", "n.d.")
            title = p.get("title", "Untitled")
            pub = p.get("publication", "")
            lines.append(f"- {authors} ({year}). {title}. {pub}")
        return "\n".join(lines)

    def generate_visualization(
        self,
        request: str,
        n_results: int = 20,
        year_range: Optional[tuple] = None,
    ) -> str:
        """
        Generate an interactive HTML visualization based on a user request.

        Args:
            request: Description of desired visualization
            n_results: Number of chunks to retrieve for context
            year_range: Optional (min_year, max_year) filter

        Returns:
            Complete HTML string
        """
        # Retrieve relevant context
        min_year = year_range[0] if year_range else None
        max_year = year_range[1] if year_range else None
        results = self.retriever.retrieve(
            query=request,
            n_results=n_results,
            min_year=min_year,
            max_year=max_year,
        )

        # Build context from results (RetrievalResult Pydantic model with .chunk attribute)
        context_parts = []
        for r in results:
            chunk = r.chunk
            authors = "; ".join(chunk.authors) if chunk.authors else "Unknown"
            year = chunk.year or ""
            title = chunk.title or ""
            text = chunk.text or ""
            context_parts.append(
                f"**[{authors} ({year}): {title}]**\n{text}\n"
            )
        context = "\n---\n".join(context_parts)

        papers_list = self._format_papers_list()

        # Build prompt
        user_prompt = VISUALIZATION_USER_PROMPT.format(
            context=context,
            papers_list=papers_list,
            request=request,
        )

        # Call Claude with high token limit for HTML generation
        logger.info(f"Generating visualization for: {request[:80]}...")
        response = self.client.messages.create(
            model=settings.llm_model,
            max_tokens=8000,
            temperature=0.7,
            system=VISUALIZATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        html_content = response.content[0].text

        # Extract HTML if wrapped in code blocks
        if "```html" in html_content:
            start = html_content.index("```html") + 7
            end = html_content.rindex("```")
            html_content = html_content[start:end].strip()
        elif "```" in html_content:
            start = html_content.index("```") + 3
            end = html_content.rindex("```")
            html_content = html_content[start:end].strip()

        logger.info(f"Generated HTML visualization: {len(html_content)} chars")
        return html_content
