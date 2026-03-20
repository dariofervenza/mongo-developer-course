# Perfomance issues / improvements in a real atlas cluster


## Performance advisor

Does not detect any index to drop, neither to improve schemas

however, it proposes to create indexes -> reduce 500 mb or disk reads


In another cluster it recommends to drop 7 indexes


To create indexes, you can filter per date range and that proposal will adapt to the usage.

It will sort the recommendaitons by the impact it will have


## Query profiler

he selected a view of last 5 days

it shows the slow queries registered by the profiler (by default > 100 ms)

it has a 11 min query, which is not normal at all


# SHARDING part II

## Review sharding a collection

Ensure the cluster is sharded with ocmmand

```sh
sh.status()
```

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

In general we will practice advanced queries

# A surprising array query

```sh
query = { age: { $gt : 18 , $lt: 30 } }
db.ages.insertOne({ name: "Tom", age: 27 })
db.ages.find(query)
```

- Now, we mix a field with scalar values and an array in different documents for the same field:

```sh
db.ages.insertOne({ name: "Roy family", age: [5, 40] })
```

- The previous query will mach the array and the scalar:

```sh
db.ages.find(query)
```

# APPEND TO ARRAY (PUSH)

```sh
db.playlists.insertOne(
{name: "funky",
 tracks : [
  { artist : "Queen", track : "Bicycle Race" },
  { artist : "Abba",  track : "Waterloo" },
 ]})

db.playlists.updateOne({name:"funky"},
{ $push : { tracks : { artist: "AC/DC", track: "Thunderstruck" } }})

db.playlists.find({})
```

# POP AN ELEMENT: it will remove the last element with 1

```sh
db.playlists.find({},{_id:0})
```

## pop last element

```sh
db.playlists.updateOne({name:"funky"},
{ $pop: {tracks: 1}})

db.playlists.find({},{_id:0})
```

## pop first element in the array


```sh
db.playlists.updateOne({name: "funky"},
{ $pop: {tracks: -1}})

db.playlists.find({},{_id:0})
```

# PULL: REMOVE THE ELEMENTS IN THE ARRAY THAT MATCH THE VALUE

```sh
db.playlists.drop()

db.playlists.insertOne(
{name: "funky",
 tracks : [
  { artist:"Queen", track:"Bicycle Race"},
  { artist:"Abba",  track:"Waterloo"},
  { artist:"Queen", track:"Under Pressure"},
  { artist:"AC/DC", track:"Thunderstruck"},
 ]})

db.playlists.updateOne({name:"funky"},
{ $pull : { tracks : { artist: "Queen" }}}) 

db.playlists.find({},{_id:0}).pretty()
```

# $addToSet

- only adds (pushes) it the element is new

```sh
db.fave_bands.insertOne({genre: "funky", bands: ["Abba", "AC/DC", "Queen"]})

db.fave_bands.updateOne({genre: "funky"}, {$addToSet: {bands: "Pink Floyd"}})

db.fave_bands.findOne({genre: "funky"})

db.fave_bands.updateOne({genre: "funky"}, {$addToSet: {bands: "Queen"}})

db.fave_bands.find()
```

# push and array

```sh
db.a.drop()
db.a.insertOne({ "name" : "Tom", "hrs" : [ 4, 1, 3 ] })
db.a.updateOne({name:"Tom"}, {$push:{hrs:[2,9]}})
db.a.find({},{_id:0})
```

**adds the array as element, does not concatenate**

# Solution push each

```sh
db.a.drop()
db.a.insertOne({ "name" : "Tom", "hrs" : [ 4, 1, 3 ] })
db.a.updateOne({name:"Tom"}, {$push:{hrs:{ $each : [2,9]}}})
db.a.find({},{_id:0})
```

# push each and sort

Apart to concatenate the pushed array, will sort the entire array, including old elements

```sh
db.a.drop()
db.a.insertOne({ "name" : "Tom", "hrs" : [ 4, 1, 3 ] })
db.a.updateOne({name:"Tom"}, {$push:{hrs: {$each: [2,9], $sort: -1}}})
db.a.find({},{_id:0})
```


# push each sort and slice

- We push each 2 elements, sort descending and keep only the first 4 values

```sh
db.a.drop()
db.a.insertOne({ "name" : "Tom", "hrs" : [ 4, 1, 3 ] })
db.a.updateOne({name: "Tom"}, {$push: {hrs: {$each : [2,9], $sort: -1, $slice: 4}}})
db.a.find({},{_id:0})
```

# increment += an array element

The fourth element goes from 0 to 1
 
```sh
db.a.drop()
db.a.insertOne({ name: "Tom", hrs: [ 0, 0, 1, 0, 0 ] })
db.a.find({},{_id:0})
db.a.updateOne({name: "Tom"}, { $inc: { "hrs.3": 1 }})
db.a.find({},{_id:0})
```

Only increment the first element (with "field.$") that is less than one

```sh
db.a.drop()
db.a.insertOne({ name: "Tom", hrs: [ 0, 0, 1, 0, 0 ] })
db.a.updateOne({name:"Tom",hrs:{$lt:1}},{ $inc: { "hrs.$": 2 }})
db.a.find({},{_id:0})
```

# arrayFilters

The $[new_name] get the hrs less than one in a new variable that has to have the same name in the arrayFilters field

The thing is that the `{name:"Tom",hrs:{$lt:1}}` get you the documents to update and
from these documents, update the values that are less that on, without the array filters it would update all the values
in the array

```sh
db.a.drop()
db.a.insertOne({ name: "Tom", hrs: [ 0, 0, 1, 0, 0 ] })
db.a.updateOne({name:"Tom",hrs:{$lt:1}}, {$inc : { "hrs.$[nohrs]" : 2 }}, {"arrayFilters": [{"nohrs":{"$lt":1}}]})
db.a.find({},{_id:0})
```

# upsert: create a field or update it

```sh
db.players.drop()
```

- this will not do anything because there is no match

```sh
db.players.updateOne({name:"joe"},{$inc:{games:1}})
db.players.find()
```

- if found it will update, if there is no games field it will add if
- if there is no document match it creates one with name: joe and games:1

```sh
db.players.updateOne({name:"joe"},{$inc:{games:1}},{upsert:true})
db.players.find()
```

- here it does exist so goes from 1 to 2

```sh
db.players.updateOne({name:"joe"},{$inc:{games:1}},{upsert:true})
db.players.find()
```

# store one field value in a var and use that to filter documents

```sh
db.rooms.drop()
db.rooms.insertOne({room: '303', reserved: false})
db.rooms.findOne({reserved: false})

room = db.rooms.findOne({reserved: false}).room
db.rooms.updateOne({room: room}, {$set: {reserved: true}})
db.rooms.find()
print("You have reserved room "+room)

room = db.rooms.findOne({reserved: false}).room
db.rooms.updateOne({room: room}, {$set: {reserved: true}})
print("You have reserved room "+room)
```

# compound operations

they are safe to use with concurrency and parallelism, return the document before updating

- it ensures atomicity

## findOneAndUpdate: returns the document BEFORE modifying

find, modifies, and returns the match BEFORE MODIFYING so we can capture one field value in a var

```sh
db.rooms.drop()
db.rooms.insertOne({room: '909', reserved: false})
db.rooms.findOne({reserved: false})

room = db.rooms.findOneAndUpdate({ reserved: false },  { $set: { reserved: "true" } })
print("You have reserved room that was " + room.reserved)
```

- now it is reserved:true

```sh
db.rooms.findOne()

room_no = room.room
print("You have reserved room "+room)

now it does not match and triggers an error

room = db.rooms.findOneAndUpdate({ reserved: false },  { $set: { reserved: "true" } }).room
```

## findOneAndReplace()

```sh
db.maintenance.drop()
db.maintenance.insertMany([
  { id: 101, status: "broken", tech: "none" },
  { id: 102, status: "broken", tech: "none" }
])

// Finds a broken machine and replaces the whole record with a 'fixed' template
old_job = db.maintenance.findOneAndReplace(
  { status: "broken" }, 
  { id: 101, status: "operational", last_inspected: new Date() }
)

print("Started repair on ID: " + old_job.id) // Returns 101
print("Old status was: " + old_job.status)   // Returns "broken"

// Verification: The document is now completely different
db.maintenance.find({id: 101}, {_id:0}) 
// Result: { "id": 101, "status": "operational", "last_inspected": ... } (tech field is GONE)
```

## findOneAndDelete()

```sh
db.queue.drop()
db.queue.insertMany([
  { task: "email_welcome", priority: "high" },
  { task: "process_payment", priority: "urgent" }
])

// Pulls the most urgent task off the list and deletes it so no one else grabs it
next_task = db.queue.findOneAndDelete({ priority: "urgent" })

print("Processing deleted task: " + next_task.task)

// Verification: Only the welcome email remains
db.queue.find({}, {_id:0})
// Result: { "task": "email_welcome", "priority": "high" }
```

## returnNewDocument: True

returns after modifying

```sh
db.scores.drop()
db.scores.insertMany([
  { name: "Player1", points: 10 },
  { name: "Player2", points: 50 }
])

// We want to see the score AFTER the boost
updated_player = db.scores.findOneAndUpdate(
  { name: "Player1" },
  { $inc: { points: 5 } },
  { returnDocument: 'after' } // This is the magic switch
)

print("Player1 now has: " + updated_player.points) 
// Result: "Player1 now has: 15" (If this was default, it would have printed 10)

db.scores.find({name: "Player1"}, {_id:0})
```

# EXAM examples

queries that return a document containign the field {scores: [1, 2, 3]}?

1. find({scores: 3})  --> will work but will return more

2. find({scores: [3, 2, 1]})  -> WILL NOT work

3. find({scores: {$all: [1, 7]}})  --> the array will have to have 1 and 7, it could match [1, 1, 7] --> WILL NOT work

4. find({scores: {$in: [1, 3, 7]}})   -> all least one element of the array -_> will NOT work

this will work because it checks the sum of elements = 6, but can get more documents

5. THIS QUERY:

```sh
find({
    $expr: {
        $eq: [{$sum: "$scores"}, 6]
    }
})
```

So solution is 1., 4. and 5.

## why is findOneAndUpdate() better that find() and update()

- because prevents other clients to modify and having a different result when the updates launches
- because it reduces network traffic

## what does this do in an empty colection?

Queries are:

```sh
updateOne({_id: 700}, {
    $push: {sensor: {$each: [4,0,2], $sort: -1}}},
    {upsert: true}
)
updateOne({_id:700 }, { $push: { sensor: { $each: [0, 7, 3, 4, 5], $slice: 5}}})
```

Question is: `Select the number of array elements stored in the sensor array field:`

the first adds an element with the array [4,2,0]
the seconds adds if elements and only maintains in the document the first 5, hence: [4, 2, 0, 0, 7]

the result will be {_id: 700, sensor: [4, 2, 0, 0, 7]}

# COMPOUND OPERATIONS

## AGREGGATION

there stages:

- match
- project
- some stages are blocking like $group, have to get the documents before applying them

## basic aggregation stages

- $match
- $project
- $sort   -> this is blocking, until we got the documents we can not sort
- $limit
- $skip --> filter out the first n documents like in find().skip(3)
- $count

```sh
db.twitter.drop();
db.twitter.insertMany([
  { user: { name: "Alice", followers_count: 500 } },      // Regular user
  { user: { name: "Bob", followers_count: 150000 } },    // High-end non-celeb (The Winner)
  { user: { name: "Charlie", followers_count: 800000 } }, // Celeb (Filtered out)
  { user: { name: "Dave", followers_count: 100 } }       // Regular user
]);
```

It does:
    FILTER elements with no_celebs
    add a projection with name_only
    sorts the matches with most_popular
    limits to one result with first_in_list

```sh
no_celebs = {$match:{"user.followers_count":{$lt:200000}}}
name_only = {$project:{"user.name":1, "user.followers_count":1,_id:0}}
most_popular = {$sort: {"user.followers_count":-1}}
first_in_list = {$limit:1}
pipeline = [no_celebs,name_only,most_popular,first_in_list]
db.twitter.aggregate(pipeline)
```


## Dollar Overloading

```sh
    {$match: {a: 5}} - Dollar on left means a stage name - in this case a $match stage
    {$set: {b: "$a"}} - Dollar on right of colon "$a" refers to the value of field a
    {$set: {area: {$multiply: [5,10]}} - $multiply is an expression name left of colon
    {$set: {
        priceswithtax: {$map: {input: "$prices",
            as: "p",
            in: {
                $multiply :["$$p",1.08]
                }
            }
        }}
    }

    $$p -> temporary loop variable "p" declared in $map
    {$set: {displayprice: {$literal: "$12"}}} - Use $literal when you want either a
    string with a $ or to $project an explicit number
```

## Aggregation Expressions










## Arithmetic Expression Operators










## String Expression Operators











## Expression Operator Categories

|               Category            |        Explanation    |
|-----------------------------------|-----------------------|
| Arithmetic Expression Operators  |Perform calculations on numbers (e.g., $add, $subtract, $multiply, $divide, $mod).|
| Array Expression Operators  | Manipulate or extract data from arrays (e.g., $arrayElemAt, $filter, $map, $push, $size, $slice).  |
| Boolean Expression Operators |    Evaluate values based on "true/false" logic (e.g., $and, $or, $not). | 
| Comparison Expression Operators |  Return a boolean based on the relationship between two values (e.g., $eq, $gt, $lt, $ne).   | 
| Conditional Expression Operators | Use logic to return different values based on conditions (e.g., $cond for if/then/else and $ifNull). | 
| Date Expression Operators |  Extract parts of a Date object or convert time (e.g., $dayOfMonth, $year, $dateToString, $dateDiff). | 
| Literal Expression Operator |  Returns a value without interpreting it; useful for preventing MongoDB from parsing strings as field paths (e.g., $literal). | 
| Object Expression Operators |  Handle or create document structures/objects (e.g., $mergeObjects, $objectToArray, $setField). | 
| Set Expression Operators | Compare two or more arrays as mathematical sets (e.g., $setEquals, $setIntersection, $setUnion). | 
| String Expression Operators |Perform operations on text (e.g., $concat, $split, $toUpper, $toLower, $substrCP).| 
| Text Expression Operator | Used in $match stages with text indexes to calculate search relevance (e.g., $meta: "textScore"). | 
| Trigonometry Expression Operators |Perform math on geometric/angular values (e.g., $sin, $cos, $tan, $asin, $degreesToRadians) | 
| Type Expression Operators | Check or convert the BSON data type of a value (e.g., $type, $convert, $toInt, $toString). | 
| Accumulators ($group) | Calculate values across multiple documents within a $group stage (e.g., $sum, $avg, $min, $max, $count). | 

</br>

# FUNCTIONS

Returns a filter dinamycally created

1. empty and add data:

```sh
db.people.drop()

const today = new Date();
const fourMonthsAgo = new Date(today.getTime() - (120 * 24 * 60 * 60 * 1000));
const sevenMonthsAgo = new Date(today.getTime() - (210 * 24 * 60 * 60 * 1000)); // > 180 days

db.people.insertMany([
  { name: "Recent User", create_date: today },
  { name: "Semi-Recent User", create_date: fourMonthsAgo },
  { name: "Old User", create_date: sevenMonthsAgo } // This one matches!
]);

```

2. dynamic filter:


```sh
function recs_older_than(days) {
  days_in_millis = days*24*60*60*1000
  today = new Date()
  n_days_ago =  new Date(today - days_in_millis)
  return  { create_date: { "$lte" : n_days_ago}}
}
pipe = [{$match : recs_older_than(180)}]
db.people.aggregate(pipe)
```
