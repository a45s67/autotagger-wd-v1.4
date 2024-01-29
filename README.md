# autotagger-wd-v1.4

## prequisite
- git lfs: `git lfs install`

## Usage
```
docker-composer up -d
```

## Test
Upload any image you want to test. (e.g. yamata.png)
```
curl -F file=@yamata.png 127.0.0.1:5000/evaluate | jq '.[0].tags'
```
