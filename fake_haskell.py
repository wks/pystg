
def identity(x): return x

class Closure:
    def __init__(self, func, args):
        self.patch(func, args)

    def __repr__(self):
        return "<Closure {!r} {!r}>".format(self.func, self.args)

    @staticmethod
    def stub():
        return Closure(None, None)

    @staticmethod
    def of_value(value):
        return Closure(identity, [value])

    @staticmethod
    def of_func(func):
        return Closure(identity, [func])

    @staticmethod
    def of_dc(tag, *args):
        return Closure(identity, [DataCons(tag, *args)])

    def patch(self, func, args):
        self.func = func
        self.args = args

    def patch_value(self, value):
        self.patch(identity, [value])

    def patch_func(self, func):
        self.patch(identity, [func])

    def patch_dc(self, tag, *args):
        self.patch(identity, [DataCons(tag, *args)])

    def force(self):
        val = self.func(*self.args)
        self.func = identity
        self.args = [val]
        return val

class DataCons:
    def __init__(self, tag, *args):
        self.tag = tag
        self.args = args
        for arg in args:
            assert(isinstance(arg, Closure))

    def __repr__(self):
        return "({}, {})".format(self.tag, ", ".join(map(repr, self.args)))

def force(closure):
    return closure.force()

zero = Closure.of_value(0)
one  = Closure.of_value(1)
fibs     = Closure.stub()
fibstail = Closure.stub()
fibsrest = Closure.stub()

def run_plus(x, y):
    xx = force(x)
    yy = force(y)
    return xx + yy

plus = Closure.of_func(run_plus)

def run_minus(x, y):
    xx = force(x)
    yy = force(y)
    return xx - yy

minus = Closure.of_func(run_minus)

nil = Closure.of_dc("nil")

def run_cons(x, xs):
    return ("cons", x, xs)

cons = Closure.of_func(run_cons)

def apply(func, *args):
    funcc = force(func)
    return funcc(*args)

zipWith = Closure.stub()

def run_zipWith(op, x, y):
    xx = force(x)
    assert(isinstance(xx, DataCons))
    if xx.tag == "nil":
        return DataCons("nil")
    elif xx.tag == "cons":
        yy = force(y)
        assert(isinstance(yy, DataCons))
        if yy.tag == "nil":
            return DataCons("nil")
        elif yy.tag == "cons":
            xx_head, xx_tail = xx.args
            yy_head, yy_tail = yy.args
            
            head = Closure(apply, [op, xx_head, yy_head])
            tail = Closure(apply, [zipWith, op, xx_tail, yy_tail])
            return DataCons("cons", head, tail)
        else:
            raise Exception("y is neither nil nor cons")
    else:
        raise Exception("x is neither nil nor cons")
    
zipWith.patch_func(run_zipWith)

fibsrest.patch(apply, [zipWith, plus, fibs, fibstail])

fibstail.patch_dc("cons", one, fibsrest)

fibs.patch_dc("cons", zero, fibstail)

take = Closure.stub()

def run_take(num, lst):
    numm = force(num)
    assert(isinstance(numm, int))
    if numm == 0:
        return DataCons("nil")
    else:
        lstt = force(lst)
        assert(isinstance(lstt, DataCons))
        if lstt.tag == "nil":
            return DataCons("nil")
        elif lstt.tag == "cons":
            head, tail = lstt.args
            num_minus_1 = Closure(apply, [minus, num, one])
            rest = Closure(apply, [take, num_minus_1, tail])
            return DataCons("cons", head, rest)
        else:
            raise Exception("lstt is neither nil nor cons")

take.patch_func(run_take)

ten = Closure.of_value(10)

fibs10 = Closure(apply, [take, ten, fibs])

def show():
    cur = fibs10
    while True:
        # print(cur)
        node = force(cur)
        assert(isinstance(node, DataCons))
        if node.tag == "nil":
            break
        else:
            assert(node.tag == "cons")
            head, tail = node.args
            head_val = force(head)
            assert(isinstance(head_val, int))
            print(head_val)
        cur = tail

