import cx_Oracle as _ora
import os as _os

dbConnection = None

def connect():
    '''
        Setup a database connection to OMDS
    '''
    global dbConnection
    user = 'cms_calol1'
    pwPath = '/nfshome0/centraltspro/secure/%s.txt' % user
    if not _os.path.exists(pwPath):
        raise Exception("Cannot open password file for database connection")
    with open(pwPath) as pwfile:
        pw = pwfile.read().strip()
    dbConnection = _ora.connect('{user}/{pw}@CMS_OMDS_LB'.format(user=user,pw=pw))

def list_rs_keys():
    cur = dbConnection.cursor()
    cur.execute("select id from cms_trg_l1_conf.calol1_rs order by creation_date desc")
    for row in cur:
        yield row[0]

def get_rs_key(key):
    cur = dbConnection.cursor()
    fields = ['id', 'description', 'author', 'creation_date', 'conf']
    query = "select %s from cms_trg_l1_conf.calol1_rs where id=:id order by creation_date desc" % ','.join(fields)
    cur.execute(query, id=key)
    row = cur.fetchone()
    if row:
        return dict(zip(fields, row))
    raise Exception("No run setting entry with key %s exists!" % key)
