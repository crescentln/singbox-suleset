# My Sing-box Ruleset

Simple, automated Sing-box ruleset generator.

## How to use

1. **Add Rules**: Open the `rules/` folder and edit the `.txt` files.
    - Add one domain or IP per line.
    - Lines starting with `#` are ignored.
    - You can create new `.txt` files (e.g., `rules/my-reject.txt`).

2. **Update**: Commit and push your changes to GitHub.

3. **Get Links**:
    - The GitHub Action will automatically run.
    - The compiled rule sets will be in the `output/` folder.
    - You can use the Raw GitHub URL in your Sing-box configuration.
    - Example: `https://raw.githubusercontent.com/<USERNAME>/<REPO>/main/output/demo-proxy.json`
    - Or if compiled to srs: `https://raw.githubusercontent.com/<USERNAME>/<REPO>/main/output/demo-proxy.srs`

## External Rules

The system mirrors rulesets from `SukkaW/Surge` (converted to Sing-box compatible format).
Included by default:
- **ALL** rulesets found on [SukkaW/Surge](https://github.com/SukkaW/Surge) are automatically mirrored.
- The system scrapes the README page daily to discover new rules.
- Included categories: AdBlocking, Streaming, AI, Apple, Microsoft, Direct/Proxy, etc.

To add more external sources, edit `scripts/sources.json`.

## Local Development

To build locally:

```bash
python3 scripts/build.py
```
