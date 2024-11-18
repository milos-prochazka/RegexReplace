import re
from typing import List
from typing import Dict

class SpannedElement:

    name: str = ""
    text: str = ""
    start: int = 0
    end: int = 0
    spans = []
    ownded: bool = False

    def __init__(self,name, text, start, end):
        self.text = text
        self.start = start
        self.end = end

    def __str__(self):
        index = 0
        result = ""
        for span in self.spans:
            # Add the text before the span
            if index < span.start:
                result += self.text[index:span.start]
            # Add the span
            result += str(span)
            index = span.end

        # Add the remaining text
        if index < self.end:
            result += self.text[index:self.end]

        return result

class SpannedText:
    text: str = ""
    spans: List[SpannedElement] = []
    spans_dict: dict = {}

    def _set_span_children(self, index:int):
        selfSpan = self.spans[index]
        for i in range(index+1,len(self.spans)):
            child = self.spans[i]
            if not child.ownded and child.start >= selfSpan.start and child.end <= selfSpan.end:
                selfSpan.spans.append(child)
                child.owned = True
                self._set_span_children(i)


    def __init__(self, match: re.Match):

        # Create a list of SpannedElement objects        
        for i in range(0, len(match.groups())):
            span = SpannedElement(match.group(i), match.group(i), match.start(i), match.end(i))        
            self.spans.append(span)

        # Create a dictionary of SpannedElement objects
        for name in match.groupdict():
            index = match.re.groupindex[name]
            self.spans[index].name = name
            self.spans_dict[name] = self.spans[index]

        # Set the children of each span
        self._set_span_children(0)

        # Sort children by start position
        for span in self.spans:
            span.spans.sort(key=lambda x: x.start)

    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        if (self.text != ""):
            return self.text
        elif (len(self.spans) > 0):
            return str(self.spans[0])
        else:
            return ""

    def setText(self, text: str):
        """
        Sets the text for the object.

        Args:
            text (str): The text to be set.
        """
        self.text = text

    def setText(self, name: str, text: str):
        """
        Sets the text for a given span name and clears its spans.

        Args:
            name (str): The name of the span to update.
            text (str): The new text to set for the span.
        """
        if name in self.spans_dict:
            span = self.spans_dict[name]
            span.text = text
            span.spans.clear()

    def setText(self, index: int, text: str):
        """
        Sets the text of the span at the specified index.

        Args:
            index (int): The index of the span to update.
            text (str): The new text to set for the span.
        """
        if index < len(self.spans):
            span = self.spans[index]
            span.text = text

    def getText(self):
        """
        Retrieves the text if it is not empty; otherwise, returns the string representation of the first span.

        Returns:
            str: The text if it is not empty, otherwise the string representation of the first span.
        """
        if (self.text != ""):
            return self.text
        else:
            return str(self.spans[0])
        

if __name__ == "__main__": 
    p = re.compile(r"(?P<first>\w+) (?P<last>\w+)")
    m = p.fullmatch (r"zilofon Reynolds")
    print(m[0].groups())
