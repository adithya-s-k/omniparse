from abc import ABC, abstractmethod
import re
from collections import Counter
import string
from nltk.tokenize import sent_tokenize
from omniparse.web.model_loader import load_nltk_punkt


# Define the abstract base class for chunking strategies
class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> list:
        """
        Abstract method to chunk the given text.
        """
        pass


# Regex-based chunking
class RegexChunking(ChunkingStrategy):
    def __init__(self, patterns=None, **kwargs):
        if patterns is None:
            patterns = [r"\n\n"]  # Default split pattern
        self.patterns = patterns

    def chunk(self, text: str) -> list:
        paragraphs = [text]
        for pattern in self.patterns:
            new_paragraphs = []
            for paragraph in paragraphs:
                new_paragraphs.extend(re.split(pattern, paragraph))
            paragraphs = new_paragraphs
        return paragraphs


# NLP-based sentence chunking
class NlpSentenceChunking(ChunkingStrategy):
    def __init__(self, **kwargs):
        load_nltk_punkt()
        pass

    def chunk(self, text: str) -> list:
        sentences = sent_tokenize(text)
        sens = [sent.strip() for sent in sentences]

        return list(set(sens))


# Topic-based segmentation using TextTiling
class TopicSegmentationChunking(ChunkingStrategy):
    def __init__(self, num_keywords=3, **kwargs):
        import nltk as nl

        self.tokenizer = nl.toknize.TextTilingTokenizer()
        self.num_keywords = num_keywords

    def chunk(self, text: str) -> list:
        # Use the TextTilingTokenizer to segment the text
        segmented_topics = self.tokenizer.tokenize(text)
        return segmented_topics

    def extract_keywords(self, text: str) -> list:
        # Tokenize and remove stopwords and punctuation
        import nltk as nl

        tokens = nl.toknize.word_tokenize(text)
        tokens = [
            token.lower()
            for token in tokens
            if token not in nl.corpus.stopwords.words("english")
            and token not in string.punctuation
        ]

        # Calculate frequency distribution
        freq_dist = Counter(tokens)
        keywords = [word for word, freq in freq_dist.most_common(self.num_keywords)]
        return keywords

    def chunk_with_topics(self, text: str) -> list:
        # Segment the text into topics
        segments = self.chunk(text)
        # Extract keywords for each topic segment
        segments_with_topics = [
            (segment, self.extract_keywords(segment)) for segment in segments
        ]
        return segments_with_topics


# Fixed-length word chunks
class FixedLengthWordChunking(ChunkingStrategy):
    def __init__(self, chunk_size=100, **kwargs):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list:
        words = text.split()
        return [
            " ".join(words[i : i + self.chunk_size])
            for i in range(0, len(words), self.chunk_size)
        ]


# Sliding window chunking
class SlidingWindowChunking(ChunkingStrategy):
    def __init__(self, window_size=100, step=50, **kwargs):
        self.window_size = window_size
        self.step = step

    def chunk(self, text: str) -> list:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.step):
            chunks.append(" ".join(words[i : i + self.window_size]))
        return chunks


# Structural cue based chunking
class StructuralCueChunking(ChunkingStrategy):
    """
    Inspired by https://jina.ai/tokenizer/#chunking which leverage common structural cues 
    and build a set of rules and heuristics which should perform exceptionally well across 
    diverse types of content, including Markdown, HTML, LaTeX, and more, 
    ensuring accurate segmentation of text into meaningful chunks.
    
    Reference: https://gist.github.com/JeremiahZhang/2f8ae87dad836b25f40c02b8c43d16ec
    Original x post: https://x.com/JinaAI_/status/1823756993108304135
    """
    def __init__(self, max_chunk_size: int=500, **kwargs):
        """
        Args:
            max_chunk_size (int, optional): The maximum size of a chunk. Defaults to 500.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        import regex
        self.MAX_TABLE_ROWS = 20
        self.LOOKAHEAD_RANGE = 100
        self.MAX_HEADING_LENGTH = 7
        self.MAX_SENTENCE_LENGTH = 400
        self.MAX_NESTED_LIST_ITEMS = 6
        self.MAX_BLOCKQUOTE_LINES = 15
        self.MAX_NESTED_PARENTHESES = 5
        self.MAX_LIST_INDENT_SPACES = 7
        self.MAX_LIST_ITEM_LENGTH = 200
        self.MAX_TABLE_CELL_LENGTH = 200
        self.MAX_MATH_BLOCK_LENGTH = 500
        self.MAX_PARAGRAPH_LENGTH = 1000
        self.MAX_QUOTED_TEXT_LENGTH = 300
        self.MAX_INDENTED_CODE_LINES = 20
        self.MAX_CODE_BLOCK_LENGTH = 1500
        self.MAX_HTML_TABLE_LENGTH = 2000
        self.MAX_MATH_INLINE_LENGTH = 100
        self.MAX_CODE_LANGUAGE_LENGTH = 20
        self.MIN_HORIZONTAL_RULE_LENGTH = 3
        self.max_chunk_size = max_chunk_size
        self.MAX_BLOCKQUOTE_LINE_LENGTH = 200
        self.MAX_HEADING_CONTENT_LENGTH = 200
        self.MAX_STANDALONE_LINE_LENGTH = 800
        self.MAX_HEADING_UNDERLINE_LENGTH = 200
        self.MAX_HTML_TAG_CONTENT_LENGTH = 1000
        self.MAX_HTML_TAG_ATTRIBUTES_LENGTH = 100
        self.MAX_PARENTHETICAL_CONTENT_LENGTH = 200
        self.MAX_HTML_HEADING_ATTRIBUTES_LENGTH = 100
        
        self.pattern = self.__pattern__()
        
    def __pattern__(self) -> str:
        
        # 1. Headings (Setext-style, Markdown, and HTML-style, with length constraints)
        heading_regex = rf"""(?:^(?:[#*=-]{{1,{self.MAX_HEADING_LENGTH}}}|\w[^\r\n]{{0,{self.MAX_HEADING_CONTENT_LENGTH}}}\r?\n[-=]{{2,{self.MAX_HEADING_UNDERLINE_LENGTH}}}|<h[1-6][^>]{{0,{self.MAX_HTML_HEADING_ATTRIBUTES_LENGTH}}}>)[^\r\n]{{1,{self.MAX_HEADING_CONTENT_LENGTH}}}(?:</h[1-6]>)?(?:\r?\n|$))"""

        # 2. New pattern for citations
        citation_regex = rf"(?:\[[0-9]+\][^\r\n]{{1,{self.MAX_STANDALONE_LINE_LENGTH}}})"

        # 3. List items (bulleted, numbered, lettered, or task lists, including nested, up to three levels, with length constraints)
        list_item_regex = rf"(?:(?:^|\r?\n)[ \t]{{0,3}}(?:[-*+•]|\d{{1,3}}\.\w\.|\[[ xX]\])[ \t]+(?:(?:\b[^\r\n]{{1,{self.MAX_LIST_ITEM_LENGTH}}}\b(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:\b[^\r\n]{{1,{self.MAX_LIST_ITEM_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{1,{self.MAX_LIST_ITEM_LENGTH}}}\b(?=[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?))"
        list_item_regex += rf"(?:(?:\r?\n[ \t]{{2,5}}(?:[-*+•]|\d{{1,3}}\.\w\.|\[[ xX]\])[ \t]+(?:(?:\b[^\r\n]{{1,{self.MAX_LIST_ITEM_LENGTH}}}\b(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:\b[^\r\n]{{1,${self.MAX_LIST_ITEM_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{1,${self.MAX_LIST_ITEM_LENGTH}}}\b(?=[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?)))"
        list_item_regex += rf"{{0,{self.MAX_NESTED_LIST_ITEMS}}}(?:\r?\n[ \t]{{4,{self.MAX_LIST_INDENT_SPACES}}}(?:[-*+•]|\d{{1,3}}\.\w\.|\[[ xX]\])[ \t]+(?:(?:\b[^\r\n]{{1,{self.MAX_LIST_ITEM_LENGTH}}}\b(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:\b[^\r\n]{{1,{self.MAX_LIST_ITEM_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{1,{self.MAX_LIST_ITEM_LENGTH}}}\b(?=[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?)))"
        list_item_regex += rf"{{0,{self.MAX_NESTED_LIST_ITEMS}}})?)"

        # 4. Block quotes (including nested quotes and citations, up to three levels, with length constraints)
        block_regex = rf"(?:(?:^>(?:>|\s{{2,}}){{0,2}}(?:(?:\b[^\r\n]{{0,{self.MAX_BLOCKQUOTE_LINE_LENGTH}}}\b(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:\b[^\r\n]{{0,{self.MAX_BLOCKQUOTE_LINE_LENGTH}}}\b(?=[\r\n]|$))|(?:\b[^\r\n]{{0,{self.MAX_BLOCKQUOTE_LINE_LENGTH}}}\b(?=[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?))\r?\n?){{1,{self.MAX_BLOCKQUOTE_LINES}}})"

        # 5. Code blocks (fenced, indented, or HTML pre/code tags, with length constraints)
        code_block_regex = rf"(?:(?:^|\r?\n)(?:\`\`\`|~~~)(?:\w{{0,{self.MAX_CODE_LANGUAGE_LENGTH}}})?\r?\n[\s\S]{{0,{self.MAX_CODE_BLOCK_LENGTH}}}?(?:\`\`\`|~~~)\r?\n?"
        code_block_regex += rf"|(?:(?:^|\r?\n)(?: {{4}}|\t)[^\r\n]{{0,{self.MAX_LIST_ITEM_LENGTH}}}(?:\r?\n(?: {{4}}|\t)[^\r\n]{{0,{self.MAX_LIST_ITEM_LENGTH}}}){{0,{self.MAX_INDENTED_CODE_LINES}}}\r?\n?)"
        code_block_regex += rf"|(?:<pre>(?:<code>)?[\s\S]{{0,{self.MAX_CODE_BLOCK_LENGTH}}}?(?:</code>)?</pre>))"

        # 6. Tables (Markdown, grid tables, and HTML tables, with length constraints)
        table_regex = rf"(?:(?:^|\r?\n)(?:\|[^\r\n]{{0,{self.MAX_TABLE_CELL_LENGTH}}}\|(?:\r?\n\|[-:]{{1,{self.MAX_TABLE_CELL_LENGTH}}}\|){{0,1}}(?:\r?\n\|[^\r\n]{{0,{self.MAX_TABLE_CELL_LENGTH}}}\|){{0,{self.MAX_TABLE_ROWS}}}"
        table_regex += rf"|<table>[\s\S]{{0,{self.MAX_HTML_TABLE_LENGTH}}}?</table>))"

        # 7. Horizontal rules (Markdown and HTML hr tag)
        horizontal_rule_regex = rf"(?:^(?:[-*_]){{{self.MIN_HORIZONTAL_RULE_LENGTH},}}\s*$|<hr\s*/?>)"

        # 8. Standalone lines or phrases (including single-line blocks and HTML elements, with length constraints)
        single_line_regex = rf"(?:^(?:<[a-zA-Z][^>]{{0,{self.MAX_HTML_TAG_ATTRIBUTES_LENGTH}}}>)?(?:(?:[^\r\n]{{1,{self.MAX_STANDALONE_LINE_LENGTH}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:[^\r\n]{{1,{self.MAX_STANDALONE_LINE_LENGTH}}}(?=[\r\n]|$))|(?:[^\r\n]{{1,{self.MAX_STANDALONE_LINE_LENGTH}}}(?=[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?))(?:</[a-zA-Z]+>)?(?:\r?\n|$))"

        # 9. Sentences or phrases ending with punctuation (including ellipsis and Unicode punctuation)
        sentence_regex = rf"(?:(?:[^\r\n]{{1,{self.MAX_SENTENCE_LENGTH}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:[^\r\n]{{1,{self.MAX_SENTENCE_LENGTH}}}(?=[\r\n]|$))|(?:[^\r\n]{{1,{self.MAX_SENTENCE_LENGTH}}}(?=[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.\.\.|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?))"

        # 10. Quoted text, parenthetical phrases, or bracketed content (with length constraints)
        quoted_text = "(?:"
        quoted_text += rf"(?<!\w)\"\"\"[^\"]{{0,{self.MAX_QUOTED_TEXT_LENGTH}}}\"\"\"(?!\w)"
        quoted_text += rf"""|(?<!\w)(?P<quote>['"\`'"])[^\r\n]{{0,{self.MAX_QUOTED_TEXT_LENGTH}}}(?P=quote)(?!\w)"""
        quoted_text += rf"|\([^\r\n()]{{0,{self.MAX_PARENTHETICAL_CONTENT_LENGTH}}}(?:\([^\r\n()]{{0,{self.MAX_PARENTHETICAL_CONTENT_LENGTH}}}\)[^\r\n()]{{0,{self.MAX_PARENTHETICAL_CONTENT_LENGTH}}}){{0,{self.MAX_NESTED_PARENTHESES}}}\)"
        quoted_text += rf"|\[[^\r\n\[\]]{{0,{self.MAX_PARENTHETICAL_CONTENT_LENGTH}}}(?:\[[^\r\n\[\]]{{0,{self.MAX_PARENTHETICAL_CONTENT_LENGTH}}}\][^\r\n\[\]]{{0,{self.MAX_PARENTHETICAL_CONTENT_LENGTH}}}){{0,{self.MAX_NESTED_PARENTHESES}}}\]"
        quoted_text += rf"|\$[^\r\n$]{{0,{self.MAX_MATH_INLINE_LENGTH}}}\$"
        quoted_text += rf"|\`[^\`\r\n]{{0,{self.MAX_MATH_INLINE_LENGTH}}}\`"
        quoted_text += ")"

        # 11. Paragraphs (with length constraints)
        paragraph_regex = rf"(?:(?:^|\r?\n\r?\n)(?:<p>)?(?:(?:[^\r\n]{{1,{self.MAX_PARAGRAPH_LENGTH}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:[^\r\n]{{1,{self.MAX_PARAGRAPH_LENGTH}}}(?=[\r\n]|$))|(?:[^\r\n]{{1,{self.MAX_PARAGRAPH_LENGTH}}}(?=[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?))(?:</p>)?(?=\r?\n\r?\n|$))"

        # 12. HTML-like tags and their content (including self-closing tags and attributes, with length constraints)
        html_like_regex = rf"(?:<[a-zA-Z][^>]{{0,{self.MAX_HTML_TAG_ATTRIBUTES_LENGTH}}}(?:>[\s\S]{{0,{self.MAX_HTML_TAG_CONTENT_LENGTH}}}?</[a-zA-Z]+>|\s*/>))"

        #13. LaTeX-style math expressions (inline and block, with length constraints)
        latex_regex = rf"(?:(?:\$\$[\s\S]{{0,{self.MAX_MATH_BLOCK_LENGTH}}}?\$\$)|(?:\$[^\$\r\n]{{0,{self.MAX_MATH_INLINE_LENGTH}}}\$))"

        # 14. Fallback for any remaining content (with length constraints)
        fallback_regex = rf"(?:(?:[^\r\n]{{1,{self.MAX_STANDALONE_LINE_LENGTH}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))|(?:[^\r\n]{{1,{self.MAX_STANDALONE_LINE_LENGTH}}}(?=[\r\n]|$))|(?:[^\r\n]{{1,{self.MAX_STANDALONE_LINE_LENGTH}}}(?=[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?:.{{1,{self.LOOKAHEAD_RANGE}}}(?:[.!?…]|\.{{3}}|[\u2026\u2047-\u2049]|[\p{{Emoji_Presentation}}\p{{Extended_Pictographic}}])(?=\s|$))?))"
        
        return re.compile('|'.join((f"({heading_regex}", citation_regex, list_item_regex, block_regex, code_block_regex, table_regex, horizontal_rule_regex, single_line_regex, sentence_regex, quoted_text, paragraph_regex, html_like_regex, latex_regex, f"{fallback_regex})")), re.MULTILINE | re.DOTALL)

    def chunk(self, text: str) -> list:
        """
        Breaks down a given text into smaller chunks based on common stuctural cues and maximum chunk size.
        
        Args:
            text (str): The input text to be chunked.
        
        Returns:
            list: A list of chunked text, where each chunk is a string.
        """
        chunks = re.findall(self.pattern, text)
        
        temp_chunk = ""
        final_chunks = []
        
        for chunk in chunks:
            chunk=chunk[0]
            if len(temp_chunk) + len(chunk) > self.max_chunk_size:
                final_chunks.append(temp_chunk.strip())
                temp_chunk = chunk
            else:
                temp_chunk += chunk
        
        if temp_chunk:
            final_chunks.append(temp_chunk.strip())
        
        # If a chunk is too large, break it down further
        refined_chunks = []
        for chunk in final_chunks:
            if len(chunk) > self.max_chunk_size:
                sentences = re.split(r'(?<=[.!?]) +', chunk)  # Split by sentence
                temp_chunk = ""
                for sentence in sentences:
                    if len(temp_chunk) + len(sentence) > self.max_chunk_size:
                        refined_chunks.append(temp_chunk.strip())
                        temp_chunk = sentence
                    else:
                        temp_chunk += f" {sentence}"
                if temp_chunk:
                    refined_chunks.append(temp_chunk.strip())
            else:
                refined_chunks.append(chunk)
        
        return refined_chunks