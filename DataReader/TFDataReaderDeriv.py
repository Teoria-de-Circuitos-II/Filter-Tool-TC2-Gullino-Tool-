import logging
import sys

import numpy as np
from DataReader.DataReaderBase import *
from pandas import DataFrame
from scipy import signal
from sympy.parsing.sympy_parser import parse_expr, T
import sympy as sp


class TFDataReader(DataReader):

    def __init__(self, tfstr: str):
        super().__init__()

        s = sp.Symbol('s')  # Variable de expresion
        # Se Toma la expresion tfstr ingresada por el usuario y se interpreta
        self.expr = parse_expr(tfstr, local_dict={'s': s}, transformations=T[:])


    '''
        Devuelve un dataframe con dos columnas la primera el eje X y la segunda el Y
        Si es un Bode, deberia devolver Modulo o Fase, pero nunca ambas.
        En caso de ser de Respuesta del sistema devuelve
    '''
    def read(self) -> DataFrame:            # TODO

        #self.w, self.mag, self.phase = signal.bode(self.transFunc)
        #self.tout, self.yout, self.xout = signal.lsim(self.transFunc, inputsignalpoints, timepoints)

        print(self.tout)
        data = np.array([self.tout])
        df = DataFrame(data=data, columns=["time"])

        return df

    def getExpression(self):
        return self.expr

    def initTransferFunction(self):

        self.symbolslist = self.expr.free_symbols
        expr = sp.simplify(self.expr)
        for symb in self.symbolslist:
            if symb != s:
                expr = expr.subs(symb, 1)
        expr = sp.fraction(expr)

        if expr[0] == 1 or expr[0] == sp.Symbol('s') or expr[1] == 1 or expr[1] == sp.Symbol('s'):
            denCoeffs = np.array([1], dtype=float)
            numCoeffs = np.array([1], dtype=float)
        else:
            logging.debug(sp.poly_from_expr(expr[1]))
            denCoeffs = np.array(sp.poly_from_expr(expr[1]).all_coeffs(), dtype=float)
            numCoeffs = np.array(sp.poly_from_expr(expr[0]).all_coeffs(), dtype=float)

        self.transFunc = signal.TransferFunction(numCoeffs, denCoeffs)

if __name__ == "__main__":
    TFdata = TFDataReader("(s*2+1)/(s^2*2+3)")
