# Deployment

To deploy the application via Docker, you can run:

```bash
docker-compose up -d --build
```

Ensure the configuration models exist in `models/` (like `nous-hermes-2-solar-10.7b.Q4_K_M.gguf`).

Locally, you may also launch the frontend using:

```bash
python ui/main.py
```
