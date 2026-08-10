#!/usr/bin/env node
// manim-web-mcp npm wrapper — spawns the Python MCP server
// Usage: npx manim-web-mcp [--transport stdio] [--work-dir /path]

"use strict";

const { spawn } = require("child_process");
const path = require("path");

// --- Python detection ---
function findPython() {
  const candidates = ["python3", "python"];
  for (const cmd of candidates) {
    try {
      // synchronous check — only runs at startup
      const result = require("child_process").execSync(
        `${cmd} --version 2>&1`,
        { encoding: "utf-8", timeout: 5000, stdio: "pipe" }
      );
      if (result.match(/Python 3\.(1[2-9]|[2-9]\d)/)) {
        return cmd;
      }
    } catch {
      // not found or version too old
    }
  }
  return null;
}

const pythonCmd = findPython();
if (!pythonCmd) {
  console.error(
    "manim-web-mcp: Python >= 3.12 is required but not found.\n" +
    "Install Python 3.12+ from https://www.python.org/downloads/ or via your package manager."
  );
  process.exit(127);
}

// --- Check manim-web-mcp is installed ---
try {
  require("child_process").execSync(
    `${pythonCmd} -m manim_web.mcp.server --help`,
    { encoding: "utf-8", timeout: 10000, stdio: "pipe" }
  );
} catch (e) {
  console.error(
    "manim-web-mcp: Python package 'manim-web-mcp' is not installed.\n" +
    "Install it with:  pip install manim-web-mcp\n" +
    "Or with uvx:     uvx manim-web-mcp\n\n" +
    "Details: " + (e.stderr || e.message)
  );
  process.exit(126);
}

// --- Build args ---
const userArgs = process.argv.slice(2);
const args = ["-m", "manim_web.mcp.server", ...userArgs];

// --- Spawn child process ---
const child = spawn(pythonCmd, args, {
  stdio: "inherit",
  env: { ...process.env },
  windowsHide: true,
});

// --- Signal forwarding ---
process.on("SIGINT", () => child.kill("SIGINT"));
process.on("SIGTERM", () => child.kill("SIGTERM"));
process.on("SIGHUP", () => child.kill("SIGHUP"));

child.on("exit", (code, signal) => {
  if (signal) {
    process.exit(128 + (signal === "SIGINT" ? 2 : signal === "SIGTERM" ? 15 : 1));
  }
  process.exit(code ?? 1);
});

child.on("error", (err) => {
  console.error("manim-web-mcp: Failed to start Python process:", err.message);
  process.exit(1);
});