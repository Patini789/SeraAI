# bot_config

bot_settings = {
"MAX_TOKENS":8192,
# custom instructions for the model
"INSTRUCTIONS" : """

""",

# boolean toggles
"VOICE_ACTIVE": True, # Text to speech
"SCHOOL": False, # if you want to use the bot in school whith a schedule
"SPEECH_TO_TEXT": False, # Speech to text
"IMAGE_VISION": False, # Image Vision
"CREATE_MEMORIES": False, # if you want the bot to create memories from the conversation
"USE_MEMORIES": True, # if you want the bot to use memories from the conversation
"TRANSLATE_ENABLE": False, # improves de cuality in small models but add latency (a lot of)
# Voice
"VOICE":'es-HN-KarlaNeural',
"RATE":"+10%",
"PITCH":"-10Hz",

# For you database tags
"EXTRA_DATA":[""],
}
discord_config = {
"ENABLE_DISCORD_BOT" : False,
# message for command $help
# Spanish example, change it to your language
"HELP": """ 
**Comandos disponibles:**
1. **$chat [mensaje]**: 
    Envía un mensaje al bot para obtener una respuesta generada por IA. 
    Ejemplo: `$chat ¿Qué opinas del arte digital?`
2. **$help**: 
    Muestra esta lista de comandos y ayuda general sobre el uso del bot. 
    Ejemplo: `$help`
3. **$cls**: 
    Limpia la memoria del bot asociada al usuario. Esto es útil si quieres comenzar una nueva conversación desde cero. 
    Ejemplo: `$cls`
4. **$context [información]**: 
    Establece o actualiza el contexto personalizado para el usuario, que se utilizará en futuras respuestas.
    Ejemplo: `$context Me gusta la ciencia ficción y la programación.`
5. **$check [usuario|list]**: 
    Consulta el contexto guardado de un usuario específico o muestra todos los contextos disponibles.
    - **$check tu_nombre**: Muestra tu contexto actual.
    - **$check list**: Lista todos los contextos guardados.
    Ejemplos: `$check Maria`, `$check list`
**Nota:** El contexto se guarda por nombre de usuario y se reutiliza para hacer las respuestas más personalizadas.
""",

"DISCORD_NAMES": { # if you want to use a nickname for Sera. This also change your user_context name.

},
# User : discord ID
# if you only wanna save put in users but not in active
"notify": {

    "users": {
    "active": {
        "Example": 1111111111111111111
        },
    },
    "channels": {
    "active": {
        },
    }
}

}