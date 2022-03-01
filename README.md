# netstat-tool

## Summary
netstat-tool processes reppeated pattern of timestamp (YYYY/mm/dd HH:MM) and netstat -s output from Linux and generates csv file and html file which contains graph of netstat -s metrics.

Following shell script generate the expected input.  The output needs to be redirected to a file.

```sh
#!/bin/bash

while true; do
  date +"%Y/%m/%d %H:%M"
  netstat -s
  sleep 60
done
```

The tool is a Python 3 script and it requires Python 3.5 or higher.

## Output
If the script completes successfully, it creates two outputs, out.csv and out.html.

out.csv can be read by spreadsheet applications.

sample:
```
$ cut -d, -f 1-8 out.csv | sed 's/$/,.../'
"ts","Ip__total-packets-received","Ip__with-invalid-addresses","Ip__forwarded","Ip__incoming-packets-discarded","Ip__incoming-packets-delivered","Ip__requests-sent-out","Icmp__ICMP-messages-received",...
"2022/03/02 06:44","3632","2","0","0","3630","2369","0",...
"2022/03/02 06:45","3800","2","0","0","3798","2495","0",...
"2022/03/02 06:46","4025","2","0","0","4023","2712","2",...
"2022/03/02 06:47","4027","2","0","0","4025","2712","2",...
"2022/03/02 06:48","4029","2","0","0","4027","2712","2",...
"2022/03/02 06:49","4087","2","0","0","4085","2743","2",...
"2022/03/02 06:50","4316","2","0","0","4314","2882","2",...
"2022/03/02 06:51","4641","2","0","0","4639","3195","9",...
"2022/03/02 06:52","5846","2","0","0","5844","4495","106",...
"2022/03/02 06:53","6699","2","0","0","6697","5409","182",...
"2022/03/02 06:54","6996","2","0","0","6994","5720","202",...
"2022/03/02 06:55","7001","2","0","0","6999","5723","202",...
"2022/03/02 06:56","7097","2","0","0","7095","5781","202",...
```

out.html contains graphs written by c3 library (https://c3js.org/) and d3.js (https://d3js.org/).  You need to copy cs.css, c3.min.js and d3.min.js extracted from c3/d3 library to js sub-directory.  my.css is an optional css file to customize fonts, etc.  Sample is listed later.

```
$ ls js
c3.css		c3.min.js	d3.min.js	my.css
```

```html
<html>
<header>
<!-- Load c3.css -->
<link href="./js/c3.css" rel="stylesheet">
<link href="./js/my.css" rel="stylesheet">

<!-- Load d3.js and c3.js -->
<script src="./js/d3.min.js" charset="utf-8"></script>
<script src="./js/c3.min.js"></script>
</header>
<body>
netstat graph<br/>
<div class="note">xaxis to time: [(0, '2022/03/02 06:44'), (1, '2022/03/02 06:45'), (2, '2022/03/02 06:46'), (3, '2022/03/02 06:47')]...[(11, '2022/03/02 06:55'), (12, '2022/03/02 06:56')]</div>
<div id="Ip__total-packets-received" style="height: 200px; width: 500px; display: inline-block;">Ip__total-packets-received</div>
<div id="Ip__with-invalid-addresses" style="height: 200px; width: 500px; display: inline-block;">Ip__with-invalid-addresses</div>
```
  
js/my.css sample
```
js/my.css 
body {
  font-family: "SF Pro JP", "SF Pro Text", "SF Pro Icons", "Hiragino Kaku Gothic Pro", "ヒラギノ角ゴ Pro W3", メイリオ, Meiryo, "ＭＳ Ｐゴシック", "Helvetica Neue", Helvetica, Arial, sans-serif;
}
.note {
  font-size: 80%;
}

```

## Known Issues

It turned out that netstat may add new metrics which did not appear in earlier output.  netstat-tool.py does not handle this situation properly and it would show messages like below.  This issue will be addressed in future.

```
E: IndexError in writeCSV i: 5, k: TcpExt__Quick-ack-mode-was-activated-times, ndata 13, msg: key TcpExt__Quick-ack-mode-was-activated-times is in data, datak_len 5
E: IndexError in writeCSV i: 5, k: TcpExt__TCPLossProbes, ndata 13, msg: key TcpExt__TCPLossProbes is in data, datak_len 5
E: IndexError in writeCSV i: 5, k: TcpExt__DSACKs-sent-for-old-packets, ndata 13, msg: key TcpExt__DSACKs-sent-for-old-packets is in data, datak_len 5
E: IndexError in writeCSV i: 5, k: TcpExt__DSACKs-received, ndata 13, msg: key TcpExt__DSACKs-received is in data, datak_len 5
E: IndexError in writeCSV i: 5, k: TcpExt__TCPDSACKIgnoredNoUndo, ndata 13, msg: key TcpExt__TCPDSACKIgnoredNoUndo is in data, datak_len 5

```
