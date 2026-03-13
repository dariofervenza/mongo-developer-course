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

