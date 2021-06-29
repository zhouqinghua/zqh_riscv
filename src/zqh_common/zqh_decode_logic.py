import sys
import os
from phgl_imp import *
#source code coming from: https://github.com/chipsalliance/rocket-chip/tree/master/src/main/scala/rocket/Decode.scala
#re-write by python and do some modifications

class zqh_decode_logic(object):
    caches = {}

    def term(self, lit):
        if (isinstance(lit, value)):
            lit = bit_pat(lit)
        return zqh_term(lit.value, 2**(lit.get_w())-(lit.mask+1))

    def logic(self, addr, addrWidth, cache, terms):
        return reduce(lambda x, y: x | y, list(map(lambda t: cache.setdefault(t, (addr if (t.mask == 0) else (addr & value(2**(addrWidth)-(t.mask+1), addrWidth))) == value(t.value, addrWidth)), terms)), value(0))

    def decode_sig(self, addr, default, mapping):
        if (id(addr) in self.caches):
            cache = self.caches[id(addr)]
        else:
            self.caches[id(addr)] = {}
            cache = self.caches[id(addr)]
        dterm = self.term(default)
        keys = list(map(lambda x : x[0], mapping))
        values = list(map(lambda x : x[1], mapping))
        addrWidth = max(list(map(lambda x:x.get_w(),keys)))
        terms = list(map(lambda k : self.term(k), keys))
        termvalues = list(zip(terms, list(map(lambda v : self.term(v), values))))

        tmp = []
        for i in range(max(default.get_w(),max(list(map(lambda x:x.get_w(), values))))):
            mint = list(map(lambda x: x[0], list(filter(lambda _:((_[1].mask >> i) & 1) == 0 and ((_[1].value >> i) & 1) == 1, termvalues))))
            maxt = list(map(lambda x: x[0], list(filter(lambda _:((_[1].mask >> i) & 1) == 0 and ((_[1].value >> i) & 1) == 0, termvalues))))
            dc   = list(map(lambda x: x[0], list(filter(lambda _:((_[1].mask >> i) & 1) == 1, termvalues))))

            if (((dterm.mask >> i) & 1) != 0):
                tmp.append(self.logic(addr, addrWidth, cache, zqh_simplify_dc().apply(mint, maxt, addrWidth)))
            else:
                defbit = (dterm.value >> i) & 1
                t = mint if (defbit == 0) else maxt
                bit = self.logic(addr, addrWidth, cache, zqh_simplify().apply(t, dc, addrWidth))
                tmp.append(bit if (defbit == 0) else ~bit)
        return cat_rvs(tmp)

    def decode_sig_list(self, addr, default, mappingIn):
        mapping = list(map(lambda _ : [], range(len(default))))
        for (key, values) in  mappingIn:
            for i in range(len(values)):
                mapping[i].append((key if (isinstance(key, bit_pat)) else bit_pat(key), values[i]))
        return list(map(lambda _: self.decode_sig(addr, _[0], _[1]), list(zip(default,mapping))))

    def decode_sig_ture_false(self, addr, trues, falses):
        return self.decode_sig(addr, bit_pat('b?'), list(map(lambda _:(bit_pat(_), bit_pat("b1")), trues)) + list(map(lambda _:(bit_pat(_), bit_pat("b0")), falses)))

class zqh_term(object):
    def __init__(self, value, mask = 0):
        self.prime = True
        self.value = value
        self.mask = mask

    def covers(self, x):
        return ((self.value ^ x.value) & ~self.mask | x.mask & ~self.mask) == 0
    def intersects(self, x):
        return ((self.value ^ x.value) & ~self.mask & ~x.mask) == 0
    def __eq__(self, that):
       if (isinstance(that, zqh_term)):
           return (that.value == self.value) and (that.mask == self.mask)
       else:
           return False
    def __ne__(self, that):
        return not self.__eq__(that)
    def __hash__(self):
        return self.value
    def __lt__(self, that):
        return (self.value < that.value) or ((self.value == that.value) and (self.mask < that.mask))
    def similar(self, x):
        diff = self.value - x.value
        return (self.mask == x.mask) and (self.value > x.value) and ((diff & diff-1) == 0)
    def merge(self, x):
        self.prime = False
        x.prime = False
        bit = self.value - x.value
        return zqh_term(self.value & ~bit, self.mask | bit)
    def __str__(self):
        return "%x-%x" % (self.value, self.mask) + ('p' if (self.prime) else '')

class zqh_simplify(object):
    def get_prime_implicants(self, implicants, bits):
        prime = []
        for i in implicants:
            i.prime = True

        cols = list(map(lambda b : list(filter(lambda y : b == count_ones(y.mask), implicants)), range(bits + 1)))
        table = list(map(lambda c : list(map(lambda b : set(list(filter(lambda a : b == count_ones(a.value),c))),range(bits + 1))),cols))
        for i in range(bits + 1):
            for j in range(bits-i):
                for a in table[i][j]:
                    table[i+1][j] = table[i+1][j] | set(list(map(lambda y : y.merge(a),list(filter(lambda x : x.similar(a),table[i][j+1])))))
            for r in table[i]:
                for p in r:
                    if p.prime:
                        prime.insert(0,p)
        prime.sort()
        return prime

    def get_essential_prime_implicants(self, prime, minterms):
        primeCovers = list(map(lambda p : list(filter(lambda x : p.covers(x),minterms)),prime))
        for ((icover, pi), i) in list(map(lambda x : ((primeCovers[x], prime[x]), x),range(len(prime)))):
            for ((jcover, pj), j) in list(map(lambda x : ((primeCovers[x], prime[x]), x),range(len(prime))))[i+1:]:
                if (len(icover) > len(jcover) and all(list(map(lambda x : pi.covers(x),jcover)))):
                    return self.get_essential_prime_implicants(list(filter(lambda x : x != pj,prime)), minterms)

        essentiallyCovered = list(filter(lambda t : len(list(filter(lambda x : x.covers(t),prime))) == 1 ,minterms))
        essential = list(filter(lambda p : len(list(filter(lambda x : p.covers(x),essentiallyCovered))) > 0, prime))
        nonessential = list(filter(lambda x : x not in essential, prime))
        uncovered = list(filter(lambda t : len(list(filter(lambda x : x.covers(t), essential))) == 0, minterms))
        if (len(essential) == 0 or len(uncovered) == 0):
            return (essential, nonessential, uncovered)
        else:
            (a, b, c) = self.get_essential_prime_implicants(nonessential, uncovered)
            return (essential + a, b, c)

    def get_cost(self, cover, bits):
        return sum(list(map(lambda x : bits - count_ones(x.mask),cover)))

    def cheaper(self, a, b, bits):
        ca = self.get_cost(a, bits)
        cb = self.get_cost(b, bits)
        def listLess(a, b):
            return (len(b) > 0) and (len(a) == 0 or a[0] < b[0] or a[0] == b[0] and listLess(a[1:], b[1:]))
        al = list(a)
        bl = list(b)
        al.sort()
        bl.sort()
        return ca < cb or ca == cb and listLess(al, bl)

    def get_cover(self, implicants, minterms, bits):
        if (len(minterms) > 0):
            cover = list(map(lambda m : list(filter(lambda x : x.covers(m), implicants)), minterms))
            all = reduce(lambda c0,c1: flatten(list(map(lambda a : list(map(lambda x : a | set([x]), c1)), c0))), cover[1:], list(map(lambda y : set([y]), cover[0])))
            return reduce(lambda a, b: a if (self.cheaper(a, b, bits)) else b, list(map(lambda x : list(x), all)))
        else:
            return []

    def stringify(self, s, bits):
        return reduce(lambda x1, y1 : x1+' + '+y1, list(map(lambda t : reduce(lambda x0, y0 : x0+y0, list(map(lambda i : 'x' if ((t.mask & (1 << i)) != 0) else str((t.value >> i) & 1), range(bits)))).reverse(), s)))

    def apply(self, minterms, dontcares, bits):
        prime = self.get_prime_implicants((minterms + dontcares) if (len(dontcares) > 0) else minterms , bits)
        for t in minterms:
            assert(len(list(filter(lambda x : x.covers(t), prime))) > 0)

        (eprime, prime2, uncovered) = self.get_essential_prime_implicants(prime, minterms)
        cover = eprime + self.get_cover(prime2, uncovered, bits)
        for t in minterms:
            assert(len(list(filter(lambda x : x.covers(t), cover))) > 0) ## sanity check
        return cover

class zqh_simplify_dc(object):
    def get_implicit_dc(self, maxterms, term, bits, above):
        for i in range(bits):
            t = None
            if (above and ((term.value | term.mask) & (1 << i)) == 0):
                t = zqh_term(term.value | (1 << i), term.mask)
            elif ((not above) and (term.value & (1 << i)) != 0):
                t = zqh_term(term.value & ~(1 << i), term.mask)
            if (t != None and (not (len(list(filter(lambda x : x.intersects(t), maxterms))) > 0))):
                return t
        return None

    def get_prime_implicants(self, minterms, maxterms, bits):
        prime = []
        for i in minterms:
            i.prime = True
        mint = list(map(lambda t : zqh_term(t.value, t. mask), minterms))
        cols = list(map(lambda b : list(filter(lambda x : b == count_ones(x.mask), mint)), range(bits+1)))
        table = list(map(lambda c : list(map(lambda b : set(list(filter(lambda x : b == count_ones(x.value), c))), range(bits+1))), cols))

        for i in range(bits+1):
            for j in range(bits-i):
                for a in table[i][j]:
                    table[i+1][j] = table[i+1][j] | set(list(map(lambda y : y.merge(a), list(filter(lambda x : x.similar(a), table[i][j+1])))))
            for j in range(bits-i):
                for a in list(filter(lambda x : x.prime, table[i][j])):
                    dc = self.get_implicit_dc(maxterms, a, bits, True)
                    if (dc != None):
                        table[i+1][j].add(dc.merge(a))
                for a in list(filter(lambda x : x.prime, table[i][j+1])):
                    dc = self.get_implicit_dc(maxterms, a, bits, False)
                    if (dc != None):
                        table[i+1][j].add(a.merge(dc))
            for r in table[i]:
                for p in r:
                    if (p.prime):
                        prime.insert(0,p)
        prime.sort()
        return prime

    def verify(self, cover, minterms, maxterms):
        assert(all(list(map(lambda t : len(list(filter(lambda x : x.covers(t), cover))) > 0, minterms))))
        assert(all(list(map(lambda t : not (len(list(filter(lambda x : x.intersects(t),cover))) > 0), maxterms))))

    def apply(self, minterms, maxterms, bits):
        prime = self.get_prime_implicants(minterms, maxterms, bits)
        (eprime, prime2, uncovered) = zqh_simplify().get_essential_prime_implicants(prime, minterms)
        cover = eprime + zqh_simplify().get_cover(prime2, uncovered, bits)
        self.verify(cover, minterms, maxterms)
        return cover
