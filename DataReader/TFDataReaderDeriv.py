import logging
import sys

import numpy as np
from DataReader.DataReaderBase import *
from pandas import DataFrame
from scipy import signal
from sympy.parsing.sympy_parser import parse_expr, T
import sympy as sp
from typing import Tuple, Type
from Utils.Trace import Trace


class TFDataReader(DataReader):

    def __init__(self, tfstr: str):
        super().__init__()
        self.data2get = 'Mod'
        self.transFunc: signal.TransferFunction = None
        self.s = sp.Symbol('s')  # Variable de expresion
        self.expr = parse_expr(tfstr, local_dict={'s': self.s, 'S': self.s}, transformations=T[:])
        self.symbolslist = self.expr.free_symbols

        for symb in self.symbolslist:
            if symb != self.s:
                self.expr = self.expr.subs(symb, 1)

    def getExpression(self):
        return self.expr

    def initTransferFunction(self, data2get: str):
        self.data2get = data2get
        self.expr = sp.simplify(self.expr)
        self.expr = self.expr.evalf()
        self.expr = sp.fraction(self.expr)

        if self.s not in self.expr[0].free_symbols:
            numCoeffs = np.array(self.expr[0].evalf(), dtype=float)
        else:
            numCoeffs = np.array(sp.Poly(self.expr[0]).all_coeffs(), dtype=float)
        if self.s not in self.expr[1].free_symbols:
            denCoeffs = np.array(self.expr[1].evalf(), dtype=float)
        else:
            denCoeffs = np.array(sp.Poly(self.expr[1]).all_coeffs(), dtype=float)

        self.transFunc = signal.TransferFunction(numCoeffs, denCoeffs)

        return
    '''
        Devuelve un dataframe con dos columnas la primera el eje X y la segunda el Y
        Si es un Bode, deberia devolver Modulo o Fase, pero nunca ambas.
        En caso de ser de Respuesta del sistema devuelve
    '''
    def read(self) -> DataFrame:

        match self.data2get:
            case 'Mod':
                w, mag, phase = signal.bode(self.transFunc, n=2000)
                w = np.array(w, dtype=float)
                mag = np.array(mag, dtype=float)
                data = DataFrame.from_dict({'Frquency': w / (2 * np.pi), 'Module': 10**(mag/20)})
            case 'Phase':
                w, mag, phase = signal.bode(self.transFunc, n=2000)
                w = np.array(w, dtype=float)
                phase = np.array(phase, dtype=float)
                data = DataFrame.from_dict({'Frquency': w / (2 * np.pi), 'Phase': phase})
            case 'Signal':
                data = DataFrame.from_dict({'Frquency': (2 * np.pi), 'Module': 10})

        return data


if __name__ == "__main__":
    TFdata = TFDataReader("(s*2+1)/(s^2*2+3)")
