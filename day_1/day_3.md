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









