# Perfomance issues / improvements in a real atlas cluster


- Performance advisor

Does not detect any index to drop, neither to improve schemas

however, it proposes to create indexes -> reduce 500 mb or disk reads


In another cluster it recommends to drop 7 indexes


To create indexes, you can filter per date range and that proposal will adapt to the usage.

It will sort the recommendaitons by the impact it will have


- query profiler

he selected a view of last 5 days

it shows the slow queries registered by the profiler (by default > 100 ms)

it has a 11 min query, which is not normal at all


# SHARDING part II

## Review sharding a collection

Ensure the cluster is sharded with ocmmand

sh.status()


# How config metadara caching works

Driver senc operations to mongoS

Mongos has a cached copy of config data which is versioned

Mongos has no storage, it has a cache in RAM with the most used data for that config

Has a versioning system to know when to update it

If the system detect changes, the mongos will update the config. eg the data has changed from one shard to another

you have to know that there is a system to know when to update the cache


# Balancing data

## data and query imbalance

what happends when all incoming writes to only one shard? it is imbalanced, we need to adjust the sharding key

remember the pareto 80/20, 20 % of petitions will contain 80% of data?

20% of shard keys will contain the 80% of the data, if you configure these 20% in one shard, you will have to reconfigure

- you can automatically assign the sahd key, even if it was automated, some shards will abosorb more data


# Automatic balancing in mongodb

- you could set store 1 to 33 to shard A
34 to 66 to shard B 
etc

MAYBE WE NEED TO ADAPT IT

- The balancer (background process) does this task


## key ranges

It is the unit of balancing in mongodb

by default it moves chunks of 128mb

eg. range store 1 to 4 --> will include stores 1, 2 and 3 (last is out)

# how does automatic balancing work?

In the primary node in the config cluster is the balancer running

we it data in shard A increases much more than in THE rest, when it passes a threshold (more or less 3 * 128 mb)

it will trigger a split. it will take a chunk of 128mb of data and it will move it to the next shard+


it just copies data to the next shard

until the copy does not end, mongo will think that the data is in shard 1 (read write)

once the data is copied to the next shard, it will update config and locate the metadata in the next shard --> queries will go to the next shard

Data from original shard will be removed


note: when a collection is entirely removed, the space is free

if the collection is partilly removed, disk is fragmented and is shown as occupied, over time it wil use that space

once the metadata changes, if a new query apears, mongoS will update the cache to send the query to the next shard and not to the original


# Presplitting before bulk loading

it is a technique to  split when we load data in bulk (eg migrate from psql and load the entire db)

we can set the process:

- you have to analyze the data and propose the split (it is NOT AUTOMATIC)
- you tell to which shard upload and mongo does it as you have told

# sharding pitfalls

- balancing is a big workload, moving data takes resources
- it has to first write in shard A and then move it and then remove it, it would be better to have configured a better key 


- first balance takes a while


- it is not a good idea to use a monotonic incremental key because it will happend what we said before and we will need to use the automatic balancing --> we will get bad performance 


- use multi field keys to add variety


# Common sharding challenges

- data may be badly distributed
    - the cluster will automatically move it if possible

- you could configure to avoid it, eg, for geographic reasons

# sharding for parallelism

- unusual case but powerfull
    - bad for OLTP/ normal queries
    - for a small number of analytic queries we may want to use as much CPU's as possible
    - it will work if all data fits on each primary node RAM

- we could have many shards in ONE SERVER: however it is a very specific case



# load bulk faster

- presplit

- reduce write concern

- configure parallelism in the loader and some extra manual configs


# APPENDIX: Downsides of hashed indexes

- normal indexes are b-trees (not b-tree +)

under normal conditions when we need a subset of data, there is a subset that if often readed and a subset that is often written / modified

in normal indexes (not hashed indexes), we will work with fragment of these indexes that we can maintain in RAM

hashed indexes will not allow this because they can not allows similar data to be closed, they sparse the data, separate them randomly and will not allows the read often data to be close together --> hashed indexes are not efficient for this

- HASHED indexes: we have to know that exist but are not commonly used, you have to know that they are not the most efficient, you will use them when normal indexes does not work


# Index misconceptions

- there is a common thought that noSQL uses hashed indexes, that is not true, we use b-trees


# index types

single field

compound indexes

multikey indexes --> uses one array field, only one multikey index per collection? NO! WRONG -> it is if i have 1 index with array field, the other fields in that index can not be arrays, they have to be normal fields
    - but I could have 3 indexes, EACH one with only ONE array field

geospatial indexes

other indexes:
    - text
    - hashed  -> creates a hash with the selected fields, each each entry is a hash of name, surname and city
    - wildcard  -> indexes all fields, each entry contains all fields  -> can be unefficient, it may not fit the RAM if my documents have to many fields. they can be useful when you do not know exactly which fields will be queried

- 4 indexes per collection is a good number, recommended, write performance downgrades with more than 20 indexes

# DEV400 POWERPOINT

we will see:

- array queries
- array updates
- expressive updates  -> use other fields values to query
- upsert operations
- findOneAndUpdate --> has some advantages

# a surprising array query

query = { age: { $gt : 18 , $lt: 30 } }
db.ages.insertOne({ name: "Tom", age: 27 })
db.ages.find(query)

we mix a field with scalar values and an array:


db.ages.insertOne({ name: "Roy family", age: [5, 40] })

the previous query will mach the array and the scalar:

db.ages.find(query)
