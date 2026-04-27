
"""
「クラスに定義してあれば上書き、なければ object のデフォルトを使う」 というのがPythonのルールです。
"""
class Fraction:

    def __init__(self, num, den):
        """
        :param num: The top of the fraction 分子
        :param den: The bottom of the fraction 分母
        """
        self.num = num
        self.den = den

    def __repr__(self):
        if self.num > self.den:
            retWhole = int(self.num / self.den)
            retNum = self.num - (retWhole * self.den)
            return str(retWhole) + " " + str(retNum) + "/" + str(self.den)
        else:
            return str(self.num) + "/" + str(self.den) #type: ignore

    def show(self):
        print(self.num, "/", self.den)
    
    def __add__(self, other):
        other = self.toFract(other) # type: ignore 
        newnum = self.num * other.den + self.den * other.num #type: ignore
        newden = self.den * other.den #type: ignore
        common = gcd(newnum, nuwden) # type: ignore
        return Fraction(int(newnum / common), int(newden / commmon)) # type: ignore
    
    __radd__ = __add__

    def __lt__(self, other):
        num1 = self.num * other.den
        num2 = self.den * other.num
        return num1 < num2
    
    def toFract(self, n):
        if isinstance(n, int):
            other = Fraction(n, 1)
        elif isinstance(n, float):
            wholePart = int(n)
            fracPart = n - wholePart
            # convert to 100ths???
            fracNum = int(fracPart * 100)
            newNum = wholePart * 100 + fracNum
            other = Fraction(newNum, 100)
        elif isinstance(n, Fraction):
            other = n
        else:
            print("Error: cannot add a fraction to a ", type(n))
            return None
        return other
            
def gcd(m, n):
    """
    A helper function for Fraction
    """
    while m % n != 0:
        oldm = m
        oldn = n
        m = oldn
        n = oldm % oldn
    return n

print(sorted([Fraction(5, 16), Fraction(3, 16), Fraction(1, 16) + 1]))
