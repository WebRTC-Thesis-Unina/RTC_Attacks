const express = require("express");
const http = require('http');
const mongoose = require('mongoose');
const {spawn, exec} = require("child_process")
const fs = require("fs");
const path = require("path");
const util = require("util");
const execAsync = util.promisify(exec);

const app = express();
app.use(express.static("public"))
app.use(express.json())

// Funzione per popolare il database all'avvio a partire da file JSON
async function loadScenarios() {
  try {
    const count = await Scenario.countDocuments();
    if (count === 0) {  // se la collection è vuota
      const dataPath = path.join(__dirname, "database", "scenarios.json");
      const rawData = fs.readFileSync(dataPath, "utf8");
      const scenarios = JSON.parse(rawData);

      await Scenario.insertMany(scenarios);
    } 
  } catch (err) {
    console.error("Error:", err.message);
  }
}

// Funzione che attende finché non è stabilita la connessione con il DB
async function connectMongoWithRetry() {
  while (true) {
    try {
      await mongoose.connect(
        "mongodb://root:example@localhost:27017/rtc_attacks?authSource=admin"
      );
      console.log("Mongo connected");
      break;
    } catch (err) {
      console.log("Mongo not ready, retry in 3s...");
      await new Promise(r => setTimeout(r, 3000));
    }
  }
}

// Funzione che builda e avvia i container principali, collega nodeJS al DB e carica gli scenari
async function start(){
    console.log("Starting containers...");
    await execAsync(`make build start`);
    console.log("Connecting...");
    await connectMongoWithRetry();
    await loadScenarios();
    server.listen(8888, () => console.log("Server listen on port 8888"));
}

function escape(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

const scenarioSchema = new mongoose.Schema({
    id: Number,
    name: String,
    description: String,
    steps: String,
    containers: Array
});

const Scenario = mongoose.model("scenario", scenarioSchema);

const server = http.createServer(app)

app.get("/scenarios",async (req, res)=>{
    try {
        const scenarios = await Scenario.find().sort({id: 1});

        const names = scenarios.map(s => s.name);
        const ids = scenarios.map(s => s.id);

        return res.json({names: names, ids: ids});    
    } catch(err){
        return res.status(500).json({ok: false, err: err.message});
    }
})

app.get("/scenario/:id", async(req, res) => {
    const id = parseInt(req.params.id);
    try {
        const scenario = await Scenario.findOne({id: id})

        if (!scenario) {
            return res.status(404).json({ error: "Scenario not found" });
        }

        return res.json({name: scenario.name, description: scenario.description, steps: scenario.steps});
    } catch(err){
        return res.status(500).json({ok: false, err: err.message});
    }
})

app.post("/make-start", async(req, res) => {
    const folder = req.body.folder;

    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("Transfer-Encoding", "chunked");
    
    let buildCmd = `
        make start && cd ${__dirname}/public/labs/${folder} && make start
    `;

    const stream = spawn(buildCmd, { shell: true });

    stream.stdout.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.stderr.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.on("close", () => {
        res.end();
    });
})

app.post("/make-stop", async(req, res) => {
    const folder = req.body.folder;
        
    let buildCmd = `cd ${__dirname}/public/labs/${folder} && make stop`;

    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("Transfer-Encoding", "chunked");

    const stream = spawn(buildCmd, { shell: true });

    stream.stdout.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.stderr.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.on("close", () => {
        res.end();
    });
})

app.get("/search", async(req, res) => {
    const name = escape(req.query.name);
    try {
        const scenarios = await Scenario.find({ name:{ $regex: name, $options: "i" }}).sort({id: 1});;
        if (scenarios.length === 0) {
            return res.status(404).json({ error: "Scenario not found" });
        }
        return res.json(scenarios)
    } catch(err){
        return res.status(500).json({ok: false, err: err.message});
    }
})

app.post("/build-all", async(req, res) => {
    const folder = req.body.folder;
    const elements = req.body.elements;
    
    const container = elements.replaceAll(","," ")

    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("Transfer-Encoding", "chunked");

    let buildCmd = `cd ${__dirname}/public/labs/${folder} && make build SERVICE="${container}"`
    
    
    const stream = spawn(buildCmd, { shell: true });

    stream.stdout.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.stderr.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.on("close", () => {
        res.end();
    });
})

app.post("/build", async(req, res) => {
    const image = req.body.image;
    const folder = req.body.folder;

    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.setHeader("Transfer-Encoding", "chunked");

    let buildCmd = `cd ${__dirname}/public/labs/${folder} && make build SERVICE="${image}"`
    
    const stream = spawn(buildCmd, { shell: true });

    stream.stdout.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.stderr.on("data", (chunk) => {
        res.write(chunk.toString());
    });

    stream.on("close", () => {
        res.end();
    });
})

app.post("/images-to-build", async(req, res) =>{
    const id = req.body.id;

    try {
        const scenario = await Scenario.findOne({id: id})
        const containers = scenario.containers;

        if (!scenario) {
            return res.status(404).json({ error: "Scenario not found" });
        }

        exec(`docker images --format "{{.Repository}}"`, (err, stdout, stderr) => {
            if (err) {
                return res.status(500).json({ ok: false, err: err.message });
            }

            const dockerImages = stdout
                .split("\n")
                .map(i => i.trim())
                .filter(Boolean);

            const dockerSet = new Set(dockerImages);

            const containersToSend = containers.filter(img => !dockerSet.has(img));

            res.json({ containers: containersToSend });
        });

    } catch (err) {
        return res.status(500).json({ok: false, err: err.message});
    }
})

start()

async function shutdown() {
  try {
    console.log("Stopping containers...");

    exec("make stop", (err) => {
      if (err) {
        console.error("Error:", err);
      } 
      process.exit(0);
    });

  } catch (err) {
    console.error("Error:", err);
    process.exit(1);
  }
};

process.on("SIGINT", shutdown);