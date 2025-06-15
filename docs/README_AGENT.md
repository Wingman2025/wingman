# Wingman AI Chatbot – Detailed Architecture

Este documento profundiza en la arquitectura y el flujo de contexto del agente `InstructorWingfoil`, responsable de motivar a los usuarios y guiarlos en su progreso con el wingfoil.

---
## 1. Objetivo del Agente

El chatbot es como tu **entrenador personal** de wingfoil.

• **Entrenador** → `wingfoil_agent` (objeto `Agent[UserProfile]`).
• **Ficha de alumno** → `UserProfile` (modelo con tus datos: nombre, nivel, etc.).
• Cuando el entrenador necesita detalles, abre la ficha con el tool `get_user_profile`.
• Para recordar tus últimas prácticas, consulta el tool `fetch_user_sessions`.
• Para revisar tus metas activas, usa el tool `fetch_user_goals`.

Con esto puede:
1. Animarte a practicar y registrar más sesiones.
2. Sugerir ejercicios o clases según tu nivel.
3. Hablar contigo de forma clara usando sólo los datos necesarios.

### ⚠️ ¿Qué pasa si no hay datos?
- El agente **siempre** recibe una ficha `UserProfile`, aunque esté vacía (todos los campos en None).
- Si no hay datos, los tools (`get_user_profile`, `fetch_user_sessions`, `fetch_user_goals`) devuelven respuestas neutras como "Perfil no disponible" o listas vacías.
- El modelo tiene instrucciones claras: _No debes asumir información personal o progreso del usuario a menos que te sea explícitamente proporcionado vía contexto o herramientas. Si no tienes datos concretos, mantén la conversación neutra._

**Ventajas:**
- El agente nunca inventa ni asume datos del usuario.
- Experiencia segura y profesional para usuarios nuevos o no autenticados.
- Código más robusto y predecible.

---
## 2. Componentes Clave
| Componente | Descripción |
|------------|-------------|
| `gpt-4o` | Modelo usado para todas las respuestas. |
| `UserProfile` (Pydantic) | Contexto estructurado con datos del usuario (id, nombre, nivel, etc.). |
| `generate_instructions` | Prompt base. Indica al modelo que puede llamar a los tools para obtener contexto cuando lo necesite. |
| `get_user_profile` (tool) | Devuelve resumen compacto del perfil actual. |
| `fetch_user_sessions` (tool) | Devuelve JSON con las últimas 5 sesiones del usuario. |
| `fetch_user_goals` (tool) | Devuelve JSON con las metas recientes del usuario. |
| `inappropriate_guardrail` | Bloquea lenguaje ofensivo antes de que llegue al modelo. |



- **messages**: lista de dicts con rol (`user` o `assistant`) y `content`, limitada a los últimos 10 turnos.
- **context**: instancia de `UserProfile`; _no se serializa en la prompt_. Los tools la consumen cuando se invocan.

---
## 4. Estrategias de Contexto
1. **Perfil bajo demanda**: el modelo lo obtiene llamando `get_user_profile`, evitando repetir datos innecesarios.
2. **Historial acotado**: sólo se envían los últimos 10 turnos. Se puede ajustar mediante `MAX_HISTORY=10`.
3. **Guardrails**: aseguran que no se procese lenguaje abusivo y mantienen la conversación profesional.

### Posibles Mejoras Futuras
| Mejora | Ventaja | Consideración |
|--------|---------|---------------|
| Resumen automático cada 20 turnos | Menos tokens en conversaciones largas | Costo extra de llamada LLM |
| Vector Store (Redis/Pinecone) | Memoria a largo plazo y búsqueda semántica | Infraestructura adicional |
| Cache de `UserProfile` en frontend | Menos lecturas de BD | Mantener sincronización cuando el usuario edite su perfil |

---
## 5. Configuración del Agente (código)
```python
wingfoil_agent = Agent[UserProfile](
    name="InstructorWingfoil",
    model="gpt-4o",
    instructions=generate_instructions,
    tools=[get_user_profile, fetch_user_sessions, fetch_user_goals],
    input_guardrails=[inappropriate_guardrail]
)
```

---
## 6. Seguridad & Privacidad
- **Datos personales**: El agente accede a perfil e historial sólo del usuario autenticado.
- **Guardrails**: Evitan contenido ofensivo tanto de entrada como de salida.
- **Límites de tokens**: Se controla el número de mensajes e incluye truncado a 200 caracteres para prevenir fugas de datos extensos.

---
## 7. Preguntas Frecuentes
1. **¿Por qué enviar contexto en cada request?**  
   El backend es sin estado; cada petición puede llegar a un worker distinto. Se necesita reenviar la parte mínima de contexto (perfil + últimos mensajes) para mantener coherencia.
2. **¿El perfil se muestra al usuario?**  
   No. Se pasa como estructura de datos y sólo se expone vía `get_user_profile` cuando el modelo decide que es relevante.
3. **¿Cómo ajusto la cantidad de historial?**  
   Modifica el límite en `chat_api` (`if len(history_list) > 10:`).

---
## 8. Referencias
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [Flask](https://flask.palletsprojects.com)
