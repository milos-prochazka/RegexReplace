import re
from typing import List
from typing import Dict

class SpannedElement:

    name: str = ""
    text: str = ""
    start: int = 0
    end: int = 0
    owned: bool = False

    def __init__(self,name, text, start, end):
        self.spans = []
        self.text = text
        self.start = start
        self.end = end

    def __str__(self):
        index = self.start
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
            result += self.text[index-self.start:]

        return result

class SpannedText:
    text: str = ""
    spans: List[SpannedElement]
    spans_dict: dict
    lineNumber: int = 0

    def _set_span_children(self, index:int):
        selfSpan = self.spans[index]
        for i in range(index+1,len(self.spans)):
            child = self.spans[i]
            if not child.owned and child.start >= selfSpan.start and child.end <= selfSpan.end:
                selfSpan.spans.append(child)
                child.owned = True
                print (f"Adding {child.text} to {selfSpan.text}")
                self._set_span_children(i)


    def __init__match(self, match: re.Match):

        offset = match.start()

        # Create a list of SpannedElement objects        
        for i in range(0, len(match.groups())+1):
            span = SpannedElement(match.group(i), match.group(i), match.start(i)-offset, match.end(i)-offset)        
            self.spans.append(span)

        # Create a dictionary of SpannedElement objects
        for name in match.groupdict():
            index = match.re.groupindex[name]
            self.spans[index].name = name
            self.spans_dict[name] = self.spans[index]

        # Set the children of each span
        if len(self.spans)>0:
            self.spans[0].owned = True
            self._set_span_children(0)

        # Sort children by start position
        for span in self.spans:
            if (len(span.spans) > 0):   
                span.spans.sort(key=lambda x: x.start)

    def __init__str(self, text: str):
        self.text = text

    def __init__(self, pattern=None):
        self.spans = []
        self.spans_dict = {}
        if isinstance(pattern, re.Match):
            self.__init__match(pattern)
        elif isinstance(pattern, str):
            self.__init__str(pattern)

    @staticmethod
    def listFromPattern(pattern: re.Pattern, text: str) -> List['SpannedText']:
        """
        Generate a list of SpannedText objects from a given regex pattern and text.
        Args:
            pattern (re.Pattern): The compiled regular expression pattern to search for in the text.
            text (str): The input text to search within.
        Returns:
            List['SpannedText']: A list of SpannedText objects representing the spans of text that match the pattern
                                 and the spans of text between the matches.
        """
        spans = []
        index: int = 0

        vvv = pattern.search(text)

        while True:
            match = pattern.search (text, index)
            if match is None:
                break

            if index < match.start():
                span = SpannedText(text[index:match.start()])
                spans.append(span)

            span = SpannedText(match)
            spans.append(span)
            index = match.end()

        if index < len(text):
            span = SpannedText(text[index:])
            spans.append(span)

        return spans

    @staticmethod
    def listToString(spans: List['SpannedText']) -> str:
        """
        Concatenate a list of SpannedText objects into a single string.
        Args:
            spans (List['SpannedText']): A list of SpannedText objects to concatenate.
        Returns:
            str: The concatenated string of all the spans in the list.
        """
        result: str = ""
        for span in spans:
            result += str(span)
            print (result)
        return result
    
    @staticmethod
    def iterateOverList(spans: List['SpannedText'],func,state=None) -> None:
        """
        Iterate over a list of SpannedText objects and print each one.
        Args:
            spans (List['SpannedText']): A list of SpannedText objects to iterate over.
        """
        for span in spans:
            func(state,span,len(span.spans) >0)

    def __str__(self):
        if (self.text != ""):
            return self.text
        elif (len(self.spans) > 0):
            return str(self.spans[0])
        else:
            return ""

    @staticmethod
    def iterateOverText(regex,text:str, func,state=None,flags:int=0) -> str:        
        """
        Iterates over the text, applying a function to each match of the given regex pattern.

        Args:
            regex (str or Pattern): The regular expression pattern to search for in the text. 
                                    If a string is provided, it will be compiled into a regex pattern.
            text (str): The input text to search within.
            func (callable): A function to apply to each match found by the regex pattern.
            state (optional): An optional state object that can be passed to the function.
            flags (int, optional): Optional regex flags to modify the regex pattern's behavior. Default is 0.

        Returns:
            str: The modified text after applying the function to each match.
        """
        if isinstance(regex, str):
            regex = re.compile(regex,flags)
        spans = SpannedText.listFromPattern(regex,text)
        SpannedText.iterateOverList(spans,func,state)
        return SpannedText.listToString(spans)

    @staticmethod
    def iterateOverLines(regex,text:str, func,state=None,flags:int=0,newLine:str="\r\n") -> str:     
        """
        Iterates over each line in the given text, applies a function to each line using a regex pattern, and returns the modified text.
        Args:
            regex (Union[str, Pattern]): The regex pattern to match in each line. Can be a string or a compiled regex pattern.
            text (str): The input text to process.
            func (Callable): The function to apply to each line that matches the regex pattern.
            state (Any, optional): An optional state to pass to the function. Defaults to None.
            flags (int, optional): Regex flags to use when compiling the regex pattern. Defaults to 0.
            newLine (str, optional): The newline character(s) to use when joining the processed lines. Defaults to "\r\n".
        Returns:
            str: The modified text with the function applied to each line that matches the regex pattern.
        """
        if isinstance(regex, str):
            regex = re.compile(regex,flags)

        lines = re.split(r'\r\n|\n|\r',text)
        result = ""
        lineNumber = 0

        for line in lines:
            spans = SpannedText.listFromPattern(regex,text)
            for span in spans:
                span.lineNumber = lineNumber
            SpannedText.iterateOverList(spans,func,state)
            result += SpannedText.listToString(spans)+newLine

        return result


    def setText(self, index, text = None):
        """
        Sets the text for a given span identified by index.

        If text is not provided, the index itself is used as the text.

        Args:
            index (int or str): The index of the span to set the text for. If an integer, it refers to the position in the spans list. If a string, it refers to a key in the spans_dict.
            text (str, optional): The text to set for the span. If not provided, the index is used as the text.

        """

        if text is None:
            self.text = index

        if isinstance(index, int):
            if index < len(self.spans):
                span = self.spans[index]
                span.text = text
                span.spans.clear()

        else:
            if index in self.spans_dict:
                span = self.spans_dict[index]   
                span.text = text
                span.spans.clear()

        
    def getText(self,index = None):
        """
        Retrieve text based on the provided index.

        Parameters:
        index (int or any, optional): The index to retrieve the text from. If None, the method calls itself recursively.

        Returns:
        str: The text at the specified index. If the index is out of range or not found, returns an empty string.
        """

        if (index is None):
            return self.getText()
        
        elif isinstance(index,int):
            if index < len(self.spans):
                return self.spans[index].text
            else:
                return ""
            
        else:
            if index in self.spans_dict:
                return self.spans_dict[index].text
            else:
                return ""
        

ttt = """
p = re.compile(r"(?P<first>\w+) (?P<last>\w+)")
list = SpannedText.listFromPattern(p,"Xilofon Reynolds is a musician and composer")
"""

if __name__ == "__main__":
 
    exec (ttt) 
    lines = re.split(r'\r\n|\n|\r',"aaa\r\n\r\nbbb\nccc\rddd")
    p = re.compile(r"(?P<first>\w+) (?P<last>\w+)")
    list = SpannedText.listFromPattern(p,"Xilofon Reynolds is a musician and composer")

    def spanFUNC(state,span,found):
        print(str(found)+":'"+str(span)+"'")
        if (found):
            pass
            #span.setText("first","Sisonek")
            #span.setText("last","Momosek")
        else:
            span.setText("...")

    SpannedText.iterateOverList(list,spanFUNC)

    print (SpannedText.listToString(list))


