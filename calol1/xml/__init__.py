import util as _util
import towerMask as _towerMask


class run_settings():
    def __init__(self, document):
        # XML Documents always have one root note
        # So the document's first child must be <run-settings />
        run_settings = document.firstChild
        if not run_settings:
            run_settings = document.createElement("run-settings")
            run_settings.setAttribute('id', "calol1")
            document.appendChild(run_settings)

        if run_settings.tagName != 'run-settings':
            raise Exception("Malformed xml: root tag not 'run-settings', but '%s'" % run_settings.tagName)

        tagId = run_settings.getAttribute('id')
        if tagId != 'calol1':
            raise Exception("Malformed xml: root tag id not 'calol1', but '%s'" % tagId)

        # We have to delete whitespace from the DOM to not double it on output
        _util.stripNode(run_settings)

        self.document = document
        self.run_settings = run_settings

    def __str__(self):
        out = ''
        contexts = self.run_settings.getElementsByTagName('context')
        for context in contexts:
            tmp = ''
            empty = True
            contextId = context.getAttribute('id')
            if contextId == 'processors':
                tmp += 'All processors:\n'
            else:
                tmp += 'Processor %s:\n' % contextId

            masks = context.getElementsByTagName('mask')
            for mask in masks:
                empty = False
                tmp += '    Masked link: %s\n' % mask.getAttribute('id')

            params = context.getElementsByTagName('param')
            for param in params:
                maskId = param.getAttribute('id')
                if 'towerMask' in maskId:
                    mask = param.firstChild
                    maskedTowers = _towerMask.describe(contextId, maskId, mask)
                    if len(maskedTowers) > 0:
                        empty = False
                        tmp += '    Masked tower(s): %s\n' % maskedTowers

            if not empty:
                out += tmp
        return out

    def addLinkMaskByTower(self, tower):
        contextId = tower.contextId()
        linkId = tower.linkId()
        context = _util.findOrCreateElement(self.document, self.run_settings, 'context', contextId)
        _util.findOrCreateElement(self.document, context, 'mask', linkId)

    def addTowerMaskByTower(self, tower):
        # if there's no base mask for all processors, make one
        allProcessors = _util.findOrCreateElement(self.document, self.run_settings, 'context', 'processors')
        paramsAll = allProcessors.getElementsByTagName('param')
        for side in ['Pos', 'Neg']:
            for p in paramsAll:
                if 'towerMask{0}Eta'.format(side) in _util.getId(p):
                    break
            else:
                # no default mask, make one
                paramAll = _util.findOrCreateElement(self.document, allProcessors, 'param', 'towerMask{0}Eta'.format(side))
                paramAll.setAttribute('type', 'vector:uint')
                maskAll = self.document.createTextNode(_towerMask.blankMask())
                paramAll.appendChild(maskAll)

        contextId = tower.contextId()
        context = _util.findOrCreateElement(self.document, self.run_settings, 'context', contextId)

        paramPosEta = _util.findOrCreateElement(self.document, context, 'param', 'towerMaskPosEta')
        paramPosEta.setAttribute('type', 'vector:uint')
        maskPosEta = paramPosEta.firstChild
        if not maskPosEta:
            maskPosEta = self.document.createTextNode(_towerMask.blankMask())
            paramPosEta.appendChild(maskPosEta)

        paramNegEta = _util.findOrCreateElement(self.document, context, 'param', 'towerMaskNegEta')
        paramNegEta.setAttribute('type', 'vector:uint')
        maskNegEta = paramNegEta.firstChild
        if not maskNegEta:
            maskNegEta = self.document.createTextNode(_towerMask.blankMask())
            paramNegEta.appendChild(maskNegEta)

        if tower._ieta > 0:
            _towerMask.addTower(maskPosEta, tower)
        else:
            _towerMask.addTower(maskNegEta, tower)

    def addTowerMaskAllContexts(self, dummyTower):
        # TODO
        pass
