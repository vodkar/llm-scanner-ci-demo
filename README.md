# llm-scanner CI demo

A tiny Flask service used to demonstrate [llm-scanner](https://github.com/vodkar/llm_scanner)
running on pull requests.

## How the scan works

`.github/workflows/llm-scanner.yml` runs on every pull request:

1. Neo4j 5 runs as a GitHub Actions service container on the runner.
2. The runner joins the tailnet with `tailscale/github-action` (ephemeral node, `tag:ci`).
3. The LLM (`google/gemma-4-E2B-it`, GGUF via llama.cpp) runs on a self-hosted Mac and is
   reached over Tailscale at `http://$LLM_HOST:8000/v1`.
4. `llm-scanner scan --mode diff` reviews only the lines changed by the PR, then the
   SARIF report goes to GitHub code scanning, and the JSON report is saved as a build artifact.

## Required configuration

| Kind     | Name                       | Value                                           |
|----------|----------------------------|-------------------------------------------------|
| Secret   | `TS_OAUTH_CLIENT_ID`       | Tailscale OAuth client id (scope `auth_keys`, tag `tag:ci`) |
| Secret   | `TS_OAUTH_SECRET`          | Tailscale OAuth client secret                   |
| Variable | `LLM_HOST`                 | Tailscale IP / MagicDNS name of the LLM host    |

Serve the model on the LLM host:

```bash
llama-server -hf ggml-org/gemma-4-E2B-it-GGUF:Q8_0 --alias google/gemma-4-E2B-it \
  --jinja --host 0.0.0.0 --port 8000 -c 196608 -np 6 --no-kv-unified
```

Six 32K-token slots serve two concurrent contexts × three self-consistency samples
(`--llm-self-consistency 3` sends one `n=3` request per context).
