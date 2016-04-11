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

    def lphi(self):
        '''
        From Layer-1 point of view, entire calo rotated by +2 (mod 72) in phi
        All measurements for Layer 1 card and subcard tower indexing are based
        on this coordinate rather than calorimeter iphi
        '''
        lphi = (self._iphi + 1) % 72 + 1
        return lphi

    def card(self):
        card = self.lphi() / 4
        if card < 0 or card > 17:
            raise Exception("Invalid card (%d) while trying to find context for tower: %s" % (card, str(self)))
        return card

    def towerOffset(self):
        '''
        Despite the strangeness with ECAL links,
        the tower offset is consistent for them.
        That implies there are a few impossible link+tower combinations.
        '''
        eta = abs(self._ieta)
        if eta < 29:
            nibble = (eta - 1) % 2
            localPhi = self.lphi() % 4
            offset = nibble * 4 + localPhi
        elif eta < 40:
            offset = eta - 30
        else:
            offset = 10
        return offset

    def contextId(self):
        return "CTP7_Phi%d" % self.card()

    def linkOffset(self):
        '''
        Within the card, ECAL Links carry two strips of 4 phi, except
        for links 8,9,11,13 (zero-indexed) which only have one phi strip
        HCAL is consistent
        HF is weird, there are 'A' and 'B' links (0,1)
        A contains iphi, B contains iphi+2, except for 40 and 41
        '''
        eta = abs(self._ieta)
        if self._caloType == 'E':
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
            link = 16 + (eta - 1) / 2
        else:
            if (eta < 40) and (self._iphi % 4 == 1):
                link = 16 + 14
            elif (eta < 40) and (self._iphi % 4 == 3):
                link = 16 + 14 + 1
            elif eta == 40:
                link = 16 + 14
            elif eta == 41:
                link = 16 + 14 + 1
            else:
                raise Exception("I should not have gotten here... tower: %s" % str(self))
        return link

    def linkId(self):
        side = 'Pos'
        if self._ieta < 0:
            side = 'Neg'

        link = self.linkOffset()
        if link < 16:
            calo = 'ECAL'
        elif link < 16 + 14:
            calo = 'HCAL'
            link = link - 16
        elif link < 16 + 14 + 2:
            calo = 'HF'
            link = link - 16 - 14
        else:
            raise Exception("I should not have gotten here... link: %d, tower: %s" % (link, str(self)))

        return "inputPorts.%s_%s_LINK_%02d" % (side, calo, link)
