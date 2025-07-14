# werf

Docs:

- https://werf.io/

## Secrets

Generate a secret key:

```sh
werf helm secret generate-secret-key
```

Encrypt a yaml file:

```sh
werf helm secret values encrypt .cleartext-secrets.yaml
```
