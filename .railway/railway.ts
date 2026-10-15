import { defineRailway, project, service } from "railway/iac";

export default defineRailway(() => {
  const cybercareApi = service("cybercare-api", {
    source: { type: "github", rootDirectory: "/backend" },
    build: { buildEnvironment: "V3", builder: "DOCKERFILE", dockerfilePath: "Dockerfile" },
    healthcheck: "/api/health",
    healthcheckTimeout: 120,
    deploy: { restartPolicyType: "ON_FAILURE", restartPolicyMaxRetries: 3 },
    replicas: { "iad": 1 },
  });
  const cybercareWeb = service("cybercare-web", {
    source: { type: "github", rootDirectory: "/frontend" },
    build: { buildEnvironment: "V3", builder: "DOCKERFILE", dockerfilePath: "Dockerfile" },
    healthcheck: "/",
    healthcheckTimeout: 120,
    deploy: { restartPolicyType: "ON_FAILURE", restartPolicyMaxRetries: 3 },
    replicas: { "iad": 1 },
  });

  return project("CyberCare", {
    variables: { managed: false },
    resources: [cybercareApi, cybercareWeb],
  });
});
