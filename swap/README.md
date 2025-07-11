# SWAP

Show status:

```sh
swapon --show
```

Create the file:

```sh
fallocate -l 16G /swapfile
chmod 600 /swapfile
```

Init:

```sh
mkswap /swapfile
```

Activate:

```sh
swapon /swapfile
```

