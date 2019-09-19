# hostfile_to_rpz

Purpose for this is producing an rpz zone file starting from one or more hostfile.

## Usage
 
```
hostfile_to_rpz.py [-v] [-n] [-d /etc/hostfiles/] [-o /var/bind/rpz/rpz_zone_file.rpz]
```
  - **-n** don't suppress duplicated record 
  - **-v** print steps to stdout
  - **-d** set input dir path
  - **-o** set output file path

## Contributing
Not much contributing here, in the insane case you are willing to, next wanted feature are:
  - A config file to control parameters to avoid control switch explicitation.
  - More control switch (syslog suppression/facility, verblevel,...)

## Disclaimer
This is not a script, call it whatever you want but not script, alternative suggested name are:
  - this, thing
  - stuff, gudget, gimmik
  - program, scheduled job
  - integration, automation, project

## See also
[https://github.com/f3sty/hosts2rpz]
