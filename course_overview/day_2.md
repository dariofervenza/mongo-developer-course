# default db

we have always local and admin dbs

```sh
db.employees.find({})
```

- You can create variables and send them later

```sh
var employee = {"name": "manolo"}
db.employees.find(employee)

use sample_mflix
show collections
db.comments.find({})
```

- You can use the help command

```sh
help
```

- db command help


```sh
db.help
```

- VS COde extensions

see the presentation


- Compass

Agregation builder -> you can see partial results and check if go are creating the correct query

It is useful when we will create indexes and check if they are optimized

# Functions that are not present in mongo db core

- Stored procedures

- Triggers

# correct statements about mongo

Data stored in bson in disk
it creates primary jey id even if not present in the data
data distributed over a cluster when sharding

## incorrect

- data is homomgeneous in a collection (it is not, it has a flexibel schema)
- queries are made using bson syntax (no, we use json with find({...}))

# correct mongo functions

- SQL is not native, however there are connectors for compatibility
- there are no foreign keys
- there are no joins, there is a similar mechanism (lookup) but it not a join

- we can enforce data types (optional)
- we can enforce schema (optional)

# Components in MQL (mongo query language)

- atlas search
- atlas vector search
- atlas cloud database
- altlas mongodb charts (dashboards like grafana in atlas gui)
- atlas data federation

# how to describe mongodb atlas

- managed database service on the cloud

- it is not a cloud provider to deploy clusters because you choose one provider (aws, azure) but it is not itself 

# Laboratorio Instruqt general para módulos MDB100 - 200 y 300 y DEV400

https://play.instruqt.com/mongodb-ps/invite/x97tdl0fwuuy

# Remember to load sample data in Atlas

(sample training)

# Count documents: Its the most efficient

- With `find().count()` we can do it but its slower

db.comments.countDocuments()

# CRUD

- Create

```sh
insertOne()
insertMany([])
``

- Read

```sh
findOne(query, projection)  -> return the first it finds
find(query, projection)
```

- Update

```sh
updateOne(query, change)  -> updates the first match
undateMany(query, change)
```

- Delete

```sh
deleteOne(query) -> deletes the first match
deleteMany(query)
```

EXAM: the can put removeOne() --> you have to know that it is wrong

```sh
var myDocument = {
    name: "manolo",
    birth: new Date("Jan 03, 2023")
}

db.test.insertOne(myDocument)
```

# LIMITS: Max 16 MB per document

- It is relaxed JSON, var names do nort need quotes ""

```sh
var otherDoc = {
    name: "paco",
    nested: {
        thing: "data"
    }
}
```

- Fields with be recovered in the same order as inserted

eg.

```sh
{
    name: "manolo",
    thing: "data"
}
```

and not:

```sh
{
    thing: "data"
    name: "manolo",
    
}
```

- Hence its a bad idea continously append data into a document, 16mb in a document is crazy though

# insertOne()

- id has to be unique within the collection

```sh
db.test.insertOne({_id: 0, name: 1})
db.test.insertOne({_id: 0, name: 2}) -> error duplicated id
db.test.find({_id: 0})
```

- If you do not provide the _id after inserting it returns the _id (it always returns the insertedId)

```sh
{
  acknowledged: true,
  insertedId: ObjectId('69b2eb1eb18c3a04788563b2')
}

{
    acknowledged: true,
    insertedId: 0
}
```

# Orderedd inserts and unordered inserts

```sh
db.test1.insertMany([
    {_id: 0, name: 0},
    {_id: 1, name: 1},
])

{ acknowledged: true, insertedIds: { '0': 0, '1': 1 } }

db.test1.insertMany([
    {_id: "manolo", name: 0},
    {_id: "jesus", name: 1},
])

{ acknowledged: true, insertedIds: { '0': 'manolo', '1': 'jesus' } }

db.test1.insertMany([
    {_id: "repeated", name: 0},
    {_id: "repeated", name: 1},
])
```

BulkWriteResult {
  insertedCount: 1,
  matchedCount: 0,
  modifiedCount: 0,
  deletedCount: 0,
  upsertedCount: 0,
  upsertedIds: {},
  insertedIds: { '0': 'repeated' }
}
Write Errors: [
  WriteError {
    err: {
      index: 1,
      code: 11000,
      errmsg: 'E11000 duplicate key error collection: sample_mflix.test1 index: _id_ dup key: { _id: "repeated" }',
      errInfo: undefined,
      op: { _id: 'repeated', name: 1 }
    }
  }
]

- It stops inserting in the error and does not continue with the rest

- This is because by default it is an Ordered insert

- UNORDERED: does not stop in the first error

```sh
db.test3.insertMany(
    [
        {_id: "repeated1", name: 0},
        {_id: "repeated1", name: 1},
        {_id: "non_repeated1", name: -1},
        
    ],
    {ordered: false}
)

db.test3.find()  -> inserted 2
```

- We could use ordered: false to send each document to the corresponding shard

# findOne()

```sh
db.test3.find()
db.test3.find({})
```

- Both are correct

```sh
db.test3.findOne()
db.test3.findOne({})

db.test3.findOne({name: -1}) -> returns 1 doc
db.test3.findOne({name: "-1"})  -> returns null because the match is an integer
```

- It the collection is big, the find({}) (no parameters) returns the first page (it paginates the collection)

- Common find queries has to use an index ideally

## If the find has to fields it applies AND operastor

```sh
db.test3.find({ _id: 'non_repeated1', name: -1 })
db.test3.find({ _id: 'non_repeated1', name: -5 }) --> nothign returned
```

## You could use regex but it is not optimal regarding to the performance (you have to use concrete regex expressions, that limit the results)+

Also, it is case sensitive and sensitive to the dtypes

# Regex in queries

$regex operator

```sh
db.test.find(
    {
        city: {$regex: /LA/i}
    }
)
```

If you write

/something/i  -> it understand without the "" that it is a regex

the / is a shortcut for regex


# Projection: choose fields to return

By default returns the entire document in the original order, we change it with projections

```sh
db.test3.findOne({name: 0}, {city: 1})
```

{city: 1} --> show field city only ..> will show "city" and "_id"

```sh
db.test3.findOne({name: 0}, {city: 0}) 
```

do not show city field

db.test3.findOne({name: 0}, {city: 0, other_field: 1})  --> INCORRECT, you can only specify the fields to see or not to see but no combinations

```sh
db.test4.insertOne({
    name: "paco",
    data: "something",
    number: 3
})

db.test4.find({}, {data:0})

db.test4.find({}, {data:1})

db.test4.find({}, {data:0, _id:0})

db.test4.find({}, {data:0, _id:0, wrong_field: 0})  -> no error

db.test4.find({}, {wrong_field: 1}) --> only returns _id because there are no matching fields
```

- find converts 30.0 to 30 if the field is integer so no error would be produced

# cursor

- if there are too many matches in a find() it returns a cursor, it does return 20 documents, add:

find().toArray()  -> all elements

next element in the cursor

use -> it

```sh
db.comments.find()
it
it
```

```sh
db.comments.find({}, {name:1}).toArray()  -> dangerous if there are too many documents
```

## use cursor object

```sh
var cursor = db.comments.find()
cursor.next()                    only next document-> 
```

### last element of the cursor will have _id: 0

by default it returns 101 documents with a limit of 16mb

# for

```sh
for(let x=0;x<200;x++) {
    db.test5.insertOne({random:0})
}

db.test5.find()
```

## insert the variable of the for loop

```sh
for(let x=0;x<200;x++) {
    db.test6.insertOne({random:x})
}

db.test6.find()


var cursor = db.test6.find()  -> it does not execute the find, its lazy execution

cursor.forEach(doc => {
    printjson(doc)
    })

cursor.forEach(doc => printjson(doc))   -> also valid without {} because its only one instruction

for(let x=0;x<20;x++) {let cursor = db.test.find()}
```

# sort

ASCENDING: use 1
DESCENDING: use -1

```sh
db.test.find().sort({name: 1, id_: -1})
db.test.find().sort({name: -1, id_: -1})
```

# limit

```sh
db.comments.find().limit(5)
db.comments.find().sort({date: 1}).limit(5)
```

# skip

```sh
db.comments.find().skip(20).limit(5)
```

- Note: skip adds workload to the server, its not free, it the collection is to big using skip to iterate its not ok

# while

while()

# array of randoms

```sh
let rnd = (x)=>Math.floor(Math.random()*x)
```

- rnd is function that is why each time it returns a different value

```sh
for(let x=0;x<20;x++) {db.test6.insertOne({ride: rnd(1)})}

db.test6.find()
```

# ISODate("2024-11-04")

```sh
db.test.insertOne({date: ISODate("2024-11-04")})

db.test.find({date: ISODate("2024-11-04")})
db.test.find({date: ISODate("2024-11-02")})
```

# less than, greater than ( or equal)

```sh
db.test.insertMany([
    {number: 20},
    {number: 21},
    {number: 22},
    {number: 23},
    {number: 300},
])

db.test.find({number: {$lt: 22}})
db.test.find({number: {$lte: 22}})
db.test.find({number: {$lte: 22, $gt: 20}}, {_id: 0}).sort({number: -1}).toArray()
db.test.find({number: {$eq: 22}})
```

### or condition

```sh
db.test.find({
  $or: [
    { number: 21 },
    { number: 22 }
  ]
}, { _id: 0 })
.sort({ number: -1 })
.toArray();
```

# insertmany
can be faster than insertone because (
    the system can parallelize (eg, write to many shards),
    perform the write batched (be aware of ordered vs unordered writes),
    reduces network time because there are less calls
    )

# OPERATORS

$ne -> not equal
$eq -> equal
$gt -> greater than

```sh
$or: [
    {number: 3, color: "white"},
    {number: 5, color: "black"},
]

find({species: {$not: {$le: 2}}})
```

$le: "cat"  -> by the order or letters "bat" would be a match


# count

find({...}).count()

# In operator

```sh
find(
    {result: {
        $in: ["Pass", "Fail"]
        }
    }
)
```

Equivalent to -> $or: [{result: "Pass"}, {"result": "Fail"}]


# query nested docs

```sh
db.test.insertOne({
    data: 1,
    nested: {
        date: 6
    }
})

db.test.find({"nested.date": 6})
```

- without quotes it will think we are sending a js object (IMPORTANT)
db.test.find({nested.date: 6})  -> error nested var does not exist

it is equivalente to:

```sh
db.test.find({"nested": {"date": 6}})

db.test.insertOne({
    data: 1,
    nested: {
        date: 6
    },
    list: [2, 3]
})
db.test.insertOne({
    data: 1,
    nested: {
        date: 6
    },
    list: [5, 3]
})

db.test.insertOne({
    data: 1,
    nested: {
        date: 6
    },
    list: [5, 1, 9]
})

db.test.find({"list": [2, 3]})    -> the list have to have the same order


db.test.find({"list": 2})  --> BE AWARE, it will work because it tries to find inside the list and it matches

db.test.find({$or: [{"list": 2}, {"list": 5}]}) 
```

# $all

```sh
db.test.find({"list": {$all: [3, 5]}})   -> the array has to contain all these elements
```

# $size

```sh
db.test.find({"list": {$size: 3}})  -> fetch arrays of this size
```

# AVOID the or -> $elemMatch

# ElemmMatch (important!!)

```sh
db.testel.insertMany([
    {_id: "player1", results: [{game: "pacman", score: 10}, {game: "pong", "score": 5}]},
    {_id: "player2", results: [{game: "pacman", score: 5}, {game: "pong", "score": 7}]},
])

db.testel.find({
    results: {$elemMatch: {game: "pacman", "score": 5}}
})
``

- finds 1 element

```sh
db.testel.find({
    "results.game": "pacman", "results.score": 5
})
```

- finds 2 elements

# without elem match matches first element in array with second

# with elem match the same element in results array has to satisfy both

element match has to satisfy all condition in one concrete array element

# Expressive queries
- Use internal values of the documents to compose dynamic queries

use sample_mflix

- tomatoes.viewer.rating is greater than the value in imdb.rating
- when gt has more than one value it compares 2 values

```sh
db.movies.find({ 
   $expr: { $gt: [ "$tomatoes.viewer.rating" ,"$imdb.rating" ] } 
})
```

- documents with scores.score  has average less than 50 (scores is an array)

```sh
db.grades.find({ 
    $expr: { $lt: [ 
        { $avg: "$scores.score" },
        50
    ]}
})
```sh
