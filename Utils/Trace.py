import enum
from dataclasses import dataclass
from DataReader.DataReaderBase import DataReader

linestyle_dict = {
    'solid': 'solid',  # Same as (0, ()) or '-'
    'dotted': 'dotted',  # Same as (0, (1, 1)) or ':'
    'dashed': 'dashed',  # Same as '--'
    'dashdot': 'dashdot',  # Same as '-.'

    'loosely dotted': (0, (1, 10)),
    'densely dotted': (0, (1, 1)),

    'loosely dashed': (0, (5, 10)),
    'densely dashed': (0, (5, 1)),

    'loosely dashdotted': (0, (3, 10, 1, 10)),
    'dashdotted': (0, (3, 5, 1, 5)),
    'densely dashdotted': (0, (3, 1, 1, 1)),

    'dashdotdotted': (0, (3, 5, 1, 5, 1, 5)),
    'loosely dashdotdotted': (0, (3, 10, 1, 10, 1, 10)),
    'densely dashdotdotted': (0, (3, 1, 1, 1, 1, 1))}


class TraceType(enum.Enum):
    Module = "(Modulo)"
    Phase = "(Fase)"
    Signal = "(Señal)"


@dataclass
class Trace:
    tracename: str
    reader: DataReader
    color: str
    linetype: str
    type: TraceType

    def __repr__(self):
        return self.tracename + " " + self.type.value
