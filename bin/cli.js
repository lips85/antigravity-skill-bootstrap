#!/usr/bin/env node

import { Command } from 'commander';
import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import chalk from 'chalk';
import ora from 'ora';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const program = new Command();

program
    .name('agv-skills-setup')
    .description('Install Antigravity Skills to your local project or global environment')
    .version('1.0.0');

program
    .option('-l, --local', 'Install skills locally to ./.agent/skills')
    .option('-g, --global', 'Install skills globally to ~/.gemini/antigravity/skills');

program.parse(process.argv);

const options = program.opts();

// Show help if no arguments provided
if (!process.argv.slice(2).length) {
    program.outputHelp();
    process.exit(0);
}

async function run() {
    const spinner = ora('Initializing installation...').start();

    try {
        // Determine source path (skills folder in the package)
        const sourcePath = path.resolve(__dirname, '../skills');

        if (!fs.existsSync(sourcePath)) {
            throw new Error(`Skills directory not found at: ${sourcePath}`);
        }

        let targetPath = '';
        let mode = '';

        if (options.local) {
            mode = 'Local';
            targetPath = path.resolve(process.cwd(), '.agent', 'skills');
        } else if (options.global) {
            mode = 'Global';
            const homeDir = os.homedir();
            targetPath = path.join(homeDir, '.gemini', 'antigravity', 'skills');
        }

        spinner.text = `Installing skills (${mode})...`;

        // Calculate size (optional/simplistic)

        // Copy Files
        // For local: we want .agent/skills structure (which targetPath is already set to)
        // For global: we want content directly in skills (which targetPath is already set to)

        // If target exists, maybe warn? or overwrite? We will overwrite for now as "setup/update".

        await fs.ensureDir(targetPath);
        await fs.copy(sourcePath, targetPath, {
            overwrite: true,
            errorOnExist: false
        });

        // Copy index file if it exists separately (it should be inside skills/ based on current structure)
        // Based on previous step, we moved .agent/skills -> root/skills.
        // So root/skills contains everything including skills_index.json.
        // So copying root/skills to targetPath is correct.

        spinner.succeed(chalk.green(`Skills installed successfully to: ${targetPath}`));

        if (mode === 'Local') {
            console.log(chalk.blue(`\nPro tip: Make sure .agent is in your .gitignore!`));
        }

    } catch (error) {
        spinner.fail(chalk.red('Installation failed.'));
        console.error(chalk.red(error.message));
        process.exit(1);
    }
}

run();
