#!/usr/bin/env python
# 
"""netstat-tool.py
Process netstat -s outputs

2021/5/24 9:00
Ip:
    103427751422 total packets received
    527 forwarded
    0 incoming packets discarded
    :
Icmp:
    13535584 ICMP messages received
    1711 input ICMP message failed.
    ICMP input histogram:
        destination unreachable: 46993
        timeout in transit: 1470
        echo requests: 13485660
        echo replies: 1461
    13536498 ICMP messages sent
    0 ICMP messages failed
    ICMP output histogram:
        destination unreachable: 47407
        echo request: 3539
        echo replies: 13485552
"""

import sys,os,re,copy
from string import Template
assert sys.version_info >= (3, 5)

#metricLinePattern = re.compile('(?P<pre>[^\d]*)(?P<val>\d+)(?P<post>[^\d]*)$')
#metricLinePattern = re.compile('(?P<pre>[^\d]*)(?P<val>\d+)(?P<post>[^\d]*)$')
#metricLinePattern = re.compile('(?P<pre>[^\d]+)(?P<val>\d+)(?P<post>[^\d]*)$')
#metricLinePattern = re.compile('(?P<pre>([^\d]+|[a-zA-Z ]+\d+: +))(?P<val>\d+)(?P<post>[^\d]*)$')  
metricLinePattern = re.compile('(?P<pre>([^\d]+|[^\d]+\d+:[ ]+))(?P<val>\d+)(?P<post>[^\d]*)$')  
secHdrPtn = re.compile('^(?P<hdr>[a-zA-Z]+):')
subHdrPtn = re.compile('^ +(?P<hdr>[a-zA-Z ]+): *$')
indPtn = re.compile('^(?P<ind> +)')
tsPtn = re.compile('^(?P<ts>\d+/\d+/\d+ \d+:\d+)')

def addData(data, key, value):
    if key not in data.keys():
        data[key] = [value]
    else:
        data[key].append(value)

def mkMetName(sec, subSec, omet):
    return sec + '_' + subSec + '_' + omet 

def concatPrePost(pre, post):
    if pre == '':
        return post
    elif post == '':
        return pre
    else:
        return pre + " " + post


class NetstatUtil:
    def __init__(self, stream, verbose=False):
        self.stream = stream
        self.lastICMPLine = ''
        self.lastSecHdr = ''
        self.lastSubHdr = ''

    def process(self): 
        data = dict()
        lastNind = 0
        for line in self.stream:
            tsm = tsPtn.match(line)
            matched = False
            if tsm != None:
                matched = True
                ts = tsm.group('ts')
                addData(data, 'ts', ts)
                #print("TS: %s" % (tsm.group('ts')))
                #print(data)

            shm = secHdrPtn.match(line)
            if shm != None:
                matched = True
                self.lastSecHdr = shm.group('hdr') 
                self.lastSubHdr = ''


            nind = 0
            ins = indPtn.match(line)
            if ins != None:
                nind = len(ins.group("ind"))
            else:
                nind = 0

            sbhm = subHdrPtn.match(line)
            if sbhm != None:
                matched = True
                #print("D: subhdr match" + sbhm.group('hdr').strip())
                self.lastSubHdr = sbhm.group('hdr').strip()

            mt = metricLinePattern.match(line)
            if mt != None:
                matched = True
                #print("%s / %s / %s" % (mt.group("val"), mt.group("pre"), mt.group("post")))
                #print("%s / %s" % (mt.group("val"), 
                #    (mt.group("pre") + mt.group("post")).strip().replace(" ", "-").replace(":","")))
                #print("%s / %s / %s / %d" % (mt.group("val"), 
                #    (mt.group("pre") + mt.group("post")).strip().replace(" ", "-").replace(":",""), self.lastSecHdr, nind))
                #print("D: " + (mt.group("pre") + '-' + mt.group("post")).strip())
                #print("D: " + concatPrePost(mt.group("pre").strip(), mt.group("post").strip()))
                cmet = concatPrePost(mt.group("pre").strip(), mt.group("post").strip())
                #mn = mkMetName(self.lastSecHdr, self.lastSubHdr, (mt.group("pre") + '-' + mt.group("post")).strip().replace(" ", "-").replace(":",""))
                mn = mkMetName(self.lastSecHdr, self.lastSubHdr.replace(" ", "-"), cmet.replace(" ", "-").replace(":","").replace(".",""))
                #print(mn)
                addData(data, mn, mt.group("val"))
            #else:
                #    print("NG: " + line)

            lastNind = nind 
            
            if matched == False:
                print("W: not matched with any: " + line)

        return data
                   

def processFile(path):
    print("processFile: " + path)
    with open(path) as f:
        nu = NetstatUtil(f)
        return nu.process()

def writeCSV(fn, data):
    keys = data.keys()
    hdr = ",".join(list(map(lambda v: '"'+v+'"', keys)))
    ndata = len(data['ts'])
    #print(hdr) 
    #print("len: %d" % ndata)
    with open(fn, 'w') as f:
        f.write(hdr + "\n")
        for i in range(ndata):
            vs = []
            for k in keys:
                try:
                    vs.append('"' + data[k][i] + '"')
                except IndexError:
                    msg = "key %s is NOT in data" % (k)
                    if k in data:
                        msg = "key %s is in data" % (k)
                    datak_len = len(data[k])
                    print("E: IndexError in writeCSV i: %d, k: %s, ndata %d, msg: %s, datak_len %d" % (i, k, ndata, msg, datak_len));
            l = ",".join(vs)
            f.write(l + "\n")
      
def writeC3(fn, data):
    keys = data.keys()
    p1 = '''<html>
<header>
<!-- Load c3.css -->
<link href="./js/c3.css" rel="stylesheet">
<link href="./js/my.css" rel="stylesheet">

<!-- Load d3.js and c3.js -->
<script src="./js/d3.min.js" charset="utf-8"></script>
<script src="./js/c3.min.js"></script>
</header>
<body>
'''
    p2 = '''</body>
</html>
'''
    divTs = '''<div id="$k" style="height: 200px; width: 500px; display: inline-block;">$k</div>
'''
    divt = Template(divTs)
    c3genTs = '''var chart = c3.generate({
    bindto: '#$k',
    data: {
      columns: [
        $vals 
      ]
    }
});
'''
    c3gent = Template(c3genTs)

    keys = list(data.keys()).copy()
    keys.remove('ts')
    with open(fn, 'w') as f:
        f.write(p1)
        f.write("netstat graph<br/>\n")
        f.write("<div class=\"note\">xaxis to time: ")
        ets = list(enumerate(data['ts']))
        head = ets[:4]
        tail = ets[-2:]
        #f.write(str(list(enumerate(data['ts'][:4]))) + "..." + str(data['ts'][-2:]))
        f.write(str(head) + "..." + str(tail))
        f.write("</div>\n")
        for k in keys:
            f.write(divt.substitute(k=k))
        f.write("<script>\n")
        for k in keys:
            vals = list(data[k]).copy()
            vals.insert(0, k)
            f.write(c3gent.substitute(k=k, vals=vals))
        f.write("</script>\n")
        f.write(p2)

def showHelp():
    m = """usage: netstat-tool.py [-h] [<file> ... ]
      -h: show help and exit
    """
    print(m)

if __name__ == '__main__':
  import getopt
  optlist, args = getopt.getopt(sys.argv[1:], 'hv', [])
  enableVerboseLogging = False

  for otup in optlist:
    opt = otup[0]
    if opt == '-h':
      showHelp()
      sys.exit(0)
    elif opt == '-v':
      enableVerboseLogging = True

  # print("I: args: " + str(args))
  try:
    if len(args) > 0:
      for f in args:
        r = processFile(f)
        #print(r)
        writeCSV("out.csv", r)
        writeC3("out.html", r)
    # elif len(args) == 0:
    #   processStdin()
  except BrokenPipeError:
    sys.exit(0)
