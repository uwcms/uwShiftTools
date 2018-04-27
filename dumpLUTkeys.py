#!/usr/bin/env python
import calol1.omds

calol1.omds.connect()
cur = calol1.omds.dbConnection.cursor()
cur.execute("""
select algo.id, algo.creation_date, algo.conf, algo.description, rs.runnumber, rs.starttime
from (
    select algo.id aid, min(rs.runnumber) rid
    from cms_trg_l1_conf.calol1_clobs algo
    left join cms_trg_l1_conf.calol1_keys calokeys on algo.id = calokeys.algo                                                                                                                                
    left join cms_trg_l1_conf.l1_trg_conf_keys l1conf on calokeys.id = l1conf.calol1_key
    left join cms_wbm.runsummary rs on l1conf.id = rs.tsckey
    where algo.keyname='algo_Base'
    group by algo.id
) algo_firstrun
inner join cms_trg_l1_conf.calol1_clobs algo on algo.id = algo_firstrun.aid
left join cms_wbm.runsummary rs on rs.runnumber = algo_firstrun.rid
where rs.runnumber is not null
order by algo.creation_date asc
""")

print "| Key name | Checksum | Insertion date | First run | First run date | Description |"
for row in cur:
    name, time, clob, desc, firstrun, firstrun_time = row
    clobstr = clob.read()
    p = clobstr.find("md5checksum")
    cksum = clobstr[p+27:p+27+32].strip('</p')  # strip because of bug in old keys where not exactly 32 characters
    cksum = '=%s=' % cksum  # for nice TWiki formatting
    print "| %20s | %34s | %10s | %7d | %10s | %s |" % (name, cksum, time.strftime("%Y-%m-%d"), firstrun, firstrun_time.strftime("%Y-%m-%d"), desc.replace("\n", " "))
