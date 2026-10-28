# Ticket Assistant

Proyecto de práctica: FastAPI + Claude (salida estructurada y streaming) + React/TypeScript con TanStack Query.

## Cómo correrlo

El proveedor del LLM se elige con la variable `LLM_PROVIDER`:

| Valor            | Qué usa                                   | Necesita                          |
| ---------------- | ----------------------------------------- | --------------------------------- |
| `ollama` (default) | Modelo local (`OLLAMA_MODEL`, default `qwen2.5:0.5b`) | Ollama instalado, gratis |
| `claude`         | Claude vía API de Anthropic               | `ANTHROPIC_API_KEY` (pago)        |
| `fake`           | Respuestas fijas, sin modelo              | Nada                              |

**Backend** (terminal 1):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:LLM_PROVIDER = "ollama"   # o "fake" / "claude"
uvicorn app.main:app --reload
```

Docs interactivas en http://localhost:8000/docs

**Frontend** (terminal 2):

```powershell
cd frontend
npm run dev
```

Abrí http://localhost:5173

**Tests:**

```powershell
cd backend;  .\.venv\Scripts\python.exe -m pytest
cd frontend; npm test
```

## Estructura

```
backend/app/
  schemas.py   Modelos Pydantic (Ticket, TicketAnalysis, ChatRequest)
  llm.py       Cliente de Claude detrás de una interfaz (LLMClient)
  main.py      Endpoints FastAPI
backend/tests/ pytest con un LLM fake inyectado vía dependency_overrides

frontend/src/
  api.ts                    fetch + lectura del stream
  components/TicketList.tsx useQuery (listar) + useMutation (analizar)
  components/Chat.tsx       chat que va mostrando la respuesta de a poco
  *.test.ts(x)              Vitest + Testing Library
```

## Temas para explicar en la entrevista

- **Salida estructurada**: `messages.parse(output_format=TicketAnalysis)` le pasa el JSON schema
  de Pydantic al modelo y valida la respuesta. Los `Literal` restringen los valores posibles,
  así el frontend nunca recibe una categoría inventada.
- **Streaming**: el backend devuelve un `StreamingResponse` que va emitiendo los chunks de
  `stream.text_stream`. El frontend los lee con `response.body.getReader()`. `TextDecoder` con
  `stream: true` evita romper caracteres multibyte (tildes) partidos entre chunks.
  Alternativa: Server-Sent Events, que suma eventos con nombre y reconexión automática.
- **Testeabilidad y proveedores intercambiables**: los endpoints dependen de la interfaz `LLMClient`,
  no de un proveedor concreto. Hay tres implementaciones (Ollama, Claude, Fake) y en los tests se
  inyecta el fake con `app.dependency_overrides`: rápido, gratis y determinístico.
- **No confiar en la salida del LLM**: aunque Ollama restringe la salida al JSON schema, igual se
  valida con Pydantic y un resultado inválido se convierte en un 422 (hay un test para eso).
- **TanStack Query**: `useQuery` para leer (cache, loading, error, reintentos) y `useMutation`
  para acciones que el usuario dispara. En tests se usa `retry: false`.
- **Manejo de errores**: un rechazo del modelo (`stop_reason == "refusal"`) se convierte en un 422.
  Además está activado el fallback del lado del servidor (beta), que reintenta con otro modelo.

## Ideas para extenderlo si te sobra tiempo

- Cancelar el stream desde el front con `AbortController`.
- Invalidar/actualizar el cache de tickets después de analizar (`queryClient.invalidateQueries`).
- Guardar los tickets en SQLite con SQLModel.
- Pasarle al chat el ticket seleccionado como contexto.
