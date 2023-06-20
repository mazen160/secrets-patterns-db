<#
.SYNOPSIS
This function scans the provided files against regular expressions defined in a set of YAML files.
It captures and stores any matches, and produces an output report in a specified format: JSON, CSV, or HTML.

.DESCRIPTION
The Invoke-StaticCodeScan function takes as input the paths of files to scan, the directory of regex definition files in YAML format,
the desired output format, and the path to store the output file.

.PARAMETER pathsToScan
The file paths that will be scanned.

.PARAMETER regexYamlDirectory
The directory where the YAML files containing regex patterns are stored.  Make sure to use the Powershell folder within this repo for the yaml files.

.PARAMETER outputFormat
The format of the output file. Valid options are 'JSON', 'CSV', and 'HTML'.

.PARAMETER outputFilePath
The path where the output file will be stored.

.EXAMPLE
Get-ChildItem -Path "C:\scripts" -Filter "*.ps1" | Invoke-StaticCodeScan -regexYamlDirectory "C:\regexDefinitions" -outputFormat 'CSV' -outputFilePath "C:\Results\output.csv"

.NOTES
Dependencies:
This function requires the powershell-yaml module from Powershell Gallery.
#>

function Invoke-StaticCodeScan {
    [CmdletBinding()]
    param (
        [Parameter(ValueFromPipeline=$true)]
        [System.IO.FileInfo]$fileInfo,

        [Parameter(Mandatory=$true)]
        [string]$regexYamlDirectory,

        [Parameter(Mandatory=$true)]
        [ValidateSet('JSON', 'CSV', 'HTML')]
        [string]$outputFormat,

        [Parameter(Mandatory=$true)]
        [string]$outputFilePath
    )

    begin {
        Import-Module powershell-yaml
        # Create an array to store the results
        $results = @()
        $exceptions = @()

        # Get all YAML files in the directory
        $regexYamlFiles = Get-ChildItem -Path $regexYamlDirectory -Filter "*.yml"

        # Initialize an array to store regex definitions
        $regexDefs = @()

        # Loop through each YAML file and load the regex definitions
        foreach ($regexYamlFile in $regexYamlFiles) {
            $regexYamlContent = ConvertFrom-Yaml (Get-Content -Raw -Path $regexYamlFile.FullName)
            $regexDefs += $regexYamlContent.patterns
        }

    }

    process {
        # Read the file content
        $fileContent = Get-Content -Path $fileInfo.FullName

        # Loop through each pattern in the regex definitions
        foreach ($pattern in $regexDefs) {
            $regex = [Regex]::new($pattern.Values.regex)  # Create a [regex] object

            # Loop through each line in the file content
            for ($i = 0; $i -lt $fileContent.Count; $i++) {
                try {
                    # Get all matches in the line
                    $matched = $regex.Matches($fileContent[$i])

                    # Loop through each match
                    foreach ($match in $matched) {
                        # Add the result to the array
                        $results += New-Object PSObject -Property @{
                            FilePath     = $fileInfo.FullName
                            LineNumber   = $i + 1
                            PatternName  = $pattern.Values.name
                            Regex        = $pattern.Values.regex
                            MatchedLine  = $fileContent[$i]
                            Confidence   = $pattern.Values.confidence
                            MatchedValue = $match.Value
                        }
                    }
                }
                catch {
                    # If an exception is encountered, add it to the exceptions list
                    $exceptions += $_.Exception.Message
                }
            }
        }
    }

    end {
        # If exceptions occurred during the scanning process, write them out and exit the function
        if ($exceptions.Count -gt 0) {
            foreach ($exception in $exceptions) {
                Write-Error $exception
            }
            exit(1)
        }

        # Ensure the output directory exists
        $outputDirectory = Split-Path -Path $outputFilePath -Parent
        if (!(Test-Path $outputDirectory)) {
            New-Item -ItemType Directory -Path $outputDirectory | Out-Null
        }

        # Sort the results by FilePath, PatternName, and LineNumber
        $sortedResults = $results | Sort-Object FilePath, PatternName, LineNumber

        # Output the sorted results based on the chosen output format
        switch ($outputFormat) {
            'JSON' {
                $sortedResults | ConvertTo-Json | Out-File $outputFilePath
            }
            'CSV' {
                $sortedResults | Export-Csv -NoTypeInformation -path $outputFilePath
            }
            'HTML' {
                $html = $sortedResults | ConvertTo-Html -Property FilePath, LineNumber, PatternName, MatchedLine, Confidence
                $html = $html -replace "<table>", "<table style='border-collapse: collapse; width: 100%;'>"
                $html = $html -replace "<th>", "<th style='border: 1px solid #dddddd; text-align: left; padding: 8px;'>"
                $html = $html -replace "<td>", "<td style='border: 1px solid #dddddd; text-align: left; padding: 8px;'>"
                $html | Out-File $outputFilePath
            }
        }
    }
}
