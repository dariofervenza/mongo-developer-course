# we are starting the mdb200 today

# Multikey indexes

Until now we only saw simple indexes (one single flied)

- Indexes in fields like arrays


- `createIndex()` is still valid.

But now the index, is created on each element of the array

eg marks: [10, 5, 3]  --> it will create 3 index entries --> one entry per unique value

```sh
find({"lap_times.2": 4 })  --> the array has a 4 in the third position
```

- Element 1 -> index 0

- Element 2 -> index 1

```sh
use test
db.race_results.drop()
db.race_results.createIndex( { "lap_times" : 1 } )
- here there will be an index with the value of 3 that points to [ 3, 5, 2, 8 ] and to [ 6, 3, 3, 8 ] (see data below)
db.race_results.insertMany([ 
{ "lap_times" : [ 3, 5, 2, 8 ] },   
{ "lap_times" : [ 1, 6, 4, 2 ] }, 
{ "lap_times" : [ 6, 3, 3, 8 ] } 
  ])
db.race_results.find( { lap_times : 1 } )
db.race_results.find( { "lap_times.2" : 3 } )
```

- When we see IXScan is because we have used the index (in the explain command)

# indexes in subdocuments

- the 1 in the create index comments : 1 is because it is an ascending index

```sh
db.blog.drop()
db.blog.insertMany([
    {"comments": [{ "name" : "Bob", "rating" : 1 }, 
                    { "name" : "Frank", "rating" : 5.3 }, 
                    { "name" : "Susan", "rating" : 3 } ]},

    {"comments": [{ name : "Megan", "rating" : 1 } ] },

    {"comments": [{ "name" : "Luke", "rating" : 1.4 },
                    { "name" : "Matt", "rating" : 5 }, 
                    { "name" : "Sue", "rating" : 7 } ] }
])
db.blog.createIndex( { "comments" : 1 } )
db.blog.createIndex( { "comments.rating" : 1 } )
db.blog.find( { "comments" : { "name" :"Bob", "rating": 1 }})
db.blog.find( { "comments" : { "rating" : 1 } } )
db.blog.find( { "comments.rating" : 1 } )
```


```sh
db.blog.find( { "comments.rating" : 1 } ).explain()   --> important to know which index is using
```

DELETE INDEX

```sh
db.blog.dropIndex("index_name")
```


nested arrrays:

```sh
db.player.drop()
db.player.createIndex( { "last_moves" : 1 } )
```

- here there will be an index with the element  [ 1, 2 ] that points to [ 1, 2 ], [ 2, 3 ], [ 3, 4] 

```sh
db.player.insertMany([
 { "last_moves" : [ [ 1, 2 ], [ 2, 3 ], [ 3, 4] ] },
 { "last_moves" : [ [ 3, 4 ], [ 4, 5 ] ] },
 { "last_moves" : [ [ 4, 5 ], [ 5, 6 ] ] }, 
 { "last_moves" : [ [ 3, 4 ] ] }, 
 { "last_moves" : [ [ 4, 5 ] ] } 
])
db.player.find( { "last_moves" : [ 3, 4 ] } )   -> any internal element that contains this element [3, 4]
db.player.find( { "last_moves" : 3 } )          -> no match because there is no internal element that is not an array
db.player.find( { "last_moves.1" : [ 4, 5 ] } )   -> one match has this exact array in position index=1
```

explain() -> winningPLan: stage: "COLLSCAN" OR "IXSCAN"

# Nested queries | NESTED ARRAYS

```sh
db.player.find({ "last_moves" : 3 })  -> no result

db.player.find({ "last_moves" : { 
    $elemMatch : { $elemMatch : {$eq : 3} }    -> first elem match targets first outer array, second the inner array elements
   	   }
})
```

- this is how you find a value inside the inner array

# How is the index?

In "last_moves" we have an index, but this index points to arrays therefore,
the previous query is not covered by the index  -> it has to do a collScan

# COMPOUND INDEXES


Indexes that are set in more than one field


createIndex({field1: 1, field2: -1, field3: 1}) --> ACS in field 1 and field3 / DESC in field2

USAGE

find({country: "UK", city: "Glasgow"})  --> ideally we need an index with both fields


If not available, we need an index with the first field to be "country" or "city"

It will work an index with country, city and other fields (but the most efficient is the one that only has these 2 fields)


Valid indexes:

 {city: 1 , others...}
 {country: 1 , others...}
 {city: 1 , country: 1}
 {city: 1 , country: 1, others...}


Invalid:
 {other: 1, other2: 1, city: 1}
 {other: 1, city: 1}
 {other: 1, city: 1, country: 1}

If we search by country or by city ideally we need city or country in the first position of the index

This is because the index is a btree

If the index is "state, country, city" and I search by city, we have to scan all the tree until we reach city, so it is not useful

# Field order matters

- ESR rule
    - E: equality first  -> if we search by field: value is the fastest
        - If the field is male / female --> searching by male returns half the collection, hence it is not selective
        - Therefore try to search a value that has a low number of entries
    - S: sort then  -> it is more computational intensive (but less than range)
    - R: range the slowest --> search between >= 10 and <= 50  --> the slowest


# EXAMPLE : A SIMPLE MESSAGE BOARD: how the query changes with different indexes

- search by timestamp 

```sh
msgs = [ 
{ "timestamp": 1, "username": "anonymous", "rating": 3}, 
{ "timestamp": 2, "username": "anonymous", "rating": 5}, 
{ "timestamp": 3, "username": "sam", "rating": 2 }, 
{ "timestamp": 4, "username": "anonymous", "rating": 2}, 
{ "timestamp": 5, "username": "martha", "rating" : 5 } 
]
db.messages.drop()
db.messages.insertMany(msgs)
db.messages.createIndex({ timestamp : 1 })
```

- that would be an optimized query

in the explain we would like to see

scanned documents: 2
returned documents: 2


if we see

scanned documents: 500
returned documents: 2  

that would not be the most efficient

```sh
db.col.find({timestamp: {$gt: 5, $lt: 10}, rating: 3})
```

# Example of unoptimized

```sh
db.messages.find(
    {timestamp:{$gte : 2, $lte : 4 }, username: "anonymous" }
).explain("executionStats")

db.messages.dropIndex("timestamp_1")

db.messages.createIndex( { timestamp: 1, username: 1 })   -> this index does NOT OPTIMIZE next query

db.messages.find({timestamp:{$gte : 2, $lte : 4 }, username: "anonymous" }).explain("executionStats")
```

## why is not optimized?

because we are are searching username=1 and a range of timestamp (equality in username and range in timestamp)

THERefore, the best index (by equality first rule) is the one that has username as first field

best index is {username:1 , timestamp: 1} by EQUALITY FIRST

HENCE WHEN WE HAVE A FIND THAT HAS FIELD=VALUE, THAT FIELD HAS TO BE FIRST IN THE INDEX

# iNDEXING for sort

in explain we can see "executionstages: stage: SORT" --> THIS IS because it had to get the documents and sort them


Example of scan

stage1:
    IXSCAN

    stage2:
        FETCH  --> READ documents

        stage2:
            SORT  -> IT had to sort

It is not as bad as a COLLSCAN but it could be better, in this case we will see that it scanned more than returned documents


This can happen if my index is:

username: 1 , timestamp: 1 , rating: 1

- Query is: range timestamp, username: "anonymous" and sort by stage
    - even if i have my three fields indexed, it has to sort

REMEMBER: EQUALITY, SORT, RANGE
    tHE FIRST ELEMENT IN THE INDEX HAS TO BE THE ONE THAT IS SEARCHED AS field: value
    then the second element has to be the one that you use to sort
    the last one has to be the one you search by range

example:

query-> 
    field1: value,
    field2: value,
    field3: range
    and sort by field4

the ideal index is->
    field1: 1,
    field2: 1,
    field4: 1,
    field3: 1
    - HENCE EVEN IF I DO NOT SEARCH BY FIELD4 is is more important than field3 to be before in the index
    - this because when we use that index we got the data already ordered and we do not need to do the sort operation


- query with equiality, sort and range:

```sh
db.messages.find( 
   {timestamp: {$gte:2, $lte:4}, username:"anonymous"} 
).sort({rating:1}).explain("executionStats")
```

Idealy, in explain() wee will see IXSCAN, fetch and NOT a SORT stage

IXSCAN + FETCH is better than IXSCAN + FETCH + SORT

aLSO we would like to read as many documents as we return

# Order of compound indexes

query is find().sort({name:1, surname: -1})

1. index is {year: 1, name: 1, surname: -1}  --> year is first so this index does not help

2. index is {name:1, year:1, surname: -1}  -> it helps but is not ideal, we will need to sort by surname

EXAM: something like this will be asked
3. index is  {name: -1, surnamme: 1}  ->  this is the inverse search we want 1, -1 and we got -1, 1 in the index, this will work because it is the same but reversed, we only have to read it in reverse order, it is the second best index we can get
    - If we had a third element in the query that is not in the inverse order as we want to get, it breaks it and we would have to sort
    - example
        query is name: 1, surname: -1, year: 1
        index is name: -1, surname: 1, year: 1   -> this is not the exact inverse, it has to sort by yeart
        index is name: -1, surname: 1, year: -1   -> this indeed the inverse

Example:

index is a:1, b:1
my queries are ->
    a:value, b: value --> the index willl work
    b: value    -------- the index will not work because b is not in the first position --> create an index with only b or an index with b and a

# Compound index size

- Compound indexes can grow very large!
    - tHERE WILL be one entry in the index per each combination of values

- The indexes depend on the queries you have, hence if the queries change, the indexes may need to be changed

- PREFIX COMPRESSION
    - two or more entries that have the same value in the first position only generate one entry in the index
      eg. index in {field1: 1} all the values that are the same only generate one entry in the index (they are trees). this applies only in the first field of the index

- try to reduce cardinality (remember the male, female case, requesting male returns half the entries in the index)

# Multikey compound indexes

Indexes with many fields that are: array + fields

- We CANNOT create an index with 2 array fields --> only 1 array + simple fields
- That is because it would explode in entries (remember that we generate an entry in the index with each combination of values)

# Index covered queries

Best possible case: get the data directly from the index, do not fetch the documents

It woudl be always a projection that removes the index and shows only the indexed fields


explain()
    PROJECTION_COVERED    -> SECOND OPERATION
        IDXSCAN            ->> FIRST OPERATION


THIS is the fastest query possible ( does not have a FETCH)

# exercise:

Copio el ejercicio:

## we separately define the different parts of the find

### we use the example db `sample_airbnb`

```sh
query = { amenities: "Waterfront",

  "bed_type" : { $in : [ "Futon", "Real Bed" ] },

  first_review : { $lt: ISODate("2018-12-31") },

  last_review : { $gt : ISODate("2019-02-28") } 
  }

project = { bedrooms:1 , price: 1, _id:0, "address.country":1}

order = {bedrooms:-1,price:1}
```

```sh
use sample_airbnb

db.listingsAndReviews.find(query,project).sort(order)
```
 
Best index for this query?


Solution:


- It is not exagerated to create a 6 field index (it is not uncommon in production)
- However, in some cases it could explode --> you have to analyze each case

It could be:
{amenities: 1, bed_type: 1, bedrooms:-1,price:1, first_review: 1, last_review: 1}


This case is complicated because of the $in

You could think that it is an equality, hovewer it is a middle point between equiality and range

Hnece, dependiong on the data it could be equality or not

$in: [few values]  -> more like equality

$in: [many values]  -> range


The solution that mongo proposes is:
{amenities: 1, bedrooms: -1, price: 1, bed_type:1, first_review:1, last_review: 1}

so equality -> sort -> $in -> range


# Time to live (TTL) Indexes

Mongo has a background 

Is an index we you say that the data indexed will be auto removed from the db

```sh
createIndex({colname: 1}, {expireAfterSeconds:600})
```

# Index usage tips

- They will add wrokload to write operations
- Even worse in multikey
- ideally they have to fit the cache of the server
- use $indexStats() aggregation to know how much an index is used

- {a: 1} is redundant is we have {a:1, b:1} (second already covers the fisrt)

# In production: Hidden index

check it yourself ( i may have lost more content, check the powerpoint )

- never create a ttl hidden index

# Native text indexes

- Tokenizes the words (like an sparse arrray)
- does OR searches by default

- it is better atlas search

ALgorithm: 
    - removed words like the a an and
    - apply language specific sufix 

Limits:
    - the search has to be tuned, it is not intelligent as atlas search
