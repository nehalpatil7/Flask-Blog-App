const express = require("express");
const nearAPI = require("near-api-js");
const bodyParser = require("body-parser");

const app = express();
const port = 3001;

accountName = "thereis.testnet";

app.use(express.json());
app.use(bodyParser.json());
app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE");
  res.header(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept"
  );
  next();
});

async function initNearConnection() {
  const { keyStores, KeyPair, connect } = nearAPI;
  const myKeyStore = new keyStores.InMemoryKeyStore();
  const PRIVATE_KEY ="ed25519:4d89deWNtHj6XvZSsiSajupB8Y7iSBnZHyeLC85XT9mQGAYM78eLKQBv5rvKNyjK21TS4yEb9dR13zMv5QDqL512"
   
  // creates a public / private key pair using the provided private key
  const keyPair = KeyPair.fromString(PRIVATE_KEY);
  // adds the keyPair you created to keyStore
  await myKeyStore.setKey("testnet", accountName, keyPair);

  const connectionConfig = {
    networkId: "testnet",
    keyStore: myKeyStore, // first create a key store
    nodeUrl: "https://rpc.testnet.near.org",
    walletUrl: "https://testnet.mynearwallet.com/",
    helperUrl: "https://helper.testnet.near.org",
    explorerUrl: "https://testnet.nearblocks.io",
  };
  const nearConnection = await connect(connectionConfig);
  return nearConnection;
}

const createContract = (account) => {
  return new nearAPI.Contract(account, accountName, {
    createMethods: ["create_claim"],
    viewMethods: ["view_claim"]
  });
};

// Express route to fetch data from MySQL
app.get("/getAccountBalance", async (req, res) => {
  try {
    const connectionData = await initNearConnection();
    const account = await connectionData.account(accountName);
    const data = await account.getAccountBalance();

    console.log("data", data);
    res.json(data);
  } catch (error) {
    console.error("Internal server error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});

// Express route to fetch data from MySQL
app.get("/getClaims", async (req, res) => {
  try {
    const val=req.query.usertype != null ? { usertype: req.query.usertype } : true;
    const connectionData = await initNearConnection();
    const account = await connectionData.account(accountName);
    const contract = await createContract(account);
    const data = await contract.view_claim({ insurer_id: val });
    res.json(data);
  } catch (error) {
    console.error("Internal server error:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});
app.post("/createClaim", async (req, res) => {

  const requestData = req.body;
  const connectionData = await initNearConnection();
  const account = await connectionData.account(accountName);
  const contract = await createContract(account);
  console.log("======================================");
  console.log(contract, "contract methods");
  const ans = await contract.create_claim(requestData);
  console.log("======================================", ans);
  res.json(ans);
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
