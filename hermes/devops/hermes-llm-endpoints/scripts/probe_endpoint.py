#!/usr/bin/env python3
"""
Probe an OpenAI-compatible LLM endpoint.

Usage:
    python probe_endpoint.py <base_url> <api_key>

Returns:
    0 = endpoint up, key valid, models listed
    1 = endpoint up, key rejected (401)
    2 = endpoint up, but no /v1/models endpoint (wrong path)
    3 = DNS / network failure
    4 = other HTTP error
    64 = usage error (bad args)
"""
import sys
import json
import ssl
import urllib.request
import urllib.error


def probe(base_url: str, api_key: str) -> int:
    base = base_url.rstrip('/')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(
            f'{base}/models',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        r = urllib.request.urlopen(req, timeout=10, context=ctx)
        j = json.loads(r.read())
        if 'data' in j:
            models = [m.get('id', m) if isinstance(m, dict) else m
                      for m in j['data'][:30]]
            count = len(j.get('data', []))
            print(f'OK: {count} models available')
            for m in models:
                print(f'  - {m}')
            if count > 30:
                print(f'  ... and {count - 30} more')
            return 0
        else:
            print(f'WARN: 200 OK but no "data" field')
            print(f'      body[:200]: {str(j)[:200]}')
            return 2
    except urllib.error.HTTPError as e:
        body = e.read()[:300].decode('utf-8', errors='replace')
        if e.code == 401:
            print(f'AUTH_FAIL: 401')
            print(f'  {body[:200]}')
            return 1
        elif e.code == 404:
            print(f'NO_MODELS_ENDPOINT: 404 at {base}/models')
            print(f'  Try paths: {base}/api/v1/models, {base}/v2/models')
            return 2
        else:
            print(f'HTTP_{e.code}')
            print(f'  {body[:200]}')
            return 4
    except urllib.error.URLError as e:
        reason = str(e.reason) if hasattr(e, 'reason') else str(e)
        if 'getaddrinfo' in reason or 'NameResolution' in reason:
            print(f'DNS_FAIL: {base_url} does not resolve')
            print(f'  Domain is fake or typo. Do NOT edit .env. Abort.')
        elif 'Connection refused' in reason:
            print(f'CONN_REFUSED: {base_url} is down or port is closed')
        elif 'timeout' in reason.lower() or 'timed out' in reason.lower():
            print(f'TIMEOUT: {base_url} did not respond within 10s')
        else:
            print(f'NET_FAIL: {reason[:200]}')
        return 3
    except Exception as e:
        print(f'UNEXPECTED: {type(e).__name__}: {e}')
        return 4


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print()
        print('Examples:')
        print('  python probe_endpoint.py https://moosecloud.cc/v1 sk-...')
        print('  python probe_endpoint.py https://api.openai.com/v1 sk-proj-...')
        sys.exit(64)
    base_url = sys.argv[1]
    api_key = sys.argv[2]
    rc = probe(base_url, api_key)
    sys.exit(rc)


if __name__ == '__main__':
    main()
