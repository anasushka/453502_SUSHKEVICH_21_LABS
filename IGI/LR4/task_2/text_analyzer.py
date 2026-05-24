# Laboratory Work #4
# Topic: Files, classes, serializers, regular expressions, and standard libraries.
# Program version: 1.0
# Developer: Sushkevich A.Y.
# Date of development: 2026-05-05

"""Text analysis logic for task 2."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from typing import List


WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё]+", re.UNICODE)
LETTER_RE = re.compile(r"[A-Za-zА-Яа-яЁё]", re.UNICODE)
PHONE_RE = re.compile(r"\b29\d{7}\b")
EMOJI_RE = re.compile(r"(?::|;)-*([()\[\]])\1*")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
VOWELS = set("аеёиоуыэюяAEIOUYаеёиоуыэюя")
CONSONANTS = set(
    "бвгджзйклмнпрстфхцчшщBCDFGHJKLMNPQRSTVWXYZбвгджзйклмнпрстфхцчшщ"
)


@dataclass
class AnalysisReport:
    """Container for text analysis results."""

    source_file: Path
    sentence_count: int
    declarative_count: int
    interrogative_count: int
    imperative_count: int
    avg_sentence_length: float
    avg_word_length: float
    emoji_count: int
    word_count: int
    word_count_by_spaces: int
    phones: List[str]
    words_second_consonant_third_vowel: List[str]
    letter_frequency: List[tuple[str, int]]
    sorted_phrases: List[str]

    def to_text(self) -> str:
        """Convert the report into a readable text block."""
        lines = [
            f"Source file: {self.source_file}",
            f"Total sentences: {self.sentence_count}",
            f"Declarative sentences: {self.declarative_count}",
            f"Interrogative sentences: {self.interrogative_count}",
            f"Imperative sentences: {self.imperative_count}",
            f"Average sentence length (characters, words only): {self.avg_sentence_length:.2f}",
            f"Average word length: {self.avg_word_length:.2f}",
            f"Total words (regex): {self.word_count}",
            f"Total words (bounded by spaces): {self.word_count_by_spaces}",
            f"Total smileys: {self.emoji_count}",
            "",
            "Phones (9 digits, start with 29):",
            ", ".join(self.phones) if self.phones else "None",
            "",
            "Words with second letter consonant and third letter vowel:",
            ", ".join(self.words_second_consonant_third_vowel)
            if self.words_second_consonant_third_vowel
            else "None",
            "",
            "Letter frequency:",
        ]
        if self.letter_frequency:
            for letter, count in self.letter_frequency:
                lines.append(f"{letter}: {count}")
        else:
            lines.append("None")
        lines.extend([
            "",
            "Comma-separated phrases in alphabetical order:",
            ", ".join(self.sorted_phrases) if self.sorted_phrases else "None",
        ])
        return "\n".join(lines)


class TextAnalyzerBase:
    """Base class with file I/O and ZIP archive helpers."""

    def read_text(self, file_path: str | Path) -> str:
        """Read text from a UTF-8 file."""
        return Path(file_path).read_text(encoding="utf-8")

    def write_text(self, file_path: str | Path, content: str) -> None:
        """Write text to a UTF-8 file."""
        Path(file_path).write_text(content, encoding="utf-8")

    def archive_file(self, file_path: str | Path, archive_path: str | Path) -> None:
        """Pack a file into a ZIP archive."""
        source = Path(file_path)
        with ZipFile(Path(archive_path), "w", compression=ZIP_DEFLATED) as zf:
            zf.write(source, arcname=source.name)

    def get_archive_info(self, archive_path: str | Path, member_name: str) -> str:
        """Return information about a file stored in the archive."""
        with ZipFile(Path(archive_path), "r") as zf:
            info = zf.getinfo(member_name)
            return (
                f"Archive member: {info.filename}\n"
                f"Compressed size: {info.compress_size} bytes\n"
                f"Original size: {info.file_size} bytes\n"
                f"Modified: {info.date_time}"
            )


class RegexTextAnalyzer(TextAnalyzerBase):
    """Text analyzer based on regular expressions.

    Inherits file I/O and archive helpers from TextAnalyzerBase.
    """

    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        return [
            part.strip()
            for part in SENTENCE_SPLIT_RE.split(text.strip())
            if part.strip()
        ]

    def count_sentence_type(self, sentence: str) -> str:
        """Determine the type of sentence by the last punctuation mark."""
        sentence = sentence.strip()
        if sentence.endswith("?"):
            return "question"
        if sentence.endswith("!"):
            return "exclamation"
        return "declarative"

    def extract_words(self, text: str) -> List[str]:
        """Extract all words from text using a regular expression."""
        return WORD_RE.findall(text)

    def count_words(self, text: str) -> int:
        """Count words in text using a regular expression."""
        return len(self.extract_words(text))

    def count_words_by_spaces(self, text: str) -> int:
        """Count words bounded by whitespace (simple split)."""
        return len(text.split())

    def average_sentence_length(self, sentences: List[str]) -> float:
        """Calculate average sentence length in characters, counting only words."""
        if not sentences:
            return 0.0
        total = sum(
            sum(len(w) for w in self.extract_words(s)) for s in sentences
        )
        return total / len(sentences)

    def average_word_length(self, text: str) -> float:
        """Calculate average word length in characters."""
        words = self.extract_words(text)
        if not words:
            return 0.0
        return sum(len(w) for w in words) / len(words)

    def count_emojis(self, text: str) -> int:
        """Count smileys according to the given rule."""
        return len(list(EMOJI_RE.finditer(text)))

    def extract_phones(self, text: str) -> List[str]:
        """Extract all 9-digit phone numbers that start with 29."""
        return PHONE_RE.findall(text)

    def words_second_consonant_third_vowel(self, text: str) -> List[str]:
        """Get words whose second letter is consonant and third is vowel."""
        result = []
        for word in self.extract_words(text):
            if len(word) >= 3 and word[1] in CONSONANTS and word[2] in VOWELS:
                result.append(word)
        return result

    def letter_frequency(self, text: str) -> List[tuple[str, int]]:
        """Count how many times each letter appears."""
        counter = Counter(l.lower() for l in LETTER_RE.findall(text))
        return sorted(counter.items(), key=lambda item: item[0])

    def sorted_comma_phrases(self, text: str) -> List[str]:
        """Return comma-separated phrases in alphabetical order."""
        phrases = [p.strip(" \t\r\n.;:!?") for p in text.split(",")]
        return sorted((p for p in phrases if p), key=str.lower)

    def analyze(self, file_path: str | Path) -> AnalysisReport:
        """Analyze the text file and return a structured report."""
        source = Path(file_path)
        text = self.read_text(source)
        sentences = self.split_sentences(text)

        declarative = interrogative = imperative = 0
        for s in sentences:
            kind = self.count_sentence_type(s)
            if kind == "declarative":
                declarative += 1
            elif kind == "question":
                interrogative += 1
            else:
                imperative += 1

        return AnalysisReport(
            source_file=source,
            sentence_count=len(sentences),
            declarative_count=declarative,
            interrogative_count=interrogative,
            imperative_count=imperative,
            avg_sentence_length=self.average_sentence_length(sentences),
            avg_word_length=self.average_word_length(text),
            emoji_count=self.count_emojis(text),
            word_count=self.count_words(text),
            word_count_by_spaces=self.count_words_by_spaces(text),
            phones=self.extract_phones(text),
            words_second_consonant_third_vowel=self.words_second_consonant_third_vowel(text),
            letter_frequency=self.letter_frequency(text),
            sorted_phrases=self.sorted_comma_phrases(text),
        )
