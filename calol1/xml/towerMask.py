from ..geometry import caloTower


def arrayToMask(array):
    if len(array) != 32:
        raise Exception("Tried to pass incorrect array length to mask text?!")
    return ', '.join(map(hex, array))


def maskToArray(mask):
    array = mask.split(',')
    if len(array) != 32:
        raise Exception("Tower mask text length is invalid! (not 32)\n" + mask)

    array = map(lambda s: s.strip(' \n\t'), array)

    looksLikeHex = sum(map(lambda x: x[:2] == '0x', array)) == 32
    if not looksLikeHex:
        raise Exception("Tower mask text is invalid! (some number doesn't look like a hex value)\n" + mask)

    return map(lambda x: int(x, 16), array)


def blankMask():
    mask = [0] * (16 + 14 + 2)
    return arrayToMask(mask)


def addTower(mask, tower):
    array = maskToArray(mask.wholeText)
    link = tower.linkOffset()
    t = tower.towerOffset()
    array[link] |= (1 << t)
    mask.replaceWholeText(arrayToMask(array))


def readTowers(contextId, maskId, mask):
    array = maskToArray(mask.wholeText)
    towersMasked = []
    for link in range(32):
        maxOffset = 8
        if link >= 30:
            maxOffset = 11
        for offset in range(maxOffset):
            if array[link] & (1 << offset):
                towersMasked.append(caloTower.initFromContextMaskLinkOffset(contextId, maskId, link, offset))
    return towersMasked


def describe(contextId, maskId, mask):
    towers = readTowers(contextId, maskId, mask)
    return ' '.join(map(str, towers))
