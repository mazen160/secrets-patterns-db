package main

import (
	"fmt"
	"os"
	"regexp"
	"strings"

	"gopkg.in/yaml.v2"
)

type Pattern struct {
	Name       string `yaml:"name"`
	Regex      string `yaml:"regex"`
	Confidence string `yaml:"confidence"`
}

type PatternWrapper struct {
	Pattern Pattern `yaml:"pattern"`
}

type Config struct {
	Patterns []PatternWrapper `yaml:"patterns"`
}

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("\nUsage:\n\t%s [regex-db.yml]\n", os.Args[0])
		os.Exit(1)
	}

	// Read YAML file
	data, err := os.ReadFile(os.Args[1])
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		os.Exit(1)
	}

	// Parse YAML
	var config Config
	err = yaml.Unmarshal(data, &config)
	if err != nil {
		fmt.Printf("Error parsing YAML: %v\n", err)
		os.Exit(1)
	}

	allRegexes := make(map[string]bool)
	allNames := make(map[string]bool)

	for _, item := range config.Patterns {
		fmt.Println(item)

		pattern := item.Pattern

		// Validate confidence level
		if pattern.Confidence != "low" && pattern.Confidence != "high" {
			fmt.Printf("Error: confidence must be 'low' or 'high', got '%s'\n", pattern.Confidence)
			os.Exit(1)
		}

		// Check for valid regex
		_, err := regexp.Compile(pattern.Regex)
		if err != nil {
			fmt.Printf("Error: invalid regex '%s': %v\n", pattern.Regex, err)
			os.Exit(1)
		}

		// Check for duplicated regexes
		if allRegexes[pattern.Regex] {
			fmt.Printf("Error: Repeated regex '%s'\n", pattern.Regex)
			os.Exit(1)
		}
		allRegexes[pattern.Regex] = true

		// Check for duplicated names (case insensitive)
		nameLower := strings.ToLower(pattern.Name)
		if allNames[nameLower] {
			fmt.Printf("Error: Duplicated name '%s'\n", pattern.Name)
			os.Exit(1)
		}
		allNames[nameLower] = true
	}

	fmt.Println("\n✅ CI Passed!")
}
