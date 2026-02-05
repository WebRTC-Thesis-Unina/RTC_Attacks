const fs = require("fs")
const express = require("express")
const https = require("https")
const mongoose = require("mongoose")

const app = express()
app.use(express.static('public'))
app.use(express.json())

mongoose.connect("mongodb://root:example@localhost:27017/rtc_attacks?authSource=admin")

const server = https.createServer({
    key: fs.readFileSync('key.pem'),
    cert: fs.readFileSync('cert.pem')
}, app)

const utenteSchema = new mongoose.Schema({
    username: String,
    password: String
});

const User = mongoose.model('nosqli_user', utenteSchema);

app.post("/login", async (req, res) => {
    const {username, password} = req.body;

    const user = await User.findOne({username, password}).exec()
    if(!user){
        return res.status(404).send('User not found')
    } 
    
    return res.status(200).send('Welcome');
    
})

server.listen(443, () => console.log('Server listen on 443'))