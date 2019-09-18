#!/usr/bin/python
#Takes a directory of host files and produce an rpz zone
#This is not a script, call it whatever you want but not script, alternative suggested name are:
#  - this, thing
#  - stuff, gudget, gimmik
#  - program, scheduled job
#  - integration, automation, project
#You are also encuraged to rewrite it in any interpreted and not compiled language you wish

import os, sys, re, syslog, \
       getopt, fcntl, time

hosts_dir='./tmp/'
verbose=0
verbose_level=1

hostifle_suffix='\.host'
syslog.openlog('hostfile_to_rpz',logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)

def shout(level,message,too=''):
  if level < verbose_level:
    syslog.syslog(message)
    if verbose:
      print (message+' '+too)


def main(myself,argv):
  inputdir = './tmp/'
  outputfile = '/tmp/block_zone.rpz'
  print_dups = 0
  myself=os.path.basename(myself)
  lock_name='/tmp/'+myself+'.lock'
  #avoid multiple concurrent run
  lock_fh=open(lock_name,'a+')
  try:
    fcntl.flock(lock_fh.fileno(),fcntl.LOCK_EX | fcntl.LOCK_NB)
  except IOError:
    shout(0,myself+' aborting other istance running' )
    sys.exit(2)

  shout(0,myself+' starting')

  try:
    opts, args = getopt.getopt(argv,"hvnd:o:",["idir=","ofile="])
  except getopt.GetoptError:
    print('test.py -n -d <inputdir> -o <outputfile>')
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print('test.py -n -d <inputdir> -o <outputfile>')
      sys.exit()
    elif opt == '-n':
      print_dups = 1
    elif opt == '-v':
      verbose = 1
    elif opt in ("-d", "--idir"):
      inputdir = arg
    elif opt in ("-o", "--ofile"):
      outputfile = arg
  print ('Input file is ', inputdir)
  print ('Output file is ', outputfile)

  try:
    rpz_fh=open(outputfile+'.tmp',"w")
  except EnvironmentError:
   shout(0,'cannot open '+outputfile+'.tmp')
   sys.exit(2)

  #head_zonefile(rpz_fh,'pippo.it','ns1.pippo.it',None)
  head_zonefile(rpz_fh,'pippo.it','ns1.pippo.it.','ns2.pippo.it')
  write_rpz_content(inputdir,rpz_fh,print_dups)
  rpz_fh.close()
  try:
    os.rename(outputfile+'.tmp',outputfile)
  except EnvironmentError:
   shout(0,'cannot rename '+outputfile+'.tmp to '+outputfile)
   sys.exit(2)


  #release lock
  fcntl.flock(lock_fh.fileno(),fcntl.LOCK_UN);
  lock_fh.close()

def head_zonefile(rpz_fh,rpz_domain,rpz_master,rpz_slave, rpz_hostmaster='null@irds.it', \
  rpz_ttl='2h', rpz_refresh='12h', rpz_retry='15m',rpz_expire='3w',rpz_minttl='2h'):
  rpz_fh.write('$TTL '+rpz_ttl+";\n")
  rpz_fh.write('$ORIGIN '+rpz_domain+".\n")
  rpz_fh.write('@       SOA '+rpz_master.rstrip('.')+'. '+rpz_hostmaster.replace('@','.').rstrip('.')+". (\n")
  #rpz_fh.write('        '+format(int(time.mktime(time.localtime())))+"\n")
  rpz_fh.write('        '+time.strftime("%s")+"\n") #undocumented "%s"
  rpz_fh.write('        '+rpz_refresh+"\n")
  rpz_fh.write('        '+rpz_retry+"\n")
  rpz_fh.write('        '+rpz_expire+"\n")
  rpz_fh.write('        '+rpz_minttl+")\n")
  rpz_fh.write(";ns list\n")
  rpz_fh.write('        NS '+rpz_master.rstrip('.')+".\n")
  if rpz_slave != None:
    rpz_fh.write('        NS '+rpz_slave.rstrip('.')+".\n")
  rpz_fh.write(";begin RPZ RR definitions\n")

  


def write_rpz_content(hosts_dir,rpz_fh,print_dups):
  #read file list
  try:
    hostfiles=os.listdir(hosts_dir)
  except EnvironmentError:
    shout(0,'cannot os.listdir '+hosts_dir)
    sys.exit(2)

    
  domain_cache={}
  for hostfile in hostfiles:
    if re.match('.*'+hostifle_suffix+'$',hostfile):
      shout(0,'parsing '+hostfile)

      try:
        hostfile_content_ary=open(hosts_dir+'/'+hostfile).readlines()
      except EnvironmentError:
        shout(0,'cannot open '+hosts_dir+'/'+hostfile)
        sys.exit(2)

      rcnt=0
      for host_row in hostfile_content_ary:
        rcnt+=1
        if (re.match('^(#.*|)$',host_row)):
          continue
        host_row=host_row.rstrip().rstrip('\r\n')
        #parse and validate host row
        row_field=re.search('^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([\w\.\s]+)$',host_row)
        if row_field == None:
            shout(0,'malformed row '+hostfile+':'+format(rcnt),host_row)
            continue
        domain=row_field.group(2)
        #check dups
        if domain not in domain_cache:
          domain_cache[domain]=row_field.group(1)
          #output a formatted string "{: <32}" will not truncate rows
          rpz_fh.write('{: <32}'.format(domain)+' IN A '+row_field.group(1)+"\n")
        elif print_dups:
          rpz_fh.write('{: <32}'.format(domain)+' IN A '+row_field.group(1)+"\n")
        else:
          #suppress duplicates
          shout(2,'suppressing dups '+hostfile+':'+format(rcnt)+' '+domain,'')

        #print(row_field.group(1)+' '+row_field.group(0))

main(sys.argv[0],sys.argv[1:])
#main(sys.argv)
