try:
    import cx_Oracle as _ora
except ImportError:
    print "ERROR: Could not load cx_Oracle library necessary for OMDS database queries"
    print "       Suggestion: check that you have CMSSW environment or otherwise find"
    print "       a method to add cx_Oracle to your python path."
    raise
import os as _os
import datetime

dbConnection = None


def connect(user='cms_calol1'):
    '''
        Setup a database connection to OMDS
    '''
    global dbConnection
    if user == 'cms_trg_r':
        dbConnection = _ora.connect('cms_trg_r/X3lmdvu4@cms_omds_adg')
        return
    pwPath = '/nfshome0/centraltspro/secure/%s.txt' % user
    if not _os.path.exists(pwPath):
        raise Exception("Cannot open password file for database connection")
    with open(pwPath) as pwfile:
        pw = pwfile.read().strip()
    dbConnection = _ora.connect('{user}/{pw}@CMS_OMDS_LB'.format(user=user, pw=pw))


def list_rs_keys():
    cur = dbConnection.cursor()
    cur.execute("select id from cms_trg_l1_conf.calol1_rs order by creation_date desc")
    for row in cur:
        yield row[0]


def get_rs_key(key):
    cur = dbConnection.cursor()
    fields = ['id', 'description', 'author', 'creation_date', 'conf']
    query = "select %s from cms_trg_l1_conf.calol1_rs where id=:id" % ','.join(fields)
    cur.execute(query, id=key)
    row = cur.fetchone()
    if row:
        return dict(zip(fields, row))
    raise Exception("No run setting entry with key %s exists!" % key)


def get_mask_xml(rs_key):
    cur = dbConnection.cursor()
    query = """
        select link_masks.conf, tower_masks.conf
        from cms_trg_l1_conf.calol1_rs_keys rs_keys
        left join cms_trg_l1_conf.calol1_rs link_masks on rs_keys.link_masks = link_masks.id
        left join cms_trg_l1_conf.calol1_rs tower_masks on rs_keys.tower_masks = tower_masks.id
        where rs_keys.id=:id
    """
    cur.execute(query, id=rs_key)
    row = cur.fetchone()
    if row:
        return (row[0], row[1])
    raise Exception("No run setting entry with key %s exists!" % rs_key)


def current_rs_keys():
    cur = dbConnection.cursor()
    fields = ['l1hlt.l1_hlt_mode', 'l1hlt.id', 'l1rs.calol1_rs_key']
    query = """
        select {fields}
        from cms_l1_hlt.v_l1_hlt_conf_extended l1hlt
        left join cms_trg_l1_conf.l1_trg_rs_keys l1rs on l1hlt.l1_trg_rs_key = l1rs.id
    """.format(fields=','.join(fields))
    cur.execute(query)
    fields_underscore = map(lambda s: s.replace('.', '_'), fields)
    for i, row in enumerate(cur):
        yield dict(zip(fields_underscore, row))


def run_summary(sinceDate=None, toDate=None, minEvents=1000, limit=200):
    cur = dbConnection.cursor()
    fields = [
        'rs.runnumber',
        'rs.starttime',
        'rs.triggers',
        'rs.events',
        'rs.lhcfill',
        'rs.ecal_present',
        'rs.hcal_present',
        'rs.tier0_transfer',
        'rs.triggermode',
        'l1hlt.l1_trg_conf_key',
        'l1hlt.l1_trg_rs_key',
        'l1conf.calol1_key',
        'l1rs.calol1_rs_key',
        'calol1rs.link_masks',
        'calol1rs.tower_masks',
        'calol1rs.author',
    ]

    if not toDate:
        # Default: now
        toDate = datetime.datetime.now()
    if not sinceDate:
        # Default: toDate - day
        sinceDate = toDate - datetime.timedelta(1)

    query = """select {fields}
        from cms_wbm.runsummary rs
        left join cms_l1_hlt.l1_hlt_conf_upgrade l1hlt on rs.triggermode = l1hlt.id
        left join cms_trg_l1_conf.l1_trg_conf_keys l1conf on l1hlt.l1_trg_conf_key = l1conf.id
        left join cms_trg_l1_conf.l1_trg_rs_keys l1rs on l1hlt.l1_trg_rs_key = l1rs.id
        left join cms_trg_l1_conf.calol1_rs_keys calol1rs on l1rs.calol1_rs_key = calol1rs.id
        where rs.username = 'toppro' and rs.trg_present = 1
            and rs.starttime between :sinceDate and :toDate
            and rs.events > :minEvents
        order by rs.runnumber desc
    """.format(fields=','.join(fields))
    cur.execute(query, sinceDate=sinceDate, toDate=toDate, minEvents=minEvents)
    fields_underscore = map(lambda s: s.replace('.', '_'), fields)
    for i, row in enumerate(cur):
        if i < limit:
            yield dict(zip(fields_underscore, row))
        else:
            return
