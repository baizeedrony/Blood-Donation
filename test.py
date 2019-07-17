class Rectangel():
    def __init__(self,w,h):
        self.w = w
        self.h = h

    def area(self):
        self.w*self.h

    def parimeter(self):
        return 2 * (self.w+self.h)


class square(Rectangel):
    def __init__(self, s):
        super(square, self).__init__(s,s)
        self.s = s
