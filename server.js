import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

// HTML failai
app.use(express.static(path.join(__dirname, "html")));

// start server
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => console.log(`Serveris paleistas ant ${PORT}`));
