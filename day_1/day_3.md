# UPDATE DOCUMENTS

- updateOne(query, change)
- updateMany(query, change)

We will use $set

db.players.insertMany([
 { _id: "mary", points: 150, wins: 25, highscore: 60 },
 { _id: "tom", points: 95, wins: 18, highscore: 110 }])

db.players.updateOne(
    {_id:"mary"},
    {$set : { points :160, wins: 26}}
    )

db.players.find({_id:"mary"})

- set a field that does not exist hence it CREATES it

db.players.updateMany(
    { points : {$lt:200} },
    { $set: {level:"beginner"} }
)
db.players.find()

# update unset

db.bands.insertOne(
    { _id: "genesis2", Singer: "Peter", Drums: "Phil", Keyboard:"Tony", Guitar:"Mike", comp: {data: 1}}
    )
db.bands.findOne()

- removes one field

db.bands.updateOne(
    { _id :"genesis2" }, 
    { $unset: { "Singer": "" } }
)
db.bands.findOne()


- update subelement (nested json)
- update one updates the first match if you want to update al matches use many

db.bands.updateOne(
    { _id :"genesis2" }, 
    { $set: { "comp.data": "2" } }
)
db.bands.find()


# multiply instead of $set, we can use other operators

db.employees.insertOne({name: "Carol", salary: 10000, bonus: 500})

db.employees.updateMany({},{$mul : {salary: 1.1}})

db.employees.find({},{_id:0}) -> salary is 20000 now

# increment value

db.employees.updateOne({name:"Carol"}, {$inc:{bonus:1000}})


# max and min

- max only updates if its superior that that value

db.gamescores.insertOne({name: "pacman", highscore: 10000 })
db.gamescores.updateOne({name:"pacman"},{$max: { "highscore": 9000}})
db.gamescores.find({})  -> didnt updated


db.gamescores.updateOne({name:"pacman"},{$max: { "highscore": 12000}})
db.gamescores.find({})  -> now it indeed updated and set it to 120000

- $min is similar but opposite direction


# delete


- similar to find but deletes


# replaceOne()

modifies the entire document and preserves the _id

# SECURITY

the can ask EXAM what is the best way to do ...
- Originally installing mongo automatically created a db without any type of security, anyone could enter

- authentication: who enters in the db, which user
- authorization: what resources you can access
- views
...

# Authentication

- Use many factor, passwords + certificate, if possible + biometrics or incoming ip address

- ways to auth:
    - scram-sha (user + pass)
    - x.509 : certificates
    - LDAP: active directory  -> it is deprecated in the newer versions
    - kerberos (short lived tokens)
    - Mongodb-aws: use IAM
    - OpenID Connect / Oauth 2.0 --> workforce and workload identity federation in atlas

# SCRAM-SHA

- mONGO HOLDS the user + password

- mongo does some checks and takes some second  -> helps with brute force, it does extra rounds to delay the connection to ssh

- Create only one conenction and reuse it or it will add to much workload in the server


- PROS:
    - sIMPLE
    -secure

- CONS:
    - Managed separately per cluisted
    - Administration is local and manual, you have to do it

# X.509 Certificate

- Client presents the certificate as part of the TSL connection
- Mongo checks if the user is trusted for than cert
- You still need to use user + password
- but you can centrally manage certificates
- however you need mechanism to update the,

# OPENid connect (OIDC) / Oauth2.0

- External identity providers (IdP) for Workforce and Workload Identity Federatio

- Workforce --> human users, protocol OIDC, signle sing obnn , centralized managemen

- Workload identity federation --> applications, OATH2.0 protocol, cloud provider integration, passwordless authentication


- PROS:
    - common in big organizations to have this already implemented
    - easy to add users or remove them from the db
- CONS:
    - DEPENDS on external provider, if it fails you can not enter
    - supports alternate servers
    - OpenID security weakness --> exposed to phising in these systems
    - However you could maintain user + pass as alternative way to authenticate (advantage)

# LDAP (deprecated)

- use always tls
- it is deprecated though

- PROS:
    - sINGLE SIGN ON
    - SINGLE mechanish to auth
    - easy to add or remove users
- CONS:
    - REquires config tls

# Kerberos

Similar to X.509, it is proven and regarded

# WHEN TO USE AND WHEN: BEST PRACTICES

- Human users_:
    - use an individual login per user 

    - users has to be traceable to knowwhat they did
    - oidc kerberos ldap is preferable
    - scram is secure but not centralized

- Applicaiton user
    - has to use different credentials than humans
    - kerberos is interesting for windows services
    - use workload identity if possible
    - passwords not hardcoded in the code

exam: WHICH SYSTEMS ARE SUPPORRTED IN MONGO
EXAM: which is preferer? --> as many security layers (factors) or the most modern system

# Authorization (AUTHZ)

- users defined by user@database
- default db is "admin"
- "system.users" collection is the one that saves users and permissions

- users have 1 or more roles:
    - built in roles (write, read)
    - roles can inherit from others
    - custom roles can be created

- roles include 1 or more privileges, one privilege is an action that can be done in one resource

eg. custom role "analyst" with privileges
    read@datawarehhouse (one db) and readWrite@reporting_db
    + custom role with prioivileges = finances.read + ...

- DATABase resources: cluster, db, collections

# databaase actions:

- crud, management, ...

# Builtin roles
- dbAdmin
- clusterAdmin
- userAdminAnyDatabase
- readAnyDatabase
- readWriteAnyDatabase
- clusterMonitor
....

# ATLAS user privileges
- admin
- read write any db
- 
-


# Scope of authorization

- User with root or __system roles can do everything

- 3 types of admins, some of them can not read data

# Document level security options

- Application level -> encrypt

- using views

- client Side Field Level Encryption: encrypt some fields in the document, it stays encrypted at rest, the client has to recover encrypted data and decrypt it, not even admins could see the data


# Defining authorization

- Some methods need to map user acocunt to permissions (ldap, x.509)

# authorization best paractices

- minimum permissions per user / role

- same for app users

- read only if possible

- create user and roles only in the "admin" db

- always have an user that can enter only with user + password in caase other auth methods fail


# Encryption

1. communications -> tls

    client with server traffic
    the network --> eg replica set, communicaiton between dones encrypted

2. data

    at rest (while stored)
    in use client -> mongo will never know how to decrypt

EXAM: WHICH SCENARIOS IS MORE SECURE --> the one with more communications encrypted and data encryption

exam: CAN AN ADMIN HAVE ACCEESS TO DECRYPT? -_> NO if it is client encryption (the client handles it, eg youur web server)

# Network encryption:

- disabled
- enabled (allowTLS)
- enabled and preferred (preferTLS) -> SERVER ACCEPTS BOTH ENCRIPTED AND ENCRYPTED (see ppowerpoint)
- mandatory (requireTLS)

Mongo can provide on its server X.509
ITS A GOOD PRACTRICE
IN atlas you cannot deactivate tls


# Encrpytion at rest

- encrypts in disk
- needs users and password  seret key
- store keys in local is not considered secure
- keys must manually rotate

- does not protect if anyone acces to machine or stoles keys


# CLIENT SIDE FIELD LEVEL ENCRYPTION

- relevant for devs
- you have to incorpoate in the app
- extra layuer of security

- [Important] Dumping client RAM (by an attacker) or a compromised client is a security risk (because this encryption is manaaged by the user (FINAL app))

# Encrypt and decrypt at the client

- Using field level

## Field level encrpytion modes

- free mongo community -> function exposed in the drived, done manually 

- enterprise & arlas --> jsonschema defines encrypted fields + driver automatically encrypts crus operations

1. inplementing encryption is hard, mongo provides a secure way to do it (aNd an easy one)


# CSFLE Keys and encryption

- driver provdes varios options .> local keys opr hardcoded, encrypted key vault in the serer, third partty AWS. AZURE for master vault

can de used -> determinisstic, ....

# Queryable encryption

- from mongo 7.0
- encrypt data in the client side

# Auditing (auditorias in spanish)

- mongo has options --> activate audit logs (who did what? is what it does)
- it is not useful for debugging
- in case of app user -> it is not what the user did, what app did each request (we can not know whuich user, it will appear the user of the app, not the final user (eg, web user))

- it is responsibility of the DBA (db admins)

# Mongo db auditing capability

- does not impone excessive workload, but it is an extra workload

- you can add some extra levels of logs and that will increase the prod db load

- the audit logs tell if the operations were successful, who did what and if it acocomplished it

- audit outpuit .-> either format syslog, JSON or BSON
    - USE JSON TO EXPORT LOGS TO ANOTHER MONGO collection
    - logs can be encrypted 

- the auditing cna configure whuich operation we want to audit, control

# audit best practices

- separate user for human and apps

- log everything doen by a human but not for apps

- have service accounts the human can not use (in hteory, in pracitce it edepnds, is complex and the dev might want to avoid security)


# additional security features

- obfuscate info (redacting PII) (info that identified people uniquely (that person, eg RGDP compliance))
- mongo listens on 127.0.0.1 (localhost) by default (another ips access must be granted manually)
- can autorize ips (CIDRs) per user

- for personal data there is a flag to configure some fields to not  appear in the logs


# internal authentication

- encrypt internal between nodes communications and from user to server (user + pass + optional certificates)

- with SCRAM.SHA there us a shared secret calle keyfile the user is connect as is __systme@local
. with X.509, the crtr mustr have the same organization and organization units and A cn MAtching ...


# About sql injection??

- because of BSON:
    - INJECTION IS not the thing it is in sql
    - mnogo never parses text or json on the server
    - there are some simialr attacks that affect mongo

- javascript browser apps / node.js
    - client side js injection is still possible
    - be sure to validate user input even if injection is not a thing



# INDEXES

to do a query over a field without index, it will load hte entire colelction in memory, if its big it will have to batch it
this could mean big worload

- indexes are elements ordered by default that avoid loading the entire colleciton
- the index shoudl be small eough to load in the server cache to not batch the search

- the search in the index will return which documents have to be retrieved


# Index misconceptions

- mongo is so fast it does not need indexes

- every field is automatically indexes

- noSQL uses hashes not indexes

however, indexes will increase thje load when inserting a docunment that has an indexed field --> indexs negsatively affects writting


# indexes are btress

- data in an idex is ordered
- values of the index point to document identity
- if the document moves,, the index does not change
- indexes are sorted and compressed, if values are too similar, it reduces size by keepijng common pattern

# when to use an index

- if a query is common
- without index mongo does colScan (colleciton scan), foreach doc, read from disk the entire doc, decompress into memory, store in cache --> it can kill hte cache so it has to do it in batches, which is even more slow


# Using indexes and choosign them

- for each query, it tries to find an index to fits, some indexes may partilly fit or not fit at all
- hence, it picks all candidate indexes and chooses the best index plan


https://www.mongodb.com/docs/manual/administration/production-notes/?msockid=094519b12fc56a620aa10eaa2e716bc5

https://www.mongodb.com/es/docs/manual/administration/security-checklist/?msockid=094519b12fc56a620aa10eaa2e716bc5


https://learn.mongodb.com/redeem


- it it detects and index performnace is slow, there are new indexes or server restarts, it tries to evaluate again which indexes are the most suitable

db.test.getPlanCache().clear() -> manually clear which indexes to use in order to check if there are better index combinations

- ideally for a 10 doc query, we want to read only 10 index entries and 10 documents

# Viewing Explain Plans (explain command)

explain() shows how mongo db will execute the query

- the most important if it did a colleciton scan oor an index scan

# Explain command verbosity

- queryPlanner ..> shows the winning query plan but does not execute it

- executionStats ..> executes query and gather stats

- allPlansExecution runs candidate plans and gathers statistics

If you do not specify verbosity, by defualt value is "queryPlanner"

# Interpret explain plan results

find().explain("executionStats")

COLLSCAN --> AVOID


# CREATING AN INDEX

- createIndex({number_of_reviews: 1})
    - by default will be called "field_name_1" 



# index types

- Single field indexes

- Compound (multiple field) indexes

- Multikey indexes: field with array or nested doc

- geospatial indexes

- others:
    - text indexes (free text index) -> atlas search to do semantic search is better than a text index
    - hashes index (fields that are hashes)
    - wildcard: to index all the fields in the documents


# Single field indexes:
- we send the field name and the direction (ASC: 1, DESC -1) anscending oir descending index
- the direction is not relevant in a single field index though (we take the same starting form beginning or from end)

- avoid: indexing an object type ..> index that the whole object as a comparable blob, it is better to use individual fields with simple dtypes

# Unique index

- indexes can enforce a unique constraint

db.a.createIndex({custid: 1}, {unique: true})


# Partial index

- avoid indexing all documents, only document that has a concrete value in the index field

db.a.createIndex({email: 1}, {partialFilterExpression: {status: "active"}}) -_> INMDEXES email field in the documents that have the field status equal to "active"

# Hashed index

- a 20 byte md5 of the bson value

- support exact martch only

- can not be used with unique constrains

- can reduce index size if the vlaue us to big

- downstream cons-->


# listing indexes

complete tghis please

# index sizes

db.a.stats().indexSizes


# indexes and performance

- improve read operations but affect writes IMPORTANT! (more or less 10% overhead in writes, applies to single and compound indexes)

- Hash indexes, multikey, text inmndex and wiildcard can addm ore than 10% overhead for writes

- the index is modified anytime that a document
:
    - is inserted
    - is deleted
    - is updated in a way that the change affects index field and the resulting index is differeten to the previous (it could affect but compute the same index)

- hence if my db is 90% writes, indexes will affect a los


# Index limits

- 64 per collection, do not be close

- wrote performance degrades to unusable between 20, 30 indexes

- 4 indexes per collection is hte ideal

# Use inddexes withh care

- every query should use an index (if its frequent)

every index should be used by a query

- indexes require server memory,m, be aware of the choice you do



