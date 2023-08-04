#!/usr/bin/env zx

import { exitWithError, readEnvJson } from "./lib/utils.mjs";

const shell = process.env.SHELL | "/bin/zsh";
$.shell = shell;
$.verbose = false;

const {
  tenancyId,
  regionName,
  compartmentId,
  riotGamesApiKey,
  desiredNumberCPUs,
  sshPublicKey,
} = await readEnvJson();

const sshPublicKeyEscaped = sshPublicKey.replaceAll("/", "\\/");
const replaceCmdSSHPublicKey = `s/SSH_PUBLIC_KEY/${sshPublicKeyEscaped}/`;

try {
  let { exitCode, stderr } =
    await $`sed 's/REGION_NAME/${regionName}/' dev/terraform/terraform.tfvars.template \
                   | sed 's/TENANCY_OCID/${tenancyId}/' \
                   | sed 's/COMPARTMENT_OCID/${compartmentId}/' \
                   | sed 's/DESIRED_NUMBER_CPU/${desiredNumberCPUs}/' \
                   | sed 's/RIOT_GAMES_API_KEY/${riotGamesApiKey}/' \
                   | sed ${replaceCmdSSHPublicKey} > dev/terraform/terraform.tfvars`;
  if (exitCode !== 0) {
    exitWithError(`Error creating dev/terraform/terraform.tfvars: ${stderr}`);
  }
  console.log(`${chalk.green("dev/terraform/terraform.tfvars")} created.`);
} catch (error) {
  exitWithError(error.stderr);
}
