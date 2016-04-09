class caloTower:
    def __init__(self, *args):
        if len(args) == 1 and type(args[0]) is str:
            caloTower.initFromString(args[0])
        elif len(args) == 3:
            # No validation, not for user input!!
            self._caloType = args[0]
            self._ieta = args[1]
            self._iphi = args[2]

    def __str__(self):
        return '%s%d,%d' % (self._caloType, self._ieta, self._iphi)

    # To use with argparse
    @staticmethod
    def initFromString(string):
        from argparse import ArgumentTypeError as error
        caloType = string[0]
        if caloType not in ['E', 'H']:
            raise error("Malformed caloTower string: %s.  Must specify either E or H" % string)
        tok = string[1:].split(',')
        if len(tok) != 2:
            raise error("Malformed caloTower string: %s.  Example format: E3,10" % string)
        ieta, iphi = map(int, tok)
        if caloType == 'E':
            if ieta < -28 or ieta > 28 or ieta == 0:
                raise error("Malformed caloTower string: %s.  iEta out of bounds (-28,28) excluding 0" % string)
        elif caloType == 'H':
            if ieta < -41 or ieta > 41 or ieta == 0 or abs(ieta) == 29:
                raise error("Malformed caloTower string: %s.  iEta out of bounds (-41,41) excluding -29,0,29" % string)
            if abs(ieta) > 29 and iphi % 2 == 0:
                raise error("Malformed caloTower string: %s.  Impossible iPhi for given iEta" % string)
            if abs(ieta) > 39 and iphi % 4 != 3:
                raise error("Malformed caloTower string: %s.  Impossible iPhi for given iEta" % string)
        if iphi <= 0 or iphi > 72:
            raise error("Malformed caloTower string: %s.  iEta out of bounds (1-72)" % string)
        return caloTower(caloType, ieta, iphi)

    def contextId(self):
        lphi = (self._iphi + 1) % 72 + 1  # Layer1 Phi (old RCT/GCT Phi)
        if lphi < 0 or lphi > 17:
            raise Exception("Invalid lphi (%d) while trying to find context for tower: %s" % (lphi, str(self)))
        return "CTP7_Phi%d" % lphi

    def linkMaskId(self):
        side = 'Pos'
        if self._ieta < 0:
            side = 'Neg'

        eta = abs(self._ieta)
        if self._caloType == 'E':
            calo = 'ECAL'
            if eta < 17:
                link = (eta - 1) / 2
            elif eta == 17:
                link = 8
            elif eta == 18:
                link = 9
            elif eta == 19 or eta == 20:
                link = 10
            else:
                link = (eta - 1) / 2 + 2
        elif self._caloType == 'H' and abs(self._ieta) < 29:
            calo = 'HCAL'
            link = (eta - 1) / 2
        else:
            calo = 'HF'
            if (eta < 40) and (self._iphi % 4 == 1):
                link = 0
            elif (eta < 40) and (self._iphi % 4 == 3):
                link = 1
            elif eta == 40:
                link = 0
            elif eta == 41:
                link = 1
            else:
                raise Exception("I should not have gotten here... tower: %s" % str(self))

        return "inputPorts.%s_%s_LINK_%02d" % (side, calo, link)
