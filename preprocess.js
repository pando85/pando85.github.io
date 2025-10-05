"use strict";

// on publish this script will check all docs projects and versions and prepare static data
// so it does not have to be generated using complicated logic from liquid templates / jekyll

const fs = require("fs");
const jsonfile = require("jsonfile");
const path = require("path");
const semver = require("semver");

function getDirectories(srcpath) {
  return fs
    .readdirSync(srcpath)
    .filter(file => fs.lstatSync(path.join(srcpath, file)).isDirectory());
}

const ROOT_DIR = `${__dirname}`;

// collect all docs projects with versions (forcing master to the end)
const projects = [
  ...getDirectories(`${ROOT_DIR}/docs`).map(project => {
    // get all versions except latest
    const versions = getDirectories(`${ROOT_DIR}/docs/${project}`)
      .filter(v => v !== "latest")
      .sort((a, b) => {
        // Custom comparison for beta versions
        if (a.includes('beta') && b.includes('beta')) {
          // Extract beta numbers for comparison
          const aBeta = a.match(/beta\.?(\d+)/i);
          const bBeta = b.match(/beta\.?(\d+)/i);
          if (aBeta && bBeta) {
            return parseInt(bBeta[1]) - parseInt(aBeta[1]); // Descending order
          }
        }

        // For non-beta versions or mixed cases, use semver
        try {
          return semver.rcompare(semver.coerce(a).version, semver.coerce(b).version);
        } catch (e) {
          // Fallback to string comparison
          return b.localeCompare(a);
        }
      });

    // Process versions and mark stable ones
    const processedVersions = versions.map(version => {
      const versionObj = {
        version,
        path: `/docs/${project}/${version}`
      };
      // Mark stable versions (non-prerelease versions)
      if (!version.includes('beta') && !version.includes('alpha') && !version.includes('rc')) {
        try {
          const coercedVersion = semver.coerce(version);
          if (coercedVersion && !semver.prerelease(coercedVersion.version)) {
            versionObj.stable = true;
          }
        } catch (e) {
          // If semver parsing fails, don't mark as stable
        }
      }
      return versionObj;
    });

    // Separate stable and prerelease versions
    const stableVersions = processedVersions.filter(v => v.stable);
    const prereleaseVersions = processedVersions.filter(v => !v.stable);

    // Create final ordered list: latest first, then stable versions, then prerelease versions
    const latestVersion = { version: "latest", path: `/docs/${project}/latest` };
    const orderedVersions = [latestVersion, ...stableVersions, ...prereleaseVersions];

    return {
      project,
      path: `/docs/${project}`,
      versions: orderedVersions
    };
  })
];

// write json for jekyll (and browser)
jsonfile.writeFileSync(`${ROOT_DIR}/_data/projects.json`, projects);
