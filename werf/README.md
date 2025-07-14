# werf

Docs:

- https://werf.io/

## Secrets

Generate a secret key:

```sh
werf helm secret generate-secret-key
```

Encrypt a yaml files:

```sh
werf helm secret values encrypt .cleartext-secrets.yaml
```
