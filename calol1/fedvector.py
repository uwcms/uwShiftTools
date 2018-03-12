class fedvector:
    def __init__(self, fedstring):
        self._fedmap = dict([tuple(map(int, x.split('&'))) for x in str(fedstring).strip('%').split('%')])

    def count_feds_in(self, fedlist):
        return sum(1 for fed in fedlist if self._fedmap.get(fed, 0) > 0)

    def feds_fraction(self, fedlist):
        feds_in = self.count_feds_in(fedlist)
        return "%d/%d" % (feds_in, len(fedlist))

    def ecal_presence(self):
        ecal_feds = range(601, 654+1)
        return self.feds_fraction(ecal_feds)

    def hcal_presence(self):
        hcal_feds = range(1100, 1123+1)
        return self.feds_fraction(hcal_feds)

    def calol1_presence(self):
        calol1_feds = [1354, 1356, 1358]
        return self.feds_fraction(calol1_feds)

