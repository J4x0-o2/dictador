# Dictador

Dictado por voz local para Windows. Presioná un atajo, hablá, y el texto aparece en la aplicación donde estés. Todo corre en tu PC con [faster-whisper](https://github.com/SYSTRAN/faster-whisper): el audio nunca sale de tu máquina.

## Instalación

Abrí PowerShell y ejecutá:

```powershell
irm https://raw.githubusercontent.com/J4x0-o2/dictador/main/install.ps1 | iex
```

El instalador te pregunta qué modelo usar (por defecto `small`), instala Python y las dependencias de forma aislada con [uv](https://github.com/astral-sh/uv), descarga el modelo y configura el inicio automático con Windows.

## Uso

| Acción | Cómo |
| --- | --- |
| Empezar / terminar de dictar | `Ctrl+Alt+Espacio` |
| Pausar / reanudar | Clic derecho en el ícono de la bandeja |
| Salir | Clic derecho → Salir |

El texto se pega con `Ctrl+V` **sin presionar Enter**, para que puedas revisarlo antes de enviarlo.

Colores del ícono: naranja = cargando, azul = listo, rojo = grabando, gris = en pausa.

## Configuración

Todo queda en `%LOCALAPPDATA%\Dictador`:

- `config.json`: modelo de Whisper (`base`, `small`, `medium`, `large-v3-turbo`). Reiniciá Dictador después de cambiarlo.
- `dictado.log`: registro de cada grabación y transcripción.

## Desinstalación

```powershell
irm https://raw.githubusercontent.com/J4x0-o2/dictador/main/uninstall.ps1 | iex
```

## Desarrollo

```powershell
uv venv --python 3.11
uv pip install -r requirements.txt pytest
.venv\Scripts\python -m pytest
.venv\Scripts\python dictado.py
```
