#!/usr/bin/env zx

import { createSSHKeyPair } from "./lib/crypto.mjs";
import {
  getRegions,
  getTenancyId,
  searchCompartmentIdByName,
} from "./lib/oci.mjs";
import {
  checkRequiredProgramsExist,
  printRegionNames,
  setVariableFromEnvOrPrompt,
  writeEnvJson,
  readEnvJson,
} from "./lib/utils.mjs";

const shell = process.env.SHELL | "/bin/zsh";
$.shell = shell;
$.verbose = false;

let properties = await readEnvJson();

console.log("Check dependencies...");
const dependencies = ["git", "unzip", "oci"];
await checkRequiredProgramsExist(dependencies);

const tenancyId = await getTenancyId();
properties = { ...properties, tenancyId };
await writeEnvJson(properties);

const regions = await getRegions();
const regionName = await setVariableFromEnvOrPrompt(
  "OCI_REGION",
  "OCI Region name",
  async () => printRegionNames(regions)
);
properties = { ...properties, regionName };
await writeEnvJson(properties);

const compartmentName = await setVariableFromEnvOrPrompt(
  "LOL_COMPARTMENT_NAME",
  "Compartment Name (root)"
);

const riotGamesApiKey = await setVariableFromEnvOrPrompt(
  "RIOT_API_KEY",
  "Riot Games API Key"
);
properties = { ...properties, riotGamesApiKey };
await writeEnvJson(properties);

const compartmentId = await searchCompartmentIdByName(
  compartmentName || "root"
);
properties = { ...properties, compartmentId };
await writeEnvJson(properties);

const defaultSSHPublicKeyPath = path.join(os.homedir(), ".ssh", "id_rsa.pub");
const publicSSHKeyExists = await fs.pathExists(defaultSSHPublicKeyPath);

if (publicSSHKeyExists) {
  const content = (await $`cat ${defaultSSHPublicKeyPath}`).stdout.trim();
  properties = { ...properties, sshPublicKey: content };
} else {
  const publicKey̧Content = await createSSHKeyPair();
  properties = { ...properties, sshPublicKey: publicKey̧Content };
}
await writeEnvJson(properties);
