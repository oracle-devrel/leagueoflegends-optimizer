#!/usr/bin/env zx
import { exitWithError } from "./utils.mjs";

export async function getRegions() {
  try {
    const tenancyId = await getTenancyId();
    const output = (
      await $`oci iam region-subscription list --tenancy-id ${tenancyId}`
    ).stdout.trim();
    const { data } = JSON.parse(output);
    return data
      .filter((r) => r.status === "READY")
      .map((r) => ({
        key: r["region-key"].toLowerCase(),
        name: r["region-name"],
        isHomeRegion: r["is-home-region"],
      }));
  } catch (error) {
    exitWithError(`Error: get regions ${error.message}`);
  }
}

export async function getNamespace() {
  const output = (await $`oci os ns get`).stdout.trim();
  const { data } = JSON.parse(output);
  return data;
}

export async function listAdbDatabases(compartmentId) {
  try {
    const { stdout, exitCode, stderr } =
      await $`oci db autonomous-database list --all --compartment-id ${compartmentId}`;
    if (exitCode !== 0) {
      exitWithError(stderr);
    }
    return JSON.parse(stdout.trim()).data;
  } catch (error) {
    exitWithError(`Error: download wallet ${error.stderr}`);
  }
}

export async function downloadAdbWallet(adbId, walletFilePath, walletPassword) {
  try {
    const { stdout, exitCode, stderr } =
      await $`oci db autonomous-database generate-wallet \
      --autonomous-database-id ${adbId} \
      --file ${walletFilePath} \
      --password ${walletPassword}`;
    if (exitCode !== 0) {
      exitWithError(stderr);
    }
    console.log(`Wallet downloaded on ${chalk.green(walletFilePath)}`);
  } catch (error) {
    exitWithError(`Error: download wallet ${error.stderr}`);
  }
}

export async function getAvailableShapes(options = {}) {
  try {
    const output = (
      await $`oci compute shape list --compartment-id ${await getTenancyId()}`
    ).stdout.trim();
    const { data } = JSON.parse(output);
    const { type = "*", flex, includeOld = false } = options;
    return data
      .filter((shape) => {
        if (shape.shape.includes("Standard1.")) return false;
        return true;
      })
      .filter((shape) => {
        if (type === "*") return true;
        if (type === "bm") return shape.shape.startsWith("BM.");
        if (type === "vm") return shape.shape.startsWith("VM.");
      })
      .filter((shape) => {
        if (flex === undefined) return true;
        return flex
          ? shape.shape.endsWith(".Flex")
          : !shape.shape.endsWith(".Flex");
      })
      .sort((s1, s2) => {
        return s1.shape.localeCompare(s2.shape);
      });
  } catch (error) {
    exitWithError(`Error: get available shapes ${error.message}`);
  }
}

export async function getTenancyId() {
  const tenancyIdEnv = process.env.OCI_TENANCY;
  const tenancyId = tenancyIdEnv
    ? tenancyIdEnv
    : await question("OCI tenancy: ");
  return tenancyId;
}

export async function searchCompartmentIdByName(compartmentName) {
  if (!compartmentName) {
    exitWithError("Compartment name required");
  }
  if (compartmentName === "root" || !compartmentName.length) {
    return getTenancyId();
  }
  try {
    const { stdout, exitCode, stderr } =
      await $`oci iam compartment list --compartment-id-in-subtree true --name ${compartmentName} --query "data[].id"`;
    if (exitCode !== 0) {
      exitWithError(stderr);
    }
    if (!stdout.length) {
      exitWithError("Compartment name not found");
    }
    const compartmentId = JSON.parse(stdout.trim())[0];
    return compartmentId;
  } catch (error) {
    exitWithError(error.stderr);
  }
}

export async function uploadApiKeyFile(userId, publicKeyPath) {
  if (!userId) {
    exitWithError("User ID required");
  }
  if (!publicKeyPath) {
    exitWithError("Public RSA key required");
  }
  const rsaPublicKeyExists = await fs.pathExists(publicKeyPath);
  if (!rsaPublicKeyExists) {
    exitWithError(`RSA Public key ${publicKeyPath} does not exists`);
  }
  try {
    const { stdout, exitCode, stderr } =
      await $`oci iam user api-key upload --user-id ${userId} --key-file ${publicKeyPath}`;
    if (exitCode !== 0) {
      exitWithError(stderr);
    }
    if (!stdout.length) {
      exitWithError("Compartment name not found");
    }
    const { fingerprint } = JSON.parse(stdout.trim()).data;
    return fingerprint;
  } catch (error) {
    exitWithError(error.stderr);
  }
}

export async function getUserId() {
  const userIdEnv = process.env.OCI_CS_USER_OCID;
  if (userIdEnv) {
    return userIdEnv;
  }
  const userEmail = await question("OCI User email: ");
  const { stdout, exitCode, stderr } = await $`oci iam user list --all`;
  if (exitCode !== 0) {
    exitWithError(stderr);
  }
  if (!stdout.length) {
    exitWithError("User name not found");
  }
  const data = JSON.parse(stdout.trim()).data;
  const userFound = data.find((user) => user.email === userEmail);
  if (!userFound) {
    exitWithError(`User ${userEmail} not found`);
  }
  return userFound.id;
}
