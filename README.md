# autotagger-wd-v1.4

## prequisite
- git lfs: `git lfs install`

## Test
```
curl -F file=@yamata.png 127.0.0.1:5000/evaluate | jq '.[0].tags'

```
