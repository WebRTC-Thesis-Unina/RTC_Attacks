const fs = require("fs")
const express = require("express")
const https = require("https")
const mongoose = require("mongoose")

const app = express()
app.use(express.static('node/public'))
app.use(express.json())

mongoose.connect("mongodb://192.168.1.100:27017/sqli_login")

const server = https.createServer({
    key: fs.readFileSync('node/key.pem'),
    cert: fs.readFileSync('node/cert.pem')
}, app)

const utenteSchema = new mongoose.Schema({
    username: String,
    password: String
});

const User = mongoose.model('user', utenteSchema);

app.post("/login", async (req, res) => {
    const {username, password} = req.body;

    const user = await User.findOne({username, password}).exec()
    if(!user){
        return res.status(404).send('User not found')
    } 
    
    return res.status(200).send('Welcome');
    
})

server.listen(443, () => console.log('Server listen on 443'))