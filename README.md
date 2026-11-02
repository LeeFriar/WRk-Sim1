# Splunk Notable Incident Simulator

A small FastAPI service that simulates Splunk notable incident results for integration and deployment testing.

## API

- `GET /` — service information and links.
- `GET /health` — health check for Docker and Jenkins.
- `GET /api/incidents` — returns 1–5 randomly generated notable incidents per request.

Optional query parameters on `/api/incidents`:

- `count` — set an exact count from 1 to 5.
- `seed` — use a deterministic random seed for repeatable tests.

## Run with Docker

```sh
docker build -t sim1 .
docker run --rm --network lee-net -p 3000:3000 sim1
```

For deployment, the container listens on port 3000 and is attached to `lee-net`; the Compose file intentionally does not publish a host port. Nginx Proxy Manager should connect to the container on `lee-net` at port 3000. Add `lee-net-1` to the Compose networks if the service needs outbound internet access.

## Jenkins

The included `Jenkinsfile` builds the image, runs the test suite in the image, then replaces the running `sim1` container. Configure the Jenkins GitHub webhook job to run this pipeline. Jenkins needs Docker access and a shared Docker network named `lee-net` on the deployment host.

## Cortex XSOAR 8 integration

The custom integration is in `xsoar/integrations/Sim1IncidentSimulator/Sim1IncidentSimulator.yml`. Import the YAML as a custom integration in XSOAR, create an instance, and configure the base URL, Basic Auth username/password, and optional incident count (1–5). Keep certificate validation enabled for the public HTTPS endpoint; the insecure TLS option is only for testing.

The integration's `sim1-get-incidents` command returns incident data in `SIM1.Incident` context. The integration is also configured for periodic fetch, which maps each result to XSOAR's standard `name`, `occurred`, and `rawJSON` fields. Because NPM enforces Basic Auth, supply the same credentials configured in NPM. XSOAR must be able to reach the public URL (or another route to the service).
