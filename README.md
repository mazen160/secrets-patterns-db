# 🗄️ Secrets Patterns Database 🗄️

The largest open-source database for detecting secrets, API keys, passwords, tokens, and more. Use secrets-patterns-db to feed your secret scanning engine with regex patterns for identifying secrets.

---

# 🚀 Features

- Over 1600 regular expressions for detecting secrets, passwords, API keys, tokens, and more.
- Format agnostic. A Single format that supports secret detection tools, including Trufflehog and Gitleaks.
- Tested and reviewed Regular expressions.
- Categorized by confidence levels of each pattern.
- All regular expressions are tested against ReDos attacks.

# ❔ Why?

There are limited resources online for Regular Expressions patterns for secrets. TruffleHog offers ~700 as built-in rules. GitLeaks offers ~60 rules. While it's a good start, it's not enough. There's a lot of work that needs to be done for maintenance and keeping up with new secrets patterns.

I have collected and curated Regular Expressions Patterns for Secrets, API Tokens, Keys, and Passwords. I'm open-sourcing the database I built (Secrets-Patterns-DB), and hope that security teams contribute to it!

The Secrets-Patterns-DB contains over 1600 Regular Expressions. I have also written scripts to validate Regexes against ReDoS attacks, and CI jobs to load and validate Regexes, and I also manually cleaned-up invalid ones.

It's in Beta. There’s a lot of room for improvement on the project. I'm looking forward to your Pull Requests and Issues on Github to enhance Secrets-Patterns-DB for everyone.

Are you planning to enhance your secrets detection in your AppSec program? Please take some time to contribute to the project! :pray:

---

# 💻 Contribution

Contribution is always welcome! Please feel free to report issues on Github and create Pull Requestss for new features.

## 📌 Ideas to Start on

Would like to contribute to secrets-patterns-db? Here are some ideas that you may start with:

- Support severity
- Categorize patterns by type?
- Categorize patterns by tags?
- Support more tools?

---

# 📄 License

This work is licensed under a Creative Commons Attribution 4.0 International License.

# 💚 Author

**Mazin Ahmed**

- **Website**: [https://mazinahmed.net](https://mazinahmed.net)
- **Email**: `mazin [at] mazinahmed [dot] net`
- **Twitter**: [https://twitter.com/mazen160](https://twitter.com/mazen160)
- **Linkedin**: [http://linkedin.com/in/infosecmazinahmed](http://linkedin.com/in/infosecmazinahmed)
