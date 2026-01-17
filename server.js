const express = require("express");
const http = require('http');
const mongoose = require('mongoose');
const {spawn, exec} = require("child_process")

const app = express();
app.use(express.static("public"))
app.use(express.json())

require('dotenv').config(); 
mongoose.connect(process.env.MONGODB_URI)

const scenarioSchema = new mongoose.Schema({
    id: Number,
    name: String,
    description: String,
    steps: String,
    containers: Array
});

const Scenario = mongoose.model("scenario", scenarioSchema);

const server = http.createServer(app)

server.listen(8888, () => console.log("Server listen on port 8888"));

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
    const name = req.query.name;
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

    let buildCmd;

    if (container.includes("ttyd") && container.includes("collector")){
        const [ttyd, collector] = container.split(" ").slice(-2);
        const containerNew = container.replaceAll(/ttyd|collector/g, "").trim();
        
        buildCmd = `make build SERVICE="${ttyd} ${collector}" &&
            cd ${__dirname}/public/labs/${folder} && make build SERVICE="${containerNew}"`
    
    } else if (container.includes("ttyd") || container.includes("collector")){
        const [ttyd_collector] = container.split(" ").slice(-1);
        const containerNew = container.replaceAll(/ttyd|collector/g, "").trim();
    
        buildCmd = `make build SERVICE="${ttyd_collector}" &&
            cd ${__dirname}/public/labs/${folder} && make build SERVICE="${containerNew}"`
    
    } else {
        buildCmd = `cd ${__dirname}/public/labs/${folder} && make build SERVICE="${container}"`
    }
    
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

    let buildCmd;

    if(image === "ttyd" || image === "collector"){
        buildCmd = `make build SERVICE="${image}"`
    } else {
        buildCmd = `cd ${__dirname}/public/labs/${folder} && make build SERVICE="${image}"`
    }
    
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
        const containers = [...scenario.containers, "ttyd", "collector"];

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