# The idea of majority


I have **missed a part of the lesson (5 min)**






# Elections

- Mongo uses RAFT protocol

- Only one primary can be chosen at a time --> avoid "split brain"

For a node to be chosen:
    - The chosen primary has to be able to communicate with the majority of members
    - The chosen primary has to have the data updated (or has to have the most recent version among the candidates)

Process:
- One secondary detects that the primary connection is lost after some time
- checks that it has access to the majority
- checks if it can become itself a primary
- launches an election and proposes itself as primary

- in the proposal:
    - it says its latest transaction time
    - votes for itself by default

Rules:
    - a node can be voted if has the nost recent data
    - it is not already voted in a previous election
    - it is not the current primary

When it receives the majority of votes:
    - becomes a primary
    - goes through an on boarding
    - starts to accept writes

# Onboarding a primary

- If one node haas been chosen:
    - checks if any secondary has a more recent data copy and updates itself
    - checks if any secondary has a bigger priority, in that case, resigns and gives the primary title to the other
- the onboarding takes a few seconds

- it could happend that a primary downgrades itself and proposes another

- The goal is to not lose any data that its confirmed

# Primary stepping down

- if the primary is overloaded or can not handle petitions or to be up to date:
    - it downgrades itself
    - the user explicitly tells to downgrade
    - it will happend if it detects that it can not contact with the majority

# In summary

There are multiple servers with the same data

- data is durable when it is confirmed in a majority of voting servers
data takes time to propagate, normally miliseconds
- there can be non voting servers for extra tasks (the will not contribute to the high availability)


Example
---------------------
Datacenter 1
2 nodes -> 1 primary

Data center 2
2 secondary nodes


If  connection between datacenters falls

In order to have a primary it needs to have a connection with 3 nodes--> the cluster will fall because there is no node that has a connection .

The primary will step down and we will have 4 secondaries and no primary --> the cluster will stay in read only until there is a node that can see 3 nodes

One solution would be autoscaling in one datacenter to add a new node. 


REMEMBER MAYORITY:
    IF THEY ARE 3 THE PRIMARY NEEDS TO SEE 2 (ITSELF PLUS ANOTHER)
    IF THEY ARE 5 THE  PRIMARY NEEDS TO SEE 3
    IF THEY ARE 6 THE PRIMARY NEEDS TO SEE 4

- the golden rule isa to use odd number of nodes: 1, 3, 5, 7, 9 etc

- mongo prioritizes availability and partition tolerence, not consistency

# DEVELOPER RESPONSIBILITIES

- devs needs to understand the implications

# Write concerns -quesitons

- when writing to the db:
    - what does durable mean? in any distributed system, we receive an acknowledge (confirmation of write) after sending the petition
    - what does it mean to receive the ACK
    - Is it acceptable losing documents?
    - Who decides which data can never be lost?
    - A lost data, what is better knowing that it has been lost or not to?

# Write concerns

- One app writes data {_id:....}

We have the "W" WRITE concern

- w=1

```sh
    In this case the data will be confirmed that the data is written in the primary, it does not duplicate before confirming

    That is why it focus on availability rather than in consistency

    - If any document is confirmed but the primary falls before the oplog is copied --> data will be lost
    - Our app will think that it was writtten, however it will be lost

    - if the primary goes back online: it sees that it has a document that it is not in the secondaries --> it makes a rollback to that write, it refuses the last insertion that was not replicated, the app does not know that its data has been lost. 
```

# Case for majority writes

In the previous case, If the primary dies before data is copied, it will be lost and the app will think that it was stored

- SOLUTION: WRITE CONCERN MAJORITY --> only send the ACK when it is written in the majority of the nodes

# Majority commit point

- Primary knows what timestamp each secondary is asking for therefore it knows:
    - they have everything before durable
    - up to what timestamp they are synched

# Write concerns

- SEND ACK even if its not confirmed in the primary, automatic ACK --> example logs (we dont care losing 1) --> w: 0
- w: 1
- w: "majority"  -> from mongo 5 it is the default value, in an old setup, w:1 by default (check it)

# w can be configured in the cluster

- but also in the connection (all operations with this connection)
- on each werite operaiton: eg this operation can only be confirmed when duplicated in all nodes

`there is also a timeout`

# Read concerns

- only read when many nodes confirm they have the same data

</br>

- read local
- read majority
- read snapshot --> not very used
- read linearizable -> not very used
- read available: in a sharded cluster

# Read preferences

Where do we want to read from (there is no write preference because the always write on the primary)

- read only form the primary
- read from primary unless no primary existes (primaryPreferred)
- reaad from any secondary
- read from secondary unless no secondary exists
- read from the nearest geographically
- read form an specific set of servers

YOu connect to a kinda DNS AND IT REDIRECTS the connection  based on your preferences

mongodb+srv --> the dns is the srv

# Arbiter

A node can be the arbiter:
    - can not become a primary
    - acts as a tie-breaker in elections (empates)
    - stores no data
    - not recommended in prod

A system with arbiters can be highly availabel or guarantee durability but not botyh

# Replication lag

time between the primary confirms and it is copied to the rest

how to reduce it?
- use the same hardware in all servers
- use appropiate read and write concerns

# troubleshooting replication lag

```sh
rs.status()
```

```sh
rs.printSecondaryReplicationInfo()  -> shows current replication lag
```

# who decides when a transaction is durable?

it is sert up by the developper, the driver, the product owner etc

# SHARDING

it will increase the scalability of the db

shard key -> decides if a document goes to a shard or another (it can be a combination of fields like in an index)

# Sharding: it is a partitioning method

- allows parallel processing
- allows infinite scaling
- allows geographical adaptation

# Sharding vs replication

replication was duplicating all data

sharding consist of different data, each shard is not a copy of the rest, it is different

# resources used by a db
- cpu  -> mongo will use less if we have good indexes and no jjoins
- memory  --> if htei ndexes fit in ram it will be faster
- disk
- network

# horizontal vs vertical scaling

- vertical -> a better pc

- horizontal --> add more servers

sharding is more complex
the first resource is a vertical scaling while i dont nned an excessive amo0unt of ram

# limitations of vertial

- ram usage iws not linear, it can suddenly spike --> shards will help with this, it can work with half the ram

# when to shard?

- in big data
- the resources spike

the data model will be important, mongo is flexible

we need to meet a RTO backup restore time and need parallelism to do so, how much time can we wait to restore from a failure?

example:

A SHARD IS europe data --> we can have that shard in 5 nodes in a cluster in europe

in america we do not have any copy of the europe data


My mongo will be composed of: europe cluster + america cluster + asia cluster
    - data from asia cluster will not be un europe cluster
    - however asia cluster will have the same data (shard) in 3 nodes (replication)

The advantage is that as it grows it auto creates the shards and moves the data if necessary when a new criteria is added
besides we have an unique entrypoint, send a query independently to europe or asia and it redirects

# why understanding sharding now?

we might not need sharding now but in the future if it scales yes, mongo can automatically adapt

# Sharding architecture

| Shard A  |  Shard B   |  Shard C
|----------|------------|------------|
|primary   | primary    | primary    |
|secondary | secondary  | secondary  |
|secondary |secondary   | secondary  |

Hence, there will be one primary node per shard

Besides when we connect, now we do not connect to a primary, we connect to MongoS -> its like a router
there can be many MongoS services to ensure high availability

|   Process  |
|------------|
|  MongoS 1  |
|  MongoS 2  |
|  MongoS 3  |

- Besides we will need a warehouse to store the metadata config

**Metadata cluster**

We will have one cluster per shard, the mongoS's AND A CONFIGURATION CLUSTER with primary and secondaries

The infrastructure would be like:

| Shard A  |  Shard B   |  Shard C   |   Metadata config cluster   |    Process  |
|----------|------------|------------|-----------------------------|-------------|
|primary   | primary    | primary    |       **primary**           |   MongoS 1  |
|secondary | secondary  | secondary  |       **secondary**         |   MongoS 2  |
|secondary |secondary   | secondary  |       **secondary**         |   MongoS 3  |
|          |            |            |                             |   MongoS 4  |

hence the horizontal scalability is clear, it just consist on adding more lcusters

# Sharding uses more hardware

Ideally we need minimum

- 2 cluster shards  
- 2 mnogo S
- 1 metadata cluster

if each cluster has 3 nodes we will have 3 + 3 + 3 + 2 machines
sometimes, the mongoS cna be in the same machine as a node, and it will be lower

# mongoS

Its like a proxy server to connect to the correspondign shard,
it does not store info
- it should be hosted near the app

The data to locate each shard and to redirect is located in theconfig cluster

# Configuration server

- stores where hte data is stored
- stores metasdata abourt users, partitioning

- accesible via mongoS

- storesv the sharding key

- it is a cluster, has a primary and secondaries

# Shard servers

Each shard:
    - a collection can be sharded
    - we need a sharding key: eg form document 1 to a million is shard 1 from one millionm to 2 million is shard 2, etc
    - other collection may not be sharded

    - a database can not be sharded, it is always at a collection level

# Primary shards vs Shard primaries

- sHARD primaries: the primary node of each shard cluester
- primary shard: the main shard, the most important one, were the data is stored if not sharded
    in a db we have 3 collections:
        - col 1 --> not  sharded goes to the primary shaard
        - col 2 --> sharded in 3 shards
        - col 3 --> not sharded, goes to the primary shard

    they often ask a where the not sharded collections go to:
        a) shard primaries? NOPE
        B) primary shard? yes

We could have many databases
    database 1 -> uses europe shard as primary shard
    database 2 -> uses asia shard as primary shard

Hence we set one primary shard per database  
whereas the sharding is configured per collection

# Splitting collecitons

Howe do we divide documents into shards?

example: location

we have 100 burger king stores, hence in the document there is a "store": <> field, we use that to shard

## Shard key

WE could set

from store 1 to 33 -> shard A
from store 34 to 66 -> shard B
from store 67 to 100 -> shard C

if null -> shard A or C (mongo will decide)

we have to consider the number of read and writes to do a good sharding
     if we have 1 TB  in shard A
     and 1 gb in shard B
     - this is not well designed.

we will want to resolve the problem with the minimum number of shards

# Sharidng: distributing operartions

how do we choose the sharding key? example group by stores as we saw

Query --> driver -> mongoS --> query config cluster -> redirect to the shard

- If we we do not send the shard id, it will be sent to all shards (the query) and will only answer the right one

- If the query contains the shard key, it will be only requested to the correct one

- IF THE query contains info from many shards -> mongoS has to do a Merge and sort operation (which is slow)
    - We prefer querys that affect only one shard

# Sharded operaitons: best practices

- Have a good shard key

- query the lowest number of shards

- if a shard is down (an entire replica set), only some operatiosn will fail


- when a query can not point to a shard --> broadcast it (scatter gather)
- if a shard is down:
    - all scather gather queries will fail (operations that need many shards)

# Choosing shard keys

- Included in most queries
- reasonably high cardinality (segregate the data and usage) . with 3 shards we can not use male / female as key
- ideally no more than 128mb of data to share a shard key value
- co-locates data you want to retrieve together.

Effects of a bad key:
    - broadcast queries
    - uneven distribution of data
    - slow down network  if we need to $lookup ( search in different collections, its like a join)

SHARD ONLY large collections

Use compound keuys: eg bank account + transaction_time + session_id  -> segregate by date

If its not possible to create a good key by inspecting the queries --> use fields that allow parallelism (distribute worload)

# changing shard keys

- its possible but avoid if possible
    - it will be like a migration
    - better to add another field to refine the key
    . get the highest cardinality (segregated data)

- you could hash the username and use that as key (idea)
- you could use username + date

If a shard key is monotonically ascending, it is not a good idea. eg the editon of a newspaper -_> over time we will store in the last shard only and we will query only the lat shard  --> SOLUTION. use a hash to add some randomness

- atlas limits to 4 TB per shard

# BACKUPS

Basic backup operations.

# why backups

data is really valuable. we need to be able to recover

# causes of data lñoss

- human error
- db failure corrupt
- system failure
- security break

# what is the hardest thing about backups

- they need to be planned

- the hardest thing: be able to test them and recover them, if not is like haviong nothing

# Backup plan

RPO: recovery point objective --> how much data you can afford to lose?
RTO: recovery time objective -> eg every hour, however if it takes more to apply it, its not real. here the sharding helps

- plan the backup retention time (since when we have copies, do we have the copy from last year? would it be useful?)

# Backup methods

- mongo db atlas continous cloud backups or cloud backups
- mongo db cloud manager or ops manager, backup snapshot

- non managed

# Atlas backup methods

- Cloud backup: snapshots native from aws or azure --> simpler, non managed by us
- continous cloud backups: saves snapshots and the OPLog, can be recoved to an exaxct point

you could recover to latest cloud backup and use the continous oplog to go further

required access: Project vbackup manager or project owner

# mONGO DB enterprisde advanced

 if you have the enterprise license

 - Ops manager / cloud manager --> ops manager is complex to set up (configure your own system to store the backups), cloud manager is simple --> both are incremental
 - additionally:

    you have mongodump + file system recovery (disk image)

# self service backups

document level
    - logical
    - mongodump / mongorestore
    - mongoexport / mongoimport

filesystem level:
    - physical
    - copy files  -> danger
    - volumne / disk snapshots

# mongodump

is the simplest option

recovery:
    - create the dump  -> its a bson file
    - restore the dump file

It has a lot of options you can restore since a point, you can chose to include hte oplog or not in the recovery

- can create backups of:
    - databases
    - collecitons
    - documents retrieved by a query

PROS:
    - simple
    - can baxckup a subset
    - bson is not excesively heavy
CONS:
    - LARGE BASCKUPS are slow
    - can not be used in a sharded cluster

command options:
    --db
    --collection
    --oplog
    --query/filter
    -- <more>

## Mongo restore options

...

# File system level

## Physical  backups

stop accepting writes:

    db.fsyncLock()
    <do the copy>
    db.fsyncUnlock()
