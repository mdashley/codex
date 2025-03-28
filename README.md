# Codex

A simple MCP server that provides a LLM with tools for accessing legislative data from the [Congress.gov API](https://github.com/LibraryOfCongress/api.congress.gov).

## Features

Over 40 tools organized into categories:

- **Amendments**: List amendments, get details, actions, cosponsors, and text
- **Bills**: Search and retrieve bill information, actions, amendments, committees, cosponsors, subjects, summaries, and text
- **Committees**: List committees and get committee details and bills
- **Members**: Access member information, sponsored and cosponsored legislation
- **Nominations**: List and get details about presidential nominations
- **Treaties**: Access treaty information and actions
- **Congressional Record**: Browse congressional record entries
- **Hearings**: Search and get details about congressional hearings
- **Communications**: Access House and Senate communications

## Requirements

- Python 3.10+
- [uv](https://astral.sh/uv) package manager
- Congress.gov API key (set as `CONGRESS_API_KEY` environment variable)

## Setup

```bash
# Clone the repository
git clone https://github.com/mdashley/codex.git
cd codex

# Set up virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

## Connecting to Claude for Desktop

1. Install [Claude for Desktop](https://claude.ai/desktop)
2. Configure Claude to use the server by editing `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "codex": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/PARENT/FOLDER/codex",
        "run",
        "codex.py"
      ],
      "env": {
        "CONGRESS_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

3. Restart Claude for Desktop
4. Look for the hammer icon to confirm tools are available

## Getting a Congress.gov API Key

To fetch data from the Congress.gov API, you need to [request an API key](https://api.congress.gov/sign-up/).

## Troubleshooting

- Check logs at `~/Library/Logs/Claude/mcp*.log`
- Update the uv path in claude_desktop_config.json to be absolute (run `which uv` to find your uv installation path)

## Learn More

- [MCP documentation](https://modelcontextprotocol.io/introduction)
- [Congress.gov API documentation](https://api.congress.gov/)
