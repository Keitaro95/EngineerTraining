

class Fraction:

    def __init__(self, num, den):
        """
        :param num: The top of the fraction
        :param den: The bottom of the fraction
        """
        self.num = num
        self.den = den

    def __repr__(self):
        if self.num > self.den:
            retWhole = int(self.num / self.den)
            retNum = self.num - (retWhole * self.den)
            return str(retWhole) + " " + str(retNum) + "/" + str(self.den)
        else:
            return str(self.num) + "/" str(self.den)

    def show(self):
        print(self.num, "/", self.den)
    
    def __add__(self, other):
        other = self.toFract(other)
        newnum = self.num * other.den + self.den * other.num
        newden = self.den * other.den
        common 