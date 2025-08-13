# Notes

## Prepare for devontainer

- Use a go-container
- Add python feature
- Add grpcurl (https://github.com/fullstorydev/grpcurl)

## Find out about the gRPC Reflection API

Example, when controller-standalone is running:

```bash
grpcurl -plaintext -d @ localhost:8080 grpc.health.v1.Health/Check
```
