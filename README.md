r53bg
---

> This tool is designed to aid in automating blue green deployments with route53.
r53bg allows for slowly transitioning load from one environment to another through the use of weighted round robin record sets.


### Usage

r53bg <Zone ID> <FQDN> <from> <to> <rate>

 - Zone ID - the Hosted Zone ID work work in
 - FQDN - full domain record to operate on e.g. test.example.com.
 - from - SetID in the WRR set you like to move from
 - to - SetID in the WRR set you like to move to
 - rate - is the change of the WRR values every 30 seconds i.e. 10 will cause r53bg to take 300 seconds to change the WRR values by 100