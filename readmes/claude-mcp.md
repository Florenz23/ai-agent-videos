# Claude Desktop Settings Configuration

https://www.anthropic.com/news/model-context-protocol

https://github.com/modelcontextprotocol/servers/tree/main


This guide explains how to configure settings for the Claude desktop application.

## Configuration Location

The Claude desktop app stores its configuration in the following location:

```bash
~/Library/Application Support/Claude/
```

## Setting Up Configuration

1. **Create the Claude configuration directory if it doesn't exist:**

    ```bash
    open ~/Library/Application\ Support/Claude
    ```

2. **Create the configuration file:**

    ```bash
    touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
    ```

## Configuration Options

The `claude_desktop_config.json` file allows you to customize various settings for the Claude desktop application. Add your desired configuration options in JSON format.

**GitHub integration configuration:**

https://github.com/modelcontextprotocol/servers/tree/main/src/github

```json
{
    "github": {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-github"
        ],
        "env": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": "access-token"
        }
    }
}
```



**Brave Search integration configuration:**

https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search


```json
{
    "brave-search": {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-brave-search"
        ],
        "env": {
            "BRAVE_API_KEY": "api-key"
        }
    }
}
```

## Notes

- **Important:** Ensure that `npx` is installed globally and not managed via `nvm`. This is crucial for the integrations to function correctly.
- Make sure to use valid JSON syntax in the configuration file.
- Restart the Claude desktop application after making changes to apply new settings.
- Back up your configuration file before making significant changes.

## Example Configuration

**Available GitHub operations:**

- `create_or_update_file`: Create/update single file
- `search_repositories`: Search repos
- `create_repository`: Create new repo
- `get_file_contents`: Get file/directory contents
- `push_files`: Push multiple files in one commit
- `create_issue`: Create new issue
- `create_pull_request`: Create new PR
- `fork_repository`: Fork a repo
- `create_branch`: Create new branch

### GitHub Operations

#### Fork Repository
Creates a copy of a repository in your account or specified organization.
```json
{
    "owner": "original-owner",
    "repo": "repository-name",
    "organization": "target-org"  // Optional
}
```

#### Create Branch
Creates a new branch from the default or specified source branch.
```json
{
    "owner": "repository-owner",
    "repo": "repository-name",
    "branch": "new-branch-name",
    "from_branch": "main"  // Optional, defaults to default branch
}
```

#### Search Repositories
Searches GitHub repositories using the provided query.
```json
{
    "query": "search query string",
    "page": 1,        // Optional
    "perPage": 30     // Optional
}
```

#### Create Repository
Creates a new repository in your account.
```json
{
    "name": "new-repository",
    "private": true,
    "description": "Repository description"  // Optional
}
```

#### Get File Contents
Retrieves contents of a file or directory.
```json
{
    "owner": "repository-owner",
    "repo": "repository-name",
    "path": "path/to/file",
    "branch": "main"  // Optional
}
```

#### Create or Update File
Creates or updates a single file.
```json
{
    "owner": "repository-owner",
    "repo": "repository-name",
    "path": "path/to/file",
    "content": "file content",
    "message": "commit message",
    "branch": "target-branch",
    "sha": "existing-file-sha"  // Optional, required for updates
}
```

#### Push Files
Pushes multiple files in a single commit.
```json
{
    "owner": "repository-owner",
    "repo": "repository-name",
    "branch": "target-branch",
    "message": "commit message",
    "files": [
        {
            "path": "path/to/file1",
            "content": "file content"
        },
        {
            "path": "path/to/file2",
            "content": "file content"
        }
    ]
}
```

#### Create Issue
Creates a new issue.
```json
{
    "owner": "repository-owner",
    "repo": "repository-name",
    "title": "Issue title",
    "body": "Issue description",
    "labels": ["bug", "help wanted"]  // Optional
}
```

#### Create Pull Request
Creates a new pull request.
```json
{
    "owner": "repository-owner",
    "repo": "repository-name",
    "title": "Pull request title",
    "head": "source-branch",
    "base": "target-branch",
    "body": "Pull request description"  // Optional
}
```

