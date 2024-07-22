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
            if token not in nl.corpus.stopwords.words("english") and token not in string.punctuation
        ]

        # Calculate frequency distribution
        freq_dist = Counter(tokens)
        keywords = [word for word, freq in freq_dist.most_common(self.num_keywords)]
        return keywords

    def chunk_with_topics(self, text: str) -> list:
        # Segment the text into topics
        segments = self.chunk(text)
        # Extract keywords for each topic segment
        segments_with_topics = [(segment, self.extract_keywords(segment)) for segment in segments]
        return segments_with_topics


# Fixed-length word chunks
class FixedLengthWordChunking(ChunkingStrategy):
    def __init__(self, chunk_size=100, **kwargs):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list:
        words = text.split()
        return [" ".join(words[i : i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]


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
