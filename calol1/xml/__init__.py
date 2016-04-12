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
        print 'Debug output, TODO'

    def addLinkMaskByTower(self, tower):
        contextId = tower.contextId()
        linkId = tower.linkId()
        context = _util.findOrCreateElement(self.document, self.run_settings, 'context', contextId)
        _util.findOrCreateElement(self.document, context, 'mask', linkId)

    def addTowerMaskByTower(self, tower):
        contextId = tower.contextId()
        context = _util.findOrCreateElement(self.document, self.run_settings, 'context', contextId)

        paramPosEta = _util.findOrCreateElement(self.document, context, 'param', 'towerMaskPosEta')
        maskPosEta = paramPosEta.firstChild
        if not maskPosEta:
            maskPosEta = self.document.createTextNode(_towerMask.blankMask())
            paramPosEta.appendChild(maskPosEta)

        paramNegEta = _util.findOrCreateElement(self.document, context, 'param', 'towerMaskNegEta')
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
