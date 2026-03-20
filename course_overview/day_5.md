Remember prefix compression


appreciate
appredo
apprea


All these 3 entries will share the same index becuase they start with "appre" -> this is what is the prefix compresssion


- ideally we will have between 4 and 10 index (more than 20 is crazy, max is 64 per collection)


explain: query Planner, executionStats, allPlansEcexution --_> the most useful is executionStats

```sh
createIndex({fiedl: 1 }, {unique: true}) --> we can not create 2 documents with the same value in the index field 
```

# Logging

<check this part>

# Accessing database logs

`/var/log/mongodb/mongod.log`

In atlas we can not access to the machine

- getLog command


There are some options in atlas to deploy yopur cluster, in that case it would be dedicated

# getLog command

```sh
var loglines = db.adminCmmand( { getLog: "global"})

db.log.insertMany(loglnes)

db.log.find().pretty()   -> we will see it but with aggregations like $sortByCount
```

# Find slow operarions using logs

By default only queries that take more than 100 ms are logged --> we can modify the threshold

However if you log everything, it increases dramatically the server workload.

# Log file output format

They will not ask the type of logs

# Database profiler

Records info about slow operations
Stored in a internal collection (up to 10mb) -> system.profile

Can be enabled or disabled per each database

- Creates extra writes, always turn off profiled unless required

# setProfilingLevel(level, slowms)

level:
    0 (off)
    1 (only slow queries)  -----------> default value
    2 (all queries, not recommended)


slowms: threshold in miliseconds for a slow operation (default is 100 ms)

Data will be stored in a collection system.profile

# db.getProfilingStatus()   -> discover how is the current profiler setup

# query profiler data

```sh
show profile
```

# server status

```sh
db.serverStatus()
```

-  HOST
- version
- process: mongod (mongo demon)
- pid
- uptime
- localtime
- connections

# tools for system monitoring

- mongotop
- mongostat
- htop

```sh
db.serverStatus().wiredTiger.status --> engine to write in disk
```

# Some causes of slow opeerairons

- The operation is not using an index --> reads a lot of docuemnts and has to sort the,

- insufficient memory

- needs to paginate because we exceed the cache

- some tasks are locking the data (eg backups)

- excessive cpu usage:
    - constantly authenticating : remember scram was slow on purpose
        never do
            with client() as c:
                only one op()
    - extremely large arrays
    - extremely complex aggregations
    - sorting without index
    - using server-side javascript eg: computed fields -> this field is a js function (deprecated, it has security concerns)

# Example slow op explain()

docsExamined: 277750
nreturned: 0
planSummary: COLLSCAN
executionTimemIllisEstimate: 15356  -> 15 seconds

# Find slow ops in atlasç

- Performance advisor: recommends to create or to drop indexes based on your usage

- query profiler: tells you which queries are heavy and often used

- real time performance panel: helps you analyze performance (coulds be asked)


In atlas we can see charts with usage over time i we could see which user launched the heavy query

# Atlas cluster metrics: something like prometheus

# atlas query insights:

paid only --> 


namespace insights --> points to the slow queries
query profiler --> shows slow operations graphically

```sh
- getLog() -> returns 1024 entries

- setProfilingLevel(1, 2)  -> 2ms slow queries, only logs slow queries --> it will cause a large write workload

- one update includes a query, if it has no index can be slow if we have too many updates

- there are different support tiers like aws business, enterprise etc..
```


# INTRO to atlas search

# Atlas search

Text indexes had some advantages while working with text.

- Atlas search is not part of the mongodb server and it is not opensource

- It uses Lucene (elastic search engine) as the backgorund engine

```sh
db.movies.find({ title: /Raising Arizona/ })  -> contains that text, remember that / was regex --> this is unefficient
```

# Using search atlas

```sh
db.movies.aggregate([{$search: {text: {query: "Raising Arizona", path: "title"}}}]) --> will find similar text that match in the title
```

Each match will have a score

eq query: Javascript Book

result:
    Javascirpt the definitive guide: SCORE=75
    Introducing to Mongo:            SCORE = 10

# Loading sample data

- create a default search index .> visual editor

in the gui, you create the atlas search index, this generates a json that you can manually modify.

# searching from the code

check the presentation, there is an example query

they can ask you the syntax , the wildcard: "*" means that it is searched in any field

```sh
{$search: {
    index: "default",
    text: {
        query: "sentence",
        path: {wildcard: "*"}
    }

}}
```

In the web there is a "Search tester" where you can do this query but in a web form, it would be equivalent to this

# Viewing the result relevance (socre)

```sh
{$search: {
    index: "default",
    text: {
        query: "sentence",
        path: {wildcard: "*"}
    }

}, {$set: {score: {"$meta": "searchScore}}}}  -> this set adds the score of the lucene search
```

# Atlas vector search

- semantic search
- Question and answer systems
- image retrieval

```sh
db.col.aggregate([{"$vectorSearch":{
    "index": "vector_index",
    path: "PLOT_EMBEDDING",
    "queryVector": [0.54151, ....],
    "numCandidates": 40,
    similarity: "euclidean"
}}])
```

besides, you can you to the atlas web to create an index type "Atlas vector search"

on top of that you have the json editor to generate queries with the gui.

```sh
db.col.aggregate([{"$vectorSearch":{
    "index": "vector_index",
    path: "PLOT_EMBEDDING",
    "queryVector": [0.54151, ....],
    "numCandidates": 40,
    similarity: "euclidean"
}, {$project: {...}}}])   -> check presentation
```

EXAM: PRACTICE and create a index for atlas search you will have to know the syntax and the $search operator


run atlas locally: https://www.mongodb.com/docs/atlas/cli/current/atlas-cli-deploy-docker/

# RAG with vector search

# dedicated search nodes

With atlas search we need some extra nodes that connect to our cluster but do not are part of it,
simply it requires some extra services to run thge lucene

- vector search requires vector search nodes also

- with this design the search and vector search workload is decoupled and scalates horizontally.

# Aggregate command:

it is a series of searches that create a pipeline

eg.
    stage1: search
    stage2: projection

Hnece it is like.

agreggate([ array of operations ])


- Remember to do $search or $vectorSearch YOU NEED TO CREATE FIRST THE INDEX"!!!

# MDB300

- rEPLICATION
- Replica set
- concept of majority
- how elections happend
- real concerns and preferences

# Replication

- we get resilience and high availability 

- with sharding we can scalate 

we get:

- high availability
- reduced read latency --> read from a node geographically close to you
- support to different access patterns

# High availability

- data still available after:
    - equipment failure
    - dataCENTER failure

- Achieved throughtr automatic failover:
    - remaining servers have an election
    - high availability means that if main node fail, the change if fast and a new node 

# Different access patterns

if 90% users only read 1% of data (small eought to remain in cache)

If 10% look at all data (analysts):
    - do not need suach a fast response ..> can read from another node

# Replica set components

- Primary member

- Secondary members

- Non voting members

# Secondary members

as a copy of the data from the primary

type of secondary:
    - priority 0 or 1 or 50 and so on --> if all have priority 5, all have the same likelihood of becoming primary -> the one with the highest priority will become the primary
    - hidden node: no client can connect to them, even if you configure the client to connect if possible to a secondary
    - delayed node: not recoomended, they were used to maintain an old backup, but nowadays are not recommended --> its functionality is covered by **backups**

# Drivers and replica sets

- as programmer you dont need to know which one is the primary, the driver routes it
- if the server is updated, you should update the driver

# replicaiton process:

- the primary sends the data to secondaries
- primary applies the changes ABD STORES THE CHANGES NI THE OPERATION LOG (OP LOG)
- secondaries observe the oplog and apply them to themselves
- then the secondaries inform the primary about to which point they are updated

# Oplog 

Is a read only capped (it has a fixed size, eg 1gb, new documents erase old once full) collection of BSON documents, we can not manually write.

Each change is registered in the op log by the primary:

    - create collecitons
    - delete indexes
    - etc

Reads are not storeds in the op log. 
It is stored in the database "local" (remember that all clusters will have the dbs local and admin)

# oplog entries are idempotent

If the change is increment 2 --> it store set 5, this is they store the final result, not the change 

- so they store the final value not the changes

- the entries in the OPLOG are not relative to the previous, its like
    we got 10 in field x
    we got 55 in field x
    we got "adxwsx" in field y
    we got 5 in field x
    we got 9 in field x

# Oplog windows

- they guarantee the preservation of the insertion order
- they support high throughtput operations
- once the fixed size is full, it removes old entries

# Sizing the oplog

- The size of the oplog has to be large enough to support replication
    - if you write 10 mb/hour and a 1gb Oplog is ok
    - if there is a peak of write 200mb/hour --> our oplog only lasts 5 hours --> it could fail if a secondary is down for 6 hours

    - IF IT FAILS: initial resynch --> copy everything, slow, document by a document -> hence physically in the disk will not be in the same order -> the index also will not be the same .


    - We should seek for at least 24 hours of oplog minimum

    - ideally 3 days of oplog 

# Initial sync

- When new replicas, the have to do a full copy
- if the oplog has rolled over
- can be realtive fragile
- can auto restart on non transient errors
- copy oplog at the same time
- could use a secondary node as source to not saturate the primary

# replication:

- increases network usage because it has to copy data
- allows in some cases to reduce latency
- idential copies so failure resistance and high availability
- allows different accessing patterns --> to not saturate the primary we can read from the secondary
