#!/usr/bin/env node
var safe = require('safe-regex');
const fs = require('fs');

var argv = process.argv.slice(2);

if (argv.length < 1) {
    console.log("\nUsage:\n\tsafe-regex-check.js [regex-db.yml]")
    process.exit(1)
}

var data = fs.readFileSync(argv[0],
            {encoding:'utf8', flag:'r'}).split("\n");


data.forEach(element => {
    if (safe(element) == false) {
        console.log(element)
    }
});
